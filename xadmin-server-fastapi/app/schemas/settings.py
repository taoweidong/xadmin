"""
设置相关Pydantic Schema模型
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from app.schemas.base import BaseSchema, BaseResponse, TimestampSchema, PaginationParams
from datetime import datetime


class SystemConfigBase(BaseSchema):
    """系统配置基础Schema"""
    key: str = Field(..., max_length=64, description="配置键")
    value: Optional[str] = Field(None, description="配置值")
    name: str = Field(..., max_length=64, description="配置名称")
    description: Optional[str] = Field(None, description="配置描述")
    category: str = Field("system", max_length=32, description="配置分类")
    config_type: str = Field("string", max_length=16, description="配置类型")
    is_active: bool = Field(True, description="是否启用")
    sort: int = Field(0, description="排序")


class SystemConfigCreate(SystemConfigBase):
    """创建系统配置Schema"""
    pass


class SystemConfigUpdate(BaseSchema):
    """更新系统配置Schema"""
    value: Optional[str] = Field(None, description="配置值")
    name: Optional[str] = Field(None, max_length=64, description="配置名称")
    description: Optional[str] = Field(None, description="配置描述")
    category: Optional[str] = Field(None, max_length=32, description="配置分类")
    config_type: Optional[str] = Field(None, max_length=16, description="配置类型")
    is_active: Optional[bool] = Field(None, description="是否启用")
    sort: Optional[int] = Field(None, description="排序")


class SystemConfigProfile(SystemConfigBase, TimestampSchema):
    """系统配置档案Schema"""
    id: int = Field(..., description="配置ID")
    
    class Config:
        from_attributes = True


class SystemConfigListParams(PaginationParams):
    """系统配置列表查询参数"""
    search: Optional[str] = Field(None, description="搜索关键词")
    category: Optional[str] = Field(None, description="配置分类")
    is_active: Optional[bool] = Field(None, description="是否启用")


class SystemConfigBatchUpdate(BaseSchema):
    """批量更新系统配置Schema"""
    configs: List[Dict[str, Any]] = Field(..., description="配置列表")
    
    @field_validator('configs')
    @classmethod
    def validate_configs(cls, v):
        for config in v:
            if 'key' not in config:
                raise ValueError('每个配置必须包含key字段')
        return v


# 用户个人配置相关Schema
class UserPersonalConfigBase(BaseSchema):
    """用户个人配置基础Schema"""
    key: str = Field(..., max_length=64, description="配置键")
    value: Optional[str] = Field(None, description="配置值")
    name: str = Field(..., max_length=64, description="配置名称")
    category: str = Field("personal", max_length=32, description="配置分类")
    config_type: str = Field("string", max_length=16, description="配置类型")


class UserPersonalConfigCreate(UserPersonalConfigBase):
    """创建用户个人配置Schema"""
    pass


class UserPersonalConfigUpdate(BaseSchema):
    """更新用户个人配置Schema"""
    value: Optional[str] = Field(None, description="配置值")
    name: Optional[str] = Field(None, max_length=64, description="配置名称")
    category: Optional[str] = Field(None, max_length=32, description="配置分类")
    config_type: Optional[str] = Field(None, max_length=16, description="配置类型")


class UserPersonalConfigProfile(UserPersonalConfigBase, TimestampSchema):
    """用户个人配置档案Schema"""
    id: int = Field(..., description="配置ID")
    user_id: int = Field(..., description="用户ID")
    
    class Config:
        from_attributes = True


class UserPersonalConfigListParams(PaginationParams):
    """用户个人配置列表查询参数"""
    search: Optional[str] = Field(None, description="搜索关键词")
    category: Optional[str] = Field(None, description="配置分类")


class UserPersonalConfigBatchUpdate(BaseSchema):
    """批量更新用户个人配置Schema"""
    configs: List[Dict[str, Any]] = Field(..., description="配置列表")
    
    @field_validator('configs')
    @classmethod
    def validate_configs(cls, v):
        for config in v:
            if 'key' not in config:
                raise ValueError('每个配置必须包含key字段')
        return v


# 配置分组Schema
class ConfigCategory(BaseSchema):
    """配置分类Schema"""
    category: str = Field(..., description="分类名称")
    name: str = Field(..., description="分类显示名称")
    description: Optional[str] = Field(None, description="分类描述")
    count: int = Field(0, description="配置数量")


class ConfigCategoriesResponse(BaseResponse[List[ConfigCategory]]):
    """配置分类响应Schema"""
    pass


# 配置值类型定义
class ConfigValue(BaseSchema):
    """配置值Schema"""
    key: str = Field(..., description="配置键")
    value: Union[str, int, float, bool, None] = Field(None, description="配置值")
    config_type: str = Field("string", description="配置类型")
    
    @field_validator('value', mode='before')
    @classmethod
    def parse_value(cls, v, info):
        if v is None:
            return None
        
        config_type = info.data.get('config_type', 'string')
        
        if config_type == 'boolean':
            if isinstance(v, str):
                return v.lower() in ('true', '1', 'yes', 'on')
            return bool(v)
        elif config_type == 'number':
            try:
                return float(v) if '.' in str(v) else int(v)
            except (ValueError, TypeError):
                return v
        elif config_type == 'json':
            if isinstance(v, str):
                try:
                    import json
                    return json.loads(v)
                except json.JSONDecodeError:
                    return v
            return v
        else:
            return str(v) if v is not None else None


class ConfigValuesResponse(BaseResponse[Dict[str, Any]]):
    """配置值响应Schema"""
    pass


# 批量设置配置
class BatchSetConfigs(BaseSchema):
    """批量设置配置Schema"""
    configs: Dict[str, Union[str, int, float, bool, None]] = Field(..., description="配置字典")


# 配置模板Schema
class ConfigTemplate(BaseSchema):
    """配置模板Schema"""
    category: str = Field(..., description="分类")
    configs: List[SystemConfigBase] = Field(..., description="配置列表")


class ConfigTemplatesResponse(BaseResponse[List[ConfigTemplate]]):
    """配置模板响应Schema"""
    pass