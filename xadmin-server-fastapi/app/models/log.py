"""
日志相关数据库模型
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, SmallInteger, JSON, Index
)
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime


class LoginLog(BaseModel):
    """登录日志表"""
    __tablename__ = 'login_log'
    
    # 用户信息
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=True, comment="用户ID")
    username = Column(String(150), nullable=False, comment="用户名")
    
    # 登录信息
    login_type = Column(String(16), default='basic', comment="登录类型: basic, code, oauth")
    login_result = Column(Boolean, default=True, comment="登录结果")
    login_message = Column(String(255), nullable=True, comment="登录消息")
    
    # 客户端信息
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    browser = Column(String(64), nullable=True, comment="浏览器")
    os = Column(String(64), nullable=True, comment="操作系统")
    device = Column(String(64), nullable=True, comment="设备类型")
    
    # 地理位置
    location = Column(String(255), nullable=True, comment="登录地点")
    
    # 时间信息
    login_time = Column(DateTime, default=datetime.utcnow, comment="登录时间")
    logout_time = Column(DateTime, nullable=True, comment="登出时间")
    duration = Column(Integer, default=0, comment="在线时长(秒)")
    
    # 关联关系
    user = relationship("UserInfo", back_populates="login_logs")
    
    def __str__(self):
        return f"{self.username} - {self.login_time}"


class OperationLog(BaseModel):
    """操作日志表"""
    __tablename__ = 'operation_log'
    
    # 用户信息
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=True, comment="用户ID")
    username = Column(String(150), nullable=False, comment="用户名")
    
    # 操作信息
    module = Column(String(64), nullable=True, comment="操作模块")
    operation = Column(String(64), nullable=False, comment="操作类型")
    method = Column(String(10), nullable=False, comment="请求方法")
    url = Column(String(512), nullable=False, comment="请求URL")
    
    # 操作描述
    description = Column(String(255), nullable=True, comment="操作描述")
    
    # 请求和响应信息
    request_data = Column(Text, nullable=True, comment="请求数据")
    response_data = Column(Text, nullable=True, comment="响应数据")
    
    # 状态信息
    status_code = Column(Integer, default=200, comment="状态码")
    success = Column(Boolean, default=True, comment="是否成功")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 性能信息
    execution_time = Column(Integer, default=0, comment="执行时间(毫秒)")
    
    # 客户端信息
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    
    # 时间信息
    operation_time = Column(DateTime, default=datetime.utcnow, comment="操作时间")
    
    # 关联关系
    user = relationship("UserInfo", back_populates="operation_logs")
    
    def __str__(self):
        return f"{self.username} - {self.operation} - {self.operation_time}"


class NoticeMessage(BaseModel):
    """通知消息表"""
    __tablename__ = 'notice_message'
    
    # 消息基本信息
    title = Column(String(255), nullable=False, comment="消息标题")
    content = Column(Text, nullable=False, comment="消息内容")
    
    # 消息类型: 1-系统通知, 2-公告, 3-私信, 4-提醒
    message_type = Column(SmallInteger, default=1, comment="消息类型")
    
    # 优先级: 1-低, 2-中, 3-高, 4-紧急
    level = Column(SmallInteger, default=2, comment="优先级")
    
    # 发送者信息
    sender_id = Column(Integer, ForeignKey('user_info.id'), nullable=True, comment="发送者ID")
    sender = relationship("UserInfo", foreign_keys=[sender_id])
    
    # 接收范围: all-全体, role-角色, dept-部门, user-指定用户
    target_type = Column(String(16), default='all', comment="接收范围类型")
    target_id = Column(String(255), nullable=True, comment="接收目标ID(多个用逗号分隔)")
    
    # 消息状态
    is_published = Column(Boolean, default=False, comment="是否发布")
    publish_time = Column(DateTime, nullable=True, comment="发布时间")
    
    # 有效期
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    
    # 统计信息
    read_count = Column(Integer, default=0, comment="已读数量")
    total_count = Column(Integer, default=0, comment="总发送数量")
    
    def __str__(self):
        return self.title


class NoticeUserRead(BaseModel):
    """用户消息阅读记录表"""
    __tablename__ = 'notice_user_read'
    
    # 关联信息
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False, comment="用户ID")
    message_id = Column(Integer, ForeignKey('notice_message.id'), nullable=False, comment="消息ID")
    
    # 阅读信息
    is_read = Column(Boolean, default=False, comment="是否已读")
    read_time = Column(DateTime, nullable=True, comment="阅读时间")
    
    # 关联关系
    user = relationship("UserInfo")
    message = relationship("NoticeMessage")
    
    # 联合唯一约束
    __table_args__ = (
        Index('idx_notice_user_read_unique', 'user_id', 'message_id', unique=True),
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.message.title}"


# 创建索引
Index('idx_login_log_user_id', LoginLog.user_id)
Index('idx_login_log_username', LoginLog.username)
Index('idx_login_log_login_time', LoginLog.login_time)
Index('idx_login_log_ip_address', LoginLog.ip_address)

Index('idx_operation_log_user_id', OperationLog.user_id)
Index('idx_operation_log_username', OperationLog.username)
Index('idx_operation_log_operation_time', OperationLog.operation_time)
Index('idx_operation_log_module', OperationLog.module)
Index('idx_operation_log_method', OperationLog.method)

Index('idx_notice_message_message_type', NoticeMessage.message_type)
Index('idx_notice_message_target_type', NoticeMessage.target_type)
Index('idx_notice_message_is_published', NoticeMessage.is_published)
Index('idx_notice_message_publish_time', NoticeMessage.publish_time)