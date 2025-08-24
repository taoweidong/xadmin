"""
测试 app.models.user 模块
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models.user import (
    UserInfo,
    UserRole,
    DeptInfo,
    DataPermission,
    user_role_association,
    user_permission_association,
    role_menu_association,
    role_permission_association,
)


class TestUserInfo:
    """测试用户信息模型"""
    
    def test_user_info_creation(self, test_db_session):
        """测试用户创建"""
        user = UserInfo(
            username="testuser",
            password="hashed_password",
            email="test@example.com",
            phone="13800138000",
            nickname="测试用户",
            gender=1,
            is_active=True,
            is_staff=False,
            is_superuser=False
        )
        
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        assert user.id is not None
        assert getattr(user, 'username') == "testuser"
        assert getattr(user, 'email') == "test@example.com"
        assert getattr(user, 'phone') == "13800138000"
        assert getattr(user, 'nickname') == "测试用户"
        assert getattr(user, 'gender') == 1
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.date_joined is not None
    
    def test_user_info_unique_username(self, test_db_session):
        """测试用户名唯一性约束"""
        user1 = UserInfo(username="testuser", password="password1")
        user2 = UserInfo(username="testuser", password="password2")
        
        test_db_session.add(user1)
        test_db_session.commit()
        
        test_db_session.add(user2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_user_info_str_representation(self, test_db_session):
        """测试用户字符串表示"""
        user_with_nickname = UserInfo(
            username="testuser1",
            password="password",
            nickname="测试用户"
        )
        user_without_nickname = UserInfo(
            username="testuser2",
            password="password"
        )
        
        test_db_session.add_all([user_with_nickname, user_without_nickname])
        test_db_session.commit()
        test_db_session.refresh(user_with_nickname)
        test_db_session.refresh(user_without_nickname)
        
        assert str(user_with_nickname) == "测试用户(testuser1)"
        assert str(user_without_nickname) == "testuser2(testuser2)"
    
    def test_user_info_default_values(self, test_db_session):
        """测试用户默认值"""
        user = UserInfo(username="testuser", password="password")
        
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        assert getattr(user, 'gender') == 0  # 默认性别为未知
        assert user.is_active is True  # 默认激活
        assert user.is_staff is False  # 默认非员工
        assert user.is_superuser is False  # 默认非超级用户
        assert user.date_joined is not None  # 默认注册时间为当前时间
    
    def test_user_info_optional_fields(self, test_db_session):
        """测试用户可选字段"""
        user = UserInfo(username="testuser", password="password")
        
        test_db_session.add(user)
        test_db_session.commit()
        
        # 这些字段应该可以为空
        assert user.email is None
        assert user.phone is None
        assert user.nickname is None
        assert user.avatar is None
        assert user.last_login is None
        assert user.dept_id is None


class TestUserRole:
    """测试用户角色模型"""
    
    def test_user_role_creation(self, test_db_session):
        """测试角色创建"""
        role = UserRole(
            name="管理员",
            code="admin",
            is_active=True,
            sort=1,
            description="系统管理员角色",
            remark="拥有所有权限"
        )
        
        test_db_session.add(role)
        test_db_session.commit()
        test_db_session.refresh(role)
        
        assert role.id is not None
        assert getattr(role, 'name') == "管理员"
        assert getattr(role, 'code') == "admin"
        assert role.is_active is True
        assert getattr(role, 'sort') == 1
        assert getattr(role, 'description') == "系统管理员角色"
        assert getattr(role, 'remark') == "拥有所有权限"
        assert role.created_at is not None
    
    def test_user_role_unique_constraints(self, test_db_session):
        """测试角色唯一性约束"""
        role1 = UserRole(name="管理员", code="admin")
        role2 = UserRole(name="管理员", code="admin")
        
        test_db_session.add(role1)
        test_db_session.commit()
        
        test_db_session.add(role2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_user_role_str_representation(self, test_db_session):
        """测试角色字符串表示"""
        role = UserRole(name="管理员", code="admin")
        
        test_db_session.add(role)
        test_db_session.commit()
        test_db_session.refresh(role)
        
        assert str(role) == "管理员"
    
    def test_user_role_default_values(self, test_db_session):
        """测试角色默认值"""
        role = UserRole(name="测试角色", code="test")
        
        test_db_session.add(role)
        test_db_session.commit()
        test_db_session.refresh(role)
        
        assert role.is_active is True  # 默认启用
        assert getattr(role, 'sort') == 0  # 默认排序为0


class TestDeptInfo:
    """测试部门信息模型"""
    
    def test_dept_info_creation(self, test_db_session):
        """测试部门创建"""
        dept = DeptInfo(
            name="技术部",
            code="tech",
            is_active=True,
            sort=1,
            leader="张三",
            phone="010-12345678",
            email="tech@example.com",
            description="技术开发部门",
            remark="负责产品研发"
        )
        
        test_db_session.add(dept)
        test_db_session.commit()
        test_db_session.refresh(dept)
        
        assert dept.id is not None
        assert getattr(dept, 'name') == "技术部"
        assert getattr(dept, 'code') == "tech"
        assert dept.is_active is True
        assert getattr(dept, 'sort') == 1
        assert getattr(dept, 'leader') == "张三"
        assert getattr(dept, 'phone') == "010-12345678"
        assert getattr(dept, 'email') == "tech@example.com"
        assert getattr(dept, 'description') == "技术开发部门"
        assert getattr(dept, 'remark') == "负责产品研发"
    
    def test_dept_info_unique_code(self, test_db_session):
        """测试部门编码唯一性"""
        dept1 = DeptInfo(name="技术部1", code="tech")
        dept2 = DeptInfo(name="技术部2", code="tech")
        
        test_db_session.add(dept1)
        test_db_session.commit()
        
        test_db_session.add(dept2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_dept_info_self_relationship(self, test_db_session):
        """测试部门自关联关系"""
        parent_dept = DeptInfo(name="总公司", code="company")
        child_dept = DeptInfo(name="技术部", code="tech")
        
        test_db_session.add_all([parent_dept, child_dept])
        test_db_session.commit()
        test_db_session.refresh(parent_dept)
        test_db_session.refresh(child_dept)
        
        # 设置父子关系
        child_dept.parent_id = parent_dept.id
        child_dept.parent = parent_dept
        test_db_session.commit()
        test_db_session.refresh(parent_dept)
        test_db_session.refresh(child_dept)
        
        # 验证关系
        assert child_dept.parent == parent_dept
        assert parent_dept in [parent for parent in [child_dept.parent]]
        assert child_dept in parent_dept.children
    
    def test_dept_info_str_representation(self, test_db_session):
        """测试部门字符串表示"""
        dept = DeptInfo(name="技术部", code="tech")
        
        test_db_session.add(dept)
        test_db_session.commit()
        test_db_session.refresh(dept)
        
        assert str(dept) == "技术部"
    
    def test_dept_info_default_values(self, test_db_session):
        """测试部门默认值"""
        dept = DeptInfo(name="测试部门", code="test")
        
        test_db_session.add(dept)
        test_db_session.commit()
        test_db_session.refresh(dept)
        
        assert dept.is_active is True  # 默认启用
        assert getattr(dept, 'sort') == 0  # 默认排序为0


class TestDataPermission:
    """测试数据权限模型"""
    
    def test_data_permission_creation(self, test_db_session):
        """测试数据权限创建"""
        permission = DataPermission(
            name="用户管理权限",
            code="user_manage",
            rules='{"scope": "dept", "filter": "dept_id"}',
            is_active=True,
            description="用户管理相关权限",
            remark="可管理本部门用户"
        )
        
        test_db_session.add(permission)
        test_db_session.commit()
        test_db_session.refresh(permission)
        
        assert permission.id is not None
        assert getattr(permission, 'name') == "用户管理权限"
        assert getattr(permission, 'code') == "user_manage"
        assert getattr(permission, 'rules') == '{"scope": "dept", "filter": "dept_id"}'
        assert permission.is_active is True
        assert getattr(permission, 'description') == "用户管理相关权限"
        assert getattr(permission, 'remark') == "可管理本部门用户"
    
    def test_data_permission_unique_code(self, test_db_session):
        """测试数据权限编码唯一性"""
        perm1 = DataPermission(name="权限1", code="test_perm")
        perm2 = DataPermission(name="权限2", code="test_perm")
        
        test_db_session.add(perm1)
        test_db_session.commit()
        
        test_db_session.add(perm2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_data_permission_str_representation(self, test_db_session):
        """测试数据权限字符串表示"""
        permission = DataPermission(name="测试权限", code="test")
        
        test_db_session.add(permission)
        test_db_session.commit()
        test_db_session.refresh(permission)
        
        assert str(permission) == "测试权限"
    
    def test_data_permission_default_values(self, test_db_session):
        """测试数据权限默认值"""
        permission = DataPermission(name="测试权限", code="test")
        
        test_db_session.add(permission)
        test_db_session.commit()
        test_db_session.refresh(permission)
        
        assert permission.is_active is True  # 默认启用
        assert permission.rules is None  # 默认无规则


class TestUserRoleRelationships:
    """测试用户角色关系"""
    
    def test_user_role_association(self, test_db_session):
        """测试用户角色关联"""
        user = UserInfo(username="testuser", password="password")
        role = UserRole(name="测试角色", code="test_role")
        
        test_db_session.add_all([user, role])
        test_db_session.commit()
        test_db_session.refresh(user)
        test_db_session.refresh(role)
        
        # 建立关联
        user.roles.append(role)
        test_db_session.commit()
        test_db_session.refresh(user)
        test_db_session.refresh(role)
        
        # 验证关联
        assert role in user.roles
        assert user in role.users
    
    def test_user_permission_association(self, test_db_session):
        """测试用户权限关联"""
        user = UserInfo(username="testuser", password="password")
        permission = DataPermission(name="测试权限", code="test_perm")
        
        test_db_session.add_all([user, permission])
        test_db_session.commit()
        test_db_session.refresh(user)
        test_db_session.refresh(permission)
        
        # 建立关联
        user.permissions.append(permission)
        test_db_session.commit()
        test_db_session.refresh(user)
        test_db_session.refresh(permission)
        
        # 验证关联
        assert permission in user.permissions
        assert user in permission.users
    
    def test_user_dept_relationship(self, test_db_session):
        """测试用户部门关系"""
        dept = DeptInfo(name="技术部", code="tech")
        user = UserInfo(username="testuser", password="password")
        
        test_db_session.add_all([dept, user])
        test_db_session.commit()
        test_db_session.refresh(dept)
        test_db_session.refresh(user)
        
        # 建立关系
        user.dept_id = dept.id
        user.dept = dept
        test_db_session.commit()
        test_db_session.refresh(dept)
        test_db_session.refresh(user)
        
        # 验证关系
        assert user.dept == dept
        assert user in dept.users
    
    def test_multiple_roles_per_user(self, test_db_session):
        """测试用户拥有多个角色"""
        user = UserInfo(username="testuser", password="password")
        role1 = UserRole(name="角色1", code="role1")
        role2 = UserRole(name="角色2", code="role2")
        
        test_db_session.add_all([user, role1, role2])
        test_db_session.commit()
        test_db_session.refresh(user)
        test_db_session.refresh(role1)
        test_db_session.refresh(role2)
        
        # 建立关联
        user.roles.extend([role1, role2])
        test_db_session.commit()
        test_db_session.refresh(user)
        test_db_session.refresh(role1)
        test_db_session.refresh(role2)
        
        # 验证关联
        assert len(user.roles) == 2
        assert role1 in user.roles
        assert role2 in user.roles
        assert user in role1.users
        assert user in role2.users
    
    def test_multiple_users_per_role(self, test_db_session):
        """测试角色拥有多个用户"""
        role = UserRole(name="测试角色", code="test_role")
        user1 = UserInfo(username="user1", password="password")
        user2 = UserInfo(username="user2", password="password")
        
        test_db_session.add_all([role, user1, user2])
        test_db_session.commit()
        test_db_session.refresh(role)
        test_db_session.refresh(user1)
        test_db_session.refresh(user2)
        
        # 建立关联
        role.users.extend([user1, user2])
        test_db_session.commit()
        test_db_session.refresh(role)
        test_db_session.refresh(user1)
        test_db_session.refresh(user2)
        
        # 验证关联
        assert len(role.users) == 2
        assert user1 in role.users
        assert user2 in role.users
        assert role in user1.roles
        assert role in user2.roles


class TestAssociationTables:
    """测试关联表"""
    
    def test_user_role_association_table(self):
        """测试用户角色关联表结构"""
        table = user_role_association
        
        assert table.name == 'user_role_association'
        assert 'user_id' in table.columns
        assert 'role_id' in table.columns
        
        # 检查外键约束
        user_id_col = table.columns['user_id']
        role_id_col = table.columns['role_id']
        
        assert user_id_col.primary_key is True
        assert role_id_col.primary_key is True
    
    def test_user_permission_association_table(self):
        """测试用户权限关联表结构"""
        table = user_permission_association
        
        assert table.name == 'user_permission_association'
        assert 'user_id' in table.columns
        assert 'permission_id' in table.columns
    
    def test_role_menu_association_table(self):
        """测试角色菜单关联表结构"""
        table = role_menu_association
        
        assert table.name == 'role_menu_association'
        assert 'role_id' in table.columns
        assert 'menu_id' in table.columns
    
    def test_role_permission_association_table(self):
        """测试角色权限关联表结构"""
        table = role_permission_association
        
        assert table.name == 'role_permission_association'
        assert 'role_id' in table.columns
        assert 'permission_id' in table.columns


class TestModelIndexes:
    """测试模型索引"""
    
    def test_user_info_indexes(self):
        """测试用户信息表索引"""
        # 这里主要验证索引字段的定义是否正确
        # 实际的索引测试需要在数据库层面进行
        
        # 验证有索引的字段
        assert UserInfo.username.index is True
        assert UserInfo.email.index is True
        assert UserInfo.phone.index is True
    
    def test_dept_info_indexes(self):
        """测试部门信息表索引"""
        # 验证部门编码有唯一索引
        assert DeptInfo.code.unique is True
    
    def test_user_role_indexes(self):
        """测试用户角色表索引"""
        # 验证角色编码有唯一索引
        assert UserRole.code.unique is True
    
    def test_data_permission_indexes(self):
        """测试数据权限表索引"""
        # 验证权限编码有唯一索引
        assert DataPermission.code.unique is True