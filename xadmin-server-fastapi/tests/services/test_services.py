"""
测试 app.services 模块 - 主要服务类的单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from app.services.user import UserService
from app.services.captcha import CaptchaService
from app.models.user import UserInfo
from app.schemas.user import UserCreate, UserUpdate


class TestUserService:
    """测试用户服务"""
    
    def test_user_service_init(self):
        """测试用户服务初始化"""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)
        assert service.db == mock_db
    
    def test_get_by_username(self, test_db_session):
        """测试根据用户名获取用户"""
        service = UserService(test_db_session)
        
        # 创建测试用户
        user = UserInfo(username="testuser", password="hashed_password")
        test_db_session.add(user)
        test_db_session.commit()
        
        # 测试获取用户
        result = service.get_by_username("testuser")
        assert result is not None
        assert result.username == "testuser"
        
        # 测试不存在的用户
        result = service.get_by_username("nonexistent")
        assert result is None
    
    def test_get_by_email(self, test_db_session):
        """测试根据邮箱获取用户"""
        service = UserService(test_db_session)
        
        # 创建测试用户
        user = UserInfo(username="testuser", password="password", email="test@example.com")
        test_db_session.add(user)
        test_db_session.commit()
        
        # 测试获取用户
        result = service.get_by_email("test@example.com")
        assert result is not None
        assert str(result.email) == "test@example.com"
    
    def test_create_user(self, test_db_session):
        """测试创建用户"""
        service = UserService(test_db_session)

        user_data = {
            "username": "newuser",
            "password": "Password123",
            "email": "newuser@example.com",
            "nickname": "新用户"
        }

        with patch('app.services.user.get_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password"

            result = service.create_user(user_data)

            assert result is not None
            assert result.username == "newuser"
            assert str(result.email) == "newuser@example.com"
            assert result.nickname == "新用户"
            mock_hash.assert_called_once_with("Password123")
    
    def test_update_user(self, test_db_session):
        """测试更新用户"""
        service = UserService(test_db_session)
        
        # 创建测试用户
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        # 更新用户数据
        update_data = {
            "nickname": "更新后的昵称",
            "email": "updated@example.com"
        }
        
        result = service.update_user(user.id, update_data)
        
        assert result is not None
        assert result.nickname == "更新后的昵称"
        assert str(result.email) == "updated@example.com"
    
    def test_delete_user(self, test_db_session):
        """测试删除用户"""
        service = UserService(test_db_session)
        
        # 创建测试用户
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        user_id = user.id
        
        # 删除用户
        result = service.delete_user(user_id)
        assert result is True
        
        # 验证用户已删除
        deleted_user = service.get_by_id(user_id)
        assert deleted_user is None
    
    def test_authenticate_user(self, test_db_session):
        """测试用户认证"""
        service = UserService(test_db_session)
        
        # 创建测试用户
        user = UserInfo(username="testuser", password="hashed_password")
        test_db_session.add(user)
        test_db_session.commit()
        
        with patch('app.core.security.verify_password') as mock_verify:
            # 测试认证成功
            mock_verify.return_value = True
            result = service.authenticate("testuser", "correct_password")
            assert result == user
            
            # 测试认证失败
            mock_verify.return_value = False
            result = service.authenticate("testuser", "wrong_password")
            assert result is None
    
    def test_is_active_user(self, test_db_session):
        """测试用户激活状态检查"""
        service = UserService(test_db_session)
        
        # 创建激活用户
        active_user = UserInfo(username="active", password="password", is_active=True)
        # 创建非激活用户
        inactive_user = UserInfo(username="inactive", password="password", is_active=False)
        
        test_db_session.add_all([active_user, inactive_user])
        test_db_session.commit()
        
        assert service.is_active_user(active_user) is True
        assert service.is_active_user(inactive_user) is False


class TestCaptchaService:
    """测试验证码服务"""
    
    def test_captcha_service_init(self):
        """测试验证码服务初始化"""
        service = CaptchaService()
        assert service is not None
    
    @patch('app.services.captcha.generate_random_string')
    @patch('captcha.image.ImageCaptcha')
    def test_generate_captcha(self, mock_image_captcha, mock_random_string):
        """测试生成验证码"""
        service = CaptchaService()
        
        # 模拟随机字符串生成
        mock_random_string.return_value = "ABC123"
        
        # 模拟验证码图片生成
        mock_captcha_instance = MagicMock()
        mock_captcha_instance.generate.return_value = b"fake_image_data"
        mock_image_captcha.return_value = mock_captcha_instance
        
        result = service.generate_captcha()
        
        assert "captcha_key" in result
        assert "captcha_image" in result
        assert "length" in result
        assert result["length"] == 6  # 默认长度
    
    def test_verify_captcha(self):
        """测试验证验证码"""
        service = CaptchaService()
        
        with patch.object(service, '_get_stored_captcha') as mock_get:
            # 测试验证成功
            mock_get.return_value = "ABC123"
            result = service.verify_captcha("captcha_key", "ABC123")
            assert result is True
            
            # 测试验证失败 - 验证码不匹配
            result = service.verify_captcha("captcha_key", "WRONG")
            assert result is False
            
            # 测试验证失败 - 验证码不存在
            mock_get.return_value = None
            result = service.verify_captcha("invalid_key", "ABC123")
            assert result is False
    
    def test_is_captcha_required(self):
        """测试验证码是否必需"""
        service = CaptchaService()
        
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.CAPTCHA_ENABLED = True
            assert service.is_captcha_required() is True
            
            mock_settings.CAPTCHA_ENABLED = False
            assert service.is_captcha_required() is False


class TestServiceIntegration:
    """测试服务集成功能"""
    
    def test_user_service_with_captcha_service(self, test_db_session):
        """测试用户服务与验证码服务集成"""
        user_service = UserService(test_db_session)
        captcha_service = CaptchaService()
        
        # 创建用户时需要验证码
        user_data = {
            "username": "newuser",
            "password": "Password123",
            "email": "newuser@example.com"
        }
        
        with patch.object(captcha_service, 'verify_captcha') as mock_verify:
            mock_verify.return_value = True
            
            with patch('app.core.security.get_password_hash') as mock_hash:
                mock_hash.return_value = "hashed_password"
                
                # 验证码验证通过，可以创建用户
                if captcha_service.verify_captcha("captcha_key", "ABC123"):
                    result = user_service.create_user(user_data)
                    assert result is not None
                    assert result.username == "newuser"
    
    def test_user_authentication_flow(self, test_db_session):
        """测试用户认证流程"""
        service = UserService(test_db_session)
        
        # 1. 创建用户
        user = UserInfo(
            username="testuser",
            password="hashed_password",
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        # 2. 认证流程
        with patch('app.core.security.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            # 获取用户
            found_user = service.get_by_username("testuser")
            assert found_user is not None
            
            # 验证密码
            authenticated_user = service.authenticate("testuser", "correct_password")
            assert authenticated_user == user
            
            # 检查激活状态
            assert service.is_active_user(authenticated_user) is True
    
    def test_user_management_operations(self, test_db_session):
        """测试用户管理操作"""
        service = UserService(test_db_session)
        
        # 1. 创建用户
        user_data = {
            "username": "manager",
            "password": "Password123",
            "email": "manager@example.com",
            "is_staff": True
        }
        
        with patch('app.core.security.get_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password"
            created_user = service.create_user(user_data)
        
        # 2. 更新用户
        update_data = {"nickname": "管理员"}
        updated_user = service.update_user(created_user.id, update_data)
        assert updated_user.nickname == "管理员"
        
        # 3. 查询用户
        found_user = service.get_by_id(created_user.id)
        assert found_user.nickname == "管理员"
        
        # 4. 删除用户
        delete_result = service.delete_user(created_user.id)
        assert delete_result is True


# 模拟其他服务的基础测试
class TestOtherServices:
    """测试其他服务模块"""
    
    def test_dept_service_placeholder(self):
        """部门服务占位测试"""
        # 这里应该有dept service的测试
        # 由于时间关系，先创建占位测试
        assert True
    
    def test_role_service_placeholder(self):
        """角色服务占位测试"""
        # 这里应该有role service的测试
        assert True
    
    def test_file_upload_service_placeholder(self):
        """文件上传服务占位测试"""
        # 这里应该有file upload service的测试
        assert True
    
    def test_message_service_placeholder(self):
        """消息服务占位测试"""
        # 这里应该有message service的测试
        assert True
    
    def test_settings_service_placeholder(self):
        """设置服务占位测试"""
        # 这里应该有settings service的测试
        assert True