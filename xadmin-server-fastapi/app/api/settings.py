"""
设置管理API路由
"""
from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import (
    get_current_active_user, get_current_superuser,
    require_permission
)
from app.schemas.base import (
    BaseResponse, ListResponse, PaginationParams, 
    BatchDeleteRequest, ChoicesResponse, SearchFieldsResponse,
    SearchColumnsResponse, ColumnInfo, FieldInfo, ChoiceItem
)
from app.schemas.settings import (
    SystemConfigProfile, SystemConfigCreate, SystemConfigUpdate, 
    SystemConfigListParams, SystemConfigBatchUpdate,
    UserPersonalConfigProfile, UserPersonalConfigCreate, 
    UserPersonalConfigUpdate, UserPersonalConfigListParams,
    UserPersonalConfigBatchUpdate, ConfigCategoriesResponse,
    ConfigCategory, ConfigValuesResponse, BatchSetConfigs
)
from app.services.settings import SystemConfigService, UserPersonalConfigService
from app.models.user import UserInfo
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# 系统配置管理接口
@router.get("/config/system", response_model=ListResponse[List[SystemConfigProfile]])
async def get_system_config_list(
    params: SystemConfigListParams = Depends(),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("config:read"))
):
    """获取系统配置列表"""
    config_service = SystemConfigService(db)
    
    filters = {}
    if params.search:
        filters['search'] = params.search
    if params.category:
        filters['category'] = params.category
    if params.is_active is not None:
        filters['is_active'] = params.is_active
    
    result = config_service.get_config_list(params, filters)
    
    # 转换为响应格式
    config_profiles = []
    for config in result['results']:
        profile = SystemConfigProfile(
            id=config.id,
            key=config.key,
            value=config.value,
            name=config.name,
            description=config.description,
            category=config.category,
            config_type=config.config_type,
            is_active=config.is_active,
            sort=config.sort,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
        config_profiles.append(profile)
    
    return ListResponse(
        code=200,
        detail="success",
        data={
            "results": config_profiles,
            "total": result['total'],
            "page": result['page'],
            "size": result['size'],
            "pages": result['pages']
        }
    )


@router.post("/config/system", response_model=BaseResponse[SystemConfigProfile])
async def create_system_config(
    config_data: SystemConfigCreate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("config:create"))
):
    """创建系统配置"""
    config_service = SystemConfigService(db)
    
    # 检查配置键是否已存在
    if config_service.check_key_exists(config_data.key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配置键已存在"
        )
    
    # 创建配置
    config = config_service.create_config(config_data.dict())
    
    profile = SystemConfigProfile(
        id=config.id,
        key=config.key,
        value=config.value,
        name=config.name,
        description=config.description,
        category=config.category,
        config_type=config.config_type,
        is_active=config.is_active,
        sort=config.sort,
        created_at=config.created_at,
        updated_at=config.updated_at
    )
    
    return BaseResponse(
        code=1000,
        detail="系统配置创建成功",
        data=profile
    )


@router.get("/config/system/{config_id}", response_model=BaseResponse[SystemConfigProfile])
async def get_system_config_detail(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("config:read"))
):
    """获取系统配置详情"""
    config_service = SystemConfigService(db)
    config = config_service.get_by_id(config_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    profile = SystemConfigProfile(
        id=config.id,
        key=config.key,
        value=config.value,
        name=config.name,
        description=config.description,
        category=config.category,
        config_type=config.config_type,
        is_active=config.is_active,
        sort=config.sort,
        created_at=config.created_at,
        updated_at=config.updated_at
    )
    
    return BaseResponse(
        code=1000,
        detail="success",
        data=profile
    )


@router.put("/config/system/{config_id}", response_model=BaseResponse[SystemConfigProfile])
async def update_system_config(
    config_id: int,
    config_data: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("config:update"))
):
    """更新系统配置"""
    config_service = SystemConfigService(db)
    
    # 检查配置是否存在
    config = config_service.get_by_id(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    # 更新配置
    update_dict = config_data.dict(exclude_unset=True)
    updated_config = config_service.update_config(config_id, update_dict)
    
    profile = SystemConfigProfile(
        id=updated_config.id,
        key=updated_config.key,
        value=updated_config.value,
        name=updated_config.name,
        description=updated_config.description,
        category=updated_config.category,
        config_type=updated_config.config_type,
        is_active=updated_config.is_active,
        sort=updated_config.sort,
        created_at=updated_config.created_at,
        updated_at=updated_config.updated_at
    )
    
    return BaseResponse(
        code=1000,
        detail="系统配置更新成功",
        data=profile
    )


@router.delete("/config/system/{config_id}", response_model=BaseResponse[None])
async def delete_system_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("config:delete"))
):
    """删除系统配置"""
    config_service = SystemConfigService(db)
    success = config_service.delete_config(config_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    return BaseResponse(
        code=1000,
        detail="系统配置删除成功",
        data=None
    )


@router.post("/config/system/batch-update", response_model=BaseResponse[None])
async def batch_update_system_configs(
    request: SystemConfigBatchUpdate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("config:update"))
):
    """批量更新系统配置"""
    config_service = SystemConfigService(db)
    
    success = config_service.batch_update_configs(request.configs)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量更新配置失败"
        )
    
    return BaseResponse(
        code=1000,
        detail="批量更新配置成功",
        data=None
    )


@router.get("/config/system/categories", response_model=ConfigCategoriesResponse)
async def get_system_config_categories(
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("config:read"))
):
    """获取系统配置分类"""
    config_service = SystemConfigService(db)
    categories_data = config_service.get_all_categories()
    
    categories = [
        ConfigCategory(
            category=cat['category'],
            name=cat['name'],
            description=cat['description'],
            count=cat['count']
        )
        for cat in categories_data
    ]
    
    return ConfigCategoriesResponse(
        code=1000,
        detail="success",
        data=categories
    )


