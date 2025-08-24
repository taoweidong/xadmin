"""
消息通知API路由
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import (
    get_current_active_user, require_permission
)
from app.schemas.base import BaseResponse, ListResponse, PaginationParams
from app.schemas.message import (
    NoticeMessageProfile, NoticeMessageCreate, NoticeMessageUpdate, 
    NoticeMessageListParams, NoticeMessagePublish, NoticeMessageBatchAction,
    NoticeUserReadProfile, NoticeUserReadListParams, UserNoticeStatsResponse,
    MarkReadRequest, MarkAllReadRequest, MessagePushRequest, MessagePushResponse,
    MessageStatisticsResponse, NotificationWebSocketMessage
)
from app.services.message import NoticeMessageService, NoticeUserReadService, MessagePushService
from app.models.user import UserInfo
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected to WebSocket")
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast(self, message: str):
        disconnected_users = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # 清理断开的连接
        for user_id in disconnected_users:
            self.disconnect(user_id)

manager = ConnectionManager()


# 通知消息管理接口（管理员）
@router.get("/message/notice", response_model=ListResponse[List[NoticeMessageProfile]])
async def get_notice_message_list(
    params: NoticeMessageListParams = Depends(),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("message:read"))
):
    """获取通知消息列表"""
    message_service = NoticeMessageService(db)
    
    filters = {}
    if params.search:
        filters['search'] = params.search
    if params.message_type:
        filters['message_type'] = params.message_type
    if params.level:
        filters['level'] = params.level
    if params.target_type:
        filters['target_type'] = params.target_type
    if params.is_published is not None:
        filters['is_published'] = params.is_published
    if params.sender_id:
        filters['sender_id'] = params.sender_id
    
    result = message_service.get_message_list(params, filters)
    
    # 转换为响应格式
    message_profiles = []
    for message in result['results']:
        profile = NoticeMessageProfile(
            id=message.id,
            title=message.title,
            content=message.content,
            message_type=message.message_type,
            level=message.level,
            target_type=message.target_type,
            target_id=message.target_id,
            is_published=message.is_published,
            start_time=message.start_time,
            end_time=message.end_time,
            sender_id=message.sender_id,
            sender_name=message.sender.nickname if message.sender else None,
            publish_time=message.publish_time,
            read_count=message.read_count,
            total_count=message.total_count,
            created_at=message.created_at,
            updated_at=message.updated_at
        )
        message_profiles.append(profile)
    
    return ListResponse(
        code=1000,
        detail="success",
        data={
            "results": message_profiles,
            "total": result['total'],
            "page": result['page'],
            "size": result['size'],
            "pages": result['pages']
        }
    )


@router.post("/message/notice", response_model=BaseResponse[NoticeMessageProfile])
async def create_notice_message(
    message_data: NoticeMessageCreate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("message:create"))
):
    """创建通知消息"""
    message_service = NoticeMessageService(db)
    
    # 设置发送者
    message_dict = message_data.dict()
    message_dict['sender_id'] = current_user.id
    
    message = message_service.create_message(message_dict)
    
    profile = NoticeMessageProfile(
        id=message.id,
        title=message.title,
        content=message.content,
        message_type=message.message_type,
        level=message.level,
        target_type=message.target_type,
        target_id=message.target_id,
        is_published=message.is_published,
        start_time=message.start_time,
        end_time=message.end_time,
        sender_id=message.sender_id,
        sender_name=current_user.nickname,
        publish_time=message.publish_time,
        read_count=message.read_count,
        total_count=message.total_count,
        created_at=message.created_at,
        updated_at=message.updated_at
    )
    
    return BaseResponse(
        code=1000,
        detail="通知消息创建成功",
        data=profile
    )


@router.get("/message/notice/{message_id}", response_model=BaseResponse[NoticeMessageProfile])
async def get_notice_message_detail(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("message:read"))
):
    """获取通知消息详情"""
    message_service = NoticeMessageService(db)
    message = message_service.get_by_id(message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    profile = NoticeMessageProfile(
        id=message.id,
        title=message.title,
        content=message.content,
        message_type=message.message_type,
        level=message.level,
        target_type=message.target_type,
        target_id=message.target_id,
        is_published=message.is_published,
        start_time=message.start_time,
        end_time=message.end_time,
        sender_id=message.sender_id,
        sender_name=message.sender.nickname if message.sender else None,
        publish_time=message.publish_time,
        read_count=message.read_count,
        total_count=message.total_count,
        created_at=message.created_at,
        updated_at=message.updated_at
    )
    
    return BaseResponse(
        code=1000,
        detail="success",
        data=profile
    )


@router.put("/message/notice/{message_id}", response_model=BaseResponse[NoticeMessageProfile])
async def update_notice_message(
    message_id: int,
    message_data: NoticeMessageUpdate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("message:update"))
):
    """更新通知消息"""
    message_service = NoticeMessageService(db)
    
    update_dict = message_data.dict(exclude_unset=True)
    updated_message = message_service.update_message(message_id, update_dict)
    
    if not updated_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    profile = NoticeMessageProfile(
        id=updated_message.id,
        title=updated_message.title,
        content=updated_message.content,
        message_type=updated_message.message_type,
        level=updated_message.level,
        target_type=updated_message.target_type,
        target_id=updated_message.target_id,
        is_published=updated_message.is_published,
        start_time=updated_message.start_time,
        end_time=updated_message.end_time,
        sender_id=updated_message.sender_id,
        sender_name=updated_message.sender.nickname if updated_message.sender else None,
        publish_time=updated_message.publish_time,
        read_count=updated_message.read_count,
        total_count=updated_message.total_count,
        created_at=updated_message.created_at,
        updated_at=updated_message.updated_at
    )
    
    return BaseResponse(
        code=1000,
        detail="通知消息更新成功",
        data=profile
    )


@router.delete("/message/notice/{message_id}", response_model=BaseResponse[None])
async def delete_notice_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("message:delete"))
):
    """删除通知消息"""
    message_service = NoticeMessageService(db)
    success = message_service.delete_message(message_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    return BaseResponse(
        code=1000,
        detail="通知消息删除成功",
        data=None
    )


@router.post("/message/notice/{message_id}/publish", response_model=BaseResponse[None])
async def publish_notice_message(
    message_id: int,
    publish_data: NoticeMessagePublish,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("message:publish"))
):
    """发布通知消息"""
    message_service = NoticeMessageService(db)
    success = message_service.publish_message(message_id, publish_data.publish_time)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    # 获取消息详情并通过WebSocket推送
    message = message_service.get_by_id(message_id)
    if message:
        notification = NotificationWebSocketMessage(
            data={
                "id": message.id,
                "title": message.title,
                "content": message.content[:100] + "..." if len(message.content) > 100 else message.content,
                "message_type": message.message_type,
                "level": message.level,
                "created_at": message.created_at.isoformat()
            }
        )
        await manager.broadcast(notification.json())
    
    return BaseResponse(
        code=1000,
        detail="消息发布成功",
        data=None
    )


@router.post("/message/notice/batch-action", response_model=BaseResponse[dict])
async def batch_action_notice_messages(
    request: NoticeMessageBatchAction,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("message:update"))
):
    """批量操作通知消息"""
    message_service = NoticeMessageService(db)
    result = message_service.batch_action(request.message_ids, request.action)
    
    return BaseResponse(
        code=1000,
        detail=f"批量操作完成，成功：{result['success_count']}，失败：{result['failed_count']}",
        data=result
    )


# 用户消息接口
@router.get("/user/notice", response_model=ListResponse[List[NoticeUserReadProfile]])
async def get_user_notice_list(
    params: NoticeUserReadListParams = Depends(),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取当前用户通知列表"""
    message_service = NoticeMessageService(db)
    
    filters = {}
    if params.is_read is not None:
        filters['is_read'] = params.is_read
    if params.message_type:
        filters['message_type'] = params.message_type
    if params.level:
        filters['level'] = params.level
    
    result = message_service.get_user_messages(current_user.id, params, filters)
    
    # 转换为响应格式
    user_read_profiles = []
    for user_read in result['results']:
        profile = NoticeUserReadProfile(
            id=user_read.id,
            user_id=user_read.user_id,
            message_id=user_read.message_id,
            is_read=user_read.is_read,
            read_time=user_read.read_time,
            message_title=user_read.message.title,
            message_type=user_read.message.message_type,
            message_level=user_read.message.level,
            created_at=user_read.created_at,
            updated_at=user_read.updated_at
        )
        user_read_profiles.append(profile)
    
    return ListResponse(
        code=1000,
        detail="success",
        data={
            "results": user_read_profiles,
            "total": result['total'],
            "page": result['page'],
            "size": result['size'],
            "pages": result['pages']
        }
    )


