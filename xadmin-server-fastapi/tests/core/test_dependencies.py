"""
测试 app.core.dependencies 模块
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    get_current_staff_user,
    PermissionChecker,
    require_permission,
    RoleChecker,
    require_roles,
    DataPermissionChecker,
    require_data_permission,
    get_optional_user,
)
from app.models.user import UserInfo
from app.models.system import MenuInfo
from app.models.user import UserRole, DataPermission


class TestGetCurrentUser:
    """测试获取当前用户功能"""
    
    def test_get_current_user_no_token(self):
        """测试无令牌情况"""
        db = Mock(spec=Session)
        token = None
        
        result = get_current_user(db, token)
        assert result is None
    
    @patch('app.core.dependencies.verify_token')
    @patch('app.core.dependencies.UserService')
    def test_get_current_user_valid_token(self, mock_user_service, mock_verify_token):
        """测试有效令牌情况"""
        db = Mock(spec=Session)
        token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        
        mock_verify_token.return_value = "testuser"
        
        mock_user = Mock(spec=UserInfo)
        mock_user.is_active = True
        mock_user_service_instance = Mock()
        mock_user_service_instance.get_by_username.return_value = mock_user
        mock_user_service.return_value = mock_user_service_instance
        
        result = get_current_user(db, token)
        
        assert result == mock_user
        mock_verify_token.assert_called_once_with("valid_token")
        mock_user_service_instance.get_by_username.assert_called_once_with("testuser")
    
    @patch('app.core.dependencies.verify_token')
    def test_get_current_user_invalid_token(self, mock_verify_token):
        """测试无效令牌情况"""
        db = Mock(spec=Session)
        token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        
        mock_verify_token.return_value = None
        
        result = get_current_user(db, token)
        assert result is None
    
    @patch('app.core.dependencies.verify_token')
    @patch('app.core.dependencies.UserService')
    def test_get_current_user_inactive_user(self, mock_user_service, mock_verify_token):
        """测试非活跃用户情况"""
        db = Mock(spec=Session)
        token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        
        mock_verify_token.return_value = "testuser"
        
        mock_user = Mock(spec=UserInfo)
        mock_user.is_active = False
        mock_user_service_instance = Mock()
        mock_user_service_instance.get_by_username.return_value = mock_user
        mock_user_service.return_value = mock_user_service_instance
        
        result = get_current_user(db, token)
        assert result is None
    
    @patch('app.core.dependencies.verify_token')
    @patch('app.core.dependencies.UserService')
    def test_get_current_user_user_not_found(self, mock_user_service, mock_verify_token):
        """测试用户不存在情况"""
        db = Mock(spec=Session)
        token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        
        mock_verify_token.return_value = "nonexistent_user"
        
        mock_user_service_instance = Mock()
        mock_user_service_instance.get_by_username.return_value = None
        mock_user_service.return_value = mock_user_service_instance
        
        result = get_current_user(db, token)
        assert result is None
    
    @patch('app.core.dependencies.verify_token')
    def test_get_current_user_exception(self, mock_verify_token):
        """测试异常情况"""
        db = Mock(spec=Session)
        token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        
        mock_verify_token.side_effect = Exception("Token verification error")
        
        result = get_current_user(db, token)
        assert result is None


class TestGetCurrentActiveUser:
    """测试获取当前活跃用户功能"""
    
    def test_get_current_active_user_valid(self):
        """测试有效活跃用户"""
        mock_user = Mock(spec=UserInfo)
        mock_user.is_active = True
        
        result = get_current_active_user(mock_user)
        assert result == mock_user
    
    def test_get_current_active_user_none(self):
        """测试用户为None的情况"""
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user(None)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "未认证" in exc_info.value.detail


class TestGetCurrentSuperuser:
    """测试获取当前超级用户功能"""
    
    def test_get_current_superuser_valid(self):
        """测试有效超级用户"""
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = True
        
        result = get_current_superuser(mock_user)
        assert result == mock_user
    
    def test_get_current_superuser_not_superuser(self):
        """测试非超级用户"""
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = False
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_superuser(mock_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "超级用户权限" in exc_info.value.detail


class TestGetCurrentStaffUser:
    """测试获取当前员工用户功能"""
    
    def test_get_current_staff_user_valid(self):
        """测试有效员工用户"""
        mock_user = Mock(spec=UserInfo)
        mock_user.is_staff = True
        
        result = get_current_staff_user(mock_user)
        assert result == mock_user
    
    def test_get_current_staff_user_not_staff(self):
        """测试非员工用户"""
        mock_user = Mock(spec=UserInfo)
        mock_user.is_staff = False
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_staff_user(mock_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "员工权限" in exc_info.value.detail


class TestPermissionChecker:
    """测试权限检查器"""
    
    def test_permission_checker_superuser(self):
        """测试超级用户权限检查"""
        checker = PermissionChecker("test_permission")
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = True
        
        result = checker(mock_user)
        assert result == mock_user
    
    def test_permission_checker_valid_permission(self):
        """测试有效权限检查"""
        checker = PermissionChecker("test_permission")
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = False
        
        # 模拟用户角色权限
        mock_role = Mock(spec=UserRole)
        mock_role.is_active = True
        mock_menu = Mock(spec=MenuInfo)
        mock_menu.permission = "test_permission"
        mock_role.menus = [mock_menu]
        mock_user.roles = [mock_role]
        mock_user.permissions = []
        
        result = checker(mock_user)
        assert result == mock_user
    
    def test_permission_checker_valid_direct_permission(self):
        """测试用户直接权限检查"""
        checker = PermissionChecker("test_permission")
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = False
        mock_user.roles = []
        
        # 模拟用户直接权限
        mock_permission = Mock(spec=DataPermission)
        mock_permission.is_active = True
        mock_permission.code = "test_permission"
        mock_user.permissions = [mock_permission]
        
        result = checker(mock_user)
        assert result == mock_user
    
    def test_permission_checker_no_permission(self):
        """测试无权限情况"""
        checker = PermissionChecker("test_permission")
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = False
        mock_user.roles = []
        mock_user.permissions = []
        
        with pytest.raises(HTTPException) as exc_info:
            checker(mock_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "test_permission" in exc_info.value.detail
    
    def test_require_permission_decorator(self):
        """测试权限要求装饰器"""
        permission_checker = require_permission("test_permission")
        assert isinstance(permission_checker, PermissionChecker)
        assert permission_checker.permission == "test_permission"


class TestRoleChecker:
    """测试角色检查器"""
    
    def test_role_checker_superuser(self):
        """测试超级用户角色检查"""
        checker = RoleChecker(["test_role"])
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = True
        
        result = checker(mock_user)
        assert result == mock_user
    
    def test_role_checker_valid_role(self):
        """测试有效角色检查"""
        checker = RoleChecker(["test_role"])
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = False
        
        mock_role = Mock(spec=UserRole)
        mock_role.is_active = True
        mock_role.code = "test_role"
        mock_user.roles = [mock_role]
        
        result = checker(mock_user)
        assert result == mock_user
    
    def test_role_checker_multiple_roles(self):
        """测试多角色检查"""
        checker = RoleChecker(["role1", "role2"])
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = False
        
        mock_role = Mock(spec=UserRole)
        mock_role.is_active = True
        mock_role.code = "role2"
        mock_user.roles = [mock_role]
        
        result = checker(mock_user)
        assert result == mock_user
    
    def test_role_checker_no_role(self):
        """测试无角色情况"""
        checker = RoleChecker(["test_role"])
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = False
        mock_user.roles = []
        
        with pytest.raises(HTTPException) as exc_info:
            checker(mock_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "test_role" in exc_info.value.detail
    
    def test_role_checker_inactive_role(self):
        """测试非活跃角色"""
        checker = RoleChecker(["test_role"])
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = False
        
        mock_role = Mock(spec=UserRole)
        mock_role.is_active = False
        mock_role.code = "test_role"
        mock_user.roles = [mock_role]
        
        with pytest.raises(HTTPException) as exc_info:
            checker(mock_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    def test_require_roles_decorator(self):
        """测试角色要求装饰器"""
        role_checker = require_roles(["test_role"])
        assert isinstance(role_checker, RoleChecker)
        assert role_checker.role_codes == ["test_role"]
    
    def test_role_checker_single_role_string(self):
        """测试单个角色字符串输入"""
        checker = RoleChecker("test_role")
        assert checker.role_codes == ["test_role"]


class TestDataPermissionChecker:
    """测试数据权限检查器"""
    
    def test_data_permission_checker_superuser(self):
        """测试超级用户数据权限检查"""
        checker = DataPermissionChecker("user", "read")
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = True
        
        result = checker(mock_user)
        assert result == mock_user
    
    def test_data_permission_checker_normal_user(self):
        """测试普通用户数据权限检查"""
        checker = DataPermissionChecker("user", "read")
        mock_user = Mock(spec=UserInfo)
        mock_user.is_superuser = False
        
        # 目前实现是直接返回用户，未来可扩展更复杂的逻辑
        result = checker(mock_user)
        assert result == mock_user
    
    def test_require_data_permission_decorator(self):
        """测试数据权限要求装饰器"""
        data_permission_checker = require_data_permission("user", "read")
        assert isinstance(data_permission_checker, DataPermissionChecker)
        assert data_permission_checker.resource == "user"
        assert data_permission_checker.action == "read"
    
    def test_data_permission_checker_default_action(self):
        """测试数据权限检查器默认操作"""
        checker = DataPermissionChecker("user")
        assert checker.resource == "user"
        assert checker.action == "read"


class TestGetOptionalUser:
    """测试获取可选用户功能"""
    
    @patch('app.core.dependencies.get_current_user')
    def test_get_optional_user(self, mock_get_current_user):
        """测试获取可选用户"""
        db = Mock(spec=Session)
        token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
        mock_user = Mock(spec=UserInfo)
        
        mock_get_current_user.return_value = mock_user
        
        result = get_optional_user(db, token)
        
        assert result == mock_user
        mock_get_current_user.assert_called_once_with(db, token)


class TestDependencyIntegration:
    """测试依赖注入集成"""
    
    def test_authentication_flow(self):
        """测试认证流程"""
        # 模拟完整的认证流程
        mock_user = Mock(spec=UserInfo)
        mock_user.is_active = True
        mock_user.is_staff = True
        mock_user.is_superuser = False
        
        # 测试活跃用户检查
        active_user = get_current_active_user(mock_user)
        assert active_user == mock_user
        
        # 测试员工用户检查
        staff_user = get_current_staff_user(mock_user)
        assert staff_user == mock_user
    
    def test_permission_hierarchy(self):
        """测试权限层级"""
        # 超级用户应该通过所有权限检查
        superuser = Mock(spec=UserInfo)
        superuser.is_superuser = True
        
        permission_checker = PermissionChecker("any_permission")
        role_checker = RoleChecker(["any_role"])
        data_permission_checker = DataPermissionChecker("any_resource")
        
        assert permission_checker(superuser) == superuser
        assert role_checker(superuser) == superuser
        assert data_permission_checker(superuser) == superuser