"""
用户相关Pydantic Schema模型
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
from app.schemas.base import BaseSchema, BaseResponse, TimestampSchema, PaginationParams
from datetime import datetime


class UserBase(BaseSchema):
    """用户基础Schema"""
    username: str = Field(..., min_length=3, max_length=150, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=16, description="手机号")
    nickname: Optional[str] = Field(None, max_length=150, description="昵称")
    gender: int = Field(0, description="性别: 0-未知, 1-男, 2-女")
    is_active: bool = Field(True, description="是否激活")
    is_staff: bool = Field(False, description="是否员工")


class UserCreate(UserBase):
    """创建用户Schema"""
    password: str = Field(..., min_length=8, description="密码")
    dept_id: Optional[int] = Field(None, description="部门ID")
    role_ids: List[int] = Field([], description="角色ID列表")


class UserUpdate(BaseSchema):
    """更新用户Schema"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=16, description="手机号")
    nickname: Optional[str] = Field(None, max_length=150, description="昵称")
    gender: Optional[int] = Field(None, description="性别")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_staff: Optional[bool] = Field(None, description="是否员工")
    dept_id: Optional[int] = Field(None, description="部门ID")
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")


class UserPasswordUpdate(BaseSchema):
    """用户密码更新Schema"""
    password: str = Field(..., min_length=8, description="新密码")


class UserProfile(UserBase, TimestampSchema):
    """用户档案Schema"""
    id: int = Field(..., description="用户ID")
    avatar: Optional[str] = Field(None, description="头像")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    date_joined: datetime = Field(..., description="注册时间")
    is_superuser: bool = Field(False, description="是否超级用户")
    
    # 关联信息
    dept_name: Optional[str] = Field(None, description="部门名称")
    role_names: List[str] = Field([], description="角色名称列表")
    
    class Config:
        from_attributes = True


class UserListParams(PaginationParams):
    """用户列表查询参数"""
    search: Optional[str] = Field(None, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否激活")
    dept_id: Optional[int] = Field(None, description="部门ID")
    role_id: Optional[int] = Field(None, description="角色ID")


class UserInfoUpdate(BaseSchema):
    """用户信息更新Schema"""
    nickname: Optional[str] = Field(None, max_length=150, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=16, description="手机号")
    gender: Optional[int] = Field(None, description="性别")
    avatar: Optional[str] = Field(None, description="头像")


# 角色相关Schema
class RoleBase(BaseSchema):
    """角色基础Schema"""
    name: str = Field(..., max_length=64, description="角色名称")
    code: str = Field(..., max_length=64, description="角色编码")
    description: Optional[str] = Field(None, description="角色描述")
    is_active: bool = Field(True, description="是否启用")
    sort: int = Field(0, description="排序")


class RoleCreate(RoleBase):
    """创建角色Schema"""
    menu_ids: List[int] = Field([], description="菜单ID列表")
    permission_ids: List[int] = Field([], description="权限ID列表")


class RoleUpdate(BaseSchema):
    """更新角色Schema"""
    name: Optional[str] = Field(None, max_length=64, description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    is_active: Optional[bool] = Field(None, description="是否启用")
    sort: Optional[int] = Field(None, description="排序")
    menu_ids: Optional[List[int]] = Field(None, description="菜单ID列表")
    permission_ids: Optional[List[int]] = Field(None, description="权限ID列表")


class RoleProfile(RoleBase, TimestampSchema):
    """角色档案Schema"""
    id: int = Field(..., description="角色ID")
    menu_count: int = Field(0, description="菜单数量")
    user_count: int = Field(0, description="用户数量")
    
    class Config:
        from_attributes = True


class RoleListParams(PaginationParams):
    """角色列表查询参数"""
    search: Optional[str] = Field(None, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否启用")


# 部门相关Schema
class DeptBase(BaseSchema):
    """部门基础Schema"""
    name: str = Field(..., max_length=64, description="部门名称")
    code: str = Field(..., max_length=64, description="部门编码")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    description: Optional[str] = Field(None, description="部门描述")
    is_active: bool = Field(True, description="是否启用")
    sort: int = Field(0, description="排序")
    leader: Optional[str] = Field(None, max_length=64, description="负责人")
    phone: Optional[str] = Field(None, max_length=16, description="联系电话")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class DeptCreate(DeptBase):
    """创建部门Schema"""
    pass


class DeptUpdate(BaseSchema):
    """更新部门Schema"""
    name: Optional[str] = Field(None, max_length=64, description="部门名称")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    description: Optional[str] = Field(None, description="部门描述")
    is_active: Optional[bool] = Field(None, description="是否启用")
    sort: Optional[int] = Field(None, description="排序")
    leader: Optional[str] = Field(None, max_length=64, description="负责人")
    phone: Optional[str] = Field(None, max_length=16, description="联系电话")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class DeptProfile(DeptBase, TimestampSchema):
    """部门档案Schema"""
    id: int = Field(..., description="部门ID")
    parent_name: Optional[str] = Field(None, description="父部门名称")
    user_count: int = Field(0, description="用户数量")
    children_count: int = Field(0, description="子部门数量")
    
    class Config:
        from_attributes = True


class DeptTreeNode(DeptProfile):
    """部门树节点Schema"""
    children: List['DeptTreeNode'] = Field([], description="子部门列表")


class DeptListParams(PaginationParams):
    """部门列表查询参数"""
    search: Optional[str] = Field(None, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否启用")
    parent_id: Optional[int] = Field(None, description="父部门ID")


# 数据权限相关Schema
class DataPermissionBase(BaseSchema):
    """数据权限基础Schema"""
    name: str = Field(..., max_length=64, description="权限名称")
    code: str = Field(..., max_length=64, description="权限编码")
    description: Optional[str] = Field(None, description="权限描述")
    rules: Optional[str] = Field(None, description="权限规则(JSON)")
    is_active: bool = Field(True, description="是否启用")


class DataPermissionCreate(DataPermissionBase):
    """创建数据权限Schema"""
    pass


class DataPermissionUpdate(BaseSchema):
    """更新数据权限Schema"""
    name: Optional[str] = Field(None, max_length=64, description="权限名称")
    description: Optional[str] = Field(None, description="权限描述")
    rules: Optional[str] = Field(None, description="权限规则(JSON)")
    is_active: Optional[bool] = Field(None, description="是否启用")


class DataPermissionProfile(DataPermissionBase, TimestampSchema):
    """数据权限档案Schema"""
    id: int = Field(..., description="权限ID")
    
    class Config:
        from_attributes = True


class DataPermissionListParams(PaginationParams):
    """数据权限列表查询参数"""
    search: Optional[str] = Field(None, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否启用")


# 搜索相关Schema
class SearchUserResult(BaseSchema):
    """搜索用户结果Schema"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像")
    dept_name: Optional[str] = Field(None, description="部门名称")


class SearchRoleResult(BaseSchema):
    """搜索角色结果Schema"""
    id: int = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")
    code: str = Field(..., description="角色编码")


class SearchDeptResult(BaseSchema):
    """搜索部门结果Schema"""
    id: int = Field(..., description="部门ID")
    name: str = Field(..., description="部门名称")
    code: str = Field(..., description="部门编码")
    parent_name: Optional[str] = Field(None, description="父部门名称")


# 更新DeptTreeNode的引用
DeptTreeNode.model_rebuild()