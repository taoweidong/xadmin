# xAdmin FastAPI 系统操作手册

## 项目概述

xAdmin FastAPI 是基于 FastAPI 框架的后端管理系统，提供用户认证、权限管理、数据管理等功能。本手册将详细说明 API 的调用顺序和使用方法。

## 服务启动

### 1. 环境准备
```bash
# 使用指定的Python虚拟环境
E:\GitHub\xadmin\xadmin\xadmin-server-fastapi\.venv\Scripts\python.exe

# 或者激活虚拟环境后使用
cd E:\GitHub\xadmin\xadmin\xadmin-server-fastapi
.venv\Scripts\activate.bat
```

### 2. 启动服务
```bash
# 开发模式启动
python build/dev.py

# 或者直接运行主文件
python main.py

# 或者使用提供的批处理文件
start.bat
```

### 3. 健康检查
```bash
# 验证服务是否正常启动
GET http://127.0.0.1:8000/health

# 期望响应
{
    "status": "healthy",
    "timestamp": 1234567890.123,
    "version": "1.0.0"
}
```

## API 接口调用顺序指南

### 第一步：获取系统配置信息

#### 1.1 获取登录配置
```http
GET /api/system/login/basic
```
**用途**：获取系统登录配置，了解是否需要验证码、登录限制等
**响应示例**：
```json
{
    "code": 1000,
    "detail": "success",
    "data": {
        "access": true,
        "captcha": true,
        "token": false,
        "encrypted": false,
        "lifetime": 691200,
        "reset": true,
        "password": [],
        "email": true,
        "sms": false,
        "basic": true,
        "rate": 5
    }
}
```

#### 1.2 获取验证码配置（如果需要）
```http
GET /api/captcha/config
```
**响应示例**：
```json
{
    "code": 1000,
    "detail": "success",
    "data": {
        "enabled": true,
        "length": 4,
        "width": 120,
        "height": 40,
        "expire_time": 300
    }
}
```

### 第二步：获取验证码（如果启用）

#### 2.1 获取图片验证码
```http
GET /api/captcha/captcha?length=4
```
**响应示例**：
```json
{
    "code": 1000,
    "detail": "验证码生成成功",
    "captcha_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH...",
    "captcha_key": "captcha_abc123",
    "length": 4
}
```

**注意**：保存 `captcha_key` 用于后续登录验证

### 第三步：用户登录

#### 3.1 基础用户名密码登录
```http
POST /api/system/login/basic
Content-Type: application/json

{
    "username": "admin",
    "password": "password123",
    "captcha_key": "captcha_abc123",
    "captcha_code": "1234"
}
```

**响应示例**：
```json
{
    "code": 1000,
    "detail": "登录成功",
    "data": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access_token_lifetime": 691200,
        "refresh_token_lifetime": 2592000
    }
}
```

**重要**：保存 `access` token 用于后续 API 调用的认证

#### 3.2 验证码登录（可选）
```http
POST /api/system/login/code
Content-Type: application/json

{
    "phone": "13800138000",
    "code": "123456"
}
```
或
```http
POST /api/system/login/code
Content-Type: application/json

{
    "email": "user@example.com",
    "code": "123456"
}
```

### 第四步：获取用户信息

#### 4.1 获取当前用户信息
```http
GET /api/system/userinfo/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应示例**：
```json
{
    "code": 1000,
    "detail": "success",
    "data": {
        "username": "admin",
        "nickname": "管理员",
        "avatar": "/media/avatars/admin.jpg",
        "email": "admin@example.com",
        "phone": "13800138000",
        "gender": 1,
        "last_login": "2024-01-01T10:00:00Z",
        "date_joined": "2023-01-01T10:00:00Z",
        "pk": 1,
        "unread_message_count": 0,
        "is_active": true,
        "roles": ["超级管理员"]
    },
    "choices_dict": [
        {"value": 0, "label": "未知"},
        {"value": 1, "label": "男"},
        {"value": 2, "label": "女"}
    ]
}
```

### 第五步：业务数据操作

#### 5.1 获取用户列表（管理员权限）
```http
GET /api/system/user?page=1&size=20&search=&is_active=true
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应示例**：
```json
{
    "code": 1000,
    "detail": "success",
    "data": {
        "results": [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "phone": "13800138000",
                "nickname": "管理员",
                "gender": 1,
                "is_active": true,
                "is_staff": true,
                "avatar": "/media/avatars/admin.jpg",
                "last_login": "2024-01-01T10:00:00Z",
                "date_joined": "2023-01-01T10:00:00Z",
                "is_superuser": true,
                "created_at": "2023-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:00:00Z",
                "dept_name": "技术部",
                "role_names": ["超级管理员"]
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20,
        "pages": 1
    }
}
```

