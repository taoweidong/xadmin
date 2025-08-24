# 数据库模型模块

from .base import BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin, DescriptionMixin
from .user import UserInfo, UserRole, DeptInfo, DataPermission
from .system import MenuInfo, SystemConfig, UserPersonalConfig, ModelLabelField, UploadFile
from .log import LoginLog, OperationLog, NoticeMessage, NoticeUserRead
from sqlalchemy.orm import relationship



# 导出所有模型类
__all__ = [
    'BaseModel',
    'TimestampMixin', 
    'SoftDeleteMixin',
    'AuditMixin',
    'DescriptionMixin',
    'UserInfo',
    'UserRole', 
    'DeptInfo',
    'DataPermission',
    'MenuInfo',
    'SystemConfig',
    'UserPersonalConfig',
    'ModelLabelField',
    'UploadFile',
    'LoginLog',
    'OperationLog',
    'NoticeMessage',
    'NoticeUserRead',

]