@router.get("/config/system/values", response_model=ConfigValuesResponse)
async def get_system_config_values(
    category: str = Query(None, description="配置分类"),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取系统配置值"""
    config_service = SystemConfigService(db)
    config_dict = config_service.get_config_dict(category)
    
    return ConfigValuesResponse(
        code=1000,
        detail="success",
        data=config_dict
    )


# 用户个人配置管理接口
@router.get("/config/user", response_model=ListResponse[List[UserPersonalConfigProfile]])
async def get_user_config_list(
    params: UserPersonalConfigListParams = Depends(),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取当前用户个人配置列表"""
    config_service = UserPersonalConfigService(db)
    
    filters = {}
    if params.search:
        filters['search'] = params.search
    if params.category:
        filters['category'] = params.category
    
    result = config_service.get_user_config_list(current_user.id, params, filters)
    
    # 转换为响应格式
    config_profiles = []
    for config in result['results']:
        profile = UserPersonalConfigProfile(
            id=config.id,
            user_id=config.user_id,
            key=config.key,
            value=config.value,
            name=config.name,
            category=config.category,
            config_type=config.config_type,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
        config_profiles.append(profile)
    
    return ListResponse(
        code=1000,
        detail="success",
        data={
            "results": config_profiles,
            "total": result['total'],
            "page": result['page'],
            "size": result['size'],
            "pages": result['pages']
        }
    )


@router.post("/config/user", response_model=BaseResponse[UserPersonalConfigProfile])
async def create_user_config(
    config_data: UserPersonalConfigCreate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """创建用户个人配置"""
    config_service = UserPersonalConfigService(db)
    
    # 检查配置键是否已存在
    existing_config = config_service.get_by_user_and_key(current_user.id, config_data.key)
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配置键已存在"
        )
    
    # 创建配置
    config_dict = config_data.dict()
    config_dict['user_id'] = current_user.id
    config = config_service.create_config(config_dict)
    
    profile = UserPersonalConfigProfile(
        id=config.id,
        user_id=config.user_id,
        key=config.key,
        value=config.value,
        name=config.name,
        category=config.category,
        config_type=config.config_type,
        created_at=config.created_at,
        updated_at=config.updated_at
    )
    
    return BaseResponse(
        code=1000,
        detail="个人配置创建成功",
        data=profile
    )


@router.put("/config/user/{config_id}", response_model=BaseResponse[UserPersonalConfigProfile])
async def update_user_config(
    config_id: int,
    config_data: UserPersonalConfigUpdate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """更新用户个人配置"""
    config_service = UserPersonalConfigService(db)
    
    # 检查配置是否存在且属于当前用户
    config = config_service.get_by_id(config_id)
    if not config or config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    # 更新配置
    update_dict = config_data.dict(exclude_unset=True)
    updated_config = config_service.update_config(config_id, update_dict)
    
    profile = UserPersonalConfigProfile(
        id=updated_config.id,
        user_id=updated_config.user_id,
        key=updated_config.key,
        value=updated_config.value,
        name=updated_config.name,
        category=updated_config.category,
        config_type=updated_config.config_type,
        created_at=updated_config.created_at,
        updated_at=updated_config.updated_at
    )
    
    return BaseResponse(
        code=1000,
        detail="个人配置更新成功",
        data=profile
    )


@router.delete("/config/user/{config_id}", response_model=BaseResponse[None])
async def delete_user_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """删除用户个人配置"""
    config_service = UserPersonalConfigService(db)
    
    # 检查配置是否存在且属于当前用户
    config = config_service.get_by_id(config_id)
    if not config or config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    success = config_service.delete_config(config_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除配置失败"
        )
    
    return BaseResponse(
        code=1000,
        detail="个人配置删除成功",
        data=None
    )


@router.post("/config/user/batch-update", response_model=BaseResponse[None])
async def batch_update_user_configs(
    request: UserPersonalConfigBatchUpdate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """批量更新用户个人配置"""
    config_service = UserPersonalConfigService(db)
    
    success = config_service.batch_update_user_configs(current_user.id, request.configs)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量更新配置失败"
        )
    
    return BaseResponse(
        code=1000,
        detail="批量更新配置成功",
        data=None
    )


@router.get("/config/user/values", response_model=ConfigValuesResponse)
async def get_user_config_values(
    category: str = Query(None, description="配置分类"),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取用户个人配置值"""
    config_service = UserPersonalConfigService(db)
    config_dict = config_service.get_user_config_dict(current_user.id, category)
    
    return ConfigValuesResponse(
        code=1000,
        detail="success",
        data=config_dict
    )


# 获取选择项
@router.get("/config/choices", response_model=ChoicesResponse)
async def get_config_choices(
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取配置相关选择项"""
    return ChoicesResponse(
        code=1000,
        detail="success",
        data={
            "config_type": [
                ChoiceItem(label="字符串", value="string"),
                ChoiceItem(label="数字", value="number"),
                ChoiceItem(label="布尔值", value="boolean"),
                ChoiceItem(label="JSON", value="json"),
                ChoiceItem(label="文件", value="file")
            ],
            "category": [
                ChoiceItem(label="基础设置", value="basic"),
                ChoiceItem(label="安全设置", value="security"),
                ChoiceItem(label="邮件设置", value="email"),
                ChoiceItem(label="存储设置", value="storage"),
                ChoiceItem(label="系统设置", value="system"),
                ChoiceItem(label="外观设置", value="appearance")
            ],
            "is_active": [
                ChoiceItem(label="启用", value=True),
                ChoiceItem(label="禁用", value=False)
            ]
        }
    )