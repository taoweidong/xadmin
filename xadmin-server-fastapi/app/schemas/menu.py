"""
菜单管理相关的Pydantic Schema
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.base import BaseSchema, TimestampSchema, BaseResponse, ListResponse, PaginationParams, BatchDeleteRequest


class MenuMetaBase(BaseSchema):
    """菜单元数据基础Schema"""
    title: Optional[str] = Field(None, max_length=64, description="菜单标题")
    icon: Optional[str] = Field(None, max_length=64, description="图标")
    r_svg_name: Optional[str] = Field(None, max_length=64, description="右侧SVG图标")
    is_show_menu: bool = Field(True, description="是否显示菜单")
    is_show_parent: bool = Field(False, description="是否显示父级菜单")
    is_keepalive: bool = Field(False, description="是否缓存页面")
    frame_url: Optional[str] = Field(None, max_length=255, description="iframe链接")
    frame_loading: bool = Field(False, description="iframe加载")
    transition_enter: Optional[str] = Field(None, max_length=64, description="进入动画")
    transition_leave: Optional[str] = Field(None, max_length=64, description="离开动画")
    is_hidden_tag: bool = Field(False, description="是否隐藏标签")
    fixed_tag: bool = Field(False, description="是否固定标签")
    dynamic_level: int = Field(0, description="动态级别")


class MenuMetaCreate(MenuMetaBase):
    """创建菜单元数据Schema"""
    pass


class MenuMetaUpdate(MenuMetaBase):
    """更新菜单元数据Schema"""
    pass


class MenuMetaProfile(MenuMetaBase, TimestampSchema):
    """菜单元数据详情Schema"""
    id: int = Field(..., description="菜单元数据ID")
    
    model_config = ConfigDict(from_attributes=True)


class MenuBase(BaseSchema):
    """菜单基础Schema"""
    name: str = Field(..., max_length=128, description="组件名称或权限代码")
    rank: int = Field(9999, description="排序")
    path: str = Field(..., max_length=255, description="路由路径或API路径")
    component: Optional[str] = Field(None, max_length=255, description="组件路径")
    menu_type: int = Field(0, description="菜单类型(0-目录,1-菜单,2-权限)")
    is_active: bool = Field(True, description="是否启用")
    method: Optional[str] = Field(None, max_length=10, description="HTTP方法")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    model_ids: Optional[List[int]] = Field(None, description="关联模型ID列表")


class MenuCreate(MenuBase):
    """创建菜单Schema"""
    meta: MenuMetaCreate = Field(..., description="菜单元数据")


class MenuUpdate(BaseSchema):
    """更新菜单Schema"""
    name: Optional[str] = Field(None, max_length=128, description="组件名称或权限代码")
    rank: Optional[int] = Field(None, description="排序")
    path: Optional[str] = Field(None, max_length=255, description="路由路径或API路径")
    component: Optional[str] = Field(None, max_length=255, description="组件路径")
    menu_type: Optional[int] = Field(None, description="菜单类型(0-目录,1-菜单,2-权限)")
    is_active: Optional[bool] = Field(None, description="是否启用")
    method: Optional[str] = Field(None, max_length=10, description="HTTP方法")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    meta: Optional[MenuMetaUpdate] = Field(None, description="菜单元数据")
    model_ids: Optional[List[int]] = Field(None, description="关联模型ID列表")


class MenuProfile(MenuBase, TimestampSchema):
    """菜单详情Schema"""
    id: int = Field(..., description="菜单ID")
    meta: MenuMetaProfile = Field(..., description="菜单元数据")
    
    model_config = ConfigDict(from_attributes=True)


class MenuListParams(PaginationParams):
    """菜单列表参数"""
    ordering: Optional[str] = Field(None, description="排序字段")
    search: Optional[str] = Field(None, description="搜索关键词")
    name: Optional[str] = Field(None, description="菜单名称")
    component: Optional[str] = Field(None, description="组件路径")
    title: Optional[str] = Field(None, description="菜单标题")
    path: Optional[str] = Field(None, description="路由路径")


class MenuBatchDeleteRequest(BatchDeleteRequest):
    """菜单批量删除请求"""
    pass