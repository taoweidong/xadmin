# 工具脚本说明

## 文件说明

### `init_db.py`
数据库初始化脚本，功能包括：
- 创建所有数据库表
- 插入初始数据
- 创建默认管理员用户
- 设置基础系统配置

使用方法：
```bash
python scripts/init_db.py
```

## 其他工具脚本

### 数据库管理
```bash
# 创建数据库迁移
alembic revision --autogenerate -m "描述信息"

# 执行数据库迁移
alembic upgrade head

# 回滚数据库
alembic downgrade -1
```

### 数据备份与恢复
```bash
# 备份数据库（SQLite）
cp xadmin.db backup/xadmin_$(date +%Y%m%d_%H%M%S).db

# 恢复数据库
cp backup/xadmin_20231201_120000.db xadmin.db
```

### 用户管理
```bash
# 创建超级用户（需要实现相应脚本）
python scripts/create_superuser.py

# 重置用户密码
python scripts/reset_password.py --username admin
```

## 注意事项

1. 运行脚本前请确保虚拟环境已激活
2. 数据库初始化脚本会清空现有数据，请谨慎使用
3. 生产环境中请使用专业的数据库管理工具