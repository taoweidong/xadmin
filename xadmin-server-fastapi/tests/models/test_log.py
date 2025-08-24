"""
测试 app.models.log 模块
"""
import pytest
from datetime import datetime
from app.models.log import LoginLog, OperationLog, NoticeMessage, NoticeUserRead
from app.models.user import UserInfo


class TestLoginLog:
    """测试登录日志模型"""
    
    def test_login_log_creation(self, test_db_session):
        """测试登录日志创建"""
        login_log = LoginLog(
            username="testuser",
            login_type="basic",
            login_result=True,
            login_message="登录成功",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0...",
            browser="Chrome",
            os="Windows",
            device="PC",
            location="北京市",
            duration=3600
        )
        
        test_db_session.add(login_log)
        test_db_session.commit()
        
        assert login_log.id is not None
        assert login_log.username == "testuser"
        assert login_log.login_type == "basic"
        assert login_log.login_result is True
        assert login_log.login_message == "登录成功"
        assert login_log.ip_address == "192.168.1.100"
        assert login_log.browser == "Chrome"
        assert login_log.os == "Windows"
        assert login_log.device == "PC"
        assert login_log.location == "北京市"
        assert login_log.duration == 3600
        assert login_log.login_time is not None
    
    def test_login_log_with_user_relationship(self, test_db_session):
        """测试登录日志与用户关系"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        login_log = LoginLog(
            user_id=user.id,
            username=user.username,
            login_type="basic",
            login_result=True
        )
        
        test_db_session.add(login_log)
        test_db_session.commit()
        
        # 验证关系
        assert login_log.user_id == user.id
        assert login_log.user == user
        assert login_log in user.login_logs
    
    def test_login_log_default_values(self, test_db_session):
        """测试登录日志默认值"""
        login_log = LoginLog(username="testuser")
        
        test_db_session.add(login_log)
        test_db_session.commit()
        
        assert login_log.login_type == "basic"  # 默认登录类型
        assert login_log.login_result is True  # 默认登录成功
        assert login_log.duration == 0  # 默认时长为0
        assert login_log.login_time is not None  # 自动设置登录时间
    
    def test_login_log_str_representation(self, test_db_session):
        """测试登录日志字符串表示"""
        login_log = LoginLog(username="testuser")
        test_db_session.add(login_log)
        test_db_session.commit()
        
        expected_str = f"testuser - {login_log.login_time}"
        assert str(login_log) == expected_str
    
    def test_login_log_failed_login(self, test_db_session):
        """测试失败登录日志"""
        login_log = LoginLog(
            username="testuser",
            login_result=False,
            login_message="密码错误"
        )
        
        test_db_session.add(login_log)
        test_db_session.commit()
        
        assert login_log.login_result is False
        assert login_log.login_message == "密码错误"


class TestOperationLog:
    """测试操作日志模型"""
    
    def test_operation_log_creation(self, test_db_session):
        """测试操作日志创建"""
        operation_log = OperationLog(
            username="testuser",
            module="user",
            operation="create",
            method="POST",
            url="/api/users/",
            description="创建用户",
            request_data='{"username": "newuser"}',
            response_data='{"id": 1, "username": "newuser"}',
            status_code=201,
            success=True,
            execution_time=150,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0..."
        )
        
        test_db_session.add(operation_log)
        test_db_session.commit()
        
        assert operation_log.id is not None
        assert operation_log.username == "testuser"
        assert operation_log.module == "user"
        assert operation_log.operation == "create"
        assert operation_log.method == "POST"
        assert operation_log.url == "/api/users/"
        assert operation_log.description == "创建用户"
        assert operation_log.status_code == 201
        assert operation_log.success is True
        assert operation_log.execution_time == 150
        assert operation_log.operation_time is not None
    
    def test_operation_log_with_user_relationship(self, test_db_session):
        """测试操作日志与用户关系"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        operation_log = OperationLog(
            user_id=user.id,
            username=user.username,
            operation="read",
            method="GET",
            url="/api/users/"
        )
        
        test_db_session.add(operation_log)
        test_db_session.commit()
        
        # 验证关系
        assert operation_log.user_id == user.id
        assert operation_log.user == user
        assert operation_log in user.operation_logs
    
    def test_operation_log_default_values(self, test_db_session):
        """测试操作日志默认值"""
        operation_log = OperationLog(
            username="testuser",
            operation="test",
            method="GET",
            url="/api/test/"
        )
        
        test_db_session.add(operation_log)
        test_db_session.commit()
        
        assert operation_log.status_code == 200  # 默认状态码
        assert operation_log.success is True  # 默认成功
        assert operation_log.execution_time == 0  # 默认执行时间
        assert operation_log.operation_time is not None  # 自动设置操作时间
    
    def test_operation_log_str_representation(self, test_db_session):
        """测试操作日志字符串表示"""
        operation_log = OperationLog(
            username="testuser",
            operation="create",
            method="POST",
            url="/api/test/"
        )
        test_db_session.add(operation_log)
        test_db_session.commit()
        
        expected_str = f"testuser - create - {operation_log.operation_time}"
        assert str(operation_log) == expected_str
    
    def test_operation_log_error_case(self, test_db_session):
        """测试操作日志错误情况"""
        operation_log = OperationLog(
            username="testuser",
            operation="delete",
            method="DELETE",
            url="/api/users/999/",
            status_code=404,
            success=False,
            error_message="用户不存在"
        )
        
        test_db_session.add(operation_log)
        test_db_session.commit()
        
        assert operation_log.status_code == 404
        assert operation_log.success is False
        assert operation_log.error_message == "用户不存在"


