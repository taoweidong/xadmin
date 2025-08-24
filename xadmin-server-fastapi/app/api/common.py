"""
通用功能API路由
"""
import time
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_permission
from app.core.config import settings
from app.schemas.base import BaseResponse, ListResponse, PaginationParams
from app.schemas.common import (
    UploadResponse, BatchUploadResponse, UploadFileProfile, 
    UploadFileListParams, UploadFileUpdate, ImageProcessRequest,
    FileStatisticsResponse, HealthCheckResponse, SystemInfoResponse,
    QRCodeRequest, QRCodeResponse, ExportRequest, ImportRequest, ImportResponse
)
from app.services.file_upload import FileUploadService, ImageProcessService
from app.services.common_tools import SystemInfoService, QRCodeService, DataExportService, DataImportService
from app.models.user import UserInfo
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# 文件上传相关接口
@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form("general"),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """单文件上传"""
    try:
        file_service = FileUploadService(db)
        uploaded_file = await file_service.upload_file(file, category, current_user.id)
        
        return UploadResponse(
            code=1000,
            detail="文件上传成功",
            data={
                "id": uploaded_file.id,
                "filename": uploaded_file.filename,
                "original_filename": uploaded_file.original_filename,
                "file_path": uploaded_file.file_path,
                "file_size": uploaded_file.file_size,
                "file_type": uploaded_file.file_type,
                "mime_type": uploaded_file.mime_type,
                "file_url": file_service.get_file_url(uploaded_file)
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件上传失败"
        )


@router.post("/upload/batch", response_model=BatchUploadResponse)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    category: str = Form("general"),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """批量文件上传"""
    try:
        file_service = FileUploadService(db)
        result = await file_service.upload_multiple_files(files, category, current_user.id)
        
        return BatchUploadResponse(
            code=1000,
            detail=f"批量上传完成，成功：{result['success_count']}，失败：{result['failed_count']}",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Batch upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量上传失败"
        )


@router.get("/file", response_model=ListResponse[List[UploadFileProfile]])
async def get_file_list(
    params: UploadFileListParams = Depends(),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("file:read"))
):
    """获取文件列表"""
    file_service = FileUploadService(db)
    
    filters = {}
    if params.search:
        filters['search'] = params.search
    if params.category:
        filters['category'] = params.category
    if params.file_type:
        filters['file_type'] = params.file_type
    if params.uploader_id:
        filters['uploader_id'] = params.uploader_id
    if params.is_active is not None:
        filters['is_active'] = params.is_active
    
    result = file_service.get_file_list(params, filters)
    
    # 转换为响应格式
    file_profiles = []
    for file_obj in result['results']:
        profile = UploadFileProfile(
            id=file_obj.id,
            filename=file_obj.filename,
            original_filename=file_obj.original_filename,
            file_path=file_obj.file_path,
            file_size=file_obj.file_size,
            file_type=file_obj.file_type,
            mime_type=file_obj.mime_type,
            category=file_obj.category,
            is_active=file_obj.is_active,
            uploader_id=file_obj.uploader_id,
            uploader_name=file_obj.uploader.nickname if file_obj.uploader else None,
            download_count=file_obj.download_count,
            created_at=file_obj.created_at,
            updated_at=file_obj.updated_at,
            file_url=file_service.get_file_url(file_obj)
        )
        file_profiles.append(profile)
    
    return ListResponse(
        code=1000,
        detail="success",
        data={
            "results": file_profiles,
            "total": result['total'],
            "page": result['page'],
            "size": result['size'],
            "pages": result['pages']
        }
    )


