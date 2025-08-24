"""
角色管理服务
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.models.user import UserRole, DataPermission
from app.models.system import MenuInfo
from app.schemas.base import PaginationParams
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RoleService:
    """角色服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, role_id: int) -> Optional[UserRole]:
        """根据ID获取角色"""
        return self.db.query(UserRole).options(
            joinedload(UserRole.menus),
            joinedload(UserRole.permissions),
            joinedload(UserRole.users)
        ).filter(UserRole.id == role_id, UserRole.is_deleted == False).first()
    
    def get_by_code(self, code: str) -> Optional[UserRole]:
        """根据编码获取角色"""
        return self.db.query(UserRole).filter(
            UserRole.code == code, 
            UserRole.is_deleted == False
        ).first()
    
    def create_role(self, role_data: dict) -> UserRole:
        """创建角色"""
        role = UserRole(**role_data)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def update_role(self, role_id: int, role_data: dict) -> Optional[UserRole]:
        """更新角色"""
        role = self.get_by_id(role_id)
        if not role:
            return None
        
        for field, value in role_data.items():
            if hasattr(role, field):
                setattr(role, field, value)
        
        role.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def delete_role(self, role_id: int) -> bool:
        """删除角色（软删除）"""
        role = self.get_by_id(role_id)
        if not role:
            return False
        
        role.is_deleted = True
        role.deleted_at = datetime.utcnow()
        role.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_role_list(self, params: PaginationParams, filters: dict = None) -> Dict[str, Any]:
        """获取角色列表"""
        query = self.db.query(UserRole).options(
            joinedload(UserRole.users)
        ).filter(UserRole.is_deleted == False)
        
        # 应用过滤条件
        if filters:
            if 'search' in filters and filters['search']:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        UserRole.name.like(search_term),
                        UserRole.code.like(search_term),
                        UserRole.description.like(search_term)
                    )
                )
            
            if 'is_active' in filters:
                query = query.filter(UserRole.is_active == filters['is_active'])
        
        # 应用排序
        if params.ordering:
            if params.ordering.startswith('-'):
                field = params.ordering[1:]
                query = query.order_by(getattr(UserRole, field).desc())
            else:
                query = query.order_by(getattr(UserRole, params.ordering))
        else:
            query = query.order_by(UserRole.sort.asc(), UserRole.created_at.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        roles = query.offset(offset).limit(params.size).all()
        
        return {
            'results': roles,
            'total': total,
            'page': params.page,
            'size': params.size,
            'pages': (total + params.size - 1) // params.size
        }
    
    def assign_menus(self, role_id: int, menu_ids: List[int]) -> bool:
        """分配菜单"""
        role = self.get_by_id(role_id)
        if not role:
            return False
        
        menus = self.db.query(MenuInfo).filter(MenuInfo.id.in_(menu_ids)).all()
        role.menus = menus
        role.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def assign_permissions(self, role_id: int, permission_ids: List[int]) -> bool:
        """分配权限"""
        role = self.get_by_id(role_id)
        if not role:
            return False
        
        permissions = self.db.query(DataPermission).filter(DataPermission.id.in_(permission_ids)).all()
        role.permissions = permissions
        role.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_role_menus(self, role_id: int) -> List[MenuInfo]:
        """获取角色菜单"""
        role = self.get_by_id(role_id)
        if not role:
            return []
        return role.menus
    
    def get_role_permissions(self, role_id: int) -> List[DataPermission]:
        """获取角色权限"""
        role = self.get_by_id(role_id)
        if not role:
            return []
        return role.permissions
    
    def check_code_exists(self, code: str, exclude_id: int = None) -> bool:
        """检查角色编码是否存在"""
        query = self.db.query(UserRole).filter(
            UserRole.code == code,
            UserRole.is_deleted == False
        )
        if exclude_id:
            query = query.filter(UserRole.id != exclude_id)
        return query.first() is not None
    
    def check_name_exists(self, name: str, exclude_id: int = None) -> bool:
        """检查角色名称是否存在"""
        query = self.db.query(UserRole).filter(
            UserRole.name == name,
            UserRole.is_deleted == False
        )
        if exclude_id:
            query = query.filter(UserRole.id != exclude_id)
        return query.first() is not None
    
    def get_all_active_roles(self) -> List[UserRole]:
        """获取所有活跃角色"""
        return self.db.query(UserRole).filter(
            UserRole.is_active == True,
            UserRole.is_deleted == False
        ).order_by(UserRole.sort.asc()).all()
    
    def search_roles(self, search: str, limit: int = 20) -> List[UserRole]:
        """搜索角色"""
        search_term = f"%{search}%"
        return self.db.query(UserRole).filter(
            and_(
                UserRole.is_deleted == False,
                UserRole.is_active == True,
                or_(
                    UserRole.name.like(search_term),
                    UserRole.code.like(search_term)
                )
            )
        ).limit(limit).all()