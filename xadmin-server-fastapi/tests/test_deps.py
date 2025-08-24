#!/usr/bin/env python
"""
依赖包测试脚本
"""

def test_imports():
    """测试所有必需的包导入"""
    imports_status = {}
    
    # 核心依赖
    try:
        import fastapi
        imports_status['fastapi'] = "OK"
    except ImportError as e:
        imports_status['fastapi'] = f"FAILED: {e}"
    
    try:
        import uvicorn
        imports_status['uvicorn'] = "OK"
    except ImportError as e:
        imports_status['uvicorn'] = f"FAILED: {e}"
    
    try:
        import pydantic
        imports_status['pydantic'] = "OK"
    except ImportError as e:
        imports_status['pydantic'] = f"FAILED: {e}"
    
    # 数据库
    try:
        import sqlalchemy
        imports_status['sqlalchemy'] = "OK"
    except ImportError as e:
        imports_status['sqlalchemy'] = f"FAILED: {e}"
    
    # PIL/Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont
        imports_status['PIL'] = "OK"
    except ImportError as e:
        imports_status['PIL'] = f"FAILED: {e}"
    
    # 其他关键包
    try:
        import redis
        imports_status['redis'] = "OK"
    except ImportError as e:
        imports_status['redis'] = f"FAILED: {e}"
    
    try:
        import jose
        imports_status['python-jose'] = "OK"
    except ImportError as e:
        imports_status['python-jose'] = f"FAILED: {e}"
    
    try:
        import passlib
        imports_status['passlib'] = "OK"
    except ImportError as e:
        imports_status['passlib'] = f"FAILED: {e}"
    
    # 输出结果
    print("=== 依赖包导入测试结果 ===")
    for package, status in imports_status.items():
        print(f"{package:15} : {status}")
    
    # 检查失败的包
    failed_packages = [pkg for pkg, status in imports_status.items() if status.startswith('FAILED')]
    if failed_packages:
        print(f"\n需要安装的包: {', '.join(failed_packages)}")
        return False
    else:
        print("\n所有依赖包都已正确安装!")
        return True

if __name__ == "__main__":
    test_imports()