@router.get("/file/{file_id}", response_model=BaseResponse[UploadFileProfile])
async def get_file_detail(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取文件详情"""
    file_service = FileUploadService(db)
    file_obj = file_service.get_by_id(file_id)
    
    if not file_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    profile = UploadFileProfile(
        id=file_obj.id,
        filename=file_obj.filename,
        original_filename=file_obj.original_filename,
        file_path=file_obj.file_path,
        file_size=file_obj.file_size,
        file_type=file_obj.file_type,
        mime_type=file_obj.mime_type,
        category=file_obj.category,
        is_active=file_obj.is_active,
        uploader_id=file_obj.uploader_id,
        uploader_name=file_obj.uploader.nickname if file_obj.uploader else None,
        download_count=file_obj.download_count,
        created_at=file_obj.created_at,
        updated_at=file_obj.updated_at,
        file_url=file_service.get_file_url(file_obj)
    )
    
    return BaseResponse(
        code=1000,
        detail="success",
        data=profile
    )


@router.put("/file/{file_id}", response_model=BaseResponse[UploadFileProfile])
async def update_file(
    file_id: int,
    file_data: UploadFileUpdate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("file:update"))
):
    """更新文件信息"""
    file_service = FileUploadService(db)
    
    update_dict = file_data.dict(exclude_unset=True)
    updated_file = file_service.update_file(file_id, update_dict)
    
    if not updated_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    profile = UploadFileProfile(
        id=updated_file.id,
        filename=updated_file.filename,
        original_filename=updated_file.original_filename,
        file_path=updated_file.file_path,
        file_size=updated_file.file_size,
        file_type=updated_file.file_type,
        mime_type=updated_file.mime_type,
        category=updated_file.category,
        is_active=updated_file.is_active,
        uploader_id=updated_file.uploader_id,
        uploader_name=updated_file.uploader.nickname if updated_file.uploader else None,
        download_count=updated_file.download_count,
        created_at=updated_file.created_at,
        updated_at=updated_file.updated_at,
        file_url=file_service.get_file_url(updated_file)
    )
    
    return BaseResponse(
        code=1000,
        detail="文件信息更新成功",
        data=profile
    )


@router.delete("/file/{file_id}", response_model=BaseResponse[None])
async def delete_file(
    file_id: int,
    physical: bool = Query(False, description="是否物理删除"),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("file:delete"))
):
    """删除文件"""
    file_service = FileUploadService(db)
    success = file_service.delete_file(file_id, physical)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    return BaseResponse(
        code=1000,
        detail="文件删除成功",
        data=None
    )


@router.get("/file/{file_id}/download")
async def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """下载文件"""
    file_service = FileUploadService(db)
    file_obj = file_service.get_by_id(file_id)
    
    if not file_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    file_path = file_service.get_file_path(file_obj)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 增加下载次数
    file_service.increase_download_count(file_id)
    
    # 返回文件流
    def iter_file():
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
    
    return StreamingResponse(
        iter_file(),
        media_type=file_obj.mime_type,
        headers={
            "Content-Disposition": f"attachment; filename={file_obj.original_filename}"
        }
    )


@router.post("/image/{file_id}/process")
async def process_image(
    file_id: int,
    process_request: ImageProcessRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """处理图片（调整大小、格式转换等）"""
    file_service = FileUploadService(db)
    image_service = ImageProcessService(file_service)
    
    processed_image = image_service.resize_image(
        file_id=file_id,
        width=process_request.width,
        height=process_request.height,
        quality=process_request.quality,
        format=process_request.format
    )
    
    if not processed_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片不存在或处理失败"
        )
    
    # 根据格式设置MIME类型
    mime_type_map = {
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
        'WEBP': 'image/webp'
    }
    
    return Response(
        content=processed_image,
        media_type=mime_type_map.get(process_request.format, 'image/jpeg')
    )


@router.get("/file/statistics", response_model=FileStatisticsResponse)
async def get_file_statistics(
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("file:read"))
):
    """获取文件统计信息"""
    file_service = FileUploadService(db)
    statistics = file_service.get_file_statistics()
    
    return FileStatisticsResponse(
        code=1000,
        detail="success",
        data=statistics
    )


# 系统工具接口
@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """健康检查"""
    health_status = SystemInfoService.check_health()
    
    return HealthCheckResponse(
        status=health_status['status'],
        timestamp=time.time(),
        version=settings.VERSION,
        database=health_status['database'],
        redis=health_status['redis']
    )


@router.get("/system/info", response_model=SystemInfoResponse)
async def get_system_info(
    current_user: UserInfo = Depends(require_permission("system:read"))
):
    """获取系统信息"""
    system_info = SystemInfoService.get_system_info()
    
    return SystemInfoResponse(
        code=1000,
        detail="success",
        data=system_info
    )


@router.post("/qrcode", response_model=QRCodeResponse)
async def generate_qrcode(
    request: QRCodeRequest,
    current_user: UserInfo = Depends(get_current_active_user)
):
    """生成二维码"""
    try:
        qrcode_data = QRCodeService.generate_qrcode(
            content=request.content,
            size=request.size,
            border=request.border,
            error_correction=request.error_correction
        )
        
        return QRCodeResponse(
            code=1000,
            detail="二维码生成成功",
            data=qrcode_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/export", response_model=BaseResponse[dict])
async def export_data(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("export:create"))
):
    """导出数据"""
    try:
        export_service = DataExportService(db)
        
        # 执行导出
        file_data = export_service.export_data(
            table_name=request.table_name,
            export_type=request.export_type,
            fields=request.fields,
            filters=request.filters,
            limit=request.limit
        )
        
        # 保存导出文件
        import uuid
        filename = f"export_{uuid.uuid4().hex}.{request.export_type}"
        file_path = settings.MEDIA_ROOT / "exports" / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        return BaseResponse(
            code=1000,
            detail="数据导出成功",
            data={
                "filename": filename,
                "download_url": f"/media/exports/{filename}",
                "file_size": len(file_data)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/import/preview", response_model=ImportResponse)
async def preview_import_data(
    request: ImportRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("import:create"))
):
    """预览导入数据"""
    try:
        file_service = FileUploadService(db)
        import_service = DataImportService(db)
        
        # 获取文件
        file_obj = file_service.get_by_id(request.file_id)
        if not file_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        file_path = file_service.get_file_path(file_obj)
        
        # 预览导入
        result = import_service.preview_import(str(file_path), request.table_name)
        
        return ImportResponse(
            code=1000,
            detail="预览成功",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/import", response_model=ImportResponse)
async def import_data(
    request: ImportRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("import:create"))
):
    """导入数据"""
    try:
        file_service = FileUploadService(db)
        import_service = DataImportService(db)
        
        # 获取文件
        file_obj = file_service.get_by_id(request.file_id)
        if not file_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        file_path = file_service.get_file_path(file_obj)
        
        # 执行导入
        result = import_service.import_data(
            str(file_path), 
            request.table_name, 
            request.mapping
        )
        
        return ImportResponse(
            code=1000,
            detail="导入完成",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )