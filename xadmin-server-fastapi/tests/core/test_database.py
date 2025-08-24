"""
测试 app.core.database 模块
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db, create_tables, drop_tables, SessionLocal, Base


class TestDatabase:
    """测试数据库相关功能"""
    
    def test_get_db_success(self):
        """测试正常获取数据库会话"""
        db_generator = get_db()
        db = next(db_generator)
        
        assert db is not None
        # 确保会话被正确关闭
        try:
            next(db_generator)
        except StopIteration:
            pass  # 这是预期的行为
    
    def test_get_db_exception_handling(self):
        """测试数据库会话异常处理"""
        with patch('app.core.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            # 模拟数据库操作异常
            mock_session.__enter__ = MagicMock(side_effect=Exception("DB Error"))
            
            db_generator = get_db()
            
            with pytest.raises(Exception):
                next(db_generator)
                
            # 确保rollback被调用
            mock_session.rollback.assert_called_once()
    
    def test_create_tables_success(self):
        """测试成功创建数据库表"""
        with patch('app.core.database.Base.metadata.create_all') as mock_create_all:
            create_tables()
            mock_create_all.assert_called_once()
    
    def test_create_tables_exception(self):
        """测试创建数据库表时的异常处理"""
        with patch('app.core.database.Base.metadata.create_all') as mock_create_all:
            mock_create_all.side_effect = Exception("Create table error")
            
            with pytest.raises(Exception, match="Create table error"):
                create_tables()
    
    def test_drop_tables_success(self):
        """测试成功删除数据库表"""
        with patch('app.core.database.Base.metadata.drop_all') as mock_drop_all:
            drop_tables()
            mock_drop_all.assert_called_once()
    
    def test_drop_tables_exception(self):
        """测试删除数据库表时的异常处理"""
        with patch('app.core.database.Base.metadata.drop_all') as mock_drop_all:
            mock_drop_all.side_effect = Exception("Drop table error")
            
            with pytest.raises(Exception, match="Drop table error"):
                drop_tables()
    
    def test_session_local_configuration(self):
        """测试SessionLocal配置"""
        # 检查SessionLocal是否正确配置
        assert SessionLocal.kw['autocommit'] is False
        assert SessionLocal.kw['autoflush'] is False
    
    def test_base_declarative_base(self):
        """测试Base声明性基类"""
        # 检查Base是否是正确的声明性基类
        assert hasattr(Base, 'metadata')
        assert hasattr(Base, 'registry')
    
    @patch('app.core.database.settings')
    def test_sqlite_engine_creation(self, mock_settings):
        """测试SQLite引擎创建"""
        mock_settings.DB_ENGINE = "sqlite"
        mock_settings.DATABASE_URL = "sqlite:///test.db"
        mock_settings.DEBUG = False
        
        # 重新导入以应用mock设置
        with patch('app.core.database.create_engine') as mock_create_engine:
            import importlib
            import app.core.database
            importlib.reload(app.core.database)
            
            # 验证create_engine被调用且使用了正确的参数
            mock_create_engine.assert_called()
            call_args = mock_create_engine.call_args
            assert "sqlite" in str(call_args[0][0])  # URL包含sqlite
    
    @patch('app.core.database.settings')
    def test_non_sqlite_engine_creation(self, mock_settings):
        """测试非SQLite引擎创建"""
        mock_settings.DB_ENGINE = "mysql"
        mock_settings.DATABASE_URL = "mysql+pymysql://user:pass@localhost/db"
        mock_settings.DEBUG = False
        
        with patch('app.core.database.create_engine') as mock_create_engine:
            import importlib
            import app.core.database
            importlib.reload(app.core.database)
            
            mock_create_engine.assert_called()
            call_args = mock_create_engine.call_args
            
            # 检查是否设置了正确的连接池参数
            call_kwargs = call_args[1]
            assert 'pool_pre_ping' in call_kwargs
            assert 'pool_recycle' in call_kwargs
    
    def test_get_db_context_manager(self):
        """测试get_db作为上下文管理器的行为"""
        db_gen = get_db()
        db = next(db_gen)
        
        # 模拟在with语句中使用
        try:
            # 模拟一些数据库操作
            assert db is not None
            
            # 正常结束
            next(db_gen)
        except StopIteration:
            # 这是预期的，表示生成器正常结束
            pass
    
    def test_database_session_isolation(self):
        """测试数据库会话隔离"""
        # 获取两个不同的数据库会话
        db_gen1 = get_db()
        db_gen2 = get_db()
        
        db1 = next(db_gen1)
        db2 = next(db_gen2)
        
        # 确保是不同的会话实例
        assert db1 is not db2
        
        # 清理
        try:
            next(db_gen1)
        except StopIteration:
            pass
        try:
            next(db_gen2)
        except StopIteration:
            pass


class TestDatabaseIntegration:
    """测试数据库集成功能"""
    
    def test_full_database_lifecycle(self, test_db_engine):
        """测试完整的数据库生命周期"""
        # 使用测试数据库引擎
        TestSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False, 
            bind=test_db_engine
        )
        
        # 创建会话
        session = TestSessionLocal()
        assert session is not None
        
        # 关闭会话
        session.close()
    
    def test_database_connection_error_handling(self):
        """测试数据库连接错误处理"""
        with patch('app.core.database.SessionLocal') as mock_session_local:
            # 模拟连接错误
            mock_session_local.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception):
                db_gen = get_db()
                next(db_gen)
    
    def test_transaction_rollback(self):
        """测试事务回滚"""
        with patch('app.core.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            # 模拟在数据库操作中发生异常
            def side_effect():
                raise Exception("Transaction error")
            
            mock_session.__enter__ = side_effect
            
            with pytest.raises(Exception):
                db_gen = get_db()
                next(db_gen)
            
            # 验证rollback被调用
            mock_session.rollback.assert_called_once()
            # 验证close被调用
            mock_session.close.assert_called_once()