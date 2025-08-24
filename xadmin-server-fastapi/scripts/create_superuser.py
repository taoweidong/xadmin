#!/usr/bin/env python
"""
创建超级用户脚本
Create Superuser Script
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_async_session
from app.models.user import UserInfo, UserRole
from app.core.security import get_password_hash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def create_superuser():
    """创建超级用户"""
    print("🔧 创建超级用户")
    print("=" * 30)
    
    # 获取用户输入
    username = input("用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空")
        return
    
    email = input("邮箱: ").strip()
    if not email:
        print("❌ 邮箱不能为空")
        return
    
    password = input("密码: ").strip()
    if not password:
        print("❌ 密码不能为空")
        return
    
    nickname = input("昵称 (可选): ").strip() or username
    
    try:
        # 获取数据库会话
        async for session in get_async_session():
            # 检查用户是否已存在
            result = await session.execute(
                select(UserInfo).where(UserInfo.username == username)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"❌ 用户 '{username}' 已存在")
                return
            
            # 检查邮箱是否已存在
            result = await session.execute(
                select(UserInfo).where(UserInfo.email == email)
            )
            existing_email = result.scalar_one_or_none()
            
            if existing_email:
                print(f"❌ 邮箱 '{email}' 已被使用")
                return
            
            # 创建用户
            user = UserInfo(
                username=username,
                nickname=nickname,
                email=email,
                password=get_password_hash(password),
                is_active=True,
                is_staff=True,
                is_superuser=True,
                gender=0,  # 未知
                user_type=1,  # 系统用户
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print(f"✅ 超级用户 '{username}' 创建成功")
            print(f"   ID: {user.id}")
            print(f"   邮箱: {user.email}")
            print(f"   昵称: {user.nickname}")
            
            break
            
    except Exception as e:
        print(f"❌ 创建失败: {e}")

async def list_users():
    """列出所有用户"""
    print("👥 用户列表")
    print("=" * 50)
    
    try:
        async for session in get_async_session():
            result = await session.execute(
                select(UserInfo).order_by(UserInfo.id)
            )
            users = result.scalars().all()
            
            if not users:
                print("📭 没有用户")
                return
            
            print(f"{'ID':<5} {'用户名':<15} {'昵称':<15} {'邮箱':<25} {'状态':<8} {'类型'}")
            print("-" * 80)
            
            for user in users:
                status = "✅激活" if user.is_active else "❌禁用"
                user_type = "🔧管理员" if user.is_superuser else "👤普通"
                
                print(f"{user.id:<5} {user.username:<15} {user.nickname:<15} {user.email:<25} {status:<8} {user_type}")
            
            break
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")

async def reset_password():
    """重置用户密码"""
    username = input("请输入要重置密码的用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空")
        return
    
    new_password = input("请输入新密码: ").strip()
    if not new_password:
        print("❌ 密码不能为空")
        return
    
    try:
        async for session in get_async_session():
            result = await session.execute(
                select(UserInfo).where(UserInfo.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ 用户 '{username}' 不存在")
                return
            
            # 更新密码
            user.password = get_password_hash(new_password)
            await session.commit()
            
            print(f"✅ 用户 '{username}' 密码重置成功")
            break
            
    except Exception as e:
        print(f"❌ 重置失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python scripts/create_superuser.py create    # 创建超级用户")
        print("  python scripts/create_superuser.py list      # 列出所有用户")
        print("  python scripts/create_superuser.py reset     # 重置用户密码")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        asyncio.run(create_superuser())
    elif command == "list":
        asyncio.run(list_users())
    elif command == "reset":
        asyncio.run(reset_password())
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()