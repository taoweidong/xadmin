#!/usr/bin/env python3
"""
xAdmin FastAPI 系统API测试脚本
演示标准的API调用流程和顺序
"""

import requests
import json
import time
from typing import Optional, Dict, Any


class XAdminAPITester:
    """xAdmin API测试器"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_info: Optional[Dict[str, Any]] = None
    
    def log_step(self, step: str, description: str):
        """记录测试步骤"""
        print(f"\n{'='*60}")
        print(f"步骤 {step}: {description}")
        print('='*60)
    
    def log_result(self, success: bool, message: str, data: Any = None):
        """记录测试结果"""
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status}: {message}")
        if data and isinstance(data, dict):
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        # 添加认证头
        if self.access_token and 'headers' not in kwargs:
            kwargs['headers'] = {}
        if self.access_token:
            kwargs.setdefault('headers', {})['Authorization'] = f"Bearer {self.access_token}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            print(f"\n📡 请求: {method} {url}")
            if 'json' in kwargs:
                print(f"📤 请求体: {json.dumps(kwargs['json'], indent=2, ensure_ascii=False)}")
            
            print(f"📥 响应码: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                print(f"📥 响应体: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
                return result
            else:
                return {"status_code": response.status_code, "content": response.text[:200]}
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            return {"error": str(e)}
    
    def step1_health_check(self) -> bool:
        """步骤1: 系统健康检查"""
        self.log_step("1", "系统健康检查")
        
        result = self.make_request("GET", "/health")
        
        if result.get("status") == "healthy":
            self.log_result(True, "系统运行正常", result)
            return True
        else:
            self.log_result(False, "系统健康检查失败", result)
            return False
    
    def step2_get_login_config(self) -> bool:
        """步骤2: 获取登录配置"""
        self.log_step("2", "获取登录配置信息")
        
        result = self.make_request("GET", "/api/system/login/basic")
        
        if result.get("code") == 1000:
            self.log_result(True, "获取登录配置成功", result.get("data"))
            return True
        else:
            self.log_result(False, f"获取登录配置失败: {result.get('detail')}")
            return False
    
    def step3_get_captcha_config(self) -> bool:
        """步骤3: 获取验证码配置"""
        self.log_step("3", "获取验证码配置")
        
        result = self.make_request("GET", "/api/captcha/config")
        
        if result.get("code") == 1000:
            data = result.get("data", {})
            captcha_enabled = data.get("enabled", False)
            self.log_result(True, f"验证码配置获取成功，验证码{'启用' if captcha_enabled else '禁用'}", data)
            return True
        else:
            self.log_result(False, f"获取验证码配置失败: {result.get('detail')}")
            return False
    
    def step4_get_captcha(self) -> Optional[Dict[str, str]]:
        """步骤4: 获取图片验证码"""
        self.log_step("4", "获取图片验证码")
        
        result = self.make_request("GET", "/api/captcha/captcha?length=4")
        
        if result.get("code") == 1000:
            captcha_key = result.get("captcha_key")
            captcha_image = result.get("captcha_image", "")[:50] + "..."  # 截取部分显示
            self.log_result(True, f"验证码获取成功，Key: {captcha_key}", {
                "captcha_key": captcha_key,
                "captcha_image_preview": captcha_image,
                "length": result.get("length")
            })
            return {
                "captcha_key": captcha_key,
                "captcha_image": result.get("captcha_image")
            }
        else:
            self.log_result(False, f"获取验证码失败: {result.get('detail')}")
            return None
    
    def step5_login(self, username: str = "admin", password: str = "admin123", 
                   captcha_info: Optional[Dict[str, str]] = None) -> bool:
        """步骤5: 用户登录"""
        self.log_step("5", f"用户登录 (用户名: {username})")
        
        login_data = {
            "username": username,
            "password": password
        }
        
        # 如果有验证码信息，添加到登录数据中
        if captcha_info:
            login_data.update({
                "captcha_key": captcha_info["captcha_key"],
                "captcha_code": "1234"  # 实际使用中需要用户输入或OCR识别
            })
            print("⚠️  注意: 使用模拟验证码 '1234'，实际环境中需要识别图片验证码")
        
        result = self.make_request("POST", "/api/system/login/basic", json=login_data)
        
        if result.get("code") == 1000:
            data = result.get("data", {})
            self.access_token = data.get("access")
            self.refresh_token = data.get("refresh")
            
            self.log_result(True, "登录成功", {
                "access_token_lifetime": data.get("access_token_lifetime"),
                "refresh_token_lifetime": data.get("refresh_token_lifetime"),
                "access_token_preview": self.access_token[:50] + "..." if self.access_token else None
            })
            return True
        else:
            self.log_result(False, f"登录失败: {result.get('detail')}")
            return False
    
    def step6_get_user_info(self) -> bool:
        """步骤6: 获取当前用户信息"""
        self.log_step("6", "获取当前用户信息")
        
        if not self.access_token:
            self.log_result(False, "未登录，无法获取用户信息")
            return False
        
        result = self.make_request("GET", "/api/system/userinfo/")
        
        if result.get("code") == 1000:
            self.user_info = result.get("data")
            self.log_result(True, "获取用户信息成功", self.user_info)
            return True
        else:
            self.log_result(False, f"获取用户信息失败: {result.get('detail')}")
            return False
    
    def step7_get_user_list(self) -> bool:
        """步骤7: 获取用户列表（需要管理员权限）"""
        self.log_step("7", "获取用户列表")
        
        if not self.access_token:
            self.log_result(False, "未登录，无法获取用户列表")
            return False
        
        params = {
            "page": 1,
            "size": 10,
            "search": "",
            "is_active": True
        }
        
        result = self.make_request("GET", "/api/system/user", params=params)
        
        if result.get("code") == 1000:
            data = result.get("data", {})
            self.log_result(True, f"获取用户列表成功，共 {data.get('total', 0)} 条记录", {
                "total": data.get("total"),
                "page": data.get("page"),
                "size": data.get("size"),
                "pages": data.get("pages"),
                "results_count": len(data.get("results", []))
            })
            return True
        else:
            self.log_result(False, f"获取用户列表失败: {result.get('detail')}")
            return False
    
    def step8_refresh_token(self) -> bool:
        """步骤8: 刷新访问令牌"""
        self.log_step("8", "刷新访问令牌")
        
        if not self.refresh_token:
            self.log_result(False, "无刷新令牌，无法刷新访问令牌")
            return False
        
        result = self.make_request("POST", "/api/system/refresh", json={
            "refresh": self.refresh_token
        })
        
        if result.get("code") == 1000:
            data = result.get("data", {})
            old_token = self.access_token[:20] + "..." if self.access_token else "None"
            
            self.access_token = data.get("access")
            self.refresh_token = data.get("refresh")
            
            new_token = self.access_token[:20] + "..." if self.access_token else "None"
            
            self.log_result(True, "令牌刷新成功", {
                "old_access_token": old_token,
                "new_access_token": new_token,
                "access_token_lifetime": data.get("access_token_lifetime"),
                "refresh_token_lifetime": data.get("refresh_token_lifetime")
            })
            return True
        else:
            self.log_result(False, f"令牌刷新失败: {result.get('detail')}")
            return False
    
    def step9_upload_file(self) -> bool:
        """步骤9: 文件上传测试"""
        self.log_step("9", "文件上传测试")
        
        if not self.access_token:
            self.log_result(False, "未登录，无法上传文件")
            return False
        
        # 创建一个测试文件
        test_content = b"This is a test file for xAdmin FastAPI system."
        
        try:
            files = {'file': ('test.txt', test_content, 'text/plain')}
            data = {'category': 'test'}
            
            result = self.make_request("POST", "/api/common/upload", files=files, data=data)
            
            if result.get("code") == 1000:
                upload_data = result.get("data", {})
                self.log_result(True, "文件上传成功", upload_data)
                return True
            else:
                self.log_result(False, f"文件上传失败: {result.get('detail')}")
                return False
        except Exception as e:
            self.log_result(False, f"文件上传异常: {str(e)}")
            return False
    
    def step10_logout(self) -> bool:
        """步骤10: 用户登出"""
        self.log_step("10", "用户登出")
        
        if not self.access_token:
            self.log_result(False, "未登录，无需登出")
            return False
        
        result = self.make_request("POST", "/api/system/logout")
        
        # 清除本地token
        self.access_token = None
        self.refresh_token = None
        self.user_info = None
        
        if result.get("code") == 1000:
            self.log_result(True, "登出成功")
            return True
        else:
            self.log_result(False, f"登出失败: {result.get('detail')}")
            return True  # 即使登出接口失败，也清除本地token
    
    def run_complete_flow(self, username: str = "admin", password: str = "admin123") -> bool:
        """运行完整的API调用流程"""
        print("\n🚀 开始xAdmin FastAPI系统API测试")
        print(f"🔗 测试地址: {self.base_url}")
        print(f"👤 测试用户: {username}")
        
        start_time = time.time()
        
        # 执行完整流程
        steps_results = []
        
        # 步骤1: 健康检查
        steps_results.append(("健康检查", self.step1_health_check()))
        
        # 步骤2: 获取登录配置
        steps_results.append(("获取登录配置", self.step2_get_login_config()))
        
        # 步骤3: 获取验证码配置
        steps_results.append(("获取验证码配置", self.step3_get_captcha_config()))
        
        # 步骤4: 获取验证码（可选）
        captcha_info = self.step4_get_captcha()
        steps_results.append(("获取验证码", captcha_info is not None))
        
        # 步骤5: 用户登录
        login_success = self.step5_login(username, password, captcha_info)
        steps_results.append(("用户登录", login_success))
        
        if login_success:
            # 步骤6: 获取用户信息
            steps_results.append(("获取用户信息", self.step6_get_user_info()))
            
            # 步骤7: 获取用户列表
            steps_results.append(("获取用户列表", self.step7_get_user_list()))
            
            # 步骤8: 刷新令牌
            steps_results.append(("刷新令牌", self.step8_refresh_token()))
            
            # 步骤9: 文件上传测试
            steps_results.append(("文件上传", self.step9_upload_file()))
            
            # 步骤10: 用户登出
            steps_results.append(("用户登出", self.step10_logout()))
        
        # 计算测试结果
        end_time = time.time()
        duration = end_time - start_time
        
        successful_steps = sum(1 for _, success in steps_results if success)
        total_steps = len(steps_results)
        
        # 输出测试总结
        print(f"\n{'='*80}")
        print(f"📊 测试总结")
        print(f"{'='*80}")
        print(f"⏱️  测试耗时: {duration:.2f}秒")
        print(f"✅ 成功步骤: {successful_steps}/{total_steps}")
        print(f"📈 成功率: {(successful_steps/total_steps)*100:.1f}%")
        
        print(f"\n📋 详细结果:")
        for i, (step_name, success) in enumerate(steps_results, 1):
            status = "✅" if success else "❌"
            print(f"  {i:2d}. {status} {step_name}")
        
        if successful_steps == total_steps:
            print(f"\n🎉 所有测试步骤均成功完成！API调用流程正常。")
            return True
        else:
            print(f"\n⚠️  部分测试步骤失败，请检查系统配置和权限设置。")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="xAdmin FastAPI 系统API测试")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="API服务地址")
    parser.add_argument("--username", default="admin", help="测试用户名")
    parser.add_argument("--password", default="admin123", help="测试密码")
    
    args = parser.parse_args()
    
    # 创建测试器并运行测试
    tester = XAdminAPITester(args.url)
    
    try:
        success = tester.run_complete_flow(args.username, args.password)
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⛔ 测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生异常: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()