#### 5.2 创建用户（管理员权限）
```http
POST /api/system/user
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
    "username": "newuser",
    "password": "password123",
    "email": "newuser@example.com",
    "phone": "13800138001",
    "nickname": "新用户",
    "gender": 1,
    "is_active": true,
    "is_staff": false,
    "dept_id": 1,
    "role_ids": [2]
}
```

#### 5.3 更新用户信息
```http
PUT /api/system/userinfo/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
    "nickname": "更新的昵称",
    "email": "updated@example.com",
    "phone": "13800138002",
    "gender": 2
}
```

### 第六步：令牌刷新

#### 6.1 刷新访问令牌
```http
POST /api/system/refresh
Content-Type: application/json

{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**：
```json
{
    "code": 1000,
    "detail": "令牌刷新成功",
    "data": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access_token_lifetime": 691200,
        "refresh_token_lifetime": 2592000
    }
}
```

### 第七步：用户登出

#### 7.1 退出登录
```http
POST /api/system/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 完整的 API 调用流程示例

### 场景：新用户首次登录并获取数据

```bash
# 1. 检查系统健康状态
curl -X GET "http://127.0.0.1:8000/health"

# 2. 获取登录配置
curl -X GET "http://127.0.0.1:8000/api/system/login/basic"

# 3. 获取验证码（如果启用）
curl -X GET "http://127.0.0.1:8000/api/captcha/captcha?length=4"

# 4. 用户登录
curl -X POST "http://127.0.0.1:8000/api/system/login/basic" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123",
    "captcha_key": "captcha_abc123",
    "captcha_code": "1234"
  }'

# 5. 使用返回的token获取用户信息
curl -X GET "http://127.0.0.1:8000/api/system/userinfo/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

# 6. 获取用户列表（需要管理员权限）
curl -X GET "http://127.0.0.1:8000/api/system/user?page=1&size=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## API 端点完整列表

### 认证相关 (`/api/system`)
- `GET /login/basic` - 获取登录配置
- `POST /login/basic` - 用户名密码登录
- `POST /login/code` - 验证码登录
- `POST /refresh` - 刷新令牌
- `POST /logout` - 用户登出

### 用户相关 (`/api/system`)
- `GET /userinfo/` - 获取当前用户信息
- `PUT /userinfo/` - 更新当前用户信息
- `PATCH /userinfo/` - 部分更新当前用户信息
- `GET /user` - 获取用户列表（管理员）
- `POST /user` - 创建用户（管理员）
- `PUT /user/{id}` - 更新用户（管理员）
- `DELETE /user/{id}` - 删除用户（管理员）

### 验证码相关 (`/api/captcha`)
- `GET /captcha` - 获取图片验证码
- `POST /captcha/verify` - 验证图片验证码
- `GET /captcha/config` - 获取验证码配置
- `GET /verify-code/config` - 获取短信/邮件验证码配置
- `POST /verify-code/send` - 发送验证码
- `POST /verify-code/verify` - 验证验证码

### 系统功能
- `GET /health` - 系统健康检查
- `GET /` - 根路径信息
- `GET /api-docs` - API 文档 (Swagger UI)
- `GET /redoc` - API 文档 (ReDoc)

## 重要注意事项

### 1. 认证机制
- 所有需要认证的接口都需要在请求头中添加：`Authorization: Bearer <access_token>`
- Token 有效期为 8 天（可配置）
- 刷新令牌有效期为 30 天（可配置）

### 2. 权限控制
- 超级用户：拥有所有权限
- 普通管理员：需要特定权限才能访问管理接口
- 普通用户：只能访问个人相关接口

### 3. 响应格式
所有接口响应都遵循统一格式：
```json
{
    "code": 1000,        // 业务状态码，1000表示成功
    "detail": "success", // 响应消息
    "data": {}          // 响应数据
}
```

### 4. 错误处理
- `400` - 请求参数错误
- `401` - 未认证或认证过期
- `403` - 权限不足
- `404` - 资源不存在
- `500` - 服务器内部错误

### 5. 分页参数
列表接口支持以下分页参数：
- `page`: 页码，默认为 1
- `size`: 每页大小，默认为 20，最大为 100
- `ordering`: 排序字段
- `search`: 搜索关键词

### 6. 开发调试
- 开发模式下可以访问 `/api/routes` 查看所有路由
- Swagger UI: `http://127.0.0.1:8000/api-docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 常见问题排查

### 1. Token 过期
**现象**：接口返回 401 错误
**解决**：使用 refresh token 刷新访问令牌

### 2. 权限不足
**现象**：接口返回 403 错误
**解决**：确认用户是否有相应权限，或使用超级管理员账户

### 3. 验证码错误
**现象**：登录时提示验证码错误
**解决**：重新获取验证码，确保验证码和key匹配

### 4. 数据库连接问题
**现象**：服务启动失败或数据操作异常
**解决**：检查数据库配置，确保数据库服务正常运行

这个操作手册提供了完整的 API 调用流程指导，按照这个顺序调用可以确保获取到正常的数据。