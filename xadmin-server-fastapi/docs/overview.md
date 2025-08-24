# xAdmin FastAPI 项目文档

## 项目概述

xAdmin FastAPI 是基于 FastAPI 框架开发的现代化管理后台系统后端，提供完整的用户权限管理、系统配置、数据管理等功能。本项目是对原有 Django 版本 xadmin-server 的重构升级。

## 技术栈

- **框架**: FastAPI 0.116.1
- **数据库**: SQLAlchemy 2.0 + SQLite/MySQL/PostgreSQL
- **认证**: JWT (JSON Web Token)
- **缓存**: Redis
- **异步**: asyncio/uvicorn
- **文档**: Swagger/OpenAPI
- **测试**: pytest

## 项目特性

- 🚀 **高性能**: 基于 FastAPI 的异步框架，性能优异
- 🔐 **安全认证**: JWT token 认证 + RBAC 权限控制
- 📖 **自动文档**: 自动生成 API 文档 (Swagger/ReDoc)
- 🧪 **完整测试**: 单元测试 + 集成测试覆盖
- 🐳 **容器化**: 支持 Docker 部署
- 🔄 **热重载**: 开发环境支持代码热重载
- 📊 **监控日志**: 完整的日志记录和错误追踪

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+ (前端开发)
- Redis (可选，用于缓存)
- MySQL/PostgreSQL (生产环境推荐)

### 安装运行
```bash
# 1. 克隆项目
git clone https://github.com/your-repo/xadmin.git
cd xadmin/xadmin-server-fastapi

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python scripts/init_db.py

# 5. 启动开发服务器
python build/run.py
```

### 访问地址
- 主页: http://localhost:8001
- API文档: http://localhost:8001/docs
- ReDoc文档: http://localhost:8001/redoc

## 相关文档

- [API 文档](./api-reference.md) - 完整的 API 接口文档
- [部署指南](./deployment.md) - 生产环境部署说明
- [开发指南](./development.md) - 开发环境配置和开发规范
- [比较分析](./COMPARISON.md) - 与 Django 版本的对比分析

## 许可证

本项目基于 MIT 许可证开源。