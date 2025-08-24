#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent  # 上级目录，包含app文件夹
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT))

from app.core.database import SessionLocal, create_tables
from app.core.security import get_password_hash
from app.models.user import UserInfo, UserRole, DeptInfo, FieldPermission
from app.models.system import MenuInfo, SystemConfig
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """初始化数据库"""
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created successfully!")


def create_default_dept(db):
    """创建默认部门"""
    # 检查是否已存在根部门
    root_dept = db.query(DeptInfo).filter(DeptInfo.code == "root").first()
    if root_dept:
        logger.info("Root department already exists")
        return root_dept
    
    # 创建根部门
    root_dept = DeptInfo(
        name="总公司",
        code="root",
        description="根部门",
        is_active=True,
        sort=0,
        leader="系统管理员",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(root_dept)
    db.commit()
    db.refresh(root_dept)
    
    logger.info(f"Created root department: {root_dept.name}")
    return root_dept


def create_default_role(db):
    """创建默认角色"""
    # 检查是否已存在超级管理员角色
    admin_role = db.query(UserRole).filter(UserRole.code == "admin").first()
    if admin_role:
        logger.info("Admin role already exists")
        return admin_role
    
    # 创建超级管理员角色
    admin_role = UserRole(
        name="超级管理员",
        code="admin",
        description="系统超级管理员，拥有所有权限",
        is_active=True,
        sort=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)
    
    logger.info(f"Created admin role: {admin_role.name}")
    return admin_role


def create_default_user(db, dept, role):
    """创建默认用户"""
    # 检查是否已存在admin用户
    admin_user = db.query(UserInfo).filter(UserInfo.username == "admin").first()
    if admin_user:
        logger.info("Admin user already exists")
        return admin_user
    
    # 创建超级管理员用户
    admin_user = UserInfo(
        username="admin",
        password=get_password_hash("admin123"),
        email="admin@example.com",
        nickname="系统管理员",
        gender=0,
        is_active=True,
        is_staff=True,
        is_superuser=True,
        dept_id=dept.id,
        date_joined=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    # 分配角色
    admin_user.roles.append(role)
    db.commit()
    
    logger.info(f"Created admin user: {admin_user.username}")
    logger.info(f"Default password: admin123")
    return admin_user


def create_default_menus(db):
    """创建默认菜单"""
    # 检查是否已存在菜单
    existing_menu = db.query(MenuInfo).first()
    if existing_menu:
        logger.info("Menus already exist")
        return
    
    # 创建系统管理菜单
    system_menu = MenuInfo(
        title="系统管理",
        name="System",
        path="/system",
        menu_type=0,  # 目录
        icon="el-icon-setting",
        sort=1,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(system_menu)
    db.commit()
    db.refresh(system_menu)
    
    # 创建用户管理菜单
    user_menu = MenuInfo(
        title="用户管理",
        name="UserManagement",
        path="/system/user",
        component="system/user/index",
        parent_id=system_menu.id,
        menu_type=1,  # 菜单
        icon="el-icon-user",
        permission="user:read",
        sort=1,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user_menu)
    
    # 创建角色管理菜单
    role_menu = MenuInfo(
        title="角色管理",
        name="RoleManagement",
        path="/system/role",
        component="system/role/index",
        parent_id=system_menu.id,
        menu_type=1,
        icon="el-icon-s-custom",
        permission="role:read",
        sort=2,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(role_menu)
    
    # 创建部门管理菜单
    dept_menu = MenuInfo(
        title="部门管理",
        name="DeptManagement",
        path="/system/dept",
        component="system/dept/index",
        parent_id=system_menu.id,
        menu_type=1,
        icon="el-icon-office-building",
        permission="dept:read",
        sort=3,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(dept_menu)
    
    db.commit()
    logger.info("Created default menus")


def create_default_configs(db):
    """创建默认配置"""
    # 检查是否已存在配置
    existing_config = db.query(SystemConfig).first()
    if existing_config:
        logger.info("System configs already exist")
        return
    
    configs = [
        {
            "key": "site_name",
            "value": "xAdmin管理系统",
            "name": "站点名称",
            "description": "系统站点名称",
            "category": "basic",
            "config_type": "string"
        },
        {
            "key": "site_logo",
            "value": "",
            "name": "站点LOGO",
            "description": "系统LOGO图片",
            "category": "basic",
            "config_type": "file"
        },
        {
            "key": "login_captcha",
            "value": "true",
            "name": "登录验证码",
            "description": "是否启用登录验证码",
            "category": "security",
            "config_type": "boolean"
        },
        {
            "key": "register_enabled",
            "value": "false",
            "name": "开放注册",
            "description": "是否允许用户注册",
            "category": "security",
            "config_type": "boolean"
        }
    ]
    
    for config_data in configs:
        config = SystemConfig(
            **config_data,
            is_active=True,
            sort=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(config)
    
    db.commit()
    logger.info("Created default system configs")


def main():
    """主初始化函数"""
    logger.info("Starting database initialization...")
    
    try:
        # 初始化数据库
        init_database()
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 创建默认数据
            dept = create_default_dept(db)
            role = create_default_role(db)
            user = create_default_user(db, dept, role)
            create_default_menus(db)
            create_default_configs(db)
            
            logger.info("Database initialization completed successfully!")
            logger.info("Default login credentials:")
            logger.info("  Username: admin")
            logger.info("  Password: admin123")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    main()