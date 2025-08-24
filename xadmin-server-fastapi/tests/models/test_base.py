"""
测试 app.models.base 模块
"""
import pytest
from datetime import datetime
from sqlalchemy import Column, String, Integer
from app.models.base import (
    TimestampMixin,
    BaseModel,
    SoftDeleteMixin,
    UUIDMixin,
    CreatorMixin,
    AuditMixin,
    DescriptionMixin,
)


class TestTimestampMixin:
    """测试时间戳混入类"""
    
    def test_timestamp_mixin_fields(self):
        """测试时间戳字段定义"""
        # 创建一个测试类来验证字段
        class TestModel(TimestampMixin):
            pass
        
        model = TestModel()
        
        # 检查字段是否存在
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        
        # 检查字段属性
        created_at_col = TestModel.__table__.columns.get('created_at')
        updated_at_col = TestModel.__table__.columns.get('updated_at')
        
        assert created_at_col is not None
        assert updated_at_col is not None
        assert created_at_col.nullable is False
        assert updated_at_col.nullable is False


class TestBaseModel:
    """测试基础模型类"""
    
    def test_base_model_abstract(self):
        """测试基础模型是抽象的"""
        assert BaseModel.__abstract__ is True
    
    def test_base_model_inheritance(self):
        """测试基础模型继承"""
        # 创建一个继承BaseModel的测试类
        class TestModel(BaseModel):
            __tablename__ = 'test_model'
            name = Column(String(50))
        
        # 检查是否继承了时间戳字段
        assert hasattr(TestModel, 'created_at')
        assert hasattr(TestModel, 'updated_at')
        assert hasattr(TestModel, 'id')
        
        # 检查ID字段属性
        id_col = TestModel.__table__.columns.get('id')
        assert id_col is not None
        assert id_col.primary_key is True
        assert id_col.index is True
    
    def test_tablename_generation(self):
        """测试表名自动生成"""
        class UserInfo(BaseModel):
            pass
        
        class DeptInfo(BaseModel):
            pass
        
        class MyTestModel(BaseModel):
            pass
        
        assert UserInfo.__tablename__ == 'user_info'
        assert DeptInfo.__tablename__ == 'dept_info'
        assert MyTestModel.__tablename__ == 'my_test_model'


class TestSoftDeleteMixin:
    """测试软删除混入类"""
    
    def test_soft_delete_fields(self):
        """测试软删除字段"""
        class TestModel(SoftDeleteMixin):
            pass
        
        model = TestModel()
        
        assert hasattr(model, 'is_deleted')
        assert hasattr(model, 'deleted_at')
        
        # 检查字段属性
        is_deleted_col = TestModel.__table__.columns.get('is_deleted')
        deleted_at_col = TestModel.__table__.columns.get('deleted_at')
        
        assert is_deleted_col is not None
        assert deleted_at_col is not None
        assert is_deleted_col.default.arg is False
        assert deleted_at_col.nullable is True


class TestUUIDMixin:
    """测试UUID混入类"""
    
    def test_uuid_field(self):
        """测试UUID字段"""
        class TestModel(UUIDMixin):
            pass
        
        model = TestModel()
        
        assert hasattr(model, 'uuid')
        
        # 检查字段属性
        uuid_col = TestModel.__table__.columns.get('uuid')
        assert uuid_col is not None
        assert uuid_col.unique is True
        assert uuid_col.index is True
        assert uuid_col.default is not None
    
    def test_uuid_generation(self):
        """测试UUID生成"""
        class TestModel(UUIDMixin):
            pass
        
        # 创建两个实例，验证UUID的唯一性
        model1 = TestModel()
        model2 = TestModel()
        
        # 由于是default函数，需要调用才能生成
        uuid1 = TestModel.__table__.columns.get('uuid').default.arg()
        uuid2 = TestModel.__table__.columns.get('uuid').default.arg()
        
        assert uuid1 != uuid2
        assert len(uuid1) == 36  # UUID v4 格式长度


class TestCreatorMixin:
    """测试创建者混入类"""
    
    def test_creator_fields(self):
        """测试创建者字段"""
        class TestModel(CreatorMixin):
            pass
        
        model = TestModel()
        
        assert hasattr(model, 'created_by')
        assert hasattr(model, 'updated_by')
        
        # 检查字段属性
        created_by_col = TestModel.__table__.columns.get('created_by')
        updated_by_col = TestModel.__table__.columns.get('updated_by')
        
        assert created_by_col is not None
        assert updated_by_col is not None
        assert created_by_col.nullable is True
        assert updated_by_col.nullable is True


