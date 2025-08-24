"""
用户相关数据库模型
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, Table, SmallInteger, Index
)
from sqlalchemy.orm import relationship, remote
from app.models.base import BaseModel, AuditMixin, DescriptionMixin
from datetime import datetime


# 用户角色关联表
user_role_association = Table(
    'user_role_association',
    BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('user_info.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('user_role.id'), primary_key=True),
    comment="用户角色关联表",
    extend_existing=True
)

# 用户数据权限关联表
user_permission_association = Table(
    'user_permission_association',
    BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('user_info.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('data_permission.id'), primary_key=True),
    comment="用户数据权限关联表",
    extend_existing=True
)


class UserInfo(BaseModel, AuditMixin):
    """用户信息表"""
    __tablename__ = 'user_info'
    
    # 基本信息
    username = Column(String(150), unique=True, index=True, nullable=False, comment="用户名")
    password = Column(String(128), nullable=False, comment="密码")
    email = Column(String(254), index=True, nullable=True, comment="邮箱")
    phone = Column(String(16), index=True, nullable=True, comment="手机号")
    
    # 个人信息
    nickname = Column(String(150), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像")
    gender = Column(SmallInteger, default=0, comment="性别: 0-未知, 1-男, 2-女")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_staff = Column(Boolean, default=False, comment="是否员工")
    is_superuser = Column(Boolean, default=False, comment="是否超级用户")
    
    # 时间信息
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    date_joined = Column(DateTime, default=datetime.utcnow, comment="注册时间")
    
    # 关联关系
    dept_id = Column(Integer, ForeignKey('dept_info.id'), nullable=True, comment="部门ID")
    dept = relationship("DeptInfo", back_populates="users")
    
    # 多对多关系
    roles = relationship("UserRole", secondary=user_role_association, back_populates="users")
    permissions = relationship("DataPermission", secondary=user_permission_association, back_populates="users")
    
    # 反向关系
    login_logs = relationship("LoginLog", back_populates="user", cascade="all, delete-orphan")
    operation_logs = relationship("OperationLog", back_populates="user", cascade="all, delete-orphan")
    
    def __str__(self):
        return f"{self.nickname or self.username}({self.username})"


class UserRole(BaseModel, AuditMixin, DescriptionMixin):
    """用户角色表"""
    __tablename__ = 'user_role'
    
    name = Column(String(64), unique=True, nullable=False, comment="角色名称")
    code = Column(String(64), unique=True, nullable=False, comment="角色编码")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort = Column(Integer, default=0, comment="排序")
    
    # 关联关系
    users = relationship("UserInfo", secondary=user_role_association, back_populates="roles")
    menus = relationship("MenuInfo", secondary="role_menu_association", back_populates="roles")
    permissions = relationship("DataPermission", secondary="role_permission_association", back_populates="roles")
    
    def __str__(self):
        return self.name


class DeptInfo(BaseModel, AuditMixin, DescriptionMixin):
    """部门信息表"""
    __tablename__ = 'dept_info'
    
    name = Column(String(64), nullable=False, comment="部门名称")
    code = Column(String(64), unique=True, nullable=False, comment="部门编码")
    parent_id = Column(Integer, ForeignKey('dept_info.id'), nullable=True, comment="父部门ID")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort = Column(Integer, default=0, comment="排序")
    leader = Column(String(64), nullable=True, comment="负责人")
    phone = Column(String(16), nullable=True, comment="联系电话")
    email = Column(String(254), nullable=True, comment="邮箱")
    
    # 自关联关系
    children = relationship("DeptInfo")
    
    # 反向关系
    users = relationship("UserInfo", back_populates="dept")
    
    def __str__(self):
        return self.name


class DataPermission(BaseModel, AuditMixin, DescriptionMixin):
    """数据权限表"""
    __tablename__ = 'data_permission'
    
    name = Column(String(64), nullable=False, comment="权限名称")
    code = Column(String(64), unique=True, nullable=False, comment="权限编码")
    rules = Column(Text, nullable=True, comment="权限规则(JSON)")
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 关联关系
    users = relationship("UserInfo", secondary=user_permission_association, back_populates="permissions")
    roles = relationship("UserRole", secondary="role_permission_association", back_populates="permissions")
    
    def __str__(self):
        return self.name


# 角色菜单关联表
role_menu_association = Table(
    'role_menu_association',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('user_role.id'), primary_key=True),
    Column('menu_id', Integer, ForeignKey('menu_info.id'), primary_key=True),
    comment="角色菜单关联表",
    extend_existing=True
)

# 角色数据权限关联表
role_permission_association = Table(
    'role_permission_association',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('user_role.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('data_permission.id'), primary_key=True),
    comment="角色数据权限关联表",
    extend_existing=True
)






# 创建索引
Index('idx_user_info_username', UserInfo.username)
Index('idx_user_info_email', UserInfo.email)
Index('idx_user_info_phone', UserInfo.phone)
Index('idx_user_info_is_active', UserInfo.is_active)
Index('idx_dept_info_code', DeptInfo.code)
Index('idx_dept_info_parent_id', DeptInfo.parent_id)
Index('idx_user_role_code', UserRole.code)
Index('idx_data_permission_code', DataPermission.code)
