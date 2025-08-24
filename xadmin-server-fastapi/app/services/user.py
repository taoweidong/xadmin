"""
用户服务层
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.models.user import UserInfo, UserRole, DeptInfo, DataPermission
from app.models.log import LoginLog, OperationLog
from app.core.security import get_password_hash, verify_password
from app.schemas.base import PaginationParams
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserService:
    """用户服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[UserInfo]:
        """根据ID获取用户"""
        return self.db.query(UserInfo).options(
            joinedload(UserInfo.roles),
            joinedload(UserInfo.dept),
            joinedload(UserInfo.permissions)
        ).filter(UserInfo.id == user_id, UserInfo.is_deleted == False).first()
    
    def get_by_username(self, username: str) -> Optional[UserInfo]:
        """根据用户名获取用户"""
        return self.db.query(UserInfo).options(
            joinedload(UserInfo.roles),
            joinedload(UserInfo.dept),
            joinedload(UserInfo.permissions)
        ).filter(UserInfo.username == username, UserInfo.is_deleted == False).first()
    
    def get_by_email(self, email: str) -> Optional[UserInfo]:
        """根据邮箱获取用户"""
        return self.db.query(UserInfo).options(
            joinedload(UserInfo.roles),
            joinedload(UserInfo.dept),
            joinedload(UserInfo.permissions)
        ).filter(UserInfo.email == email, UserInfo.is_deleted == False).first()
    
    def get_by_phone(self, phone: str) -> Optional[UserInfo]:
        """根据手机号获取用户"""
        return self.db.query(UserInfo).options(
            joinedload(UserInfo.roles),
            joinedload(UserInfo.dept),
            joinedload(UserInfo.permissions)
        ).filter(UserInfo.phone == phone, UserInfo.is_deleted == False).first()
    
    def authenticate(self, username: str, password: str) -> Optional[UserInfo]:
        """用户认证"""
        user = self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
    def create_user(self, user_data: dict) -> UserInfo:
        """创建用户"""
        # 加密密码
        if 'password' in user_data:
            user_data['password'] = get_password_hash(user_data['password'])
        
        user = UserInfo(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user(self, user_id: int, user_data: dict) -> Optional[UserInfo]:
        """更新用户"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        # 加密密码
        if 'password' in user_data:
            user_data['password'] = get_password_hash(user_data['password'])
        
        for field, value in user_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户（软删除）"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_user_list(self, params: PaginationParams, filters: dict = None) -> Dict[str, Any]:
        """获取用户列表"""
        query = self.db.query(UserInfo).options(
            joinedload(UserInfo.roles),
            joinedload(UserInfo.dept)
        ).filter(UserInfo.is_deleted == False)
        
        # 应用过滤条件
        if filters:
            if 'search' in filters and filters['search']:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        UserInfo.username.like(search_term),
                        UserInfo.nickname.like(search_term),
                        UserInfo.email.like(search_term),
                        UserInfo.phone.like(search_term)
                    )
                )
            
            if 'is_active' in filters:
                query = query.filter(UserInfo.is_active == filters['is_active'])
            
            if 'dept_id' in filters and filters['dept_id']:
                query = query.filter(UserInfo.dept_id == filters['dept_id'])
            
            if 'role_id' in filters and filters['role_id']:
                query = query.join(UserInfo.roles).filter(UserRole.id == filters['role_id'])
        
        # 应用排序
        if params.ordering:
            if params.ordering.startswith('-'):
                field = params.ordering[1:]
                query = query.order_by(getattr(UserInfo, field).desc())
            else:
                query = query.order_by(getattr(UserInfo, params.ordering))
        else:
            query = query.order_by(UserInfo.created_at.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        users = query.offset(offset).limit(params.size).all()
        
        return {
            'results': users,
            'total': total,
            'page': params.page,
            'size': params.size,
            'pages': (total + params.size - 1) // params.size
        }
    
    def update_last_login(self, user_id: int):
        """更新最后登录时间"""
        user = self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        if not verify_password(old_password, user.password):
            return False
        
        user.password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """重置密码"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def assign_roles(self, user_id: int, role_ids: List[int]) -> bool:
        """分配角色"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        roles = self.db.query(UserRole).filter(UserRole.id.in_(role_ids)).all()
        user.roles = roles
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def assign_permissions(self, user_id: int, permission_ids: List[int]) -> bool:
        """分配权限"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        permissions = self.db.query(DataPermission).filter(DataPermission.id.in_(permission_ids)).all()
        user.permissions = permissions
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """获取用户权限列表"""
        user = self.get_by_id(user_id)
        if not user:
            return []
        
        permissions = set()
        
        # 角色权限
        for role in user.roles:
            if role.is_active:
                for menu in role.menus:
                    if menu.permission:
                        permissions.add(menu.permission)
        
        # 直接权限
        for permission in user.permissions:
            if permission.is_active:
                permissions.add(permission.code)
        
        return list(permissions)
    
    def is_active_user(self, user: UserInfo) -> bool:
        """检查用户是否激活"""
        return user.is_active if user else False

    def check_username_exists(self, username: str, exclude_id: int = None) -> bool:
        """检查用户名是否存在"""
        query = self.db.query(UserInfo).filter(
            UserInfo.username == username,
            UserInfo.is_deleted == False
        )
        if exclude_id:
            query = query.filter(UserInfo.id != exclude_id)
        return query.first() is not None
    
    def check_email_exists(self, email: str, exclude_id: int = None) -> bool:
        """检查邮箱是否存在"""
        query = self.db.query(UserInfo).filter(
            UserInfo.email == email,
            UserInfo.is_deleted == False
        )
        if exclude_id:
            query = query.filter(UserInfo.id != exclude_id)
        return query.first() is not None
    
    def check_phone_exists(self, phone: str, exclude_id: int = None) -> bool:
        """检查手机号是否存在"""
        query = self.db.query(UserInfo).filter(
            UserInfo.phone == phone,
            UserInfo.is_deleted == False
        )
        if exclude_id:
            query = query.filter(UserInfo.id != exclude_id)
        return query.first() is not None


class LoginLogService:
    """登录日志服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_login_log(self, log_data: dict) -> LoginLog:
        """创建登录日志"""
        log = LoginLog(**log_data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def update_logout_time(self, log_id: int):
        """更新登出时间"""
        log = self.db.query(LoginLog).filter(LoginLog.id == log_id).first()
        if log:
            log.logout_time = datetime.utcnow()
            if log.login_time:
                log.duration = int((log.logout_time - log.login_time).total_seconds())
            self.db.commit()
    
    def get_user_login_logs(self, user_id: int, params: PaginationParams) -> Dict[str, Any]:
        """获取用户登录日志"""
        query = self.db.query(LoginLog).filter(LoginLog.user_id == user_id)
        
        # 应用排序
        query = query.order_by(LoginLog.login_time.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        logs = query.offset(offset).limit(params.size).all()
        
        return {
            'results': logs,
            'total': total,
            'page': params.page,
            'size': params.size,
            'pages': (total + params.size - 1) // params.size
        }