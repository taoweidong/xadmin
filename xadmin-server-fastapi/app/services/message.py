"""
消息通知服务
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.models.log import NoticeMessage, NoticeUserRead
from app.models.user import UserInfo, UserRole, DeptInfo
from app.schemas.base import PaginationParams
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class NoticeMessageService:
    """通知消息服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, message_id: int) -> Optional[NoticeMessage]:
        """根据ID获取通知消息"""
        return self.db.query(NoticeMessage).options(
            joinedload(NoticeMessage.sender)
        ).filter(
            NoticeMessage.id == message_id,
            NoticeMessage.is_deleted == False
        ).first()
    
    def create_message(self, message_data: dict) -> NoticeMessage:
        """创建通知消息"""
        message = NoticeMessage(**message_data)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def update_message(self, message_id: int, message_data: dict) -> Optional[NoticeMessage]:
        """更新通知消息"""
        message = self.get_by_id(message_id)
        if not message:
            return None
        
        for field, value in message_data.items():
            if hasattr(message, field):
                setattr(message, field, value)
        
        message.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def delete_message(self, message_id: int) -> bool:
        """删除通知消息（软删除）"""
        message = self.get_by_id(message_id)
        if not message:
            return False
        
        message.is_deleted = True
        message.deleted_at = datetime.utcnow()
        message.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_message_list(self, params: PaginationParams, filters: dict = None) -> Dict[str, Any]:
        """获取通知消息列表"""
        query = self.db.query(NoticeMessage).options(
            joinedload(NoticeMessage.sender)
        ).filter(NoticeMessage.is_deleted == False)
        
        # 应用过滤条件
        if filters:
            if 'search' in filters and filters['search']:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        NoticeMessage.title.like(search_term),
                        NoticeMessage.content.like(search_term)
                    )
                )
            
            if 'message_type' in filters and filters['message_type']:
                query = query.filter(NoticeMessage.message_type == filters['message_type'])
            
            if 'level' in filters and filters['level']:
                query = query.filter(NoticeMessage.level == filters['level'])
            
            if 'target_type' in filters and filters['target_type']:
                query = query.filter(NoticeMessage.target_type == filters['target_type'])
            
            if 'is_published' in filters:
                query = query.filter(NoticeMessage.is_published == filters['is_published'])
            
            if 'sender_id' in filters and filters['sender_id']:
                query = query.filter(NoticeMessage.sender_id == filters['sender_id'])
        
        # 应用排序
        if params.ordering:
            if params.ordering.startswith('-'):
                field = params.ordering[1:]
                query = query.order_by(getattr(NoticeMessage, field).desc())
            else:
                query = query.order_by(getattr(NoticeMessage, params.ordering))
        else:
            query = query.order_by(NoticeMessage.created_at.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        messages = query.offset(offset).limit(params.size).all()
        
        return {
            'results': messages,
            'total': total,
            'page': params.page,
            'size': params.size,
            'pages': (total + params.size - 1) // params.size
        }
    
    def publish_message(self, message_id: int, publish_time: datetime = None) -> bool:
        """发布通知消息"""
        message = self.get_by_id(message_id)
        if not message:
            return False
        
        message.is_published = True
        message.publish_time = publish_time or datetime.utcnow()
        message.updated_at = datetime.utcnow()
        
        # 计算目标用户并创建阅读记录
        target_users = self._get_target_users(message)
        message.total_count = len(target_users)
        
        self.db.commit()
        
        # 创建用户阅读记录
        self._create_user_read_records(message_id, target_users)
        
        return True
    
    def unpublish_message(self, message_id: int) -> bool:
        """取消发布通知消息"""
        message = self.get_by_id(message_id)
        if not message:
            return False
        
        message.is_published = False
        message.publish_time = None
        message.updated_at = datetime.utcnow()
        self.db.commit()
        
        # 删除相关的阅读记录
        self.db.query(NoticeUserRead).filter(
            NoticeUserRead.message_id == message_id
        ).delete()
        self.db.commit()
        
        return True
    
    def batch_action(self, message_ids: List[int], action: str) -> Dict[str, int]:
        """批量操作消息"""
        success_count = 0
        failed_count = 0
        
        for message_id in message_ids:
            try:
                if action == "publish":
                    if self.publish_message(message_id):
                        success_count += 1
                    else:
                        failed_count += 1
                elif action == "unpublish":
                    if self.unpublish_message(message_id):
                        success_count += 1
                    else:
                        failed_count += 1
                elif action == "delete":
                    if self.delete_message(message_id):
                        success_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Batch action failed for message {message_id}: {e}")
                failed_count += 1
        
        return {
            "success_count": success_count,
            "failed_count": failed_count
        }
    
    def get_user_messages(self, user_id: int, params: PaginationParams, filters: dict = None) -> Dict[str, Any]:
        """获取用户消息"""
        query = self.db.query(NoticeUserRead).options(
            joinedload(NoticeUserRead.message)
        ).filter(
            NoticeUserRead.user_id == user_id,
            NoticeMessage.is_published == True,
            NoticeMessage.is_deleted == False
        ).join(NoticeMessage)
        
        # 应用过滤条件
        if filters:
            if 'is_read' in filters:
                query = query.filter(NoticeUserRead.is_read == filters['is_read'])
            
            if 'message_type' in filters and filters['message_type']:
                query = query.filter(NoticeMessage.message_type == filters['message_type'])
            
            if 'level' in filters and filters['level']:
                query = query.filter(NoticeMessage.level == filters['level'])
        
        # 应用排序
        query = query.order_by(NoticeUserRead.created_at.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        user_reads = query.offset(offset).limit(params.size).all()
        
        return {
            'results': user_reads,
            'total': total,
            'page': params.page,
            'size': params.size,
            'pages': (total + params.size - 1) // params.size
        }
    
    def get_user_notice_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户通知统计"""
        # 总消息数
        total_count = self.db.query(NoticeUserRead).filter(
            NoticeUserRead.user_id == user_id
        ).count()
        
        # 未读消息数
        unread_count = self.db.query(NoticeUserRead).filter(
            NoticeUserRead.user_id == user_id,
            NoticeUserRead.is_read == False
        ).count()
        
        # 已读消息数
        read_count = total_count - unread_count
        
        # 按类型统计
        type_stats = self.db.query(
            NoticeMessage.message_type,
            func.count(NoticeUserRead.id).label('count')
        ).join(NoticeUserRead).filter(
            NoticeUserRead.user_id == user_id
        ).group_by(NoticeMessage.message_type).all()
        
        # 按优先级统计
        level_stats = self.db.query(
            NoticeMessage.level,
            func.count(NoticeUserRead.id).label('count')
        ).join(NoticeUserRead).filter(
            NoticeUserRead.user_id == user_id
        ).group_by(NoticeMessage.level).all()
        
        type_names = {1: "系统通知", 2: "公告", 3: "私信", 4: "提醒"}
        level_names = {1: "低", 2: "中", 3: "高", 4: "紧急"}
        
        return {
            'total_count': total_count,
            'unread_count': unread_count,
            'read_count': read_count,
            'type_stats': {type_names.get(stat.message_type, str(stat.message_type)): stat.count for stat in type_stats},
            'level_stats': {level_names.get(stat.level, str(stat.level)): stat.count for stat in level_stats}
        }
    
    def get_message_statistics(self) -> Dict[str, Any]:
        """获取消息统计信息"""
        # 总消息数
        total_messages = self.db.query(NoticeMessage).filter(
            NoticeMessage.is_deleted == False
        ).count()
        
        # 已发布消息数
        published_messages = self.db.query(NoticeMessage).filter(
            NoticeMessage.is_deleted == False,
            NoticeMessage.is_published == True
        ).count()
        
        # 草稿消息数
        draft_messages = total_messages - published_messages
        
        # 总接收者数
        total_recipients = self.db.query(func.sum(NoticeMessage.total_count)).filter(
            NoticeMessage.is_deleted == False,
            NoticeMessage.is_published == True
        ).scalar() or 0
        
        # 总阅读数
        total_reads = self.db.query(NoticeUserRead).filter(
            NoticeUserRead.is_read == True
        ).count()
        
        # 阅读率
        read_rate = (total_reads / total_recipients * 100) if total_recipients > 0 else 0
        
        # 类型分布
        type_distribution = self.db.query(
            NoticeMessage.message_type,
            func.count(NoticeMessage.id).label('count')
        ).filter(
            NoticeMessage.is_deleted == False
        ).group_by(NoticeMessage.message_type).all()
        
        # 优先级分布
        level_distribution = self.db.query(
            NoticeMessage.level,
            func.count(NoticeMessage.id).label('count')
        ).filter(
            NoticeMessage.is_deleted == False
        ).group_by(NoticeMessage.level).all()
        
        # 每日统计（最近7天）
        from sqlalchemy import text
        daily_stats = self.db.execute(text("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM notice_message 
            WHERE is_deleted = false 
            AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)).fetchall()
        
        type_names = {1: "系统通知", 2: "公告", 3: "私信", 4: "提醒"}
        level_names = {1: "低", 2: "中", 3: "高", 4: "紧急"}
        
        return {
            'total_messages': total_messages,
            'published_messages': published_messages,
            'draft_messages': draft_messages,
            'total_recipients': total_recipients,
            'total_reads': total_reads,
            'read_rate': round(read_rate, 2),
            'type_distribution': {type_names.get(stat.message_type, str(stat.message_type)): stat.count for stat in type_distribution},
            'level_distribution': {level_names.get(stat.level, str(stat.level)): stat.count for stat in level_distribution},
            'daily_stats': [{'date': str(stat.date), 'count': stat.count} for stat in daily_stats]
        }
    
    def _get_target_users(self, message: NoticeMessage) -> List[int]:
        """获取目标用户列表"""
        if message.target_type == "all":
            # 全体用户
            users = self.db.query(UserInfo.id).filter(
                UserInfo.is_active == True,
                UserInfo.is_deleted == False
            ).all()
            return [user.id for user in users]
        
        elif message.target_type == "role":
            # 指定角色
            if message.target_id:
                role_ids = [int(id.strip()) for id in message.target_id.split(',')]
                users = self.db.query(UserInfo.id).join(UserInfo.roles).filter(
                    UserRole.id.in_(role_ids),
                    UserInfo.is_active == True,
                    UserInfo.is_deleted == False
                ).all()
                return [user.id for user in users]
        
        elif message.target_type == "dept":
            # 指定部门
            if message.target_id:
                dept_ids = [int(id.strip()) for id in message.target_id.split(',')]
                users = self.db.query(UserInfo.id).filter(
                    UserInfo.dept_id.in_(dept_ids),
                    UserInfo.is_active == True,
                    UserInfo.is_deleted == False
                ).all()
                return [user.id for user in users]
        
        elif message.target_type == "user":
            # 指定用户
            if message.target_id:
                user_ids = [int(id.strip()) for id in message.target_id.split(',')]
                users = self.db.query(UserInfo.id).filter(
                    UserInfo.id.in_(user_ids),
                    UserInfo.is_active == True,
                    UserInfo.is_deleted == False
                ).all()
                return [user.id for user in users]
        
        return []
    
    def _create_user_read_records(self, message_id: int, user_ids: List[int]):
        """创建用户阅读记录"""
        read_records = []
        for user_id in user_ids:
            read_record = NoticeUserRead(
                user_id=user_id,
                message_id=message_id,
                is_read=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            read_records.append(read_record)
        
        if read_records:
            self.db.add_all(read_records)
            self.db.commit()


class NoticeUserReadService:
    """用户消息阅读记录服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def mark_as_read(self, user_id: int, message_ids: List[int]) -> int:
        """标记消息为已读"""
        updated_count = self.db.query(NoticeUserRead).filter(
            NoticeUserRead.user_id == user_id,
            NoticeUserRead.message_id.in_(message_ids),
            NoticeUserRead.is_read == False
        ).update({
            'is_read': True,
            'read_time': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }, synchronize_session=False)
        
        self.db.commit()
        
        # 更新消息的已读计数
        self._update_message_read_count(message_ids)
        
        return updated_count
    
    def mark_all_as_read(self, user_id: int, message_type: int = None) -> int:
        """标记全部消息为已读"""
        query = self.db.query(NoticeUserRead).filter(
            NoticeUserRead.user_id == user_id,
            NoticeUserRead.is_read == False
        )
        
        if message_type:
            query = query.join(NoticeMessage).filter(
                NoticeMessage.message_type == message_type
            )
        
        updated_count = query.update({
            'is_read': True,
            'read_time': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }, synchronize_session=False)
        
        self.db.commit()
        
        return updated_count
    
    def get_unread_count(self, user_id: int) -> int:
        """获取未读消息数量"""
        return self.db.query(NoticeUserRead).filter(
            NoticeUserRead.user_id == user_id,
            NoticeUserRead.is_read == False
        ).count()
    
    def _update_message_read_count(self, message_ids: List[int]):
        """更新消息的已读计数"""
        for message_id in message_ids:
            read_count = self.db.query(NoticeUserRead).filter(
                NoticeUserRead.message_id == message_id,
                NoticeUserRead.is_read == True
            ).count()
            
            self.db.query(NoticeMessage).filter(
                NoticeMessage.id == message_id
            ).update({
                'read_count': read_count,
                'updated_at': datetime.utcnow()
            })
        
        self.db.commit()


class MessagePushService:
    """消息推送服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.notice_service = NoticeMessageService(db)
    
    def push_to_users(
        self, 
        title: str, 
        content: str, 
        user_ids: List[int],
        message_type: int = 1,
        level: int = 2,
        push_immediately: bool = True
    ) -> Dict[str, Any]:
        """推送消息给指定用户"""
        try:
            # 创建消息
            message_data = {
                'title': title,
                'content': content,
                'message_type': message_type,
                'level': level,
                'target_type': 'user',
                'target_id': ','.join(map(str, user_ids)),
                'is_published': push_immediately,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            if push_immediately:
                message_data['publish_time'] = datetime.utcnow()
            
            message = self.notice_service.create_message(message_data)
            
            if push_immediately:
                # 立即发布
                self.notice_service.publish_message(message.id)
            
            return {
                'message_id': message.id,
                'target_users': user_ids,
                'push_time': message.publish_time,
                'status': 'published' if push_immediately else 'draft'
            }
            
        except Exception as e:
            logger.error(f"Failed to push message: {e}")
            raise ValueError(f"消息推送失败: {str(e)}")