import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

print("Testing imports...")

try:
    from main import app
    print("✓ main.app imported successfully")
except Exception as e:
    print(f"✗ Failed to import main.app: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.api import auth, user, common, settings, message, dept, menu
    print("✓ All API modules imported successfully")
except Exception as e:
    print(f"✗ Failed to import API modules: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.models import BaseModel, UserInfo, UserRole, MenuInfo
    print("✓ Models imported successfully")
except Exception as e:
    print(f"✗ Failed to import models: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")