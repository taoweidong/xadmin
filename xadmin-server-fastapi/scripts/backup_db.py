#!/usr/bin/env python
"""
数据库备份脚本
Database Backup Script
"""
import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_database():
    """备份数据库"""
    project_dir = Path(__file__).parent.parent
    db_file = project_dir / "xadmin.db"
    backup_dir = project_dir / "backups"
    
    # 创建备份目录
    backup_dir.mkdir(exist_ok=True)
    
    if not db_file.exists():
        print("❌ 数据库文件不存在")
        return
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"xadmin_{timestamp}.db"
    
    try:
        # 复制数据库文件
        shutil.copy2(db_file, backup_file)
        print(f"✅ 数据库备份成功: {backup_file}")
        
        # 清理旧备份（保留最近10个）
        backup_files = sorted(backup_dir.glob("xadmin_*.db"), reverse=True)
        for old_backup in backup_files[10:]:
            old_backup.unlink()
            print(f"🗑️  删除旧备份: {old_backup.name}")
            
    except Exception as e:
        print(f"❌ 备份失败: {e}")

def restore_database(backup_file: str):
    """恢复数据库"""
    project_dir = Path(__file__).parent.parent
    db_file = project_dir / "xadmin.db"
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"❌ 备份文件不存在: {backup_file}")
        return
    
    try:
        # 备份当前数据库
        if db_file.exists():
            current_backup = db_file.with_suffix(".db.bak")
            shutil.copy2(db_file, current_backup)
            print(f"📄 当前数据库已备份为: {current_backup}")
        
        # 恢复数据库
        shutil.copy2(backup_path, db_file)
        print(f"✅ 数据库恢复成功: {backup_file}")
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")

def list_backups():
    """列出所有备份"""
    project_dir = Path(__file__).parent.parent
    backup_dir = project_dir / "backups"
    
    if not backup_dir.exists():
        print("📁 备份目录不存在")
        return
    
    backup_files = sorted(backup_dir.glob("xadmin_*.db"), reverse=True)
    
    if not backup_files:
        print("📁 没有找到备份文件")
        return
    
    print("📋 备份文件列表:")
    for i, backup_file in enumerate(backup_files, 1):
        size = backup_file.stat().st_size / 1024 / 1024  # MB
        mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
        print(f"  {i}. {backup_file.name} ({size:.2f}MB, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python scripts/backup_db.py backup              # 备份数据库")
        print("  python scripts/backup_db.py restore <文件名>     # 恢复数据库")
        print("  python scripts/backup_db.py list                # 列出备份")
        return
    
    command = sys.argv[1]
    
    if command == "backup":
        backup_database()
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ 请指定要恢复的备份文件")
            return
        restore_database(sys.argv[2])
    elif command == "list":
        list_backups()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()