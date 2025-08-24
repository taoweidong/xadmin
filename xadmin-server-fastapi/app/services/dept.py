"""
部门管理服务
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.models.user import DeptInfo
from app.schemas.base import PaginationParams
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DeptService:
    """部门服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, dept_id: int) -> Optional[DeptInfo]:
        """根据ID获取部门"""
        return self.db.query(DeptInfo).options(
            joinedload(DeptInfo.parent),
            joinedload(DeptInfo.children),
            joinedload(DeptInfo.users)
        ).filter(DeptInfo.id == dept_id, DeptInfo.is_deleted == False).first()
    
    def get_by_code(self, code: str) -> Optional[DeptInfo]:
        """根据编码获取部门"""
        return self.db.query(DeptInfo).filter(
            DeptInfo.code == code,
            DeptInfo.is_deleted == False
        ).first()
    
    def create_dept(self, dept_data: dict) -> DeptInfo:
        """创建部门"""
        # 处理字段名映射
        mapped_data = {}
        field_mapping = {
            'rank': 'sort',
            'description': 'description'
        }
        
        for key, value in dept_data.items():
            mapped_key = field_mapping.get(key, key)
            mapped_data[mapped_key] = value
            
        # 确保sort字段有默认值
        if 'sort' not in mapped_data:
            mapped_data['sort'] = 99
            
        dept = DeptInfo(**mapped_data)
        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)
        return dept
    
    def update_dept(self, dept_id: int, dept_data: dict) -> Optional[DeptInfo]:
        """更新部门"""
        dept = self.get_by_id(dept_id)
        if not dept:
            return None
        
        # 处理字段名映射
        field_mapping = {
            'rank': 'sort'
        }
        
        for field, value in dept_data.items():
            mapped_field = field_mapping.get(field, field)
            if hasattr(dept, mapped_field):
                setattr(dept, mapped_field, value)
        
        dept.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(dept)
        return dept
    
    def delete_dept(self, dept_id: int) -> bool:
        """删除部门（软删除）"""
        dept = self.get_by_id(dept_id)
        if not dept:
            return False
        
        # 检查是否有子部门
        if dept.children:
            return False
        
        # 检查是否有用户
        if dept.users:
            return False
        
        dept.is_deleted = True
        dept.deleted_at = datetime.utcnow()
        dept.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_dept_list(self, params: PaginationParams, filters: dict = None) -> Dict[str, Any]:
        """获取部门列表"""
        query = self.db.query(DeptInfo).options(
            joinedload(DeptInfo.parent),
            joinedload(DeptInfo.users)
        ).filter(DeptInfo.is_deleted == False)
        
        # 应用过滤条件
        if filters:
            if 'search' in filters and filters['search']:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        DeptInfo.name.like(search_term),
                        DeptInfo.code.like(search_term),
                        DeptInfo.description.like(search_term),
                        DeptInfo.leader.like(search_term)
                    )
                )
            
            filter_mappings = {
                'is_active': DeptInfo.is_active,
                'code': DeptInfo.code,
                'mode_type': DeptInfo.mode_type,
                'auto_bind': DeptInfo.auto_bind,
                'name': DeptInfo.name,
                'description': DeptInfo.description,
                'pk': DeptInfo.id
            }
            
            for filter_key, filter_value in filters.items():
                if filter_key in filter_mappings and filter_value is not None:
                    query = query.filter(filter_mappings[filter_key] == filter_value)
        
        # 应用排序
        if params.ordering:
            if params.ordering.startswith('-'):
                field = params.ordering[1:]
                # 处理字段名映射
                if field == 'rank':
                    field = 'sort'
                query = query.order_by(getattr(DeptInfo, field).desc())
            else:
                field = params.ordering
                # 处理字段名映射
                if field == 'rank':
                    field = 'sort'
                query = query.order_by(getattr(DeptInfo, field))
        else:
            query = query.order_by(DeptInfo.sort.asc(), DeptInfo.created_at.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        depts = query.offset(offset).limit(params.size).all()
        
        return {
            'results': depts,
            'total': total,
            'page': params.page,
            'size': params.size,
            'pages': (total + params.size - 1) // params.size
        }
    
    def get_dept_tree(self, parent_id: int = None) -> List[DeptInfo]:
        """获取部门树"""
        query = self.db.query(DeptInfo).filter(
            DeptInfo.is_deleted == False,
            DeptInfo.is_active == True
        )
        
        if parent_id is None:
            query = query.filter(DeptInfo.parent_id.is_(None))
        else:
            query = query.filter(DeptInfo.parent_id == parent_id)
        
        return query.order_by(DeptInfo.sort.asc()).all()
    
    def build_dept_tree(self, parent_id: int = None) -> List[Dict[str, Any]]:
        """构建部门树结构"""
        def build_children(dept_id: int = None) -> List[Dict[str, Any]]:
            children = self.get_dept_tree(dept_id)
            result = []
            
            for dept in children:
                dept_dict = {
                    'id': dept.id,
                    'name': dept.name,
                    'code': dept.code,
                    'parent_id': dept.parent_id,
                    'description': dept.description,
                    'is_active': dept.is_active,
                    'sort': dept.sort,
                    'mode_type': dept.mode_type,
                    'auto_bind': dept.auto_bind,
                    'leader': dept.leader,
                    'phone': dept.phone,
                    'email': dept.email,
                    'created_at': dept.created_at,
                    'updated_at': dept.updated_at,
                    'user_count': len(dept.users) if dept.users else 0,
                    'children': build_children(dept.id)
                }
                result.append(dept_dict)
            
            return result
        
        return build_children(parent_id)
    
    def get_dept_children_ids(self, dept_id: int) -> List[int]:
        """获取部门及其所有子部门ID"""
        def get_children_recursive(parent_id: int) -> List[int]:
            children = self.db.query(DeptInfo).filter(
                DeptInfo.parent_id == parent_id,
                DeptInfo.is_deleted == False
            ).all()
            
            result = [parent_id]
            for child in children:
                result.extend(get_children_recursive(child.id))
            
            return result
        
        return get_children_recursive(dept_id)
    
    def check_code_exists(self, code: str, exclude_id: int = None) -> bool:
        """检查部门编码是否存在"""
        query = self.db.query(DeptInfo).filter(
            DeptInfo.code == code,
            DeptInfo.is_deleted == False
        )
        if exclude_id:
            query = query.filter(DeptInfo.id != exclude_id)
        return query.first() is not None
    
    def check_can_delete(self, dept_id: int) -> tuple[bool, str]:
        """检查是否可以删除部门"""
        dept = self.get_by_id(dept_id)
        if not dept:
            return False, "部门不存在"
        
        # 检查是否有子部门
        if dept.children:
            return False, "该部门存在子部门，无法删除"
        
        # 检查是否有用户
        if dept.users:
            return False, "该部门存在用户，无法删除"
        
        return True, ""
    
    def check_parent_valid(self, dept_id: int, parent_id: int) -> bool:
        """检查父部门是否有效（避免循环引用）"""
        if dept_id == parent_id:
            return False
        
        # 检查parent_id是否是dept_id的子部门
        children_ids = self.get_dept_children_ids(dept_id)
        return parent_id not in children_ids
    
    def get_all_active_depts(self) -> List[DeptInfo]:
        """获取所有活跃部门"""
        return self.db.query(DeptInfo).filter(
            DeptInfo.is_active == True,
            DeptInfo.is_deleted == False
        ).order_by(DeptInfo.sort.asc()).all()
    
    def search_depts(self, search: str, limit: int = 20) -> List[DeptInfo]:
        """搜索部门"""
        search_term = f"%{search}%"
        return self.db.query(DeptInfo).options(
            joinedload(DeptInfo.parent)
        ).filter(
            DeptInfo.is_deleted == False,
            or_(
                DeptInfo.name.like(search_term),
                DeptInfo.code.like(search_term)
            )
        ).order_by(DeptInfo.sort.asc()).limit(limit).all()