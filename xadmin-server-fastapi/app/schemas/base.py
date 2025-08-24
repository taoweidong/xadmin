"""
基础Pydantic Schema模型
"""
from typing import Optional, Generic, TypeVar, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

DataT = TypeVar('DataT')


class BaseSchema(BaseModel):
    """基础Schema"""
    model_config = ConfigDict(
        from_attributes=True, 
        arbitrary_types_allowed=True,
        protected_namespaces=()
    )


class TimestampSchema(BaseSchema):
    """时间戳Schema"""
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class BaseResponse(BaseSchema, Generic[DataT]):
    """基础响应模型 - 与Django项目保持一致"""
    code: int = Field(1000, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: Optional[DataT] = Field(None, description="响应数据")


class ListResponse(BaseSchema, Generic[DataT]):
    """列表响应模型 - 与Django项目保持一致"""
    code: int = Field(1000, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 1000,
                "detail": "success",
                "data": {
                    "results": [],
                    "total": 0,
                    "page": 1,
                    "size": 20,
                    "pages": 0
                }
            }
        }
    )


class PaginationParams(BaseSchema):
    """分页参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")
    ordering: Optional[str] = Field(None, description="排序字段")


class SearchParams(PaginationParams):
    """搜索参数"""
    search: Optional[str] = Field(None, description="搜索关键词")


class IDRequest(BaseSchema):
    """ID请求模型"""
    id: int = Field(..., description="记录ID")


class IDListRequest(BaseSchema):
    """ID列表请求模型"""
    ids: List[int] = Field(..., description="记录ID列表")


class BatchDeleteRequest(BaseSchema):
    """批量删除请求模型"""
    pks: List[int] = Field(..., description="要删除的记录ID列表")


class ChoiceItem(BaseSchema):
    """选择项模型"""
    label: str = Field(..., description="显示标签")
    value: Any = Field(..., description="选择值")
    disabled: Optional[bool] = Field(False, description="是否禁用")


class ChoicesResponse(BaseSchema):
    """选择项响应模型"""
    code: int = Field(1000, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: Dict[str, List[ChoiceItem]] = Field(..., description="选择项数据")


class FieldInfo(BaseSchema):
    """字段信息模型"""
    name: str = Field(..., description="字段名")
    label: str = Field(..., description="字段标签")
    field_type: str = Field(..., description="字段类型")
    required: bool = Field(False, description="是否必填")
    choices: Optional[List[ChoiceItem]] = Field(None, description="选择项")


class SearchFieldsResponse(BaseSchema):
    """搜索字段响应模型"""
    code: int = Field(1000, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: List[FieldInfo] = Field(..., description="字段信息列表")


class ColumnInfo(BaseSchema):
    """列信息模型"""
    prop: str = Field(..., description="列属性名")
    label: str = Field(..., description="列标签")
    width: Optional[int] = Field(None, description="列宽度")
    sortable: bool = Field(False, description="是否可排序")
    searchable: bool = Field(False, description="是否可搜索")
    fixed: Optional[str] = Field(None, description="固定位置")


class SearchColumnsResponse(BaseSchema):
    """搜索列响应模型"""
    code: int = Field(1000, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: List[ColumnInfo] = Field(..., description="列信息列表")


class StatusResponse(BaseSchema):
    """状态响应模型"""
    code: int = Field(..., description="状态码")
    detail: str = Field(..., description="响应消息")
    success: bool = Field(..., description="是否成功")


class ExportParams(BaseSchema):
    """导出参数"""
    export_type: str = Field("xlsx", description="导出类型")
    fields: Optional[List[str]] = Field(None, description="导出字段")
    
    
class ImportParams(BaseSchema):
    """导入参数"""
    action: str = Field("check", description="导入动作: check-检查, import-导入")
    file_url: str = Field(..., description="文件URL")