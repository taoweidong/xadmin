"""
测试 app.core.config 模块
"""
import pytest
import os
from unittest.mock import patch
from app.core.config import Settings


class TestSettings:
    """测试Settings配置类"""
    
    def test_default_settings(self):
        """测试默认配置"""
        settings = Settings()
        
        assert settings.PROJECT_NAME == "xAdmin FastAPI"
        assert settings.VERSION == "1.0.0"
        assert settings.API_V1_STR == "/api"
        assert settings.HOST == "127.0.0.1"
        assert settings.PORT == 8000
        assert settings.DEBUG is False
        assert settings.DB_ENGINE == "sqlite"
        
    def test_cors_origins_string_parsing(self):
        """测试CORS源的字符串解析"""
        settings = Settings()
        
        # 测试字符串格式的CORS origins
        with patch.dict(os.environ, {'BACKEND_CORS_ORIGINS': 'http://localhost:3000,http://localhost:8080'}):
            new_settings = Settings()
            assert "http://localhost:3000" in new_settings.BACKEND_CORS_ORIGINS
            assert "http://localhost:8080" in new_settings.BACKEND_CORS_ORIGINS
    
    def test_database_url_sqlite(self):
        """测试SQLite数据库URL生成"""
        settings = Settings(DB_ENGINE="sqlite")
        assert settings.DATABASE_URL == "sqlite:///./xadmin.db"
    
    def test_database_url_mysql(self):
        """测试MySQL数据库URL生成"""
        settings = Settings(
            DB_ENGINE="mysql",
            DB_USER="testuser",
            DB_PASSWORD="testpass",
            DB_HOST="localhost",
            DB_PORT=3306,
            DB_NAME="testdb"
        )
        expected_url = "mysql+pymysql://testuser:testpass@localhost:3306/testdb"
        assert settings.DATABASE_URL == expected_url
    
    def test_database_url_postgresql(self):
        """测试PostgreSQL数据库URL生成"""
        settings = Settings(
            DB_ENGINE="postgresql",
            DB_USER="testuser",
            DB_PASSWORD="testpass",
            DB_HOST="localhost", 
            DB_PORT=5432,
            DB_NAME="testdb"
        )
        expected_url = "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
        assert settings.DATABASE_URL == expected_url
    
    def test_database_url_unsupported_engine(self):
        """测试不支持的数据库引擎"""
        settings = Settings(DB_ENGINE="unsupported")
        
        with pytest.raises(ValueError, match="Unsupported database engine"):
            _ = settings.DATABASE_URL
    
    def test_redis_url_without_password(self):
        """测试无密码Redis URL生成"""
        settings = Settings(
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            REDIS_DB=0,
            REDIS_PASSWORD=""
        )
        assert settings.REDIS_URL == "redis://localhost:6379/0"
    
    def test_redis_url_with_password(self):
        """测试有密码Redis URL生成"""
        settings = Settings(
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            REDIS_DB=0,
            REDIS_PASSWORD="testpass"
        )
        assert settings.REDIS_URL == "redis://:testpass@localhost:6379/0"
    
    def test_celery_broker_url_default(self):
        """测试Celery broker URL默认值"""
        settings = Settings()
        # 应该使用Redis URL作为默认值
        assert "redis://" in settings.CELERY_BROKER_URL
    
    def test_celery_result_backend_default(self):
        """测试Celery result backend默认值"""
        settings = Settings()
        # 应该使用Redis URL作为默认值
        assert "redis://" in settings.CELERY_RESULT_BACKEND
    
    def test_environment_variable_loading(self):
        """测试环境变量加载"""
        with patch.dict(os.environ, {
            'PROJECT_NAME': 'Test Project',
            'VERSION': '2.0.0',
            'DEBUG': 'true',
            'PORT': '9000'
        }):
            settings = Settings()
            assert settings.PROJECT_NAME == 'Test Project'
            assert settings.VERSION == '2.0.0'
            assert settings.DEBUG is True
            assert settings.PORT == 9000
    
    def test_security_settings(self):
        """测试安全相关配置"""
        settings = Settings()
        
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 8  # 8 days
        assert settings.REFRESH_TOKEN_EXPIRE_MINUTES == 60 * 24 * 30  # 30 days
        assert settings.ALGORITHM == "HS256"
        assert settings.PASSWORD_MIN_LENGTH == 8
        assert settings.PASSWORD_REQUIRE_UPPERCASE is True
        assert settings.PASSWORD_REQUIRE_LOWERCASE is True
        assert settings.PASSWORD_REQUIRE_NUMBERS is True
        assert settings.PASSWORD_REQUIRE_SYMBOLS is False
    
    def test_file_upload_settings(self):
        """测试文件上传配置"""
        settings = Settings()
        
        assert settings.MEDIA_ROOT == "./media"
        assert settings.STATIC_ROOT == "./static"
        assert settings.MAX_UPLOAD_SIZE == 10 * 1024 * 1024  # 10MB
        assert isinstance(settings.ALLOWED_EXTENSIONS, list)
        assert ".jpg" in settings.ALLOWED_EXTENSIONS
        assert ".pdf" in settings.ALLOWED_EXTENSIONS
    
    def test_log_settings(self):
        """测试日志配置"""
        settings = Settings()
        
        assert settings.LOG_LEVEL == "INFO"
        assert "%(asctime)s" in settings.LOG_FORMAT
        assert "%(levelname)s" in settings.LOG_FORMAT
    
    def test_case_sensitivity(self):
        """测试配置的大小写敏感性"""
        # Settings类配置为case_sensitive=True
        with patch.dict(os.environ, {'project_name': 'Lower Case'}):
            settings = Settings()
            # 应该使用默认值而不是小写的环境变量
            assert settings.PROJECT_NAME == "xAdmin FastAPI"
    
    def test_cors_origins_validation(self):
        """测试CORS源验证"""
        # 测试列表格式
        settings = Settings(
            BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
        )
        assert len(settings.BACKEND_CORS_ORIGINS) == 2
        
        # 测试字符串格式
        settings = Settings(
            BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8080"
        )
        assert len(settings.BACKEND_CORS_ORIGINS) == 2
    
    def test_smtp_settings(self):
        """测试SMTP邮件配置"""
        settings = Settings()
        
        assert settings.SMTP_TLS is True
        assert settings.SMTP_PORT is None
        assert settings.SMTP_HOST is None
        assert settings.SMTP_USER is None
        assert settings.SMTP_PASSWORD is None
        assert settings.EMAILS_FROM_EMAIL is None
        assert settings.EMAILS_FROM_NAME is None
    
    @pytest.mark.parametrize("db_engine,expected_in_url", [
        ("sqlite", "sqlite:///"),
        ("mysql", "mysql+pymysql://"),
        ("postgresql", "postgresql+asyncpg://"),
    ])
    def test_database_url_patterns(self, db_engine, expected_in_url):
        """测试不同数据库引擎的URL模式"""
        settings = Settings(
            DB_ENGINE=db_engine,
            DB_USER="test",
            DB_PASSWORD="test",
            DB_HOST="localhost",
            DB_NAME="test"
        )
        
        if db_engine == "sqlite":
            assert settings.DATABASE_URL == "sqlite:///./xadmin.db"
        else:
            assert expected_in_url in settings.DATABASE_URL