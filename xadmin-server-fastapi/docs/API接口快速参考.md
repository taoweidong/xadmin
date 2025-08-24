# xAdmin FastAPI 接口快速参考

## 基础信息

**服务地址**: `http://127.0.0.1:8000`  
**API文档**: `http://127.0.0.1:8000/api-docs`  
**认证方式**: Bearer Token  

## 认证流程 (推荐调用顺序)

### 1. 系统配置检查
```http
GET /api/system/login/basic
GET /api/captcha/config
```

### 2. 获取验证码（如果启用）
```http
GET /api/captcha/captcha?length=4
```

### 3. 用户登录
```http
POST /api/system/login/basic
{
    "username": "admin",
    "password": "password123",
    "captcha_key": "captcha_abc123",
    "captcha_code": "1234"
}
```

### 4. 获取用户信息
```http
GET /api/system/userinfo/
Authorization: Bearer <access_token>
```

## 完整接口列表

### 🔐 认证模块 (`/api/system`)

| 方法 | 路径 | 说明 | 需要认证 |
|------|------|------|----------|
| GET | `/login/basic` | 获取登录配置 | ❌ |
| POST | `/login/basic` | 用户名密码登录 | ❌ |
| POST | `/login/code` | 验证码登录 | ❌ |
| POST | `/refresh` | 刷新令牌 | ❌ |
| POST | `/logout` | 用户登出 | ✅ |
| POST | `/register` | 用户注册 | ❌ |
| POST | `/reset-password` | 重置密码 | ❌ |
| POST | `/change-password` | 修改密码 | ✅ |
| GET | `/password-rules` | 获取密码规则 | ❌ |

### 👤 用户管理 (`/api/system`)

| 方法 | 路径 | 说明 | 需要认证 | 权限要求 |
|------|------|------|----------|----------|
| GET | `/userinfo/` | 获取当前用户信息 | ✅ | - |
| PUT | `/userinfo/` | 更新当前用户信息 | ✅ | - |
| PATCH | `/userinfo/` | 部分更新用户信息 | ✅ | - |
| GET | `/user` | 获取用户列表 | ✅ | user:read |
| POST | `/user` | 创建用户 | ✅ | user:create |
| GET | `/user/{id}` | 获取用户详情 | ✅ | user:read |
| PUT | `/user/{id}` | 更新用户 | ✅ | user:update |
| DELETE | `/user/{id}` | 删除用户 | ✅ | user:delete |
| POST | `/user/batch-delete` | 批量删除用户 | ✅ | user:delete |
| GET | `/user/search` | 搜索用户 | ✅ | user:read |
| GET | `/user/export` | 导出用户数据 | ✅ | user:export |
| POST | `/user/import` | 导入用户数据 | ✅ | user:import |

### 🎯 验证码模块 (`/api/captcha`)

| 方法 | 路径 | 说明 | 需要认证 |
|------|------|------|----------|
| GET | `/captcha` | 获取图片验证码 | ❌ |
| POST | `/captcha/verify` | 验证图片验证码 | ❌ |
| GET | `/captcha/config` | 获取验证码配置 | ❌ |
| GET | `/verify-code/config` | 获取短信/邮件验证码配置 | ❌ |
| POST | `/verify-code/send` | 发送验证码 | ❌ |
| POST | `/verify-code/verify` | 验证验证码 | ❌ |
| GET | `/temp-token` | 获取临时令牌 | ❌ |
| POST | `/temp-token/verify` | 验证临时令牌 | ❌ |

### ⚙️ 设置管理 (`/api/settings`)

| 方法 | 路径 | 说明 | 需要认证 | 权限要求 |
|------|------|------|----------|----------|
| GET | `/config/system` | 获取系统配置列表 | ✅ | config:read |
| POST | `/config/system` | 创建系统配置 | ✅ | config:create |
| GET | `/config/system/{id}` | 获取系统配置详情 | ✅ | config:read |
| PUT | `/config/system/{id}` | 更新系统配置 | ✅ | config:update |
| DELETE | `/config/system/{id}` | 删除系统配置 | ✅ | config:delete |
| POST | `/config/system/batch-update` | 批量更新系统配置 | ✅ | config:update |
| GET | `/config/categories` | 获取配置分类 | ✅ | config:read |
| GET | `/config/values/{category}` | 获取分类配置值 | ✅ | config:read |
| POST | `/config/batch-set` | 批量设置配置 | ✅ | config:update |
| GET | `/personal-config` | 获取个人配置列表 | ✅ | - |
| POST | `/personal-config` | 创建个人配置 | ✅ | - |
| PUT | `/personal-config/{id}` | 更新个人配置 | ✅ | - |
| DELETE | `/personal-config/{id}` | 删除个人配置 | ✅ | - |

