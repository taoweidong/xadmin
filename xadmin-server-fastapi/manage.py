#!/usr/bin/env python
"""
xAdmin FastAPI 项目任务管理脚本
Project Task Management Script

提供统一的项目管理命令入口
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description=""):
    """运行命令"""
    if description:
        print(f"🔧 {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=get_project_root())
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令失败: {e}")
        return False

def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent

def show_help():
    """显示帮助信息"""
    help_text = """
🚀 xAdmin FastAPI 项目管理工具

开发命令:
  dev           启动开发服务器 (带热重载)
  prod          启动生产服务器
  install       安装项目依赖
  install-dev   安装开发依赖
  init          初始化项目 (创建虚拟环境 + 安装依赖 + 初始化数据库)

测试命令:
  test          运行所有测试
  test-cov      运行测试并生成覆盖率报告
  test-api      只运行API测试
  lint          代码风格检查

数据库命令:
  db-init       初始化数据库
  db-backup     备份数据库
  db-restore    恢复数据库
  superuser     创建超级用户

构建命令:
  build         构建Docker镜像
  docker        使用Docker运行应用
  clean         清理缓存和临时文件

工具命令:
  docs          查看API文档 (启动服务器并打开浏览器)
  check         检查项目状态
  info          显示项目信息

使用方法:
  python manage.py <命令>
  
示例:
  python manage.py dev          # 启动开发服务器
  python manage.py test         # 运行测试
  python manage.py init         # 初始化项目
