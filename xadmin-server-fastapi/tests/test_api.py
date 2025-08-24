#!/usr/bin/env python3
"""
API测试脚本
"""
import sys
import os
import requests
import json
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 配置环境变量
os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT))

def test_health_check(base_url="http://127.0.0.1:8000"):
    """测试健康检查接口"""
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_auth_apis(base_url="http://127.0.0.1:8000"):
    """测试认证相关API"""
    api_base = f"{base_url}/api/system"
    
    # 测试获取登录配置
    try:
        response = requests.get(f"{api_base}/login/basic")
        print(f"Login Config: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Login config test failed: {e}")
    
    # 测试获取验证码
    try:
        response = requests.get(f"{api_base}/auth/captcha")
        print(f"Captcha: {response.status_code}")
        result = response.json()
        print(f"Captcha Key: {result.get('captcha_key', 'N/A')}")
    except Exception as e:
        print(f"Captcha test failed: {e}")
    
    # 测试获取密码规则
    try:
        response = requests.get(f"{api_base}/rules/password")
        print(f"Password Rules: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Password rules test failed: {e}")

def test_basic_login(base_url="http://127.0.0.1:8000", username="admin", password="admin123"):
    """测试基础登录"""
    api_base = f"{base_url}/api/system"
    
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(f"{api_base}/login/basic", json=login_data)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            access_token = result.get('data', {}).get('access')
            print(f"Login successful, token: {access_token[:20] if access_token else 'N/A'}...")
            return access_token
        else:
            print(f"Login failed: {response.json()}")
            return None
            
    except Exception as e:
        print(f"Login test failed: {e}")
        return None

def test_user_info(base_url="http://127.0.0.1:8000", token=None):
    """测试用户信息接口"""
    if not token:
        print("No token provided, skipping user info test")
        return
    
    api_base = f"{base_url}/api/system"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{api_base}/userinfo", headers=headers)
        print(f"User Info: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"User: {result.get('data', {}).get('username', 'N/A')}")
        else:
            print(f"User info failed: {response.json()}")
            
    except Exception as e:
        print(f"User info test failed: {e}")

def main():
    """主测试函数"""
    print("=" * 50)
    print("FastAPI Backend API Tests")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. 测试健康检查
    print("\n1. Testing Health Check...")
    if not test_health_check(base_url):
        print("Health check failed. Make sure the server is running.")
        return
    
    # 2. 测试认证API
    print("\n2. Testing Auth APIs...")
    test_auth_apis(base_url)
    
    # 3. 测试登录（如果有默认用户）
    print("\n3. Testing Login...")
    # 注意：这需要先有用户数据
    token = test_basic_login(base_url)
    
    # 4. 测试用户信息
    print("\n4. Testing User Info...")
    test_user_info(base_url, token)
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()