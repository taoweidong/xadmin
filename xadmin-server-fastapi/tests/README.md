# 测试说明文档

## 测试文件说明

### `test_api.py`
API接口测试，包含：
- 认证接口测试
- 用户管理接口测试
- 系统配置接口测试
- 文件上传接口测试

### `test_app.py`
应用程序基础测试，包含：
- 应用启动测试
- 基础路由测试
- 健康检查测试

### `test_deps.py`
依赖关系测试，包含：
- 数据库连接测试
- 认证依赖测试
- 权限检查测试

### `validate_api.py`
API验证脚本，包含：
- 所有接口的完整性验证
- 响应格式验证
- 错误处理验证

## 运行测试

### 安装测试依赖
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### 运行所有测试
```bash
# 基本测试
pytest

# 详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行特定测试
pytest tests/test_api.py::test_login
```

### 测试标记
```bash
# 只运行单元测试
pytest -m unit

# 只运行API测试
pytest -m api

# 排除慢速测试
pytest -m "not slow"
```

## 测试数据

测试使用独立的测试数据库，配置在：
- `TEST_DATABASE_URL` 环境变量
- 或使用内存SQLite数据库

## 持续集成

项目支持以下CI/CD平台：
- GitHub Actions
- GitLab CI
- Jenkins

测试配置文件位于 `.github/workflows/` 目录。

## 测试最佳实践

1. **隔离性**: 每个测试应该独立运行
2. **可重复性**: 测试结果应该一致
3. **快速反馈**: 单元测试应该快速执行
4. **清晰命名**: 测试函数名应该描述测试内容
5. **数据清理**: 测试后应清理测试数据

## 模拟和桩
```python
# 模拟Redis连接
@pytest.fixture
def mock_redis():
    with patch('app.core.cache.redis_client') as mock:
        yield mock

# 模拟数据库
@pytest.fixture
def test_db():
    # 使用测试数据库
    pass
```