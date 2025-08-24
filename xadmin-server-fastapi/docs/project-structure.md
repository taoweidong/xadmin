# xAdmin FastAPI 项目目录结构

## 📁 完整目录结构

```
xadmin-server-fastapi/
├── 📁 app/                         # 应用核心代码
│   ├── 📁 api/                     # API 路由层
│   │   ├── auth.py                 # 认证相关 API
│   │   ├── user.py                 # 用户管理 API
│   │   ├── menu.py                 # 菜单管理 API
│   │   ├── role.py                 # 角色管理 API
│   │   ├── dept.py                 # 部门管理 API
│   │   ├── settings.py             # 配置管理 API
│   │   ├── common.py               # 通用功能 API
│   │   ├── captcha.py              # 验证码 API
│   │   └── message.py              # 消息通知 API
│   ├── 📁 core/                    # 核心配置
│   │   ├── config.py               # 应用配置
│   │   ├── database.py             # 数据库连接
│   │   ├── security.py             # 安全认证
│   │   ├── dependencies.py         # 依赖注入
│   │   └── cache.py                # 缓存配置
│   ├── 📁 models/                  # 数据库模型
│   │   ├── user.py                 # 用户相关模型
│   │   ├── system.py               # 系统配置模型
│   │   ├── menu.py                 # 菜单模型
│   │   ├── log.py                  # 日志模型
│   │   └── __init__.py             # 模型初始化
│   ├── 📁 schemas/                 # Pydantic 数据验证模型
│   │   ├── auth.py                 # 认证相关 Schema
│   │   ├── user.py                 # 用户相关 Schema
│   │   ├── menu.py                 # 菜单相关 Schema
│   │   ├── role.py                 # 角色相关 Schema
│   │   ├── dept.py                 # 部门相关 Schema
│   │   ├── settings.py             # 设置相关 Schema
│   │   └── common.py               # 通用 Schema
│   ├── 📁 services/                # 业务逻辑层
│   │   ├── user.py                 # 用户服务
│   │   ├── auth.py                 # 认证服务
│   │   ├── menu.py                 # 菜单服务
│   │   ├── role.py                 # 角色服务
│   │   ├── dept.py                 # 部门服务
│   │   ├── settings.py             # 设置服务
│   │   ├── common.py               # 通用服务
│   │   ├── captcha.py              # 验证码服务
│   │   ├── message.py              # 消息服务
│   │   └── upload.py               # 文件上传服务
│   ├── 📁 utils/                   # 工具函数
│   │   └── helpers.py              # 辅助函数
│   └── __init__.py                 # 应用初始化
├── 📁 build/                       # 构建和启动脚本
│   ├── run.py                      # 主启动脚本
│   ├── dev.py                      # 开发环境启动脚本
│   ├── prod.py                     # 生产环境启动脚本
│   ├── start_venv.bat              # Windows 批处理启动脚本
│   └── README.md                   # 构建脚本说明
├── 📁 tests/                       # 测试代码
│   ├── test_api.py                 # API 接口测试
│   ├── test_app.py                 # 应用程序测试
│   ├── test_deps.py                # 依赖关系测试
│   ├── validate_api.py             # API 验证脚本
│   ├── __init__.py                 # 测试模块初始化
│   └── README.md                   # 测试说明文档
├── 📁 scripts/                     # 工具脚本
│   ├── init_db.py                  # 数据库初始化脚本
│   ├── backup_db.py                # 数据库备份脚本
│   ├── create_superuser.py         # 创建超级用户脚本
│   └── README.md                   # 脚本说明文档
├── 📁 docs/                        # 项目文档
│   ├── README.md                   # 详细使用说明
│   ├── overview.md                 # 项目概览
│   └── COMPARISON.md               # 与 Django 版本对比
├── 📁 backups/                     # 数据库备份目录（自动创建）
├── 📁 .venv/                       # Python 虚拟环境
├── 📄 main.py                      # FastAPI 主应用入口
├── 📄 manage.py                    # 项目管理脚本
├── 📄 requirements.txt             # 完整项目依赖
├── 📄 requirements_minimal.txt     # 最小依赖列表
├── 📄 requirements_simple.txt      # 简化依赖列表
├── 📄 pytest.ini                  # pytest 配置
├── 📄 .env.example                 # 环境变量示例
├── 📄 .gitignore                   # Git 忽略文件
├── 📄 Dockerfile                   # Docker 构建文件
├── 📄 docker-compose.yml           # Docker Compose 配置
└── 📄 README.md                    # 项目主说明文件
```

## 📋 目录功能说明

### 核心应用目录 (`app/`)

- **api/**: RESTful API 路由定义，按功能模块分组
- **core/**: 应用核心配置，包括数据库、安全、缓存等
- **models/**: SQLAlchemy ORM 数据库模型定义
- **schemas/**: Pydantic 数据验证和序列化模型
- **services/**: 业务逻辑层，处理复杂的业务操作
- **utils/**: 通用工具函数和辅助方法

### 构建脚本目录 (`build/`)

- **run.py**: 通用启动脚本，自动检测环境
- **dev.py**: 开发环境专用启动脚本
- **prod.py**: 生产环境启动脚本
- **start_venv.bat**: Windows 批处理启动脚本

### 测试目录 (`tests/`)

- **test_api.py**: API 接口自动化测试
- **test_app.py**: 应用程序基础功能测试
- **test_deps.py**: 依赖注入和数据库连接测试
- **validate_api.py**: API 完整性验证脚本

### 工具脚本目录 (`scripts/`)

- **init_db.py**: 数据库表创建和初始数据插入
- **backup_db.py**: 数据库备份和恢复工具
- **create_superuser.py**: 超级用户管理工具

### 文档目录 (`docs/`)

- **README.md**: 详细的使用和部署说明
- **overview.md**: 项目技术架构概览
- **COMPARISON.md**: 与原 Django 版本的详细对比

## 🚀 快速使用

### 统一管理入口

使用 `manage.py` 脚本进行项目管理：

```bash
# 查看所有可用命令
python manage.py help

# 初始化项目（创建虚拟环境、安装依赖、初始化数据库）
python manage.py init

# 启动开发服务器
python manage.py dev

# 运行测试
python manage.py test

# 数据库管理
python manage.py db-init
python manage.py db-backup
python manage.py superuser

# 项目检查
python manage.py check
python manage.py info
```

### 分层架构说明

```
┌─────────────────┐
│   API Layer    │  ← 路由定义、请求验证、响应格式化
├─────────────────┤
│ Service Layer  │  ← 业务逻辑、事务处理、数据转换
├─────────────────┤
│  Model Layer   │  ← 数据库模型、ORM操作、数据持久化
├─────────────────┤
│ Database Layer │  ← SQLite/MySQL/PostgreSQL
└─────────────────┘
```

### 开发规范

1. **API 层**: 仅处理 HTTP 请求/响应，不包含业务逻辑
2. **Service 层**: 包含所有业务逻辑，可被多个 API 复用
3. **Model 层**: 数据库模型定义，保持简洁
4. **Schema 层**: 数据验证和序列化，确保 API 接口规范

### 文件命名规范

- **模型文件**: 使用单数名词，如 `user.py`, `menu.py`
- **API 文件**: 使用复数名词或功能名，如 `users.py`, `auth.py`
- **测试文件**: 以 `test_` 前缀，如 `test_api.py`
- **脚本文件**: 使用动词，如 `init_db.py`, `backup_db.py`

这种目录结构确保了代码的可维护性、可测试性和可扩展性，同时便于团队协作和项目管理。