"""
菜单管理服务
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.models.system import MenuInfo
from app.models.user import DeptInfo
from app.schemas.base import PaginationParams
from app.schemas.menu import MenuCreate, MenuUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MenuService:
    """菜单服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, menu_id: int) -> Optional[MenuInfo]:
        """根据ID获取菜单"""
        return self.db.query(MenuInfo).options(
            joinedload(MenuInfo.parent),
            joinedload(MenuInfo.meta),
            joinedload(MenuInfo.model)
        ).filter(MenuInfo.id == menu_id, MenuInfo.is_deleted == False).first()
    
    def get_by_name(self, name: str) -> Optional[MenuInfo]:
        """根据名称获取菜单"""
        return self.db.query(MenuInfo).filter(
            MenuInfo.name == name,
            MenuInfo.is_deleted == False
        ).first()
    
    def create_menu(self, menu_data: MenuCreate) -> MenuInfo:
        """创建菜单"""
        # 创建菜单元数据
        meta_data = menu_data.meta.model_dump()
        from app.models.system import MenuMeta
        menu_meta = MenuMeta(**meta_data)
        self.db.add(menu_meta)
        self.db.flush()  # 获取meta的ID
        
        # 创建菜单
        menu_dict = menu_data.model_dump()
        menu_dict.pop('meta')  # 移除meta字段
        menu_dict['meta_id'] = menu_meta.id  # 关联菜单元数据
        menu_dict['sort'] = menu_dict.get('rank', 9999)  # 转换字段名
        menu = MenuInfo(**menu_dict)
        self.db.add(menu)
        self.db.commit()
        self.db.refresh(menu)
        return menu
    
    def update_menu(self, menu_id: int, menu_data: MenuUpdate) -> Optional[MenuInfo]:
        """更新菜单"""
        menu = self.get_by_id(menu_id)
        if not menu:
            return None
        
        # 更新菜单元数据
        if menu_data.meta and menu.meta:
            meta_data = menu_data.meta.model_dump(exclude_unset=True)
            for field, value in meta_data.items():
                if hasattr(menu.meta, field):
                    setattr(menu.meta, field, value)
            menu.meta.updated_at = datetime.utcnow()
        
        # 更新菜单数据
        menu_dict = menu_data.model_dump(exclude_unset=True)
        menu_dict.pop('meta', None)  # 移除meta字段
        
        # 转换字段名
        if 'rank' in menu_dict:
            menu_dict['sort'] = menu_dict.pop('rank')
            
        for field, value in menu_dict.items():
            if hasattr(menu, field):
                setattr(menu, field, value)
        
        menu.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(menu)
        return menu
    
    def delete_menu(self, menu_id: int) -> bool:
        """删除菜单（软删除）"""
        menu = self.get_by_id(menu_id)
        if not menu:
            return False
        
        # 检查是否有子菜单
        children_count = self.db.query(MenuInfo).filter(
            MenuInfo.parent_id == menu_id,
            MenuInfo.is_deleted == False
        ).count()
        
        if children_count > 0:
            return False
        
        menu.is_deleted = True
        menu.deleted_at = datetime.utcnow()
        menu.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_menu_list(self, params: PaginationParams, filters: dict = None) -> Dict[str, Any]:
        """获取菜单列表"""
        query = self.db.query(MenuInfo).options(
            joinedload(MenuInfo.parent),
            joinedload(MenuInfo.meta),
            joinedload(MenuInfo.model)
        ).filter(MenuInfo.is_deleted == False)
        
        # 应用过滤条件
        if filters:
            if 'search' in filters and filters['search']:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        MenuInfo.name.like(search_term),
                        MenuInfo.path.like(search_term),
                        MenuInfo.component.like(search_term)
                    )
                )
            
            # 应用其他过滤条件
            filter_mappings = {
                'name': MenuInfo.name,
                'path': MenuInfo.path,
                'component': MenuInfo.component
            }
            
            for filter_key, filter_value in filters.items():
                if filter_key in filter_mappings and filter_value is not None:
                    query = query.filter(filter_mappings[filter_key] == filter_value)
        
        # 应用排序
        if params.ordering:
            if params.ordering.startswith('-'):
                field = params.ordering[1:]
                # 转换字段名
                if field == 'rank':
                    field = 'sort'
                query = query.order_by(getattr(MenuInfo, field).desc())
            else:
                field = params.ordering
                # 转换字段名
                if field == 'rank':
                    field = 'sort'
                query = query.order_by(getattr(MenuInfo, field))
        else:
            query = query.order_by(MenuInfo.sort.asc(), MenuInfo.created_at.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        menus = query.offset(offset).limit(params.size).all()
        
        return {
            'results': menus,
            'total': total,
            'page': params.page,
            'size': params.size,
            'pages': (total + params.size - 1) // params.size
        }
    
    def check_name_exists(self, name: str, exclude_id: int = None) -> bool:
        """检查菜单名称是否存在"""
        query = self.db.query(MenuInfo).filter(
            MenuInfo.name == name,
            MenuInfo.is_deleted == False
        )
        if exclude_id:
            query = query.filter(MenuInfo.id != exclude_id)
        return query.first() is not None
    
    def check_can_delete(self, menu_id: int) -> tuple[bool, str]:
        """检查是否可以删除菜单"""
        menu = self.get_by_id(menu_id)
        if not menu:
            return False, "菜单不存在"
        
        # 检查是否有子菜单
        children_count = self.db.query(MenuInfo).filter(
            MenuInfo.parent_id == menu_id,
            MenuInfo.is_deleted == False
        ).count()
        
        if children_count > 0:
            return False, "该菜单存在子菜单，无法删除"
        
        return True, ""
    