class TestNoticeMessage:
    """测试通知消息模型"""
    
    def test_notice_message_creation(self, test_db_session):
        """测试通知消息创建"""
        notice = NoticeMessage(
            title="系统维护通知",
            content="系统将于今晚22:00-24:00进行维护",
            message_type=1,
            level=3,
            target_type="all",
            is_published=True,
            read_count=10,
            total_count=100
        )
        
        test_db_session.add(notice)
        test_db_session.commit()
        
        assert notice.id is not None
        assert notice.title == "系统维护通知"
        assert notice.content == "系统将于今晚22:00-24:00进行维护"
        assert notice.message_type == 1
        assert notice.level == 3
        assert notice.target_type == "all"
        assert notice.is_published is True
        assert notice.read_count == 10
        assert notice.total_count == 100
    
    def test_notice_message_with_sender(self, test_db_session):
        """测试通知消息与发送者关系"""
        sender = UserInfo(username="admin", password="password")
        test_db_session.add(sender)
        test_db_session.commit()
        
        notice = NoticeMessage(
            title="测试通知",
            content="这是一条测试通知",
            sender_id=sender.id
        )
        
        test_db_session.add(notice)
        test_db_session.commit()
        
        # 验证关系
        assert notice.sender_id == sender.id
        assert notice.sender == sender
    
    def test_notice_message_default_values(self, test_db_session):
        """测试通知消息默认值"""
        notice = NoticeMessage(
            title="测试通知",
            content="测试内容"
        )
        
        test_db_session.add(notice)
        test_db_session.commit()
        
        assert notice.message_type == 1  # 默认系统通知
        assert notice.level == 2  # 默认中等优先级
        assert notice.target_type == "all"  # 默认全体接收
        assert notice.is_published is False  # 默认未发布
        assert notice.read_count == 0  # 默认已读数量为0
        assert notice.total_count == 0  # 默认总数量为0
    
    def test_notice_message_str_representation(self, test_db_session):
        """测试通知消息字符串表示"""
        notice = NoticeMessage(
            title="测试通知",
            content="测试内容"
        )
        test_db_session.add(notice)
        test_db_session.commit()
        
        assert str(notice) == "测试通知"
    
    def test_notice_message_target_types(self, test_db_session):
        """测试不同的通知目标类型"""
        notices = [
            NoticeMessage(title="全体通知", content="内容1", target_type="all"),
            NoticeMessage(title="角色通知", content="内容2", target_type="role", target_id="admin,manager"),
            NoticeMessage(title="部门通知", content="内容3", target_type="dept", target_id="1,2,3"),
            NoticeMessage(title="个人通知", content="内容4", target_type="user", target_id="1,2")
        ]
        
        test_db_session.add_all(notices)
        test_db_session.commit()
        
        assert notices[0].target_type == "all"
        assert notices[1].target_type == "role"
        assert notices[1].target_id == "admin,manager"
        assert notices[2].target_type == "dept"
        assert notices[3].target_type == "user"