class TestAuditMixin:
    """测试审计混入类"""
    
    def test_audit_fields(self):
        """测试审计字段组合"""
        class TestModel(AuditMixin):
            pass
        
        model = TestModel()
        
        # 检查是否包含创建者字段
        assert hasattr(model, 'created_by')
        assert hasattr(model, 'updated_by')
        
        # 检查是否包含软删除字段
        assert hasattr(model, 'is_deleted')
        assert hasattr(model, 'deleted_at')


class TestDescriptionMixin:
    """测试描述混入类"""
    
    def test_description_fields(self):
        """测试描述字段"""
        class TestModel(DescriptionMixin):
            pass
        
        model = TestModel()
        
        assert hasattr(model, 'description')
        assert hasattr(model, 'remark')
        
        # 检查字段属性
        description_col = TestModel.__table__.columns.get('description')
        remark_col = TestModel.__table__.columns.get('remark')
        
        assert description_col is not None
        assert remark_col is not None
        assert description_col.nullable is True
        assert remark_col.nullable is True


class TestMixinCombinations:
    """测试混入类组合"""
    
    def test_multiple_mixin_combination(self):
        """测试多个混入类组合"""
        class CompleteModel(BaseModel, AuditMixin, DescriptionMixin, UUIDMixin):
            __tablename__ = 'complete_model'
            name = Column(String(50))
        
        model = CompleteModel()
        
        # 检查基础字段
        assert hasattr(model, 'id')
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        
        # 检查审计字段
        assert hasattr(model, 'created_by')
        assert hasattr(model, 'updated_by')
        assert hasattr(model, 'is_deleted')
        assert hasattr(model, 'deleted_at')
        
        # 检查描述字段
        assert hasattr(model, 'description')
        assert hasattr(model, 'remark')
        
        # 检查UUID字段
        assert hasattr(model, 'uuid')
        
        # 检查自定义字段
        assert hasattr(model, 'name')
    
    def test_mixin_field_inheritance_order(self):
        """测试混入类字段继承顺序"""
        class TestModel(BaseModel, TimestampMixin, SoftDeleteMixin):
            __tablename__ = 'test_model'
        
        # 确保所有字段都正确继承
        expected_fields = [
            'id', 'created_at', 'updated_at', 
            'is_deleted', 'deleted_at'
        ]
        
        for field_name in expected_fields:
            assert hasattr(TestModel, field_name)
            assert field_name in TestModel.__table__.columns
    
    def test_conflicting_field_resolution(self):
        """测试字段冲突解决"""
        # 这个测试确保在多重继承时字段不会冲突
        class ModelA(TimestampMixin):
            pass
        
        class ModelB(TimestampMixin):
            pass
        
        # 两个模型都应该有相同的字段定义
        assert hasattr(ModelA, 'created_at')
        assert hasattr(ModelB, 'created_at')


class TestModelInstantiation:
    """测试模型实例化"""
    
    def test_model_creation_with_mixins(self, test_db_session):
        """测试使用混入类的模型创建"""
        class TestModel(BaseModel):
            __tablename__ = 'test_creation_model'
            name = Column(String(50))
        
        # 创建表
        TestModel.__table__.create(bind=test_db_session.bind, checkfirst=True)
        
        # 创建实例
        instance = TestModel(name="test")
        test_db_session.add(instance)
        test_db_session.commit()
        
        # 验证实例
        assert instance.id is not None
        assert instance.name == "test"
        assert instance.created_at is not None
        assert instance.updated_at is not None
        
        # 清理
        TestModel.__table__.drop(bind=test_db_session.bind, checkfirst=True)
    
    def test_model_with_all_mixins(self, test_db_session):
        """测试包含所有混入类的模型"""
        class FullModel(BaseModel, AuditMixin, DescriptionMixin, UUIDMixin):
            __tablename__ = 'full_test_model'
            name = Column(String(50))
        
        # 创建表
        FullModel.__table__.create(bind=test_db_session.bind, checkfirst=True)
        
        # 创建实例
        instance = FullModel(
            name="test",
            description="test description",
            remark="test remark",
            created_by=1,
            updated_by=1
        )
        test_db_session.add(instance)
        test_db_session.commit()
        
        # 验证实例
        assert instance.id is not None
        assert instance.name == "test"
        assert instance.description == "test description"
        assert instance.remark == "test remark"
        assert instance.created_by == 1
        assert instance.updated_by == 1
        assert instance.is_deleted is False
        assert instance.deleted_at is None
        assert instance.created_at is not None
        assert instance.updated_at is not None
        assert instance.uuid is not None
        
        # 清理
        FullModel.__table__.drop(bind=test_db_session.bind, checkfirst=True)