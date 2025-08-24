# 构建和启动脚本说明

## 文件说明

### `run.py`
主要的项目启动脚本，支持以下功能：
- 自动检查虚拟环境
- 验证依赖包安装
- 启动FastAPI应用服务器
- 支持开发模式（自动重载）

使用方法：
```bash
python build/run.py
```

### `start_venv.bat`
Windows批处理启动脚本，功能包括：
- 激活虚拟环境
- 安装核心依赖
- 启动应用服务器

使用方法：
```bash
build/start_venv.bat
```

## 建议的使用方式

### 开发环境
```bash
# 使用run.py启动（推荐）
python build/run.py

# 或者手动启动
.venv/Scripts/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 生产环境
```bash
# 使用Docker部署
docker-compose up -d

# 或者直接运行
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

## 环境变量配置

创建 `.env` 文件并配置以下变量：
- `DATABASE_URL`: 数据库连接字符串
- `SECRET_KEY`: JWT密钥
- `REDIS_URL`: Redis连接地址
- `DEBUG`: 调试模式开关