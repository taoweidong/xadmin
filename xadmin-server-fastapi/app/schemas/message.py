"""
消息通知相关Pydantic Schema模型
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.schemas.base import BaseSchema, BaseResponse, TimestampSchema, PaginationParams
from datetime import datetime


class NoticeMessageBase(BaseSchema):
    """通知消息基础Schema"""
    title: str = Field(..., max_length=255, description="消息标题")
    content: str = Field(..., description="消息内容")
    message_type: int = Field(1, description="消息类型: 1-系统通知, 2-公告, 3-私信, 4-提醒")
    level: int = Field(2, description="优先级: 1-低, 2-中, 3-高, 4-紧急")
    target_type: str = Field("all", description="接收范围类型: all-全体, role-角色, dept-部门, user-指定用户")
    target_id: Optional[str] = Field(None, description="接收目标ID(多个用逗号分隔)")
    is_published: bool = Field(False, description="是否发布")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")


class NoticeMessageCreate(NoticeMessageBase):
    """创建通知消息Schema"""
    sender_id: Optional[int] = Field(None, description="发送者ID")


class NoticeMessageUpdate(BaseSchema):
    """更新通知消息Schema"""
    title: Optional[str] = Field(None, max_length=255, description="消息标题")
    content: Optional[str] = Field(None, description="消息内容")
    message_type: Optional[int] = Field(None, description="消息类型")
    level: Optional[int] = Field(None, description="优先级")
    target_type: Optional[str] = Field(None, description="接收范围类型")
    target_id: Optional[str] = Field(None, description="接收目标ID")
    is_published: Optional[bool] = Field(None, description="是否发布")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")


class NoticeMessageProfile(NoticeMessageBase, TimestampSchema):
    """通知消息档案Schema"""
    id: int = Field(..., description="消息ID")
    sender_id: Optional[int] = Field(None, description="发送者ID")
    sender_name: Optional[str] = Field(None, description="发送者名称")
    publish_time: Optional[datetime] = Field(None, description="发布时间")
    read_count: int = Field(0, description="已读数量")
    total_count: int = Field(0, description="总发送数量")
    
    model_config = ConfigDict(from_attributes=True)


class NoticeMessageListParams(PaginationParams):
    """通知消息列表查询参数"""
    search: Optional[str] = Field(None, description="搜索关键词")
    message_type: Optional[int] = Field(None, description="消息类型")
    level: Optional[int] = Field(None, description="优先级")
    target_type: Optional[str] = Field(None, description="接收范围类型")
    is_published: Optional[bool] = Field(None, description="是否发布")
    sender_id: Optional[int] = Field(None, description="发送者ID")


class NoticeMessagePublish(BaseSchema):
    """发布通知消息Schema"""
    message_id: int = Field(..., description="消息ID")
    publish_time: Optional[datetime] = Field(None, description="发布时间")


class NoticeMessageBatchAction(BaseSchema):
    """批量操作通知消息Schema"""
    message_ids: List[int] = Field(..., description="消息ID列表")
    action: str = Field(..., description="操作类型: publish-发布, unpublish-取消发布, delete-删除")
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        allowed_actions = ['publish', 'unpublish', 'delete']
        if v not in allowed_actions:
            raise ValueError(f'操作类型必须是 {", ".join(allowed_actions)} 之一')
        return v


# 用户消息阅读记录相关Schema
class NoticeUserReadBase(BaseSchema):
    """用户消息阅读记录基础Schema"""
    user_id: int = Field(..., description="用户ID")
    message_id: int = Field(..., description="消息ID")
    is_read: bool = Field(False, description="是否已读")
    read_time: Optional[datetime] = Field(None, description="阅读时间")


class NoticeUserReadCreate(NoticeUserReadBase):
    """创建用户消息阅读记录Schema"""
    pass


class NoticeUserReadUpdate(BaseSchema):
    """更新用户消息阅读记录Schema"""
    is_read: Optional[bool] = Field(None, description="是否已读")
    read_time: Optional[datetime] = Field(None, description="阅读时间")


class NoticeUserReadProfile(NoticeUserReadBase, TimestampSchema):
    """用户消息阅读记录档案Schema"""
    id: int = Field(..., description="记录ID")
    message_title: Optional[str] = Field(None, description="消息标题")
    message_type: Optional[int] = Field(None, description="消息类型")
    message_level: Optional[int] = Field(None, description="消息优先级")
    
    model_config = ConfigDict(from_attributes=True)


class NoticeUserReadListParams(PaginationParams):
    """用户消息阅读记录列表查询参数"""
    is_read: Optional[bool] = Field(None, description="是否已读")
    message_type: Optional[int] = Field(None, description="消息类型")
    level: Optional[int] = Field(None, description="优先级")


class UserNoticeStats(BaseSchema):
    """用户通知统计Schema"""
    total_count: int = Field(0, description="总消息数")
    unread_count: int = Field(0, description="未读消息数")
    read_count: int = Field(0, description="已读消息数")
    type_stats: Dict[str, int] = Field({}, description="按类型统计")
    level_stats: Dict[str, int] = Field({}, description="按优先级统计")


class UserNoticeStatsResponse(BaseResponse[UserNoticeStats]):
    """用户通知统计响应Schema"""
    pass


class MarkReadRequest(BaseSchema):
    """标记已读请求Schema"""
    message_ids: List[int] = Field(..., description="消息ID列表")


class MarkAllReadRequest(BaseSchema):
    """标记全部已读请求Schema"""
    message_type: Optional[int] = Field(None, description="消息类型(可选)")


# 消息推送相关Schema
class MessagePushRequest(BaseSchema):
    """消息推送请求Schema"""
    title: str = Field(..., max_length=255, description="消息标题")
    content: str = Field(..., description="消息内容")
    message_type: int = Field(1, description="消息类型")
    level: int = Field(2, description="优先级")
    target_users: List[int] = Field(..., description="目标用户ID列表")
    push_immediately: bool = Field(True, description="是否立即推送")


class MessagePushResponse(BaseResponse[Dict[str, Any]]):
    """消息推送响应Schema"""
    pass


# WebSocket消息相关Schema
class WebSocketMessage(BaseSchema):
    """WebSocket消息Schema"""
    type: str = Field(..., description="消息类型")
    data: Dict[str, Any] = Field(..., description="消息数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class NotificationWebSocketMessage(WebSocketMessage):
    """通知WebSocket消息Schema"""
    type: str = Field("notification", description="消息类型")
    data: Dict[str, Any] = Field(..., description="通知数据")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "notification",
                "data": {
                    "id": 1,
                    "title": "系统通知",
                    "content": "您有新的消息",
                    "message_type": 1,
                    "level": 2,
                    "created_at": "2024-08-23T10:00:00Z"
                },
                "timestamp": "2024-08-23T10:00:00Z"
            }
        }
    )


# 消息模板相关Schema
class MessageTemplate(BaseSchema):
    """消息模板Schema"""
    name: str = Field(..., description="模板名称")
    title_template: str = Field(..., description="标题模板")
    content_template: str = Field(..., description="内容模板")
    message_type: int = Field(1, description="消息类型")
    level: int = Field(2, description="优先级")
    variables: List[str] = Field([], description="变量列表")


class MessageTemplateResponse(BaseResponse[List[MessageTemplate]]):
    """消息模板响应Schema"""
    pass


class SendMessageFromTemplate(BaseSchema):
    """从模板发送消息Schema"""
    template_name: str = Field(..., description="模板名称")
    variables: Dict[str, str] = Field({}, description="变量值")
    target_users: List[int] = Field(..., description="目标用户ID列表")


# 消息统计相关Schema
class MessageStatistics(BaseSchema):
    """消息统计Schema"""
    total_messages: int = Field(0, description="总消息数")
    published_messages: int = Field(0, description="已发布消息数")
    draft_messages: int = Field(0, description="草稿消息数")
    total_recipients: int = Field(0, description="总接收者数")
    total_reads: int = Field(0, description="总阅读数")
    read_rate: float = Field(0.0, description="阅读率")
    type_distribution: Dict[str, int] = Field({}, description="类型分布")
    level_distribution: Dict[str, int] = Field({}, description="优先级分布")
    daily_stats: List[Dict[str, Any]] = Field([], description="每日统计")


class MessageStatisticsResponse(BaseResponse[MessageStatistics]):
    """消息统计响应Schema"""
    pass