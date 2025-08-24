"""
数据库基础模型
"""
from sqlalchemy import Column, Integer, DateTime, Boolean, String, Text
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base
from datetime import datetime
import uuid


class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")


class BaseModel(Base, TimestampMixin):
    """基础模型类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    
    @declared_attr
    def __tablename__(cls):
        # 自动生成表名（类名转小写加下划线）
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class SoftDeleteMixin:
    """软删除混入类"""
    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")


class UUIDMixin:
    """UUID混入类"""
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True, comment="UUID")


class CreatorMixin:
    """创建者混入类"""
    created_by = Column(Integer, nullable=True, comment="创建者ID")
    updated_by = Column(Integer, nullable=True, comment="更新者ID")


class AuditMixin(CreatorMixin, SoftDeleteMixin):
    """审计混入类（包含创建者和软删除）"""
    pass


class DescriptionMixin:
    """描述混入类"""
    description = Column(Text, nullable=True, comment="描述")
    remark = Column(Text, nullable=True, comment="备注")