### 📁 文件管理 (`/api/common`)

| 方法 | 路径 | 说明 | 需要认证 | 权限要求 |
|------|------|------|----------|----------|
| POST | `/upload` | 单文件上传 | ✅ | - |
| POST | `/upload/batch` | 批量文件上传 | ✅ | - |
| GET | `/file` | 获取文件列表 | ✅ | file:read |
| GET | `/file/{id}` | 获取文件详情 | ✅ | - |
| PUT | `/file/{id}` | 更新文件信息 | ✅ | file:update |
| DELETE | `/file/{id}` | 删除文件 | ✅ | file:delete |
| GET | `/file/{id}/download` | 下载文件 | ✅ | - |
| POST | `/image/process` | 图片处理 | ✅ | - |
| GET | `/file/statistics` | 文件统计信息 | ✅ | file:read |

### 📊 系统工具 (`/api/common`)

| 方法 | 路径 | 说明 | 需要认证 | 权限要求 |
|------|------|------|----------|----------|
| GET | `/health` | 健康检查 | ❌ | - |
| GET | `/system-info` | 获取系统信息 | ✅ | system:info |
| POST | `/qrcode` | 生成二维码 | ✅ | - |
| POST | `/export` | 数据导出 | ✅ | 根据数据类型 |
| POST | `/import` | 数据导入 | ✅ | 根据数据类型 |
| GET | `/time` | 获取服务器时间 | ❌ | - |
| POST | `/cache/clear` | 清理缓存 | ✅ | system:cache |

### 📢 消息通知 (`/api/message`)

| 方法 | 路径 | 说明 | 需要认证 | 权限要求 |
|------|------|------|----------|----------|
| GET | `/message/notice` | 获取通知消息列表 | ✅ | message:read |
| POST | `/message/notice` | 创建通知消息 | ✅ | message:create |
| GET | `/message/notice/{id}` | 获取通知消息详情 | ✅ | message:read |
| PUT | `/message/notice/{id}` | 更新通知消息 | ✅ | message:update |
| DELETE | `/message/notice/{id}` | 删除通知消息 | ✅ | message:delete |
| POST | `/message/notice/{id}/publish` | 发布通知消息 | ✅ | message:publish |
| POST | `/message/notice/batch-action` | 批量操作通知消息 | ✅ | message:update |
| GET | `/message/user-read` | 获取用户阅读记录 | ✅ | message:read |
| GET | `/message/my-notices` | 获取我的通知 | ✅ | - |
| POST | `/message/mark-read` | 标记消息为已读 | ✅ | - |
| POST | `/message/mark-all-read` | 标记所有消息已读 | ✅ | - |
| GET | `/message/statistics` | 获取消息统计 | ✅ | message:read |
| POST | `/message/push` | 消息推送 | ✅ | message:push |
| WebSocket | `/ws/message/{user_id}` | 消息WebSocket连接 | ✅ | - |

### 🗂️ 其他系统接口

| 方法 | 路径 | 说明 | 需要认证 |
|------|------|------|----------|
| GET | `/` | 根路径信息 | ❌ |
| GET | `/api-docs` | Swagger文档 | ❌ |
| GET | `/redoc` | ReDoc文档 | ❌ |
| GET | `/api/routes` | 路由列表（调试模式） | ❌ |
| GET | `/openapi.json` | OpenAPI规范 | ❌ |

## 常用请求示例

### 获取用户列表（分页、搜索、过滤）
```http
GET /api/system/user?page=1&size=20&search=admin&is_active=true&dept_id=1&role_id=1&ordering=-created_at
Authorization: Bearer <access_token>
```

### 创建用户
```http
POST /api/system/user
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "username": "newuser",
    "password": "Password123!",
    "email": "newuser@example.com",
    "phone": "13800138001",
    "nickname": "新用户",
    "gender": 1,
    "is_active": true,
    "is_staff": false,
    "dept_id": 1,
    "role_ids": [2, 3]
}
```