class TestNoticeUserRead:
    """测试用户消息阅读记录模型"""
    
    def test_notice_user_read_creation(self, test_db_session):
        """测试用户阅读记录创建"""
        user = UserInfo(username="testuser", password="password")
        notice = NoticeMessage(title="测试通知", content="测试内容")
        
        test_db_session.add_all([user, notice])
        test_db_session.commit()
        
        read_record = NoticeUserRead(
            user_id=user.id,
            message_id=notice.id,
            is_read=True,
            read_time=datetime.utcnow()
        )
        
        test_db_session.add(read_record)
        test_db_session.commit()
        
        assert read_record.id is not None
        assert read_record.user_id == user.id
        assert read_record.message_id == notice.id
        assert read_record.is_read is True
        assert read_record.read_time is not None
    
    def test_notice_user_read_relationships(self, test_db_session):
        """测试用户阅读记录关系"""
        user = UserInfo(username="testuser", password="password")
        notice = NoticeMessage(title="测试通知", content="测试内容")
        
        test_db_session.add_all([user, notice])
        test_db_session.commit()
        
        read_record = NoticeUserRead(
            user_id=user.id,
            message_id=notice.id
        )
        
        test_db_session.add(read_record)
        test_db_session.commit()
        
        # 验证关系
        assert read_record.user == user
        assert read_record.message == notice
    
    def test_notice_user_read_default_values(self, test_db_session):
        """测试用户阅读记录默认值"""
        user = UserInfo(username="testuser", password="password")
        notice = NoticeMessage(title="测试通知", content="测试内容")
        
        test_db_session.add_all([user, notice])
        test_db_session.commit()
        
        read_record = NoticeUserRead(
            user_id=user.id,
            message_id=notice.id
        )
        
        test_db_session.add(read_record)
        test_db_session.commit()
        
        assert read_record.is_read is False  # 默认未读
        assert read_record.read_time is None  # 默认无阅读时间
    
    def test_notice_user_read_str_representation(self, test_db_session):
        """测试用户阅读记录字符串表示"""
        user = UserInfo(username="testuser", password="password")
        notice = NoticeMessage(title="测试通知", content="测试内容")
        
        test_db_session.add_all([user, notice])
        test_db_session.commit()
        
        read_record = NoticeUserRead(
            user_id=user.id,
            message_id=notice.id
        )
        
        test_db_session.add(read_record)
        test_db_session.commit()
        
        expected_str = f"{user.username} - {notice.title}"
        assert str(read_record) == expected_str
    
    def test_notice_user_read_unique_constraint(self, test_db_session):
        """测试用户阅读记录唯一性约束"""
        user = UserInfo(username="testuser", password="password")
        notice = NoticeMessage(title="测试通知", content="测试内容")
        
        test_db_session.add_all([user, notice])
        test_db_session.commit()
        
        read_record1 = NoticeUserRead(user_id=user.id, message_id=notice.id)
        read_record2 = NoticeUserRead(user_id=user.id, message_id=notice.id)
        
        test_db_session.add(read_record1)
        test_db_session.commit()
        
        test_db_session.add(read_record2)
        # 应该因为唯一性约束而失败
        with pytest.raises(Exception):  # 具体异常类型取决于数据库
            test_db_session.commit()


class TestLogModelIndexes:
    """测试日志模型索引"""
    
    def test_login_log_indexes(self):
        """测试登录日志索引字段"""
        # 验证关键字段有索引
        # 注意：实际的索引测试需要在数据库层面进行
        # 这里主要验证模型定义的正确性
        assert hasattr(LoginLog, 'user_id')
        assert hasattr(LoginLog, 'username')
        assert hasattr(LoginLog, 'login_time')
        assert hasattr(LoginLog, 'ip_address')
    
    def test_operation_log_indexes(self):
        """测试操作日志索引字段"""
        assert hasattr(OperationLog, 'user_id')
        assert hasattr(OperationLog, 'username')
        assert hasattr(OperationLog, 'operation_time')
        assert hasattr(OperationLog, 'module')
        assert hasattr(OperationLog, 'method')
    
    def test_notice_message_indexes(self):
        """测试通知消息索引字段"""
        assert hasattr(NoticeMessage, 'message_type')
        assert hasattr(NoticeMessage, 'target_type')
        assert hasattr(NoticeMessage, 'is_published')
        assert hasattr(NoticeMessage, 'publish_time')


class TestLogModelIntegration:
    """测试日志模型集成功能"""
    
    def test_user_with_multiple_logs(self, test_db_session):
        """测试用户与多个日志记录"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        # 创建多个登录日志
        login_logs = [
            LoginLog(user_id=user.id, username=user.username, login_type="basic"),
            LoginLog(user_id=user.id, username=user.username, login_type="code"),
        ]
        
        # 创建多个操作日志
        operation_logs = [
            OperationLog(user_id=user.id, username=user.username, operation="read", method="GET", url="/api/users/"),
            OperationLog(user_id=user.id, username=user.username, operation="create", method="POST", url="/api/users/"),
        ]
        
        test_db_session.add_all(login_logs + operation_logs)
        test_db_session.commit()
        
        # 验证关系
        assert len(user.login_logs) == 2
        assert len(user.operation_logs) == 2
        
        for login_log in user.login_logs:
            assert login_log.user == user
        
        for operation_log in user.operation_logs:
            assert operation_log.user == user
    
    def test_notice_with_multiple_readers(self, test_db_session):
        """测试通知消息与多个读者"""
        notice = NoticeMessage(title="测试通知", content="测试内容")
        users = [
            UserInfo(username="user1", password="password"),
            UserInfo(username="user2", password="password"),
        ]
        
        test_db_session.add_all([notice] + users)
        test_db_session.commit()
        
        # 创建阅读记录
        read_records = [
            NoticeUserRead(user_id=users[0].id, message_id=notice.id, is_read=True),
            NoticeUserRead(user_id=users[1].id, message_id=notice.id, is_read=False),
        ]
        
        test_db_session.add_all(read_records)
        test_db_session.commit()
        
        # 验证关系
        for read_record in read_records:
            assert read_record.message == notice
            assert read_record.user in users