"""
    print(help_text)

def cmd_dev():
    """启动开发服务器"""
    python_path = get_venv_python()
    if not python_path.exists():
        print("❌ 虚拟环境不存在，请先运行: python manage.py init")
        return False
    
    return run_command(f'"{python_path}" build/dev.py', "启动开发服务器")

def cmd_prod():
    """启动生产服务器"""
    python_path = get_venv_python()
    return run_command(f'"{python_path}" build/prod.py', "启动生产服务器")

def cmd_install():
    """安装依赖"""
    python_path = get_venv_python()
    if not python_path.exists():
        print("❌ 虚拟环境不存在，请先创建: python -m venv .venv")
        return False
    
    return run_command(f'"{python_path}" -m pip install -r requirements.txt', "安装项目依赖")

def cmd_install_dev():
    """安装开发依赖"""
    python_path = get_venv_python()
    if not python_path.exists():
        print("❌ 虚拟环境不存在，请先创建: python -m venv .venv")
        return False
    
    # 先安装基础依赖
    if not run_command(f'"{python_path}" -m pip install -r requirements.txt', "安装基础依赖"):
        return False
    
    # 再安装开发依赖
    return run_command(f'"{python_path}" -m pip install -r requirements-dev.txt', "安装开发依赖")

def cmd_init():
    """初始化项目"""
    project_root = get_project_root()
    venv_dir = project_root / ".venv"
    
    # 1. 创建虚拟环境
    if not venv_dir.exists():
        print("🔧 创建虚拟环境...")
        if not run_command("python -m venv .venv"):
            return False
    
    # 2. 安装依赖
    if not cmd_install():
        return False
    
    # 3. 初始化数据库
    return cmd_db_init()

def cmd_test():
    """运行测试"""
    python_path = get_venv_python()
    return run_command(f'"{python_path}" -m pytest tests/', "运行测试")

def cmd_test_cov():
    """运行测试并生成覆盖率报告"""
    python_path = get_venv_python()
    return run_command(f'"{python_path}" -m pytest --cov=app --cov-report=html tests/', "运行测试并生成覆盖率报告")

def cmd_test_api():
    """运行API测试"""
    python_path = get_venv_python()
    return run_command(f'"{python_path}" -m pytest tests/test_api.py -v', "运行API测试")

def cmd_lint():
    """代码风格检查"""
    python_path = get_venv_python()
    return run_command(f'"{python_path}" -m flake8 app/ --max-line-length=88', "代码风格检查")

def cmd_db_init():
    """初始化数据库"""
    python_path = get_venv_python()
    return run_command(f'"{python_path}" scripts/init_db.py', "初始化数据库")

def cmd_db_backup():
    """备份数据库"""
    python_path = get_venv_python()
    return run_command(f'"{python_path}" scripts/backup_db.py backup', "备份数据库")

def cmd_db_restore():
    """恢复数据库"""
    python_path = get_venv_python()
    print("📋 可用的备份文件:")
    run_command(f'"{python_path}" scripts/backup_db.py list')
    
    backup_file = input("\n请输入要恢复的备份文件名: ").strip()
    if backup_file:
        return run_command(f'"{python_path}" scripts/backup_db.py restore backups/{backup_file}', "恢复数据库")
    return False

def cmd_superuser():
    """创建超级用户"""
    python_path = get_venv_python()
    return run_command(f'"{python_path}" scripts/create_superuser.py create', "创建超级用户")

def cmd_build():
    """构建Docker镜像"""
    return run_command("docker build -t xadmin-fastapi .", "构建Docker镜像")

def cmd_docker():
    """使用Docker运行"""
    return run_command("docker-compose up -d", "启动Docker容器")

def cmd_clean():
    """清理缓存文件"""
    patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "*.log"
    ]
    
    for pattern in patterns:
        run_command(f"find . -name '{pattern}' -exec rm -rf {{}} +", f"清理 {pattern}")
    
    print("✅ 清理完成")
    return True

def cmd_docs():
    """打开API文档"""
    import webbrowser
    import time
    import threading
    
    def open_browser():
        time.sleep(2)  # 等待服务器启动
        webbrowser.open("http://localhost:8001/docs")
    
    # 在后台线程中打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动开发服务器
    return cmd_dev()

def cmd_check():
    """检查项目状态"""
    project_root = get_project_root()
    venv_python = get_venv_python()
    
    print("🔍 项目状态检查")
    print("=" * 30)
    
    # 检查虚拟环境
    if venv_python.exists():
        print("✅ 虚拟环境: 已创建")
    else:
        print("❌ 虚拟环境: 未创建")
        return
    
    # 检查依赖
    try:
        result = subprocess.run([
            str(venv_python), "-c", "import fastapi, uvicorn"
        ], capture_output=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ 核心依赖: 已安装")
        else:
            print("❌ 核心依赖: 未安装")
    except:
        print("❌ 核心依赖: 检查失败")
    
    # 检查数据库
    db_file = project_root / "xadmin.db"
    if db_file.exists():
        print("✅ 数据库: 已初始化")
    else:
        print("⚠️  数据库: 未初始化")
    
    # 检查配置文件
    env_file = project_root / ".env"
    if env_file.exists():
        print("✅ 环境配置: 已配置")
    else:
        print("⚠️  环境配置: 使用默认配置")

def cmd_info():
    """显示项目信息"""
    project_root = get_project_root()
    
    print("📊 项目信息")
    print("=" * 30)
    print(f"项目名称: xAdmin FastAPI")
    print(f"项目路径: {project_root}")
    print(f"Python版本: {sys.version.split()[0]}")
    
    # 获取FastAPI版本
    venv_python = get_venv_python()
    if venv_python.exists():
        try:
            result = subprocess.run([
                str(venv_python), "-c", "import fastapi; print(fastapi.__version__)"
            ], capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                print(f"FastAPI版本: {result.stdout.strip()}")
        except:
            pass
    
    # 统计代码行数
    try:
        result = subprocess.run([
            "find", "app", "-name", "*.py", "-exec", "wc", "-l", "{}", "+", "|", "tail", "-1"
        ], capture_output=True, text=True, shell=True, cwd=project_root)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split()[-2]
            print(f"代码行数: {lines}")
    except:
        pass

def get_venv_python():
    """获取虚拟环境Python路径"""
    project_root = get_project_root()
    if os.name == 'nt':  # Windows
        return project_root / ".venv" / "Scripts" / "python.exe"
    else:  # Unix/Linux/Mac
        return project_root / ".venv" / "bin" / "python"

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    # 命令映射
    commands = {
        'dev': cmd_dev,
        'prod': cmd_prod,
        'install': cmd_install,
        'install-dev': cmd_install_dev,
        'init': cmd_init,
        'test': cmd_test,
        'test-cov': cmd_test_cov,
        'test-api': cmd_test_api,
        'lint': cmd_lint,
        'db-init': cmd_db_init,
        'db-backup': cmd_db_backup,
        'db-restore': cmd_db_restore,
        'superuser': cmd_superuser,
        'build': cmd_build,
        'docker': cmd_docker,
        'clean': cmd_clean,
        'docs': cmd_docs,
        'check': cmd_check,
        'info': cmd_info,
        'help': show_help,
    }
    
    if command in commands:
        if command == 'help':
            commands[command]()
        else:
            success = commands[command]()
            if not success:
                sys.exit(1)
    else:
        print(f"❌ 未知命令: {command}")
        print("运行 'python manage.py help' 查看可用命令")
        sys.exit(1)

if __name__ == "__main__":
    main()