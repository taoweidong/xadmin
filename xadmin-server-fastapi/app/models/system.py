from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, SmallInteger, JSON, Index, Table
)
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, AuditMixin, DescriptionMixin
from datetime import datetime


class MenuMeta(BaseModel, AuditMixin):
    """菜单元数据表"""
    __tablename__ = 'menu_meta'
    
    # 基本信息
    title = Column(String(64), nullable=True, comment="菜单标题")
    icon = Column(String(64), nullable=True, comment="左侧图标")
    r_svg_name = Column(String(64), nullable=True, comment="右侧SVG图标")
    
    # 显示控制
    is_show_menu = Column(Boolean, default=True, comment="是否显示菜单")
    is_show_parent = Column(Boolean, default=False, comment="是否显示父级菜单")
    is_keepalive = Column(Boolean, default=False, comment="是否缓存页面")
    
    # iframe配置
    frame_url = Column(String(255), nullable=True, comment="iframe链接")
    frame_loading = Column(Boolean, default=False, comment="iframe加载")
    
    # 动画效果
    transition_enter = Column(String(64), nullable=True, comment="进入动画")
    transition_leave = Column(String(64), nullable=True, comment="离开动画")
    
    # 标签控制
    is_hidden_tag = Column(Boolean, default=False, comment="是否隐藏标签")
    fixed_tag = Column(Boolean, default=False, comment="是否固定标签")
    
    # 动态路由
    dynamic_level = Column(Integer, default=0, comment="动态级别")
    
    def __str__(self):
        return self.title or ""


class MenuInfo(BaseModel, AuditMixin):
    """菜单信息表"""
    __tablename__ = 'menu_info'
    
    # 基本信息
    name = Column(String(128), unique=True, nullable=False, comment="组件名称或权限代码")
    path = Column(String(255), nullable=False, comment="路由路径或API路径")
    component = Column(String(255), nullable=True, comment="组件路径")
    
    # 层级信息
    parent_id = Column(Integer, ForeignKey('menu_info.id'), nullable=True, comment="父菜单ID")
    sort = Column(Integer, default=9999, comment="排序")
    
    # 菜单类型: 0-目录, 1-菜单, 2-权限
    menu_type = Column(SmallInteger, default=0, comment="菜单类型")
    
    # 状态控制
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # HTTP方法
    method = Column(String(10), nullable=True, comment="HTTP方法")
    
    # 关联信息
    meta_id = Column(Integer, ForeignKey('menu_meta.id'), nullable=False, comment="菜单元数据ID")
    
    # 自关联关系
    children = relationship("MenuInfo")
    parent = relationship("MenuInfo", remote_side="MenuInfo.id", back_populates="children")
    
    # 关联关系
    meta = relationship("MenuMeta")
    model = relationship("ModelLabelField", secondary="menu_model_association", back_populates="menus")
    roles = relationship("UserRole", secondary="role_menu_association", back_populates="menus")
    
    def __str__(self):
        return self.name


# 菜单与模型关联表
menu_model_association = Table(
    'menu_model_association',
    BaseModel.metadata,
    Column('menu_id', Integer, ForeignKey('menu_info.id'), primary_key=True),
    Column('model_id', Integer, ForeignKey('model_label_field.id'), primary_key=True),
    comment="菜单与模型关联表"
)


class SystemConfig(BaseModel, AuditMixin):
    """系统配置表"""
    __tablename__ = 'system_config'
    
    key = Column(String(64), unique=True, nullable=False, comment="配置键")
    value = Column(Text, nullable=True, comment="配置值")
    name = Column(String(64), nullable=False, comment="配置名称")
    description = Column(Text, nullable=True, comment="配置描述")
    
    # 配置分组
    category = Column(String(32), default='system', comment="配置分类")
    
    # 配置类型: string, number, boolean, json, file
    config_type = Column(String(16), default='string', comment="配置类型")
    
    # 是否启用
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 排序
    sort = Column(Integer, default=0, comment="排序")
    
    def __str__(self):
        return f"{self.name}({self.key})"


class UserPersonalConfig(BaseModel, AuditMixin):
    """用户个人配置表"""
    __tablename__ = 'user_personal_config'
    
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False, comment="用户ID")
    key = Column(String(64), nullable=False, comment="配置键")
    value = Column(Text, nullable=True, comment="配置值")
    name = Column(String(64), nullable=False, comment="配置名称")
    
    # 配置分组
    category = Column(String(32), default='personal', comment="配置分类")
    
    # 配置类型
    config_type = Column(String(16), default='string', comment="配置类型")
    
    # 关联关系
    user = relationship("UserInfo")
    
    # 联合唯一约束
    __table_args__ = (
        Index('idx_user_config_unique', 'user_id', 'key', unique=True),
    )
    
    def __str__(self):
        return f"{self.user.username}:{self.name}"


class ModelLabelField(BaseModel, AuditMixin):
    """模型字段标签表"""
    __tablename__ = 'model_label_field'
    
    name = Column(String(128), nullable=False, comment="字段名称")
    label = Column(String(64), nullable=False, comment="字段标签")
    
    # 父级信息
    parent = Column(String(128), nullable=True, comment="父级字段")
    
    # 字段类型和选项
    field_type = Column(String(32), nullable=True, comment="字段类型")
    choices = Column(JSON, nullable=True, comment="选择项")
    
    # 关联关系
    menus = relationship("MenuInfo", secondary="menu_model_association", back_populates="model")
    
    def __str__(self):
        return f"{self.name}:{self.label}"


class UploadFile(BaseModel, AuditMixin):
    """上传文件表"""
    __tablename__ = 'upload_file'
    
    # 文件信息
    filename = Column(String(255), nullable=False, comment="文件名")
    original_filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(512), nullable=False, comment="文件路径")
    file_size = Column(Integer, default=0, comment="文件大小(字节)")
    file_type = Column(String(64), nullable=True, comment="文件类型")
    mime_type = Column(String(128), nullable=True, comment="MIME类型")
    
    # 文件分类
    category = Column(String(32), default='general', comment="文件分类")
    
    # 上传者信息
    uploader_id = Column(Integer, ForeignKey('user_info.id'), nullable=True, comment="上传者ID")
    uploader = relationship("UserInfo")
    
    # 文件状态
    is_active = Column(Boolean, default=True, comment="是否有效")
    download_count = Column(Integer, default=0, comment="下载次数")
    
    def __str__(self):
        return self.original_filename




# 创建索引
Index('idx_menu_info_parent_id', MenuInfo.parent_id)
Index('idx_menu_info_menu_type', MenuInfo.menu_type)
Index('idx_menu_info_is_active', MenuInfo.is_active)
Index('idx_menu_info_name', MenuInfo.name)
Index('idx_system_config_key', SystemConfig.key)
Index('idx_system_config_category', SystemConfig.category)
Index('idx_upload_file_uploader_id', UploadFile.uploader_id)
Index('idx_upload_file_category', UploadFile.category)