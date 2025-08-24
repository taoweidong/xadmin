"""
文件上传和管理服务
"""
import os
import uuid
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
from PIL import Image, ImageOps
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from fastapi import UploadFile
from app.models.system import UploadFile as UploadFileModel
from app.core.config import settings
from app.schemas.base import PaginationParams
import logging

logger = logging.getLogger(__name__)


class FileUploadService:
    """文件上传服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.media_root = Path(settings.MEDIA_ROOT)
        self.static_root = Path(settings.STATIC_ROOT)
        
        # 确保目录存在
        self.media_root.mkdir(parents=True, exist_ok=True)
        self.static_root.mkdir(parents=True, exist_ok=True)
    
    def get_by_id(self, file_id: int) -> Optional[UploadFileModel]:
        """根据ID获取文件"""
        return self.db.query(UploadFileModel).options(
            joinedload(UploadFileModel.uploader)
        ).filter(
            UploadFileModel.id == file_id,
            UploadFileModel.is_deleted == False
        ).first()
    
    async def upload_file(
        self, 
        file: UploadFile, 
        category: str = "general",
        uploader_id: Optional[int] = None
    ) -> UploadFileModel:
        """上传文件"""
        # 验证文件
        self._validate_file(file)
        
        # 生成文件信息
        file_info = self._generate_file_info(file, category)
        
        # 保存文件到磁盘
        file_path = await self._save_file_to_disk(file, file_info['relative_path'])
        
        # 保存文件记录到数据库
        file_data = {
            'filename': file_info['filename'],
            'original_filename': file.filename,
            'file_path': file_info['relative_path'],
            'file_size': file_info['file_size'],
            'file_type': file_info['file_type'],
            'mime_type': file_info['mime_type'],
            'category': category,
            'uploader_id': uploader_id,
            'is_active': True,
            'download_count': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        upload_file = UploadFileModel(**file_data)
        self.db.add(upload_file)
        self.db.commit()
        self.db.refresh(upload_file)
        
        logger.info(f"File uploaded successfully: {upload_file.filename}")
        return upload_file
    
    async def upload_multiple_files(
        self, 
        files: List[UploadFile], 
        category: str = "general",
        uploader_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """批量上传文件"""
        results = {
            'success_count': 0,
            'failed_count': 0,
            'files': []
        }
        
        for file in files:
            try:
                uploaded_file = await self.upload_file(file, category, uploader_id)
                results['files'].append({
                    'status': 'success',
                    'filename': file.filename,
                    'file_id': uploaded_file.id,
                    'file_url': self.get_file_url(uploaded_file)
                })
                results['success_count'] += 1
            except Exception as e:
                results['files'].append({
                    'status': 'failed',
                    'filename': file.filename,
                    'error': str(e)
                })
                results['failed_count'] += 1
                logger.error(f"Failed to upload file {file.filename}: {e}")
        
        return results
    
    def get_file_list(self, params: PaginationParams, filters: dict = None) -> Dict[str, Any]:
        """获取文件列表"""
        query = self.db.query(UploadFileModel).options(
            joinedload(UploadFileModel.uploader)
        ).filter(UploadFileModel.is_deleted == False)
        
        # 应用过滤条件
        if filters:
            if 'search' in filters and filters['search']:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        UploadFileModel.filename.like(search_term),
                        UploadFileModel.original_filename.like(search_term)
                    )
                )
            
            if 'category' in filters and filters['category']:
                query = query.filter(UploadFileModel.category == filters['category'])
            
            if 'file_type' in filters and filters['file_type']:
                query = query.filter(UploadFileModel.file_type == filters['file_type'])
            
            if 'uploader_id' in filters and filters['uploader_id']:
                query = query.filter(UploadFileModel.uploader_id == filters['uploader_id'])
            
            if 'is_active' in filters:
                query = query.filter(UploadFileModel.is_active == filters['is_active'])
        
        # 应用排序
        if params.ordering:
            if params.ordering.startswith('-'):
                field = params.ordering[1:]
                query = query.order_by(getattr(UploadFileModel, field).desc())
            else:
                query = query.order_by(getattr(UploadFileModel, params.ordering))
        else:
            query = query.order_by(UploadFileModel.created_at.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        files = query.offset(offset).limit(params.size).all()
        
        return {
            'results': files,
            'total': total,
            'page': params.page,
            'size': params.size,
            'pages': (total + params.size - 1) // params.size
        }
    
    def update_file(self, file_id: int, file_data: dict) -> Optional[UploadFileModel]:
        """更新文件信息"""
        file_obj = self.get_by_id(file_id)
        if not file_obj:
            return None
        
        for field, value in file_data.items():
            if hasattr(file_obj, field):
                setattr(file_obj, field, value)
        
        file_obj.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(file_obj)
        return file_obj
    
    def delete_file(self, file_id: int, physical_delete: bool = False) -> bool:
        """删除文件"""
        file_obj = self.get_by_id(file_id)
        if not file_obj:
            return False
        
        if physical_delete:
            # 物理删除文件
            file_path = self.media_root / file_obj.file_path
            if file_path.exists():
                file_path.unlink()
            
            # 从数据库删除记录
            self.db.delete(file_obj)
        else:
            # 软删除
            file_obj.is_deleted = True
            file_obj.deleted_at = datetime.utcnow()
            file_obj.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def get_file_path(self, file_obj: UploadFileModel) -> Path:
        """获取文件物理路径"""
        return self.media_root / file_obj.file_path
    
    def get_file_url(self, file_obj: UploadFileModel) -> str:
        """获取文件访问URL"""
        return f"/media/{file_obj.file_path}"
    
    def increase_download_count(self, file_id: int):
        """增加下载次数"""
        file_obj = self.get_by_id(file_id)
        if file_obj:
            file_obj.download_count += 1
            self.db.commit()
    
    def get_file_statistics(self) -> Dict[str, Any]:
        """获取文件统计信息"""
        # 总文件数和总大小
        total_stats = self.db.query(
            func.count(UploadFileModel.id).label('total_files'),
            func.sum(UploadFileModel.file_size).label('total_size')
        ).filter(
            UploadFileModel.is_deleted == False,
            UploadFileModel.is_active == True
        ).first()
        
        # 按类型统计
        type_stats = self.db.query(
            UploadFileModel.file_type,
            func.count(UploadFileModel.id).label('count')
        ).filter(
            UploadFileModel.is_deleted == False,
            UploadFileModel.is_active == True
        ).group_by(UploadFileModel.file_type).all()
        
        # 按分类统计
        category_stats = self.db.query(
            UploadFileModel.category,
            func.count(UploadFileModel.id).label('count')
        ).filter(
            UploadFileModel.is_deleted == False,
            UploadFileModel.is_active == True
        ).group_by(UploadFileModel.category).all()
        
        # 每日上传统计（最近7天）
        from sqlalchemy import text
        daily_stats = self.db.execute(text("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM upload_file 
            WHERE is_deleted = false 
            AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)).fetchall()
        
        # 处理统计结果
        image_count = sum(stat.count for stat in type_stats if stat.file_type == 'image')
        document_count = sum(stat.count for stat in type_stats if stat.file_type == 'document')
        other_count = sum(stat.count for stat in type_stats if stat.file_type not in ['image', 'document'])
        
        categories = {stat.category: stat.count for stat in category_stats}
        daily_uploads = [{'date': str(stat.date), 'count': stat.count} for stat in daily_stats]
        
        return {
            'total_files': total_stats.total_files or 0,
            'total_size': total_stats.total_size or 0,
            'image_count': image_count,
            'document_count': document_count,
            'other_count': other_count,
            'categories': categories,
            'daily_uploads': daily_uploads
        }
    
    def _validate_file(self, file: UploadFile):
        """验证文件"""
        # 检查文件大小
        if hasattr(file, 'size') and file.size > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE} bytes)")
        
        # 检查文件扩展名
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in settings.ALLOWED_EXTENSIONS:
                raise ValueError(f"不支持的文件类型: {file_ext}")
    
    def _generate_file_info(self, file: UploadFile, category: str) -> Dict[str, Any]:
        """生成文件信息"""
        # 生成唯一文件名
        file_ext = Path(file.filename).suffix if file.filename else ''
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # 生成存储路径（按日期分目录）
        today = datetime.now()
        relative_path = f"uploads/{today.year}/{today.month:02d}/{unique_filename}"
        
        # 确定文件类型
        mime_type, _ = mimetypes.guess_type(file.filename)
        file_type = self._get_file_type(mime_type, file_ext)
        
        return {
            'filename': unique_filename,
            'relative_path': relative_path,
            'file_size': 0,  # 实际大小在保存时获取
            'file_type': file_type,
            'mime_type': mime_type or 'application/octet-stream'
        }
    
    async def _save_file_to_disk(self, file: UploadFile, relative_path: str) -> str:
        """保存文件到磁盘"""
        file_path = self.media_root / relative_path
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_size = 0
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            file_size = len(content)
        
        return str(file_path)
    
    def _get_file_type(self, mime_type: str, file_ext: str) -> str:
        """根据MIME类型和扩展名确定文件类型"""
        if mime_type:
            if mime_type.startswith('image/'):
                return 'image'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('audio/'):
                return 'audio'
            elif mime_type in ['application/pdf', 'application/msword', 
                              'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                              'application/vnd.ms-excel',
                              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                return 'document'
        
        # 根据扩展名判断
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        video_exts = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
        audio_exts = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
        doc_exts = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
        
        if file_ext.lower() in image_exts:
            return 'image'
        elif file_ext.lower() in video_exts:
            return 'video'
        elif file_ext.lower() in audio_exts:
            return 'audio'
        elif file_ext.lower() in doc_exts:
            return 'document'
        else:
            return 'other'


class ImageProcessService:
    """图片处理服务"""
    
    def __init__(self, file_service: FileUploadService):
        self.file_service = file_service
    
    def resize_image(
        self, 
        file_id: int, 
        width: Optional[int] = None, 
        height: Optional[int] = None,
        quality: int = 80,
        format: str = 'JPEG'
    ) -> Optional[bytes]:
        """调整图片大小"""
        file_obj = self.file_service.get_by_id(file_id)
        if not file_obj or file_obj.file_type != 'image':
            return None
        
        file_path = self.file_service.get_file_path(file_obj)
        if not file_path.exists():
            return None
        
        try:
            with Image.open(file_path) as img:
                # 转换为RGB模式（如果需要）
                if format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 调整大小
                if width or height:
                    # 计算目标尺寸
                    original_width, original_height = img.size
                    
                    if width and height:
                        # 指定了宽高，直接缩放
                        new_size = (width, height)
                    elif width:
                        # 只指定宽度，按比例计算高度
                        ratio = width / original_width
                        new_height = int(original_height * ratio)
                        new_size = (width, new_height)
                    else:
                        # 只指定高度，按比例计算宽度
                        ratio = height / original_height
                        new_width = int(original_width * ratio)
                        new_size = (new_width, height)
                    
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 保存到内存
                from io import BytesIO
                buffer = BytesIO()
                img.save(buffer, format=format, quality=quality)
                return buffer.getvalue()
                
        except Exception as e:
            logger.error(f"Failed to process image {file_id}: {e}")
            return None
    
    def generate_thumbnail(self, file_id: int, size: int = 200) -> Optional[bytes]:
        """生成缩略图"""
        return self.resize_image(file_id, width=size, height=size, quality=70)