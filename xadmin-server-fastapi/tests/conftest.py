"""
pytest配置文件，设置测试环境和mock依赖
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
from fastapi.testclient import TestClient
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 全局Mock模型，避免数据库操作
class MockBase:
    """Mock基础模型"""
    metadata = MagicMock()
    __table__ = MagicMock()
    __tablename__ = "mock_table"

class MockUserInfo(MockBase):
    """Mock用户模型"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.username = kwargs.get('username', 'testuser')
        self.email = kwargs.get('email', 'test@example.com')
        self.phone = kwargs.get('phone', '13800138000')
        self.nickname = kwargs.get('nickname', '测试用户')
        self.is_active = kwargs.get('is_active', True)
        self.is_deleted = kwargs.get('is_deleted', False)
        self.password = kwargs.get('password', 'hashed_password')
        self.roles = kwargs.get('roles', [])
        self.permissions = kwargs.get('permissions', [])
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_login = datetime.now()
        
class MockUserRole(MockBase):
    """Mock角色模型"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.name = kwargs.get('name', 'test_role')
        self.code = kwargs.get('code', 'test_role')
        self.is_active = kwargs.get('is_active', True)
        
class MockDeptInfo(MockBase):
    """Mock部门模型"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.name = kwargs.get('name', 'test_dept')
        self.code = kwargs.get('code', 'test_dept')

@pytest.fixture
def test_db_engine():
    """为测试创建内存数据库引擎"""
    # 创建内存SQLite数据库
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    yield engine


@pytest.fixture
def test_db_session(test_db_engine):
    """为模型测试创建内存数据库会话"""
    # 导入所有模型以确保表结构被创建
    from app.models.base import BaseModel
    from app.models.user import UserInfo, UserRole, DeptInfo, DataPermission
    
    # 创建所有表
    BaseModel.metadata.create_all(bind=test_db_engine)
    
    # 创建会话
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="session", autouse=True)
def setup_global_mocks():
    """设置全局mock"""
    
    # Mock必要的SQLAlchemy操作，不mock模型类
    with patch('sqlalchemy.create_engine') as mock_create_engine, \
         patch('sqlalchemy.orm.sessionmaker') as mock_sessionmaker, \
         patch('app.core.database.get_db') as mock_get_db:
        
        # Mock数据库引擎
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Mock Session
        mock_session = MagicMock()
        mock_session_class = MagicMock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_class
        
        # Mock数据库查询操作
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_query.all.return_value = []
        mock_query.count.return_value = 0
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        
        # Mock数据库写操作
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.rollback.return_value = None
        mock_session.close.return_value = None
        mock_session.refresh.return_value = None
        
        mock_get_db.return_value = mock_session
        
        yield mock_session

@pytest.fixture(scope="session", autouse=True)
def mock_external_dependencies():
    """Mock外部依赖"""
    with patch('redis.from_url') as mock_redis_from_url, \
         patch('app.core.security.get_password_hash') as mock_get_password_hash, \
         patch('app.core.security.verify_password') as mock_verify_password, \
         patch('app.core.security.create_access_token') as mock_create_access_token, \
         patch('app.core.security.create_refresh_token') as mock_create_refresh_token:
        
        # Mock Redis
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.setex.return_value = True
        mock_redis.delete.return_value = True
        mock_redis.exists.return_value = False
        mock_redis_from_url.return_value = mock_redis
        
        # Mock密码哈希
        mock_get_password_hash.return_value = "hashed_password"
        mock_verify_password.return_value = True
        
        # Mock令牌创建
        mock_create_access_token.return_value = "mock_access_token"
        mock_create_refresh_token.return_value = "mock_refresh_token"
        
        yield

@pytest.fixture(scope="session", autouse=True)
def mock_settings():
    """Mock应用设置"""
    from unittest.mock import patch
    
    mock_settings = MagicMock()
    mock_settings.DATABASE_URL = "sqlite:///:memory:"
    mock_settings.SECRET_KEY = "test-secret-key"
    mock_settings.ALGORITHM = "HS256"
    mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    mock_settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
    mock_settings.REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
    mock_settings.BACKEND_CORS_ORIGINS = ["http://localhost:3000"]
    mock_settings.PROJECT_NAME = "xAdmin FastAPI"
    mock_settings.DEBUG = True
    mock_settings.HOST = "127.0.0.1"
    mock_settings.PORT = 8000
    mock_settings.REDIS_URL = "redis://localhost:6379/0"
    mock_settings.CAPTCHA_ENABLED = True
    
    with patch('app.core.config.settings', mock_settings):
        yield mock_settings

@pytest.fixture
def client():
    """测试客户端，使用实际的app"""
    # 导入实际的应用
    from main import app
    
    return TestClient(app)

@pytest.fixture
def mock_user_data():
    """Mock用户数据"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "phone": "13800138000",
        "nickname": "测试用户",
        "is_active": True,
        "roles": ["user"]
    }

@pytest.fixture
def mock_auth_response():
    """Mock认证响应"""
    return {
        "access": "mock_access_token",
        "refresh": "mock_refresh_token",
        "access_token_lifetime": 1800,
        "refresh_token_lifetime": 604800
    }

@pytest.fixture
def mock_captcha_service():
    """Mock验证码服务"""
    with patch('app.services.captcha.CaptchaService') as mock_service_class:
        mock_service = MagicMock()
        mock_service.generate_captcha.return_value = {
            "captcha_image": "mock_base64_image",
            "captcha_key": "mock_captcha_key",
            "length": 4
        }
        mock_service.verify_captcha.return_value = True
        mock_service.is_captcha_required.return_value = False
        mock_service_class.return_value = mock_service
        yield mock_service

@pytest.fixture 
def mock_user_service():
    """Mock用户服务"""
    with patch('app.services.user.UserService') as mock_service_class:
        mock_service = MagicMock()
        mock_service.get_by_username.return_value = None
        mock_service.get_by_email.return_value = None
        mock_service.create_user.return_value = MockUserInfo(id=1, username="testuser")
        mock_service.authenticate.return_value = MockUserInfo(id=1, username="testuser")
        mock_service.authenticate_user = mock_service.authenticate  # 别名
        mock_service_class.return_value = mock_service
        yield mock_service

# Mock数据生成器
class MockDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_user_data(index=1):
        """生成用户数据"""
        return {
            "username": f"user{index}",
            "email": f"user{index}@example.com",
            "password": f"Password{index}",
            "nickname": f"用户{index}",
            "mobile": f"1380013800{index}",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False
        }
    
    @staticmethod
    def generate_role_data(index=1):
        """生成角色数据"""
        return {
            "name": f"角色{index}",
            "code": f"role_{index}",
            "sort": index,
            "status": True,
            "remark": f"测试角色{index}"
        }
    
    @staticmethod
    def generate_dept_data(index=1):
        """生成部门数据"""
        return {
            "name": f"部门{index}",
            "code": f"dept_{index}",
            "sort": index,
            "status": True,
            "remark": f"测试部门{index}"
        }


@pytest.fixture
def mock_data_generator():
    """Mock数据生成器的fixture"""
    return MockDataGenerator


# 测试标记
pytest_plugins = []


def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "unit: 标记为单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记为集成测试"
    )
    config.addinivalue_line(
        "markers", "api: 标记为API测试"
    )
    config.addinivalue_line(
        "markers", "slow: 标记为慢速测试"
    )


# 测试钩子
def pytest_runtest_setup(item):
    """测试运行前的设置"""
    # 可以在这里添加测试前的通用设置
    pass


def pytest_runtest_teardown(item):
    """测试运行后的清理"""
    # 可以在这里添加测试后的通用清理
    pass