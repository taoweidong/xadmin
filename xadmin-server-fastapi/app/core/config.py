"""
应用程序配置文件
"""
from typing import Any, Dict, List, Optional, Union
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import field_validator, computed_field
except ImportError:
    from pydantic import BaseSettings, field_validator, computed_field
    SettingsConfigDict = None
import os
import json
from pathlib import Path


class Settings(BaseSettings):
    # 应用基本配置
    PROJECT_NAME: str = "xAdmin FastAPI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False
    
    # 跨域配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str], None]) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            # 首先尝试将字符串视为逗号分隔的列表
            try:
                return [i.strip() for i in v.split(",")]
            except:
                pass
            # 如果失败，再尝试将其视为JSON字符串
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    return [i.strip() for i in v.strip("[]").split(",")]
            return [v.strip()]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid format for BACKEND_CORS_ORIGINS: {v}")
    
    # 数据库配置
    DB_ENGINE: str = "sqlite"  # sqlite, mysql, postgresql
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "xadmin"
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_ENGINE == "sqlite":
            return f"sqlite:///./xadmin.db"
        elif self.DB_ENGINE == "mysql":
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        elif self.DB_ENGINE == "postgresql":
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            raise ValueError(f"Unsupported database engine: {self.DB_ENGINE}")
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    @computed_field
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # JWT配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"
    
    # 文件上传配置
    MEDIA_ROOT: str = "./media"
    STATIC_ROOT: str = "./static"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".pdf", 
        ".doc", ".docx", ".xls", ".xlsx", ".txt"
    ]
    
    # 邮件配置
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Celery配置
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    
    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def assemble_celery_broker(cls, v: Optional[str]) -> Any:
        if isinstance(v, str) and v:
            return v
        return "redis://localhost:6379/0"
    
    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def assemble_celery_backend(cls, v: Optional[str]) -> Any:
        if isinstance(v, str) and v:
            return v
        return "redis://localhost:6379/0"
    
    # 安全配置
    # 验证码功能已移除
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SYMBOLS: bool = False
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True) if SettingsConfigDict else {"env_file": ".env", "case_sensitive": True}


# 创建配置实例
settings = Settings()