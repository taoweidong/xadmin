"""
测试 app.schemas.auth 模块
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.auth import (
    LoginRequest,
    TokenInfo,
    TokenResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    AuthInfoResponse,
    PasswordRulesResponse,
    UserInfoResponse,
    UserInfoDetailResponse,
)


class TestLoginRequest:
    """测试登录请求模型"""
    
    def test_login_request_creation(self):
        """测试登录请求创建"""
        request = LoginRequest(
            username="testuser",
            password="password123",
            captcha_key="captcha_key_123",
            captcha_code="ABC123",
            remember_me=True
        )
        
        assert request.username == "testuser"
        assert request.password == "password123"
        assert request.captcha_key == "captcha_key_123"
        assert request.captcha_code == "ABC123"
        assert request.remember_me is True
    
    def test_login_request_required_fields(self):
        """测试登录请求必填字段"""
        request = LoginRequest(
            username="testuser",
            password="password123"
        )
        
        assert request.username == "testuser"
        assert request.password == "password123"
        assert request.captcha_key is None
        assert request.captcha_code is None
        assert request.remember_me is False  # 默认值
    
    def test_login_request_validation(self):
        """测试登录请求验证"""
        # 用户名不能为空
        with pytest.raises(ValidationError):
            LoginRequest(username="", password="password")
        
        # 密码不能为空
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser", password="")
        
        # 用户名长度限制
        with pytest.raises(ValidationError):
            LoginRequest(username="a" * 151, password="password")
    
    def test_login_request_edge_cases(self):
        """测试登录请求边界情况"""
        # 最短用户名
        request_min = LoginRequest(username="a", password="p")
        assert request_min.username == "a"
        
        # 最长用户名
        request_max = LoginRequest(username="a" * 150, password="password")
        assert len(request_max.username) == 150





class TestTokenInfo:
    """测试令牌信息模型"""
    
    def test_token_info_creation(self):
        """测试令牌信息创建"""
        token_info = TokenInfo(
            access="access_token_here",
            refresh="refresh_token_here",
            access_token_lifetime=3600,
            refresh_token_lifetime=86400
        )
        
        assert token_info.access == "access_token_here"
        assert token_info.refresh == "refresh_token_here"
        assert token_info.access_token_lifetime == 3600
        assert token_info.refresh_token_lifetime == 86400
    
    def test_token_info_validation(self):
        """测试令牌信息验证"""
        # 所有字段都是必填的
        with pytest.raises(ValidationError):
            TokenInfo()


class TestTokenResponse:
    """测试令牌响应模型"""
    
    def test_token_response_creation(self):
        """测试令牌响应创建"""
        token_info = TokenInfo(
            access="access_token",
            refresh="refresh_token",
            access_token_lifetime=3600,
            refresh_token_lifetime=86400
        )
        
        response = TokenResponse(data=token_info)
        
        assert response.code == 1000
        assert response.detail == "success"
        assert response.data.access == "access_token"
        assert response.data.refresh == "refresh_token"


class TestRefreshTokenRequest:
    """测试刷新令牌请求模型"""
    
    def test_refresh_token_request_creation(self):
        """测试刷新令牌请求创建"""
        request = RefreshTokenRequest(refresh="refresh_token_here")
        
        assert request.refresh == "refresh_token_here"
    
    def test_refresh_token_request_validation(self):
        """测试刷新令牌请求验证"""
        # refresh字段是必填的
        with pytest.raises(ValidationError):
            RefreshTokenRequest()


class TestRegisterRequest:
    """测试注册请求模型"""
    
    def test_register_request_creation(self):
        """测试注册请求创建"""
        request = RegisterRequest(
            username="newuser",
            password="Password123",
            confirm_password="Password123",
            email="newuser@example.com",
            phone="13800138000",
            nickname="新用户",
            captcha_key="captcha_key",
            captcha_code="ABC123"
        )
        
        assert request.username == "newuser"
        assert request.password == "Password123"
        assert request.confirm_password == "Password123"
        assert request.email == "newuser@example.com"
        assert request.phone == "13800138000"
        assert request.nickname == "新用户"
        assert request.captcha_key == "captcha_key"
        assert request.captcha_code == "ABC123"
    
    def test_register_request_required_fields(self):
        """测试注册请求必填字段"""
        request = RegisterRequest(
            username="newuser",
            password="Password123",
            confirm_password="Password123"
        )
        
        assert request.username == "newuser"
        assert request.password == "Password123"
        assert request.confirm_password == "Password123"
        assert request.email is None
        assert request.phone is None
        assert request.nickname is None
    
    def test_register_request_password_validation(self):
        """测试注册请求密码验证"""
        # 密码不匹配
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                username="testuser",
                password="Password123",
                confirm_password="DifferentPassword"
            )
        
        assert "两次输入的密码不一致" in str(exc_info.value)
    
    def test_register_request_field_validation(self):
        """测试注册请求字段验证"""
        # 用户名长度限制
        with pytest.raises(ValidationError):
            RegisterRequest(
                username="ab",  # 少于3个字符
                password="Password123",
                confirm_password="Password123"
            )
        
        # 密码长度限制
        with pytest.raises(ValidationError):
            RegisterRequest(
                username="testuser",
                password="1234567",  # 少于8个字符
                confirm_password="1234567"
            )
        
        # 昵称长度限制
        with pytest.raises(ValidationError):
            RegisterRequest(
                username="testuser",
                password="Password123",
                confirm_password="Password123",
                nickname="a" * 151  # 超过150个字符
            )


class TestResetPasswordRequest:
    """测试重置密码请求模型"""
    
    def test_reset_password_request_with_username(self):
        """测试使用用户名重置密码"""
        request = ResetPasswordRequest(
            username="testuser",
            code="123456",
            new_password="NewPassword123",
            confirm_password="NewPassword123"
        )
        
        assert request.username == "testuser"
        assert request.email is None
        assert request.phone is None
        assert request.code == "123456"
        assert request.new_password == "NewPassword123"
        assert request.confirm_password == "NewPassword123"
    
    def test_reset_password_request_with_email(self):
        """测试使用邮箱重置密码"""
        request = ResetPasswordRequest(
            email="test@example.com",
            code="123456",
            new_password="NewPassword123",
            confirm_password="NewPassword123"
        )
        
        assert request.username is None
        assert request.email == "test@example.com"
        assert request.phone is None
    
    def test_reset_password_request_password_validation(self):
        """测试重置密码请求密码验证"""
        # 新密码不匹配
        with pytest.raises(ValidationError) as exc_info:
            ResetPasswordRequest(
                username="testuser",
                code="123456",
                new_password="NewPassword123",
                confirm_password="DifferentPassword"
            )
        
        assert "两次输入的密码不一致" in str(exc_info.value)


class TestChangePasswordRequest:
    """测试修改密码请求模型"""
    
    def test_change_password_request_creation(self):
        """测试修改密码请求创建"""
        request = ChangePasswordRequest(
            old_password="OldPassword123",
            new_password="NewPassword123",
            confirm_password="NewPassword123"
        )
        
        assert request.old_password == "OldPassword123"
        assert request.new_password == "NewPassword123"
        assert request.confirm_password == "NewPassword123"
    
    def test_change_password_request_validation(self):
        """测试修改密码请求验证"""
        # 新密码不匹配
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(
                old_password="OldPassword123",
                new_password="NewPassword123",
                confirm_password="DifferentPassword"
            )
        
        assert "两次输入的密码不一致" in str(exc_info.value)


class TestCaptchaResponse:
    """测试验证码响应模型"""
    
    def test_captcha_response_creation(self):
        """测试验证码响应创建"""
        response = CaptchaResponse(
            captcha_image="base64_image_data_here",
            captcha_key="captcha_key_123",
            length=4
        )
        
        assert response.code == 1000
        assert response.detail == "success"
        assert response.captcha_image == "base64_image_data_here"
        assert response.captcha_key == "captcha_key_123"
        assert response.length == 4


class TestTempTokenResponse:
    """测试临时令牌响应模型"""
    
    def test_temp_token_response_creation(self):
        """测试临时令牌响应创建"""
        response = TempTokenResponse(
            token="temp_token_123",
            lifetime=300
        )
        
        assert response.code == 1000
        assert response.detail == "success"
        assert response.token == "temp_token_123"
        assert response.lifetime == 300


class TestAuthInfoResponse:
    """测试认证信息响应模型"""
    
    def test_auth_info_response_creation(self):
        """测试认证信息响应创建"""
        data = {
            "access": True,
            "captcha": True,
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
        
        response = AuthInfoResponse(data=data)
        
        assert response.code == 200
        assert response.detail == "success"
        assert response.data["access"] is True
        assert response.data["captcha"] is True
        assert response.data["lifetime"] == 3600


class TestVerifyCodeSendRequest:
    """测试验证码发送请求模型"""
    
    def test_verify_code_send_request_creation(self):
        """测试验证码发送请求创建"""
        request = VerifyCodeSendRequest(
            target="13800138000",
            code_type="login",
            temp_token="temp_token_123"
        )
        
        assert request.target == "13800138000"
        assert request.code_type == "login"
        assert request.temp_token == "temp_token_123"
    
    def test_verify_code_send_request_default_code_type(self):
        """测试验证码发送请求默认类型"""
        request = VerifyCodeSendRequest(target="test@example.com")
        
        assert request.target == "test@example.com"
        assert request.code_type == "login"  # 默认值
        assert request.temp_token is None
    
    def test_verify_code_send_request_different_types(self):
        """测试不同类型的验证码发送请求"""
        types = ["login", "register", "reset"]
        
        for code_type in types:
            request = VerifyCodeSendRequest(
                target="13800138000",
                code_type=code_type
            )
            assert request.code_type == code_type


class TestPasswordRulesResponse:
    """测试密码规则响应模型"""
    
    def test_password_rules_response_creation(self):
        """测试密码规则响应创建"""
        password_rules = [
            {"key": "min_length", "value": 8, "description": "最少8个字符"},
            {"key": "require_uppercase", "value": True, "description": "必须包含大写字母"},
            {"key": "require_lowercase", "value": True, "description": "必须包含小写字母"},
            {"key": "require_numbers", "value": True, "description": "必须包含数字"}
        ]
        
        response = PasswordRulesResponse(password_rule=password_rules)
        
        assert response.code == 200
        assert response.detail == "success"
        assert len(response.password_rule) == 4
        assert response.password_rule[0]["key"] == "min_length"
        assert response.password_rule[0]["value"] == 8


class TestUserInfoResponse:
    """测试用户信息响应模型"""
    
    def test_user_info_response_creation(self):
        """测试用户信息响应创建"""
        now = datetime.now()
        
        user_info = UserInfoResponse(
            username="testuser",
            nickname="测试用户",
            avatar="/uploads/avatar.jpg",
            email="test@example.com",
            phone="13800138000",
            gender=1,
            last_login=now,
            date_joined=now,
            pk=1,
            unread_message_count=5,
            is_active=True,
            roles=["admin", "user"]
        )
        
        assert user_info.username == "testuser"
        assert user_info.nickname == "测试用户"
        assert user_info.avatar == "/uploads/avatar.jpg"
        assert user_info.email == "test@example.com"
        assert user_info.phone == "13800138000"
        assert user_info.gender == 1
        assert user_info.last_login == now
        assert user_info.date_joined == now
        assert user_info.pk == 1
        assert user_info.unread_message_count == 5
        assert user_info.is_active is True
        assert user_info.roles == ["admin", "user"]
    
    def test_user_info_response_default_values(self):
        """测试用户信息响应默认值"""
        now = datetime.now()
        
        user_info = UserInfoResponse(
            username="testuser",
            date_joined=now,
            pk=1
        )
        
        assert user_info.nickname is None
        assert user_info.avatar is None
        assert user_info.email is None
        assert user_info.phone is None
        assert user_info.gender == 0  # 默认性别
        assert user_info.last_login is None
        assert user_info.unread_message_count == 0  # 默认未读消息数
        assert user_info.is_active is True  # 默认激活状态
        assert user_info.roles == []  # 默认角色列表


class TestUserInfoDetailResponse:
    """测试用户详细信息响应模型"""
    
    def test_user_info_detail_response_creation(self):
        """测试用户详细信息响应创建"""
        now = datetime.now()
        
        user_info = UserInfoResponse(
            username="testuser",
            date_joined=now,
            pk=1
        )
        
        choices_dict = [
            {"key": "gender", "choices": [{"label": "男", "value": 1}, {"label": "女", "value": 2}]}
        ]
        
        password_rule = [
            {"key": "min_length", "value": 8, "description": "最少8个字符"}
        ]
        
        response = UserInfoDetailResponse(
            data=user_info,
            choices_dict=choices_dict,
            password_rule=password_rule
        )
        
        assert response.code == 1000
        assert response.detail == "success"
        assert response.data.username == "testuser"
        assert response.choices_dict == choices_dict
        assert response.password_rule == password_rule
    
    def test_user_info_detail_response_optional_fields(self):
        """测试用户详细信息响应可选字段"""
        now = datetime.now()
        
        user_info = UserInfoResponse(
            username="testuser",
            date_joined=now,
            pk=1
        )
        
        response = UserInfoDetailResponse(data=user_info)
        
        assert response.data.username == "testuser"
        assert response.choices_dict is None
        assert response.password_rule is None


class TestAuthSchemaIntegration:
    """测试认证Schema集成功能"""
    
    def test_complete_login_flow_schemas(self):
        """测试完整登录流程的Schema"""
        # 1. 登录请求
        login_request = LoginRequest(
            username="testuser",
            password="password123"
        )
        
        # 2. 令牌信息
        token_info = TokenInfo(
            access="access_token",
            refresh="refresh_token",
            access_token_lifetime=3600,
            refresh_token_lifetime=86400
        )
        
        # 3. 登录响应
        login_response = TokenResponse(data=token_info)
        
        assert login_request.username == "testuser"
        assert login_response.data.access == "access_token"
        assert login_response.code == 1000
    
    def test_complete_register_flow_schemas(self):
        """测试完整注册流程的Schema"""
        # 1. 验证码响应
        captcha_response = CaptchaResponse(
            captcha_image="base64_image",
            captcha_key="captcha_key",
            length=4
        )
        
        # 2. 注册请求
        register_request = RegisterRequest(
            username="newuser",
            password="Password123",
            confirm_password="Password123",
            email="newuser@example.com",
            captcha_key=captcha_response.captcha_key,
            captcha_code="1234"
        )
        
        assert captcha_response.captcha_key == register_request.captcha_key
        assert register_request.password == register_request.confirm_password
    
    def test_password_change_flow_schemas(self):
        """测试密码修改流程的Schema"""
        # 1. 修改密码请求
        change_request = ChangePasswordRequest(
            old_password="OldPassword123",
            new_password="NewPassword123",
            confirm_password="NewPassword123"
        )
        
        # 2. 重置密码请求
        reset_request = ResetPasswordRequest(
            email="test@example.com",
            code="123456",
            new_password="NewPassword123",
            confirm_password="NewPassword123"
        )
        
        assert change_request.new_password == reset_request.new_password
        assert change_request.confirm_password == reset_request.confirm_password