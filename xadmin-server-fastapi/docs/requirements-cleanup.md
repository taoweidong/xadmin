# Requirements 文件整理说明

## 📋 整理前状态

项目中存在3个requirements文件，存在冗余：

1. **requirements.txt** (62行) - 包含完整依赖，含开发工具、测试工具、文档工具
2. **requirements_minimal.txt** (24行) - 只有包名，无版本号，不适合生产环境
3. **requirements_simple.txt** (30行) - 核心功能包，有版本号，无开发工具

## ✅ 整理后状态

精简为2个依赖文件：

1. **requirements.txt** (40行) - 生产环境核心依赖
   - 包含FastAPI、数据库、认证、文件处理等核心功能
   - 所有包都指定了明确版本号
   - 按功能分类并添加了中文注释

2. **requirements-dev.txt** (15行) - 开发环境依赖
   - 包含测试工具：pytest、pytest-asyncio、pytest-cov
   - 代码格式化：black、isort、flake8、mypy
   - 文档生成：sphinx
   - 开发工具：ipython、jupyter

## 🎯 优化点

### 1. 精简依赖
- 移除了不必要的开发工具依赖
- 保留了生产环境必需的30个核心包
- 降低了生产部署的包大小和安装时间

### 2. 分类组织
生产依赖按功能分为6个类别：
- FastAPI核心框架
- 数据库相关
- 认证和安全
- 缓存和消息队列
- 文件处理
- HTTP客户端
- 实用工具
- 验证码和二维码
- WebSocket支持

### 3. 版本锁定
- 所有生产依赖都指定了精确版本号
- 确保在不同环境中的一致性
- 避免依赖升级带来的兼容性问题

### 4. 便于维护
- 添加了中文注释说明各依赖的用途
- 结构清晰，便于添加和删除依赖
- 开发依赖与生产依赖分离

## 📦 使用方式

### 生产环境
```bash
pip install -r requirements.txt
```

### 开发环境
```bash
# 方法一：分别安装
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 方法二：使用管理脚本
python manage.py install-dev
```

## 📊 对比数据

| 指标 | 整理前 | 整理后 | 改进 |
|------|--------|--------|------|
| 文件数量 | 3个 | 2个 | 减少33% |
| 生产依赖 | 50+包 | 30包 | 减少40% |
| 版本指定 | 部分 | 全部 | 100%覆盖 |
| 分类组织 | 无 | 6类 | 结构化 |
| 中文注释 | 无 | 有 | 便于理解 |

这次整理大大简化了项目的依赖管理，提高了可维护性和部署效率。