### 批量删除用户
```http
POST /api/system/user/batch-delete
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "pks": [1, 2, 3, 4, 5]
}
```

### 上传文件
```http
POST /api/common/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <file_binary>
category: "avatar"
```

### 创建系统配置
```http
POST /api/settings/config/system
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "key": "site_title",
    "value": "xAdmin 管理系统",
    "name": "网站标题",
    "description": "系统首页显示的标题",
    "category": "basic",
    "config_type": "text",
    "is_active": true,
    "sort": 1
}
```

### 发送通知消息
```http
POST /api/message/notice
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "系统维护通知",
    "content": "系统将于今晚22:00-24:00进行维护，期间可能无法正常访问。",
    "message_type": "system",
    "level": "warning",
    "target_type": "all",
    "start_time": "2024-01-01T22:00:00Z",
    "end_time": "2024-01-02T00:00:00Z"
}
```

### WebSocket消息连接
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/api/message/ws/message/1?token=<access_token>');

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('收到消息:', message);
};
```

## 响应格式说明

### 成功响应
```json
{
    "code": 1000,
    "detail": "success",
    "data": {...}
}
```

### 列表响应
```json
{
    "code": 1000,
    "detail": "success",
    "data": {
        "results": [...],
        "total": 100,
        "page": 1,
        "size": 20,
        "pages": 5
    }
}
```

### 错误响应
```json
{
    "code": 4001,
    "detail": "未认证或认证信息已过期",
    "success": false
}
```

## 状态码说明

| 状态码 | 说明 |
|-------|------|
| 1000 | 成功 |
| 4000 | 请求参数错误 |
| 4001 | 未认证 |
| 4003 | 权限不足 |
| 4004 | 资源不存在 |
| 5000 | 服务器内部错误 |

## 权限代码说明

| 权限代码 | 说明 |
|---------|------|
| user:read | 用户查看权限 |
| user:create | 用户创建权限 |
| user:update | 用户更新权限 |
| user:delete | 用户删除权限 |
| user:export | 用户导出权限 |
| user:import | 用户导入权限 |
| config:read | 配置查看权限 |
| config:create | 配置创建权限 |
| config:update | 配置更新权限 |
| config:delete | 配置删除权限 |
| message:read | 消息查看权限 |
| message:create | 消息创建权限 |
| message:update | 消息更新权限 |
| message:delete | 消息删除权限 |
| message:publish | 消息发布权限 |
| message:push | 消息推送权限 |
| file:read | 文件查看权限 |
| file:update | 文件更新权限 |
| file:delete | 文件删除权限 |
| system:info | 系统信息查看权限 |
| system:cache | 系统缓存管理权限 |

## 开发调试

### 快速测试脚本
```bash
# 设置基础URL
BASE_URL="http://127.0.0.1:8000"

# 1. 健康检查
curl -X GET "$BASE_URL/health"

# 2. 登录获取token
TOKEN=$(curl -X POST "$BASE_URL/api/system/login/basic" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | \
  jq -r '.data.access')

# 3. 获取用户信息
curl -X GET "$BASE_URL/api/system/userinfo/" \
  -H "Authorization: Bearer $TOKEN"

# 4. 获取用户列表
curl -X GET "$BASE_URL/api/system/user?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Python 示例代码
```python
import requests

# 基础配置
BASE_URL = "http://127.0.0.1:8000"
session = requests.Session()

# 1. 登录
login_response = session.post(f"{BASE_URL}/api/system/login/basic", json={
    "username": "admin",
    "password": "admin123"
})
token = login_response.json()["data"]["access"]

# 2. 设置认证头
session.headers.update({"Authorization": f"Bearer {token}"})

# 3. 获取用户信息
user_info = session.get(f"{BASE_URL}/api/system/userinfo/")
print(user_info.json())

# 4. 获取用户列表
user_list = session.get(f"{BASE_URL}/api/system/user", params={
    "page": 1,
    "size": 20,
    "search": "admin"
})
print(user_list.json())
```

这个快速参考文档提供了所有API接口的完整列表和使用示例，方便开发者快速查找和使用相应的接口。