@router.get("/user/notice/stats", response_model=UserNoticeStatsResponse)
async def get_user_notice_stats(
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取用户通知统计"""
    message_service = NoticeMessageService(db)
    stats = message_service.get_user_notice_stats(current_user.id)
    
    return UserNoticeStatsResponse(
        code=1000,
        detail="success",
        data=stats
    )


@router.post("/user/notice/mark-read", response_model=BaseResponse[dict])
async def mark_notices_as_read(
    request: MarkReadRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """标记消息为已读"""
    read_service = NoticeUserReadService(db)
    updated_count = read_service.mark_as_read(current_user.id, request.message_ids)
    
    return BaseResponse(
        code=1000,
        detail=f"已标记 {updated_count} 条消息为已读",
        data={"updated_count": updated_count}
    )


@router.post("/user/notice/mark-all-read", response_model=BaseResponse[dict])
async def mark_all_notices_as_read(
    request: MarkAllReadRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """标记全部消息为已读"""
    read_service = NoticeUserReadService(db)
    updated_count = read_service.mark_all_as_read(current_user.id, request.message_type)
    
    return BaseResponse(
        code=1000,
        detail=f"已标记 {updated_count} 条消息为已读",
        data={"updated_count": updated_count}
    )


@router.get("/user/notice/unread-count", response_model=BaseResponse[int])
async def get_unread_notice_count(
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取未读消息数量"""
    read_service = NoticeUserReadService(db)
    unread_count = read_service.get_unread_count(current_user.id)
    
    return BaseResponse(
        code=1000,
        detail="success",
        data=unread_count
    )


# 消息推送接口
@router.post("/message/push", response_model=MessagePushResponse)
async def push_message(
    request: MessagePushRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("message:push"))
):
    """推送消息"""
    push_service = MessagePushService(db)
    
    try:
        result = push_service.push_to_users(
            title=request.title,
            content=request.content,
            user_ids=request.target_users,
            message_type=request.message_type,
            level=request.level,
            push_immediately=request.push_immediately
        )
        
        # 如果立即推送，通过WebSocket发送
        if request.push_immediately:
            notification = NotificationWebSocketMessage(
                data={
                    "id": result['message_id'],
                    "title": request.title,
                    "content": request.content[:100] + "..." if len(request.content) > 100 else request.content,
                    "message_type": request.message_type,
                    "level": request.level
                }
            )
            
            # 发送给指定用户
            for user_id in request.target_users:
                await manager.send_personal_message(notification.json(), user_id)
        
        return MessagePushResponse(
            code=1000,
            detail="消息推送成功",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# 消息统计接口
@router.get("/message/statistics", response_model=MessageStatisticsResponse)
async def get_message_statistics(
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("message:read"))
):
    """获取消息统计信息"""
    message_service = NoticeMessageService(db)
    statistics = message_service.get_message_statistics()
    
    return MessageStatisticsResponse(
        code=1000,
        detail="success",
        data=statistics
    )


# WebSocket接口
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket连接端点"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # 这里可以处理客户端发送的消息
            logger.info(f"Received message from user {user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)