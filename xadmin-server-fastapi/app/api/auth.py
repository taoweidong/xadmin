"""
认证相关API路由
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_optional_user
from app.core.security import (
    create_access_token, create_refresh_token, verify_token,
    get_password_hash, validate_password_strength
)
from app.schemas.auth import (
    LoginRequest, TokenResponse, RefreshTokenRequest,
    RegisterRequest, ResetPasswordRequest, ChangePasswordRequest,
    AuthInfoResponse, PasswordRulesResponse,
    UserInfoDetailResponse, UserInfoResponse
)
from app.schemas.base import BaseResponse, StatusResponse
from app.services.user import UserService, LoginLogService
# 验证码服务已移除
from app.models.user import UserInfo
from app.core.config import settings
from app.utils.user_utils import create_token_response
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 不需要认证的路由
@router.get("/login/basic", response_model=AuthInfoResponse)
async def get_login_config():
    """获取登录配置信息"""
    return AuthInfoResponse(
        code=1000,
        detail="success",
        data={
            "access": True,
            "captcha": False,
            "token": False,
            "encrypted": False,
            "lifetime": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "reset": True,
            "password": [],
            "email": True,
            "sms": False,
            "basic": True,
            "rate": 5
        }
    )


@router.post("/login/basic", response_model=TokenResponse)
async def login_basic(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """基础登录"""
    user_service = UserService(db)
    login_log_service = LoginLogService(db)
    
    # 验证码功能已移除，直接进行用户认证
    
    # 用户认证
    user = user_service.authenticate(login_data.username, login_data.password)
    if not user:
        # 记录失败日志
        login_log_service.create_login_log({
            "username": login_data.username,
            "login_type": "basic",
            "login_result": False,
            "login_message": "用户名或密码错误",
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent")
        })
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    # 更新最后登录时间
    user_service.update_last_login(user.id)
    
    # 记录成功日志
    login_log_service.create_login_log({
        "user_id": user.id,
        "username": user.username,
        "login_type": "basic",
        "login_result": True,
        "login_message": "登录成功",
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent")
    })
    
    return create_token_response(user)


# 验证码登录功能已移除


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """刷新令牌"""
    username = verify_token(refresh_data.refresh)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期"
        )
    
    user_service = UserService(db)
    user = user_service.get_by_username(username)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.username, access_token_expires)
    
    return TokenResponse(
        code=1000,
        detail="令牌刷新成功",
        data={
            "access": access_token,
            "refresh": refresh_data.refresh,
            "access_token_lifetime": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token_lifetime": settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        }
    )


@router.post("/logout", response_model=StatusResponse)
async def logout(
    current_user: UserInfo = Depends(get_current_active_user)
):
    """登出"""
    # TODO: 将令牌加入黑名单
    return StatusResponse(
        code=1000,
        detail="退出成功",
        success=True
    )


@router.get("/register", response_model=AuthInfoResponse)
async def get_register_config():
    """获取注册配置信息"""
    return AuthInfoResponse(
        code=1000,
        detail="success",
        data={
            "access": True,
            "captcha": False,
            "email": True,
            "sms": False,
            "password": [
                {"key": "min_length", "value": settings.PASSWORD_MIN_LENGTH, "description": f"最少{settings.PASSWORD_MIN_LENGTH}个字符"},
                {"key": "require_uppercase", "value": settings.PASSWORD_REQUIRE_UPPERCASE, "description": "必须包含大写字母"},
                {"key": "require_lowercase", "value": settings.PASSWORD_REQUIRE_LOWERCASE, "description": "必须包含小写字母"},
                {"key": "require_numbers", "value": settings.PASSWORD_REQUIRE_NUMBERS, "description": "必须包含数字"},
                {"key": "require_symbols", "value": settings.PASSWORD_REQUIRE_SYMBOLS, "description": "必须包含特殊符号"}
            ]
        }
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    register_data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """用户注册"""
    user_service = UserService(db)
    
    # 验证码功能已移除，直接进行密码验证·
    
    # 验证密码强度
    is_valid, errors = validate_password_strength(register_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"密码不符合要求: {', '.join(errors)}"
        )
    
    # 检查用户名是否存在
    if user_service.check_username_exists(register_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否存在
    if register_data.email and user_service.check_email_exists(register_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 检查手机号是否存在
    if register_data.phone and user_service.check_phone_exists(register_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已存在"
        )
    
    # 创建用户
    user_data = {
        "username": register_data.username,
        "password": register_data.password,
        "email": register_data.email,
        "phone": register_data.phone,
        "nickname": register_data.nickname or register_data.username,
        "is_active": True
    }
    
    user = user_service.create_user(user_data)
    
    return create_token_response(user)


# 验证码相关接口已移除


# 临时令牌接口已移除


# 验证码配置接口已移除


# 验证码发送接口已移除


# 密码重置接口已移除（需要验证码验证）


@router.get("/rules/password", response_model=PasswordRulesResponse)
async def get_password_rules():
    """获取密码规则"""
    rules = [
        {"key": "min_length", "value": settings.PASSWORD_MIN_LENGTH, "description": f"最少{settings.PASSWORD_MIN_LENGTH}个字符"},
        {"key": "require_uppercase", "value": settings.PASSWORD_REQUIRE_UPPERCASE, "description": "必须包含大写字母"},
        {"key": "require_lowercase", "value": settings.PASSWORD_REQUIRE_LOWERCASE, "description": "必须包含小写字母"},
        {"key": "require_numbers", "value": settings.PASSWORD_REQUIRE_NUMBERS, "description": "必须包含数字"},
        {"key": "require_symbols", "value": settings.PASSWORD_REQUIRE_SYMBOLS, "description": "必须包含特殊符号"}
    ]
    
    return PasswordRulesResponse(
        code=1000,
        detail="success",
        password_rule=rules
    )