# xAdmin FastAPI 系统操作文档索引

## 📚 文档概览

本目录包含了 xAdmin FastAPI 系统的完整操作文档和测试工具，帮助开发者和用户快速上手使用系统API。

## 📖 文档列表

### 1. 📋 API操作手册.md
**详细的系统操作指南**
- 完整的API调用流程说明
- 按步骤的操作指导
- 常见问题和解决方案
- 错误处理和调试技巧

**适用场景：**
- 新用户首次使用系统
- 了解完整的API调用流程
- 排查API调用问题
- 学习系统认证机制

### 2. 🚀 API接口快速参考.md  
**API接口快速查找手册**
- 所有接口的完整列表
- 接口参数和响应格式
- 权限要求说明
- 请求示例和代码

**适用场景：**
- 快速查找特定接口
- 查看接口参数格式
- 了解权限要求
- 复制粘贴请求示例

## 🛠️ 测试工具

### 1. 📜 scripts/api_test.py
**Python API测试脚本**
- 完整的API调用流程演示
- 详细的测试结果输出
- 错误诊断和调试信息
- 支持自定义参数

**使用方法：**
```bash
# 使用默认参数
python scripts/api_test.py

# 自定义参数
python scripts/api_test.py --url http://localhost:8000 --username admin --password admin123
```

### 2. 🐚 scripts/api_quick_test.sh
**Shell快速测试脚本**
- 轻量级API测试工具
- 无需Python环境
- 快速验证系统状态
- 彩色输出易于阅读

**使用方法：**
```bash
# 使用默认参数
./scripts/api_quick_test.sh

# 自定义参数
./scripts/api_quick_test.sh http://localhost:8000 admin admin123

# 查看帮助
./scripts/api_quick_test.sh --help
```

**注意：** Shell脚本需要安装 `curl` 工具，推荐同时安装 `jq` 用于格式化JSON输出。

## 🎯 使用指南

### 新用户快速上手
1. 首先阅读 **API操作手册.md** 了解基本概念
2. 按照手册中的步骤进行首次API调用
3. 使用 **scripts/api_test.py** 验证环境配置
4. 参考 **API接口快速参考.md** 查找具体接口

### 开发者参考流程
1. 查看 **API接口快速参考.md** 找到需要的接口
2. 使用 **scripts/api_quick_test.sh** 快速测试接口可用性
3. 参考接口示例编写业务代码
4. 遇到问题时查看 **API操作手册.md** 的错误处理部分

### 系统管理员运维
1. 使用 **scripts/api_quick_test.sh** 进行日常健康检查
2. 通过 **scripts/api_test.py** 执行完整的功能验证
3. 参考 **API操作手册.md** 排查系统问题

## 📋 API调用核心流程

以下是系统API的标准调用顺序，确保获取正常数据：

### 🔐 认证流程
```
1. 健康检查        GET /health
2. 获取登录配置    GET /api/system/login/basic  
3. 获取验证码      GET /api/captcha/captcha (如果启用)
4. 用户登录        POST /api/system/login/basic
5. 保存Token       从登录响应中获取access_token
```

### 📊 数据操作流程
```
6. 获取用户信息    GET /api/system/userinfo/ (使用Token)
7. 获取业务数据    GET /api/system/user (使用Token + 权限)
8. 执行业务操作    POST/PUT/DELETE (使用Token + 权限)
9. 刷新Token      POST /api/system/refresh (Token即将过期时)
10. 安全登出       POST /api/system/logout
```

### ⚡ 快速验证命令

```bash
# 1. 检查系统状态
curl -X GET "http://127.0.0.1:8000/health"

# 2. 获取登录配置  
curl -X GET "http://127.0.0.1:8000/api/system/login/basic"

# 3. 执行登录获取Token
TOKEN=$(curl -X POST "http://127.0.0.1:8000/api/system/login/basic" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | \
  jq -r '.data.access')

# 4. 使用Token获取用户信息
curl -X GET "http://127.0.0.1:8000/api/system/userinfo/" \
  -H "Authorization: Bearer $TOKEN"
```

## ⚠️ 重要提示

### 环境要求
- **Python脚本**: Python 3.6+ 环境，requests库
- **Shell脚本**: curl工具，推荐安装jq
- **系统**: xAdmin FastAPI服务正常运行

### 安全注意事项
- 生产环境请修改默认密码
- 妥善保管访问令牌，避免泄露
- 定期刷新令牌，避免过期
- 使用HTTPS协议保护数据传输

### 常见问题
- **401错误**: Token过期或无效，需要重新登录
- **403错误**: 权限不足，检查用户角色和权限配置
- **验证码错误**: 重新获取验证码，确保key和code匹配
- **连接失败**: 检查服务地址和端口是否正确

## 🔗 相关链接

- **Swagger文档**: http://127.0.0.1:8000/api-docs
- **ReDoc文档**: http://127.0.0.1:8000/redoc
- **项目GitHub**: [项目地址](https://github.com/your-repo/xadmin)

## 📞 技术支持

如果在使用过程中遇到问题，可以：
1. 查看相关文档寻找解决方案
2. 使用测试脚本诊断问题
3. 查看系统日志了解错误详情
4. 联系技术支持团队

---

**更新时间**: 2024-01-01  
**文档版本**: 1.0.0