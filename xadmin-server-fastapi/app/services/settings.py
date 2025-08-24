"""
设置管理服务
"""
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.system import SystemConfig, UserPersonalConfig
from app.schemas.base import PaginationParams
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class SystemConfigService:
    """系统配置服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, config_id: int) -> Optional[SystemConfig]:
        """根据ID获取系统配置"""
        return self.db.query(SystemConfig).filter(
            SystemConfig.id == config_id,
            SystemConfig.is_deleted == False
        ).first()
    
    def get_by_key(self, key: str) -> Optional[SystemConfig]:
        """根据键获取系统配置"""
        return self.db.query(SystemConfig).filter(
            SystemConfig.key == key,
            SystemConfig.is_deleted == False
        ).first()
    
    def create_config(self, config_data: dict) -> SystemConfig:
        """创建系统配置"""
        config = SystemConfig(**config_data)
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def update_config(self, config_id: int, config_data: dict) -> Optional[SystemConfig]:
        """更新系统配置"""
        config = self.get_by_id(config_id)
        if not config:
            return None
        
        for field, value in config_data.items():
            if hasattr(config, field):
                setattr(config, field, value)
        
        config.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def delete_config(self, config_id: int) -> bool:
        """删除系统配置（软删除）"""
        config = self.get_by_id(config_id)
        if not config:
            return False
        
        config.is_deleted = True
        config.deleted_at = datetime.utcnow()
        config.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_config_list(self, params: PaginationParams, filters: dict = None) -> Dict[str, Any]:
        """获取系统配置列表"""
        query = self.db.query(SystemConfig).filter(SystemConfig.is_deleted == False)
        
        # 应用过滤条件
        if filters:
            if 'search' in filters and filters['search']:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        SystemConfig.name.like(search_term),
                        SystemConfig.key.like(search_term),
                        SystemConfig.description.like(search_term)
                    )
                )
            
            if 'category' in filters and filters['category']:
                query = query.filter(SystemConfig.category == filters['category'])
            
            if 'is_active' in filters:
                query = query.filter(SystemConfig.is_active == filters['is_active'])
        
        # 应用排序
        if params.ordering:
            if params.ordering.startswith('-'):
                field = params.ordering[1:]
                query = query.order_by(getattr(SystemConfig, field).desc())
            else:
                query = query.order_by(getattr(SystemConfig, params.ordering))
        else:
            query = query.order_by(SystemConfig.category.asc(), SystemConfig.sort.asc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        configs = query.offset(offset).limit(params.size).all()
        
        return {
            'results': configs,
            'total': total,
            'page': params.page,
            'size': params.size,
            'pages': (total + params.size - 1) // params.size
        }
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        config = self.get_by_key(key)
        if not config or not config.is_active:
            return default
        
        return self._convert_value(config.value, config.config_type)
    
    def set_config_value(self, key: str, value: Any) -> bool:
        """设置配置值"""
        config = self.get_by_key(key)
        if not config:
            return False
        
        config.value = self._serialize_value(value, config.config_type)
        config.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_configs_by_category(self, category: str) -> List[SystemConfig]:
        """根据分类获取配置"""
        return self.db.query(SystemConfig).filter(
            SystemConfig.category == category,
            SystemConfig.is_active == True,
            SystemConfig.is_deleted == False
        ).order_by(SystemConfig.sort.asc()).all()
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """获取所有配置分类"""
        result = self.db.query(
            SystemConfig.category,
            func.count(SystemConfig.id).label('count')
        ).filter(
            SystemConfig.is_deleted == False
        ).group_by(SystemConfig.category).all()
        
        categories = []
        category_names = {
            'basic': '基础设置',
            'security': '安全设置',
            'email': '邮件设置',
            'storage': '存储设置',
            'system': '系统设置',
            'appearance': '外观设置'
        }
        
        for category, count in result:
            categories.append({
                'category': category,
                'name': category_names.get(category, category),
                'description': f'{category_names.get(category, category)}相关配置',
                'count': count
            })
        
        return categories
    
    def batch_update_configs(self, configs: List[Dict[str, Any]]) -> bool:
        """批量更新配置"""
        try:
            for config_data in configs:
                key = config_data.get('key')
                value = config_data.get('value')
                
                if key:
                    self.set_config_value(key, value)
            
            return True
        except Exception as e:
            logger.error(f"Batch update configs failed: {e}")
            self.db.rollback()
            return False
    
    def get_config_dict(self, category: str = None) -> Dict[str, Any]:
        """获取配置字典"""
        query = self.db.query(SystemConfig).filter(
            SystemConfig.is_active == True,
            SystemConfig.is_deleted == False
        )
        
        if category:
            query = query.filter(SystemConfig.category == category)
        
        configs = query.all()
        
        result = {}
        for config in configs:
            result[config.key] = self._convert_value(config.value, config.config_type)
        
        return result
    
    def check_key_exists(self, key: str, exclude_id: int = None) -> bool:
        """检查配置键是否存在"""
        query = self.db.query(SystemConfig).filter(
            SystemConfig.key == key,
            SystemConfig.is_deleted == False
        )
        if exclude_id:
            query = query.filter(SystemConfig.id != exclude_id)
        return query.first() is not None
    
    def _convert_value(self, value: str, config_type: str) -> Any:
        """转换配置值类型"""
        if value is None:
            return None
        
        try:
            if config_type == 'boolean':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif config_type == 'number':
                return float(value) if '.' in value else int(value)
            elif config_type == 'json':
                return json.loads(value)
            else:
                return value
        except (ValueError, json.JSONDecodeError):
            return value
    
    def _serialize_value(self, value: Any, config_type: str) -> str:
        """序列化配置值"""
        if value is None:
            return ''
        
        if config_type == 'json':
            return json.dumps(value, ensure_ascii=False)
        elif config_type == 'boolean':
            return str(bool(value)).lower()
        else:
            return str(value)


class UserPersonalConfigService:
    """用户个人配置服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, config_id: int) -> Optional[UserPersonalConfig]:
        """根据ID获取用户个人配置"""
        return self.db.query(UserPersonalConfig).filter(
            UserPersonalConfig.id == config_id,
            UserPersonalConfig.is_deleted == False
        ).first()
    
    def get_by_user_and_key(self, user_id: int, key: str) -> Optional[UserPersonalConfig]:
        """根据用户ID和键获取配置"""
        return self.db.query(UserPersonalConfig).filter(
            UserPersonalConfig.user_id == user_id,
            UserPersonalConfig.key == key,
            UserPersonalConfig.is_deleted == False
        ).first()
    
    def create_config(self, config_data: dict) -> UserPersonalConfig:
        """创建用户个人配置"""
        config = UserPersonalConfig(**config_data)
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def update_config(self, config_id: int, config_data: dict) -> Optional[UserPersonalConfig]:
        """更新用户个人配置"""
        config = self.get_by_id(config_id)
        if not config:
            return None
        
        for field, value in config_data.items():
            if hasattr(config, field):
                setattr(config, field, value)
        
        config.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def delete_config(self, config_id: int) -> bool:
        """删除用户个人配置（软删除）"""
        config = self.get_by_id(config_id)
        if not config:
            return False
        
        config.is_deleted = True
        config.deleted_at = datetime.utcnow()
        config.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_user_config_list(self, user_id: int, params: PaginationParams, filters: dict = None) -> Dict[str, Any]:
        """获取用户个人配置列表"""
        query = self.db.query(UserPersonalConfig).filter(
            UserPersonalConfig.user_id == user_id,
            UserPersonalConfig.is_deleted == False
        )
        
        # 应用过滤条件
        if filters:
            if 'search' in filters and filters['search']:
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        UserPersonalConfig.name.like(search_term),
                        UserPersonalConfig.key.like(search_term)
                    )
                )
            
            if 'category' in filters and filters['category']:
                query = query.filter(UserPersonalConfig.category == filters['category'])
        
        # 应用排序
        query = query.order_by(UserPersonalConfig.category.asc(), UserPersonalConfig.created_at.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (params.page - 1) * params.size
        configs = query.offset(offset).limit(params.size).all()
        
        return {
            'results': configs,
            'total': total,
            'page': params.page,
            'size': params.size,
            'pages': (total + params.size - 1) // params.size
        }
    
    def get_user_config_value(self, user_id: int, key: str, default: Any = None) -> Any:
        """获取用户配置值"""
        config = self.get_by_user_and_key(user_id, key)
        if not config:
            return default
        
        return self._convert_value(config.value, config.config_type)
    
    def set_user_config_value(self, user_id: int, key: str, value: Any, name: str = None, category: str = 'personal', config_type: str = 'string') -> bool:
        """设置用户配置值"""
        config = self.get_by_user_and_key(user_id, key)
        
        if config:
            # 更新现有配置
            config.value = self._serialize_value(value, config_type)
            config.updated_at = datetime.utcnow()
        else:
            # 创建新配置
            config = UserPersonalConfig(
                user_id=user_id,
                key=key,
                value=self._serialize_value(value, config_type),
                name=name or key,
                category=category,
                config_type=config_type,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(config)
        
        self.db.commit()
        return True
    
    def get_user_config_dict(self, user_id: int, category: str = None) -> Dict[str, Any]:
        """获取用户配置字典"""
        query = self.db.query(UserPersonalConfig).filter(
            UserPersonalConfig.user_id == user_id,
            UserPersonalConfig.is_deleted == False
        )
        
        if category:
            query = query.filter(UserPersonalConfig.category == category)
        
        configs = query.all()
        
        result = {}
        for config in configs:
            result[config.key] = self._convert_value(config.value, config.config_type)
        
        return result
    
    def batch_update_user_configs(self, user_id: int, configs: List[Dict[str, Any]]) -> bool:
        """批量更新用户配置"""
        try:
            for config_data in configs:
                key = config_data.get('key')
                value = config_data.get('value')
                name = config_data.get('name', key)
                category = config_data.get('category', 'personal')
                config_type = config_data.get('config_type', 'string')
                
                if key:
                    self.set_user_config_value(user_id, key, value, name, category, config_type)
            
            return True
        except Exception as e:
            logger.error(f"Batch update user configs failed: {e}")
            self.db.rollback()
            return False
    
    def _convert_value(self, value: str, config_type: str) -> Any:
        """转换配置值类型"""
        if value is None:
            return None
        
        try:
            if config_type == 'boolean':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif config_type == 'number':
                return float(value) if '.' in value else int(value)
            elif config_type == 'json':
                return json.loads(value)
            else:
                return value
        except (ValueError, json.JSONDecodeError):
            return value
    
    def _serialize_value(self, value: Any, config_type: str) -> str:
        """序列化配置值"""
        if value is None:
            return ''
        
        if config_type == 'json':
            return json.dumps(value, ensure_ascii=False)
        elif config_type == 'boolean':
            return str(bool(value)).lower()
        else:
            return str(value)