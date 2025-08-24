#!/usr/bin/env python3
"""
简化的API验证脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from main import app

def test_basic_endpoints():
    """测试基础端点"""
    client = TestClient(app)
    
    print("=" * 50)
    print("FastAPI Backend API Validation")
    print("=" * 50)
    
    # 1. 测试健康检查
    print("\n1. Testing Health Check...")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        print("✅ Health check passed")
    else:
        print("❌ Health check failed")
        return False
    
    # 2. 测试根路径
    print("\n2. Testing Root Path...")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        print("✅ Root path passed")
    else:
        print("❌ Root path failed")
    
    # 3. 测试登录配置接口
    print("\n3. Testing Login Config...")
    response = client.get("/api/system/login/basic")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        print("✅ Login config passed")
    else:
        print("❌ Login config failed")
    
    # 4. 测试验证码接口
    print("\n4. Testing Captcha...")
    response = client.get("/api/system/auth/captcha")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Captcha key length: {len(result.get('captcha_key', ''))}")
        print(f"Image data length: {len(result.get('captcha_image', ''))}")
        print("✅ Captcha passed")
    else:
        print("❌ Captcha failed")
    
    # 5. 测试密码规则接口
    print("\n5. Testing Password Rules...")
    response = client.get("/api/system/rules/password")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        rules_count = len(result.get('password_rule', []))
        print(f"Password rules count: {rules_count}")
        print("✅ Password rules passed")
    else:
        print("❌ Password rules failed")
    
    # 6. 测试注册配置接口
    print("\n6. Testing Register Config...")
    response = client.get("/api/system/register")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Register config passed")
    else:
        print("❌ Register config failed")
    
    # 7. 测试API文档
    print("\n7. Testing API Docs...")
    response = client.get("/api-docs")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ API docs accessible")
    else:
        print("❌ API docs failed")
    
    print("\n" + "=" * 50)
    print("API Validation Completed!")
    print("You can now:")
    print("1. Run: python run.py")
    print("2. Visit: http://localhost:8000/api-docs")
    print("3. Initialize DB: python init_db.py")
    print("=" * 50)
    
    return True

def test_with_database():
    """测试需要数据库的接口"""
    client = TestClient(app)
    
    print("\n" + "=" * 50)
    print("Database-dependent API Tests")
    print("=" * 50)
    
    # 这些测试需要先初始化数据库
    print("Note: Run 'python init_db.py' first to test these endpoints")
    
    # 测试登录接口（需要数据库）
    print("\n1. Testing Login (requires DB)...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = client.post("/api/system/login/basic", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        access_token = result.get('data', {}).get('access')
        print("✅ Login successful")
        
        # 测试用户信息接口
        print("\n2. Testing User Info...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/system/userinfo", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ User info passed")
            result = response.json()
            username = result.get('data', {}).get('username')
            print(f"Logged in as: {username}")
        else:
            print("❌ User info failed")
            
    elif response.status_code == 401:
        print("ℹ️  Need to initialize database first")
    else:
        print(f"❌ Login failed: {response.json()}")

def main():
    """主函数"""
    try:
        # 基础端点测试（不需要数据库）
        if test_basic_endpoints():
            # 数据库相关测试
            test_with_database()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())