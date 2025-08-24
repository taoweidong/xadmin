"""
部门管理相关的Pydantic Schema
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.base import BaseSchema, TimestampSchema, BaseResponse, ListResponse, PaginationParams, BatchDeleteRequest


class DeptBase(BaseSchema):
    """部门基础Schema"""
    name: str = Field(..., max_length=128, description="部门名称")
    code: str = Field(..., max_length=128, description="部门编码")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    is_active: bool = Field(True, description="是否启用")
    rank: int = Field(99, description="排序")
    mode_type: Optional[int] = Field(None, description="模式类型")
    auto_bind: bool = Field(False, description="自动绑定")
    description: Optional[str] = Field(None, max_length=256, description="部门描述")


class DeptCreate(DeptBase):
    """创建部门Schema"""
    pass


class DeptUpdate(BaseSchema):
    """更新部门Schema"""
    name: Optional[str] = Field(None, max_length=128, description="部门名称")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    is_active: Optional[bool] = Field(None, description="是否启用")
    rank: Optional[int] = Field(None, description="排序")
    mode_type: Optional[int] = Field(None, description="模式类型")
    auto_bind: Optional[bool] = Field(None, description="自动绑定")
    description: Optional[str] = Field(None, max_length=256, description="部门描述")


class DeptProfile(DeptBase, TimestampSchema):
    """部门详情Schema"""
    id: int = Field(..., description="部门ID")
    user_count: int = Field(0, description="用户数量")
    
    model_config = ConfigDict(from_attributes=True)


class DeptListParams(PaginationParams):
    """部门列表参数"""
    ordering: Optional[str] = Field(None, description="排序字段")
    search: Optional[str] = Field(None, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否启用")
    code: Optional[str] = Field(None, description="部门编码")
    mode_type: Optional[int] = Field(None, description="模式类型")
    auto_bind: Optional[bool] = Field(None, description="自动绑定")
    name: Optional[str] = Field(None, description="部门名称")
    description: Optional[str] = Field(None, description="部门描述")
    pk: Optional[int] = Field(None, description="部门ID")


class DeptBatchDeleteRequest(BatchDeleteRequest):
    """部门批量删除请求"""
    pass