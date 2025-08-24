import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    from main import app
    print("✓ Successfully imported app from main")
except Exception as e:
    print(f"✗ Failed to import app from main: {e}")

try:
    from app.api import auth, user, common, settings, message, dept, menu
    print("✓ Successfully imported all API modules")
except Exception as e:
    print(f"✗ Failed to import API modules: {e}")

try:
    from app.models import UserModel, UserRole
    print("✓ Successfully imported models")
except Exception as e:
    print(f"✗ Failed to import models: {e}")

print("Test completed.")