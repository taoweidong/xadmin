"""
通用功能相关Pydantic Schema模型
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.schemas.base import BaseSchema, BaseResponse, TimestampSchema, PaginationParams
from datetime import datetime


class UploadFileBase(BaseSchema):
    """上传文件基础Schema"""
    filename: str = Field(..., max_length=255, description="文件名")
    original_filename: str = Field(..., max_length=255, description="原始文件名")
    file_path: str = Field(..., max_length=512, description="文件路径")
    file_size: int = Field(0, description="文件大小(字节)")
    file_type: Optional[str] = Field(None, max_length=64, description="文件类型")
    mime_type: Optional[str] = Field(None, max_length=128, description="MIME类型")
    category: str = Field("general", max_length=32, description="文件分类")
    is_active: bool = Field(True, description="是否有效")


class UploadFileCreate(UploadFileBase):
    """创建上传文件Schema"""
    uploader_id: Optional[int] = Field(None, description="上传者ID")


class UploadFileUpdate(BaseSchema):
    """更新上传文件Schema"""
    filename: Optional[str] = Field(None, max_length=255, description="文件名")
    category: Optional[str] = Field(None, max_length=32, description="文件分类")
    is_active: Optional[bool] = Field(None, description="是否有效")


class UploadFileProfile(UploadFileBase, TimestampSchema):
    """上传文件档案Schema"""
    id: int = Field(..., description="文件ID")
    uploader_id: Optional[int] = Field(None, description="上传者ID")
    uploader_name: Optional[str] = Field(None, description="上传者名称")
    download_count: int = Field(0, description="下载次数")
    file_url: Optional[str] = Field(None, description="文件访问URL")
    
    model_config = ConfigDict(from_attributes=True)


class UploadFileListParams(PaginationParams):
    """上传文件列表查询参数"""
    search: Optional[str] = Field(None, description="搜索关键词")
    category: Optional[str] = Field(None, description="文件分类")
    file_type: Optional[str] = Field(None, description="文件类型")
    uploader_id: Optional[int] = Field(None, description="上传者ID")
    is_active: Optional[bool] = Field(None, description="是否有效")


class UploadResponse(BaseSchema):
    """文件上传响应Schema"""
    code: int = Field(200, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: Dict[str, Any] = Field(..., description="上传结果")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "detail": "文件上传成功",
                "data": {
                    "id": 1,
                    "filename": "avatar.jpg",
                    "original_filename": "user_avatar.jpg",
                    "file_path": "/uploads/2024/08/avatar.jpg",
                    "file_size": 102400,
                    "file_type": "image",
                    "mime_type": "image/jpeg",
                    "file_url": "http://localhost:8000/media/uploads/2024/08/avatar.jpg"
                }
            }
        }
    )


class BatchUploadResponse(BaseSchema):
    """批量上传响应Schema"""
    code: int = Field(200, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: Dict[str, Any] = Field(..., description="批量上传结果")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "detail": "批量上传完成",
                "data": {
                    "success_count": 3,
                    "failed_count": 1,
                    "files": [
                        {
                            "status": "success",
                            "filename": "file1.jpg",
                            "file_url": "http://localhost:8000/media/uploads/file1.jpg"
                        },
                        {
                            "status": "failed",
                            "filename": "file2.txt",
                            "error": "文件类型不支持"
                        }
                    ]
                }
            }
        }
    )


class DownloadRequest(BaseSchema):
    """文件下载请求Schema"""
    file_id: int = Field(..., description="文件ID")
    filename: Optional[str] = Field(None, description="下载文件名")


class ImageProcessRequest(BaseSchema):
    """图片处理请求Schema"""
    file_id: int = Field(..., description="图片文件ID")
    width: Optional[int] = Field(None, ge=1, le=2000, description="目标宽度")
    height: Optional[int] = Field(None, ge=1, le=2000, description="目标高度")
    quality: Optional[int] = Field(80, ge=1, le=100, description="图片质量")
    format: Optional[str] = Field("JPEG", description="输出格式")
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        allowed_formats = ['JPEG', 'PNG', 'WEBP']
        if v.upper() not in allowed_formats:
            raise ValueError(f'格式必须是 {", ".join(allowed_formats)} 之一')
        return v.upper()


class FileStatistics(BaseSchema):
    """文件统计Schema"""
    total_files: int = Field(0, description="总文件数")
    total_size: int = Field(0, description="总文件大小(字节)")
    image_count: int = Field(0, description="图片文件数")
    document_count: int = Field(0, description="文档文件数")
    other_count: int = Field(0, description="其他文件数")
    categories: Dict[str, int] = Field({}, description="分类统计")
    daily_uploads: List[Dict[str, Any]] = Field([], description="每日上传统计")


class FileStatisticsResponse(BaseResponse[FileStatistics]):
    """文件统计响应Schema"""
    pass


# 通用工具接口Schema
class HealthCheckResponse(BaseSchema):
    """健康检查响应Schema"""
    status: str = Field("healthy", description="服务状态")
    timestamp: float = Field(..., description="检查时间戳")
    version: str = Field(..., description="版本号")
    database: str = Field("connected", description="数据库状态")
    redis: str = Field("connected", description="Redis状态")


class SystemInfoResponse(BaseSchema):
    """系统信息响应Schema"""
    code: int = Field(200, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: Dict[str, Any] = Field(..., description="系统信息")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "detail": "success",
                "data": {
                    "system": {
                        "platform": "Linux",
                        "platform_version": "Ubuntu 20.04",
                        "architecture": "x86_64",
                        "hostname": "fastapi-server"
                    },
                    "python": {
                        "version": "3.11.0",
                        "implementation": "CPython"
                    },
                    "memory": {
                        "total": "8 GB",
                        "available": "6 GB",
                        "percent": 25.0
                    },
                    "disk": {
                        "total": "100 GB",
                        "used": "30 GB",
                        "free": "70 GB",
                        "percent": 30.0
                    }
                }
            }
        }
    )


class QRCodeRequest(BaseSchema):
    """二维码生成请求Schema"""
    content: str = Field(..., max_length=1000, description="二维码内容")
    size: int = Field(200, ge=50, le=1000, description="二维码大小")
    border: int = Field(4, ge=0, le=20, description="边框宽度")
    error_correction: str = Field("M", description="错误纠正级别: L, M, Q, H")
    
    @field_validator('error_correction')
    @classmethod
    def validate_error_correction(cls, v):
        allowed_levels = ['L', 'M', 'Q', 'H']
        if v.upper() not in allowed_levels:
            raise ValueError(f'错误纠正级别必须是 {", ".join(allowed_levels)} 之一')
        return v.upper()


class QRCodeResponse(BaseSchema):
    """二维码生成响应Schema"""
    code: int = Field(200, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: Dict[str, Any] = Field(..., description="二维码数据")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "detail": "success",
                "data": {
                    "qrcode_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
                    "content": "https://example.com",
                    "size": 200
                }
            }
        }
    )


class ExportRequest(BaseSchema):
    """数据导出请求Schema"""
    export_type: str = Field("xlsx", description="导出类型: xlsx, csv, pdf")
    table_name: str = Field(..., description="表名")
    fields: Optional[List[str]] = Field(None, description="导出字段")
    filters: Optional[Dict[str, Any]] = Field(None, description="过滤条件")
    limit: Optional[int] = Field(None, ge=1, le=10000, description="导出数量限制")
    
    @field_validator('export_type')
    @classmethod
    def validate_export_type(cls, v):
        allowed_types = ['xlsx', 'csv', 'pdf']
        if v.lower() not in allowed_types:
            raise ValueError(f'导出类型必须是 {", ".join(allowed_types)} 之一')
        return v.lower()


class ImportRequest(BaseSchema):
    """数据导入请求Schema"""
    file_id: int = Field(..., description="导入文件ID")
    table_name: str = Field(..., description="目标表名")
    action: str = Field("preview", description="导入动作: preview, import")
    mapping: Optional[Dict[str, str]] = Field(None, description="字段映射")
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        allowed_actions = ['preview', 'import']
        if v.lower() not in allowed_actions:
            raise ValueError(f'导入动作必须是 {", ".join(allowed_actions)} 之一')
        return v.lower()


class ImportResponse(BaseSchema):
    """数据导入响应Schema"""
    code: int = Field(200, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: Dict[str, Any] = Field(..., description="导入结果")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "detail": "success",
                "data": {
                    "action": "preview",
                    "total_rows": 100,
                    "valid_rows": 95,
                    "invalid_rows": 5,
                    "columns": ["name", "email", "phone"],
                    "sample_data": [
                        {"name": "张三", "email": "zhangsan@example.com", "phone": "13800138000"},
                        {"name": "李四", "email": "lisi@example.com", "phone": "13800138001"}
                    ],
                    "errors": [
                        {"row": 10, "field": "email", "error": "邮箱格式错误"},
                        {"row": 15, "field": "phone", "error": "手机号格式错误"}
                    ]
                }
            }
        }
    )