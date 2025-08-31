"""
用户相关工具函数
"""
from typing import Optional, List
from app.models.user import UserInfo, DeptInfo, UserRole
from app.schemas.user import UserProfile, SearchUserResult
from app.schemas.auth import UserInfoResponse, TokenResponse
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings
from datetime import timedelta


def convert_user_to_profile(user: UserInfo) -> UserProfile:
    """
    将用户模型转换为用户概要信息
    
    Args:
        user: 用户模型实例
        
    Returns:
        UserProfile: 用户概要信息
    """
    # 安全地处理可能为None的关联对象
    dept_name = None
    dept_obj = getattr(user, 'dept', None)
    if dept_obj is not None:
        dept_name = getattr(dept_obj, 'name', None)
        
    role_names = []
    roles_obj = getattr(user, 'roles', None)
    if roles_obj is not None:
        role_names = [getattr(role, 'name') for role in roles_obj if getattr(role, 'is_active', True)]
    
    return UserProfile(
        id=getattr(user, 'id'),
        username=getattr(user, 'username'),
        email=getattr(user, 'email', None),
        phone=getattr(user, 'phone', None),
        nickname=getattr(user, 'nickname', None),
        gender=getattr(user, 'gender', 0),
        is_active=getattr(user, 'is_active', True),
        is_staff=getattr(user, 'is_staff', False),
        avatar=getattr(user, 'avatar', None),
        last_login=getattr(user, 'last_login', None),
        date_joined=getattr(user, 'date_joined'),
        is_superuser=getattr(user, 'is_superuser', False),
        created_at=getattr(user, 'created_at'),
        updated_at=getattr(user, 'updated_at'),
        dept_name=dept_name,
        role_names=role_names
    )


def convert_user_to_search_result(user: UserInfo) -> SearchUserResult:
    """
    将用户模型转换为搜索结果
    
    Args:
        user: 用户模型实例
        
    Returns:
        SearchUserResult: 搜索结果
    """
    # 安全地处理可能为None的关联对象
    dept_name = None
    if user.dept is not None:
        dept_name = getattr(user.dept, 'name', None)
    
    return SearchUserResult(
        id=getattr(user, 'id'),
        username=getattr(user, 'username'),
        nickname=getattr(user, 'nickname', None),
        avatar=getattr(user, 'avatar', None),
        dept_name=dept_name
    )


def convert_user_to_info_response(user: UserInfo) -> UserInfoResponse:
    """
    将用户模型转换为用户信息响应
    
    Args:
        user: 用户模型实例
        
    Returns:
        UserInfoResponse: 用户信息响应
    """
    return UserInfoResponse(
        username=getattr(user, 'username'),
        nickname=getattr(user, 'nickname', None),
        avatar=getattr(user, 'avatar', None),
        email=getattr(user, 'email', None),
        phone=getattr(user, 'phone', None),
        gender=getattr(user, 'gender', 0),
        last_login=getattr(user, 'last_login', None),
        date_joined=getattr(user, 'date_joined'),
        pk=getattr(user, 'id'),
        unread_message_count=0,  # TODO: 实现消息计数
        is_active=getattr(user, 'is_active', True),
        roles=[getattr(role, 'name') for role in user.roles if getattr(role, 'is_active', True)]
    )


def create_token_response(user) -> TokenResponse:
    """
    为用户创建令牌响应
    
    Args:
        user: 用户模型实例
        
    Returns:
        TokenResponse: 令牌响应
    """
    # 创建令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(user.username, access_token_expires)
    refresh_token = create_refresh_token(user.username, refresh_token_expires)
    
    return TokenResponse(
        code=1000,
        detail="登录成功",
        data={
            "access": access_token,
            "refresh": refresh_token,
            "access_token_lifetime": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token_lifetime": settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        }
    )