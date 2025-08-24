"""
测试 app.core.security 模块
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from jose import jwt, JWTError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_password,
    get_password_hash,
    generate_random_string,
    generate_temp_token,
    validate_password_strength,
)
from app.core.config import settings


class TestTokenOperations:
    """测试令牌操作"""
    
    def test_create_access_token_default_expiration(self):
        """测试创建访问令牌（默认过期时间）"""
        subject = "testuser"
        token = create_access_token(subject)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # 验证令牌内容
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == subject
        assert "exp" in payload
    
    def test_create_access_token_custom_expiration(self):
        """测试创建访问令牌（自定义过期时间）"""
        subject = "testuser"
        expires_delta = timedelta(minutes=30)
        token = create_access_token(subject, expires_delta)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + expires_delta
        
        # 允许5秒误差
        assert abs((exp_time - expected_exp).total_seconds()) < 5
    
    def test_create_refresh_token_default_expiration(self):
        """测试创建刷新令牌（默认过期时间）"""
        subject = "testuser"
        token = create_refresh_token(subject)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == subject
        assert payload.get("type") == "refresh"
        assert "exp" in payload
    
    def test_create_refresh_token_custom_expiration(self):
        """测试创建刷新令牌（自定义过期时间）"""
        subject = "testuser"
        expires_delta = timedelta(days=7)
        token = create_refresh_token(subject, expires_delta)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + expires_delta
        
        # 允许5秒误差
        assert abs((exp_time - expected_exp).total_seconds()) < 5
    
    def test_verify_token_valid(self):
        """测试验证有效令牌"""
        subject = "testuser"
        token = create_access_token(subject)
        
        verified_subject = verify_token(token)
        assert verified_subject == subject
    
    def test_verify_token_invalid(self):
        """测试验证无效令牌"""
        invalid_token = "invalid.token.here"
        
        result = verify_token(invalid_token)
        assert result is None
    
    def test_verify_token_expired(self):
        """测试验证过期令牌"""
        subject = "testuser"
        # 创建一个已经过期的令牌
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(subject, expires_delta)
        
        result = verify_token(token)
        assert result is None
    
    def test_verify_token_malformed(self):
        """测试验证格式错误的令牌"""
        malformed_tokens = [
            "",
            "not.a.token",
            "header.payload",  # 缺少签名
            "header.payload.signature.extra",  # 多余部分
        ]
        
        for token in malformed_tokens:
            result = verify_token(token)
            assert result is None
    
    def test_verify_token_wrong_secret(self):
        """测试用错误密钥验证令牌"""
        # 使用不同的密钥创建令牌
        wrong_secret = "wrong-secret-key"
        subject = "testuser"
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode = {"exp": expire, "sub": subject}
        token = jwt.encode(to_encode, wrong_secret, algorithm=settings.ALGORITHM)
        
        result = verify_token(token)
        assert result is None


class TestPasswordOperations:
    """测试密码操作"""
    
    def test_get_password_hash(self):
        """测试获取密码哈希"""
        password = "test123456"
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # 确保不是明文
        assert hashed.startswith("$2b$")  # bcrypt哈希特征
    
    def test_verify_password_correct(self):
        """测试验证正确密码"""
        password = "test123456"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """测试验证错误密码"""
        password = "test123456"
        wrong_password = "wrong123456"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty(self):
        """测试验证空密码"""
        password = "test123456"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is False
    
    def test_password_hash_uniqueness(self):
        """测试相同密码生成不同哈希"""
        password = "test123456"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # 即使是相同密码，由于salt的存在，哈希值应该不同
        assert hash1 != hash2
        
        # 但都应该能验证原密码
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestRandomStringGeneration:
    """测试随机字符串生成"""
    
    def test_generate_random_string_default_length(self):
        """测试生成默认长度随机字符串"""
        random_str = generate_random_string()
        
        assert isinstance(random_str, str)
        assert len(random_str) == 32  # 默认长度
        assert random_str.isalnum()  # 只包含字母和数字
    
    def test_generate_random_string_custom_length(self):
        """测试生成自定义长度随机字符串"""
        lengths = [8, 16, 64, 128]
        
        for length in lengths:
            random_str = generate_random_string(length)
            assert len(random_str) == length
            assert random_str.isalnum()
    
    def test_generate_random_string_uniqueness(self):
        """测试随机字符串的唯一性"""
        strings = [generate_random_string() for _ in range(100)]
        
        # 确保生成的字符串都是唯一的
        assert len(set(strings)) == len(strings)
    
    def test_generate_temp_token(self):
        """测试生成临时令牌"""
        token = generate_temp_token()
        
        assert isinstance(token, str)
        assert len(token) == 64
        assert token.isalnum()
    
    def test_generate_temp_token_uniqueness(self):
        """测试临时令牌的唯一性"""
        tokens = [generate_temp_token() for _ in range(50)]
        
        # 确保生成的令牌都是唯一的
        assert len(set(tokens)) == len(tokens)


class TestPasswordStrengthValidation:
    """测试密码强度验证"""
    
    def test_validate_password_strength_valid(self):
        """测试验证有效密码强度"""
        valid_passwords = [
            "Test123456",  # 包含大小写字母和数字
            "MyPassword1",
            "SecurePass99",
        ]
        
        for password in valid_passwords:
            is_valid, errors = validate_password_strength(password)
            assert is_valid is True
            assert len(errors) == 0
    
    def test_validate_password_strength_too_short(self):
        """测试验证过短密码"""
        short_password = "Test1"  # 少于8个字符
        
        is_valid, errors = validate_password_strength(short_password)
        assert is_valid is False
        assert any("长度至少需要" in error for error in errors)
    
    def test_validate_password_strength_no_uppercase(self):
        """测试验证无大写字母密码"""
        password = "test123456"  # 无大写字母
        
        is_valid, errors = validate_password_strength(password)
        assert is_valid is False
        assert any("大写字母" in error for error in errors)
    
    def test_validate_password_strength_no_lowercase(self):
        """测试验证无小写字母密码"""
        password = "TEST123456"  # 无小写字母
        
        is_valid, errors = validate_password_strength(password)
        assert is_valid is False
        assert any("小写字母" in error for error in errors)
    
    def test_validate_password_strength_no_numbers(self):
        """测试验证无数字密码"""
        password = "TestPassword"  # 无数字
        
        is_valid, errors = validate_password_strength(password)
        assert is_valid is False
        assert any("数字" in error for error in errors)
    
    @patch('app.core.config.settings')
    def test_validate_password_strength_symbols_required(self, mock_settings):
        """测试验证需要特殊符号的密码"""
        # 设置mock配置
        mock_settings.PASSWORD_REQUIRE_SYMBOLS = True
        mock_settings.PASSWORD_MIN_LENGTH = 8
        mock_settings.PASSWORD_REQUIRE_UPPERCASE = True
        mock_settings.PASSWORD_REQUIRE_LOWERCASE = True
        mock_settings.PASSWORD_REQUIRE_NUMBERS = True
        
        # 直接调用函数进行测试，而不是重新导入模块
        password_without_symbols = "Test123456"
        password_with_symbols = "Test123456!"
        
        is_valid1, errors1 = validate_password_strength(password_without_symbols)
        assert is_valid1 is False
        assert any("特殊符号" in error for error in errors1)
        
        is_valid2, errors2 = validate_password_strength(password_with_symbols)
        assert is_valid2 is True
        assert len(errors2) == 0
    
    def test_validate_password_strength_multiple_errors(self):
        """测试验证有多个错误的密码"""
        bad_password = "test"  # 太短，无大写字母，无数字
        
        is_valid, errors = validate_password_strength(bad_password)
        assert is_valid is False
        assert len(errors) >= 3  # 至少有3个错误
    
    def test_validate_password_strength_edge_cases(self):
        """测试密码验证边界情况"""
        edge_cases = [
            ("", False),  # 空密码
            ("1234567", False),  # 只有数字
            ("abcdefgh", False),  # 只有小写字母
            ("ABCDEFGH", False),  # 只有大写字母
            ("Test123", False),  # 少一个字符
            ("Test1234", True),  # 刚好满足要求
        ]
        
        for password, expected_valid in edge_cases:
            is_valid, _ = validate_password_strength(password)
            assert is_valid == expected_valid, f"Password '{password}' validation failed"


class TestSecurityIntegration:
    """测试安全功能集成"""
    
    def test_full_authentication_flow(self):
        """测试完整的认证流程"""
        username = "testuser"
        password = "Test123456"
        
        # 1. 创建密码哈希
        password_hash = get_password_hash(password)
        
        # 2. 验证密码
        assert verify_password(password, password_hash) is True
        
        # 3. 创建访问令牌
        access_token = create_access_token(username)
        
        # 4. 验证令牌
        verified_username = verify_token(access_token)
        assert verified_username == username
        
        # 5. 创建刷新令牌
        refresh_token = create_refresh_token(username)
        
        # 6. 验证刷新令牌
        verified_refresh_username = verify_token(refresh_token)
        assert verified_refresh_username == username
    
    def test_token_lifecycle(self):
        """测试令牌生命周期"""
        username = "testuser"
        
        # 创建短期令牌
        short_token = create_access_token(username, timedelta(seconds=1))
        
        # 立即验证应该成功
        assert verify_token(short_token) == username
        
        # 等待令牌过期
        import time
        time.sleep(2)
        
        # 过期后验证应该失败
        assert verify_token(short_token) is None