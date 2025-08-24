"""
认证相关Pydantic Schema模型
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict
from app.schemas.base import BaseSchema, BaseResponse
from datetime import datetime


class LoginRequest(BaseSchema):
    """登录请求模型"""
    username: str = Field(..., min_length=1, max_length=150, description="用户名")
    password: str = Field(..., min_length=1, description="密码")
    remember_me: bool = Field(False, description="记住我")


# 验证码相关Schema已移除


class TokenInfo(BaseSchema):
    """令牌信息模型"""
    access: str = Field(..., description="访问令牌")
    refresh: str = Field(..., description="刷新令牌")
    access_token_lifetime: int = Field(..., description="访问令牌有效期(秒)")
    refresh_token_lifetime: int = Field(..., description="刷新令牌有效期(秒)")


class TokenResponse(BaseResponse[TokenInfo]):
    """令牌响应模型"""
    pass


class RefreshTokenRequest(BaseSchema):
    """刷新令牌请求模型"""
    refresh: str = Field(..., description="刷新令牌")


class RegisterRequest(BaseSchema):
    """注册请求模型"""
    username: str = Field(..., min_length=3, max_length=150, description="用户名")
    password: str = Field(..., min_length=8, description="密码")
    confirm_password: str = Field(..., description="确认密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    nickname: Optional[str] = Field(None, max_length=150, description="昵称")
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('两次输入的密码不一致')
        return v


class ResetPasswordRequest(BaseSchema):
    """重置密码请求模型"""
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    code: str = Field(..., description="验证码")
    new_password: str = Field(..., min_length=8, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


class ChangePasswordRequest(BaseSchema):
    """修改密码请求模型"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=8, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


# 验证码相关Schema已移除


# 临时令牌相关Schema已移除


class AuthInfoResponse(BaseSchema):
    """认证信息响应模型"""
    code: int = Field(200, description="状态码")
    detail: str = Field("success", description="响应消息")
    data: dict = Field(..., description="认证配置信息")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "detail": "success", 
                "data": {
                    "access": True,
                    "captcha": False,
                    "token": False,
                    "encrypted": False,
                    "lifetime": 3600,
                    "reset": True,
                    "password": [],
                    "email": True,
                    "sms": False,
                    "basic": True,
                    "rate": 5
                }
            }
        }
    )


# 验证码相关Schema已移除


# 验证码配置相关Schema已移除


class PasswordRulesResponse(BaseSchema):
    """密码规则响应模型"""
    code: int = Field(200, description="状态码")
    detail: str = Field("success", description="响应消息")
    password_rule: List[dict] = Field(..., description="密码规则列表")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "detail": "success",
                "password_rule": [
                    {"key": "min_length", "value": 8, "description": "最少8个字符"},
                    {"key": "require_uppercase", "value": True, "description": "必须包含大写字母"},
                    {"key": "require_lowercase", "value": True, "description": "必须包含小写字母"},
                    {"key": "require_numbers", "value": True, "description": "必须包含数字"}
                ]
            }
        }
    )


class UserInfoResponse(BaseSchema):
    """用户信息响应模型"""
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    gender: int = Field(0, description="性别")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    date_joined: datetime = Field(..., description="注册时间")
    pk: int = Field(..., description="用户ID")
    unread_message_count: int = Field(0, description="未读消息数")
    is_active: bool = Field(True, description="是否激活")
    roles: List[str] = Field([], description="角色列表")
    
    model_config = ConfigDict(from_attributes=True)


class UserInfoDetailResponse(BaseResponse[UserInfoResponse]):
    """用户详细信息响应模型"""
    choices_dict: Optional[List[dict]] = Field(None, description="选择项字典")
    password_rule: Optional[List[dict]] = Field(None, description="密码规则")