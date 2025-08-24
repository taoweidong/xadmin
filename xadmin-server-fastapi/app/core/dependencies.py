"""
认证依赖和权限验证
"""
from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import UserInfo
from app.services.user import UserService
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer 认证方案
security = HTTPBearer(auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[UserInfo]:
    """
    获取当前用户
    """
    if not token:
        return None
        
    try:
        username = verify_token(token.credentials)
        if not username:
            return None
            
        user_service = UserService(db)
        user = user_service.get_by_username(username)
        
        if not user or not user.is_active:
            return None
            
        return user
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


def get_current_active_user(
    current_user: UserInfo = Depends(get_current_user)
) -> UserInfo:
    """
    获取当前活跃用户（必须认证）
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证或认证信息已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def get_current_superuser(
    current_user: UserInfo = Depends(get_current_active_user)
) -> UserInfo:
    """
    获取当前超级用户
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级用户权限"
        )
    return current_user


def get_current_staff_user(
    current_user: UserInfo = Depends(get_current_active_user)
) -> UserInfo:
    """
    获取当前员工用户
    """
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要员工权限"
        )
    return current_user


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, permission: str):
        self.permission = permission
    
    def __call__(self, current_user: UserInfo = Depends(get_current_active_user)) -> UserInfo:
        """
        检查用户是否具有指定权限
        """
        # 超级用户拥有所有权限
        if current_user.is_superuser:
            return current_user
            
        # 检查用户角色权限
        user_permissions = set()
        for role in current_user.roles:
            if role.is_active:
                for menu in role.menus:
                    if menu.permission:
                        user_permissions.add(menu.permission)
        
        # 检查用户直接权限
        for permission in current_user.permissions:
            if permission.is_active:
                user_permissions.add(permission.code)
        
        if self.permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要权限: {self.permission}"
            )
            
        return current_user


def require_permission(permission: str):
    """
    要求特定权限的装饰器工厂
    """
    return PermissionChecker(permission)


class RoleChecker:
    """角色检查器"""
    
    def __init__(self, role_codes: list):
        self.role_codes = role_codes if isinstance(role_codes, list) else [role_codes]
    
    def __call__(self, current_user: UserInfo = Depends(get_current_active_user)) -> UserInfo:
        """
        检查用户是否具有指定角色
        """
        # 超级用户拥有所有角色
        if current_user.is_superuser:
            return current_user
            
        user_roles = {role.code for role in current_user.roles if role.is_active}
        
        if not any(role_code in user_roles for role_code in self.role_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要角色: {', '.join(self.role_codes)}"
            )
            
        return current_user


def require_roles(role_codes):
    """
    要求特定角色的装饰器工厂
    """
    return RoleChecker(role_codes)


class DataPermissionChecker:
    """数据权限检查器"""
    
    def __init__(self, resource: str, action: str = "read"):
        self.resource = resource
        self.action = action
    
    def __call__(self, current_user: UserInfo = Depends(get_current_active_user)) -> UserInfo:
        """
        检查用户是否具有资源的数据权限
        """
        # 超级用户拥有所有数据权限
        if current_user.is_superuser:
            return current_user
            
        # TODO: 实现更复杂的数据权限逻辑
        # 可以根据部门、角色等进行数据过滤
        
        return current_user


def require_data_permission(resource: str, action: str = "read"):
    """
    要求特定数据权限的装饰器工厂
    """
    return DataPermissionChecker(resource, action)


def get_optional_user(
    db: Session = Depends(get_db),
    token: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[UserInfo]:
    """
    获取可选的当前用户（不强制认证）
    """
    return get_current_user(db, token)