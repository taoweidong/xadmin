"""
测试 app.models.system 模块
"""
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.system import (
    MenuInfo,
    MenuMeta,
    SystemConfig,
    UserPersonalConfig,
    ModelLabelField,
    UploadFile,
)
from app.models.user import UserInfo, UserRole


class TestMenuInfo:
    """测试菜单信息模型"""
    
    def test_menu_info_creation(self, test_db_session):
        """测试菜单创建"""
        # 先创建菜单元数据
        meta = MenuMeta(
            title="用户管理",
            icon="user",
            is_keepalive=True
        )
        test_db_session.add(meta)
        test_db_session.commit()
        
        # 再创建菜单
        menu = MenuInfo(
            name="UserManagement",
            path="/users",
            component="views/users/index.vue",
            menu_type=1,
            sort=10,
            is_active=True,
            meta_id=meta.id
        )
        
        test_db_session.add(menu)
        test_db_session.commit()
        
        assert menu.id is not None
        assert menu.name == "UserManagement"
        assert menu.path == "/users"
        assert menu.component == "views/users/index.vue"
        # 移除了redirect属性，因为MenuInfo模型中没有这个字段
        assert menu.menu_type == 1
        assert menu.sort == 10
        assert menu.is_active is True
        assert menu.meta_id == meta.id
        assert menu.meta.title == "用户管理"
        assert menu.meta.icon == "user"
    
    def test_menu_info_self_relationship(self, test_db_session):
        """测试菜单自关联关系"""
        # 创建父菜单元数据
        parent_meta = MenuMeta(title="系统管理")
        test_db_session.add(parent_meta)
        test_db_session.commit()
        
        # 创建子菜单元数据
        child_meta = MenuMeta(title="用户管理")
        test_db_session.add(child_meta)
        test_db_session.commit()
        
        # 创建菜单
        parent_menu = MenuInfo(name="System", path="/system", menu_type=0, meta_id=parent_meta.id)
        child_menu = MenuInfo(name="UserManagement", path="/users", menu_type=1, meta_id=child_meta.id)
        
        test_db_session.add_all([parent_menu, child_menu])
        test_db_session.commit()
        
        # 设置父子关系
        child_menu.parent_id = parent_menu.id
        test_db_session.commit()
        
        # 验证关系
        assert child_menu.parent == parent_menu
        assert child_menu in parent_menu.children
    
    def test_menu_info_default_values(self, test_db_session):
        """测试菜单默认值"""
        # 创建菜单元数据
        meta = MenuMeta(title="测试菜单")
        test_db_session.add(meta)
        test_db_session.commit()
        
        # 创建菜单
        menu = MenuInfo(name="TestMenu", path="/test", meta_id=meta.id)
        
        test_db_session.add(menu)
        test_db_session.commit()
        
        assert menu.menu_type == 0  # 默认菜单类型
        assert menu.sort == 9999  # 默认排序
        assert menu.is_active is True  # 默认启用
    
    def test_menu_info_str_representation(self, test_db_session):
        """测试菜单字符串表示"""
        # 创建菜单元数据
        meta = MenuMeta(title="用户管理")
        test_db_session.add(meta)
        test_db_session.commit()
        
        # 创建菜单
        menu = MenuInfo(name="UserManagement", path="/users", meta_id=meta.id)
        test_db_session.add(menu)
        test_db_session.commit()
        
        assert str(menu) == "UserManagement"
    
    def test_menu_info_types(self, test_db_session):
        """测试不同菜单类型"""
        # 创建菜单元数据
        meta1 = MenuMeta(title="系统管理")
        meta2 = MenuMeta(title="用户管理")
        meta3 = MenuMeta(title="新增用户")
        test_db_session.add_all([meta1, meta2, meta3])
        test_db_session.commit()
        
        # 创建菜单
        menus = [
            MenuInfo(name="System", path="/system", menu_type=0, meta_id=meta1.id),  # 目录
            MenuInfo(name="UserManagement", path="/users", menu_type=1, meta_id=meta2.id),  # 菜单
            MenuInfo(name="AddUser", path="/users/add", menu_type=2, meta_id=meta3.id),  # 按钮/权限
        ]
        
        test_db_session.add_all(menus)
        test_db_session.commit()
        
        assert menus[0].menu_type == 0  # 目录
        assert menus[1].menu_type == 1  # 菜单
        assert menus[2].menu_type == 2  # 按钮/权限
    
    def test_menu_role_relationship(self, test_db_session):
        """测试菜单与角色关系"""
        # 创建菜单元数据
        meta = MenuMeta(title="用户管理")
        test_db_session.add(meta)
        test_db_session.commit()
        
        # 创建菜单和角色
        menu = MenuInfo(name="UserManagement", path="/users", meta_id=meta.id)
        role = UserRole(name="管理员", code="admin")
        
        test_db_session.add_all([menu, role])
        test_db_session.commit()
        
        # 建立关联
        role.menus.append(menu)
        test_db_session.commit()
        
        # 验证关系
        assert menu in role.menus
        assert role in menu.roles


class TestSystemConfig:
    """测试系统配置模型"""
    
    def test_system_config_creation(self, test_db_session):
        """测试系统配置创建"""
        config = SystemConfig(
            key="site_name",
            value="xAdmin系统",
            name="站点名称",
            description="系统主页显示的站点名称",
            category="site",
            config_type="string",
            is_active=True,
            sort=1
        )
        
        test_db_session.add(config)
        test_db_session.commit()
        
        assert config.id is not None
        assert config.key == "site_name"
        assert config.value == "xAdmin系统"
        assert config.name == "站点名称"
        assert config.description == "系统主页显示的站点名称"
        assert config.category == "site"
        assert config.config_type == "string"
        assert config.is_active is True
        assert config.sort == 1
    
    def test_system_config_unique_key(self, test_db_session):
        """测试系统配置键唯一性"""
        config1 = SystemConfig(key="test_key", name="配置1", value="value1")
        config2 = SystemConfig(key="test_key", name="配置2", value="value2")
        
        test_db_session.add(config1)
        test_db_session.commit()
        
        test_db_session.add(config2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_system_config_default_values(self, test_db_session):
        """测试系统配置默认值"""
        config = SystemConfig(key="test_key", name="测试配置")
        
        test_db_session.add(config)
        test_db_session.commit()
        
        assert config.category == "system"  # 默认分类
        assert config.config_type == "string"  # 默认类型
        assert config.is_active is True  # 默认启用
        assert config.sort == 0  # 默认排序
    
    def test_system_config_str_representation(self, test_db_session):
        """测试系统配置字符串表示"""
        config = SystemConfig(key="site_name", name="站点名称")
        test_db_session.add(config)
        test_db_session.commit()
        
        assert str(config) == "站点名称(site_name)"
    
    def test_system_config_types(self, test_db_session):
        """测试不同配置类型"""
        configs = [
            SystemConfig(key="site_name", name="站点名称", config_type="string", value="xAdmin"),
            SystemConfig(key="max_users", name="最大用户数", config_type="number", value="1000"),
            SystemConfig(key="enable_register", name="开启注册", config_type="boolean", value="true"),
            SystemConfig(key="mail_config", name="邮件配置", config_type="json", value='{"host": "smtp.qq.com"}'),
            SystemConfig(key="logo", name="系统Logo", config_type="file", value="/uploads/logo.png"),
        ]
        
        test_db_session.add_all(configs)
        test_db_session.commit()
        
        assert configs[0].config_type == "string"
        assert configs[1].config_type == "number"
        assert configs[2].config_type == "boolean"
        assert configs[3].config_type == "json"
        assert configs[4].config_type == "file"


class TestUserPersonalConfig:
    """测试用户个人配置模型"""
    
    def test_user_personal_config_creation(self, test_db_session):
        """测试用户个人配置创建"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        config = UserPersonalConfig(
            user_id=user.id,
            key="theme",
            value="dark",
            name="主题设置",
            category="appearance",
            config_type="string"
        )
        
        test_db_session.add(config)
        test_db_session.commit()
        
        assert config.id is not None
        assert config.user_id == user.id
        assert config.key == "theme"
        assert config.value == "dark"
        assert config.name == "主题设置"
        assert config.category == "appearance"
        assert config.config_type == "string"
    
    def test_user_personal_config_relationship(self, test_db_session):
        """测试用户个人配置关系"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        config = UserPersonalConfig(
            user_id=user.id,
            key="language",
            value="zh-CN",
            name="语言设置"
        )
        
        test_db_session.add(config)
        test_db_session.commit()
        
        # 验证关系
        assert config.user == user
    
    def test_user_personal_config_unique_constraint(self, test_db_session):
        """测试用户个人配置唯一性约束"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        config1 = UserPersonalConfig(user_id=user.id, key="theme", name="主题1", value="light")
        config2 = UserPersonalConfig(user_id=user.id, key="theme", name="主题2", value="dark")
        
        test_db_session.add(config1)
        test_db_session.commit()
        
        test_db_session.add(config2)
        # 应该因为用户ID+键的唯一性约束而失败
        with pytest.raises(Exception):
            test_db_session.commit()
    
    def test_user_personal_config_default_values(self, test_db_session):
        """测试用户个人配置默认值"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        config = UserPersonalConfig(
            user_id=user.id,
            key="test_key",
            name="测试配置"
        )
        
        test_db_session.add(config)
        test_db_session.commit()
        
        assert config.category == "personal"  # 默认分类
        assert config.config_type == "string"  # 默认类型
    
    def test_user_personal_config_str_representation(self, test_db_session):
        """测试用户个人配置字符串表示"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        config = UserPersonalConfig(
            user_id=user.id,
            key="theme",
            name="主题设置"
        )
        test_db_session.add(config)
        test_db_session.commit()
        
        assert str(config) == "testuser:主题设置"


class TestModelLabelField:
    """测试模型字段标签模型"""
    
    def test_model_label_field_creation(self, test_db_session):
        """测试模型字段标签创建"""
        field = ModelLabelField(
            name="user.gender",
            label="性别",
            parent="user",
            field_type="choice",
            choices='{"0": "未知", "1": "男", "2": "女"}'
        )
        
        test_db_session.add(field)
        test_db_session.commit()
        
        assert field.id is not None
        assert field.name == "user.gender"
        assert field.label == "性别"
        assert field.parent == "user"
        assert field.field_type == "choice"
        assert field.choices == '{"0": "未知", "1": "男", "2": "女"}'
    
    def test_model_label_field_str_representation(self, test_db_session):
        """测试模型字段标签字符串表示"""
        field = ModelLabelField(name="user.status", label="状态")
        test_db_session.add(field)
        test_db_session.commit()
        
        assert str(field) == "user.status:状态"
    
    def test_model_label_field_with_choices(self, test_db_session):
        """测试带选择项的字段标签"""
        field = ModelLabelField(
            name="order.status",
            label="订单状态",
            field_type="select",
            choices='["pending", "paid", "shipped", "completed", "cancelled"]'
        )
        
        test_db_session.add(field)
        test_db_session.commit()
        
        assert field.field_type == "select"
        assert "pending" in field.choices
        assert "completed" in field.choices


class TestUploadFile:
    """测试上传文件模型"""
    
    def test_upload_file_creation(self, test_db_session):
        """测试上传文件创建"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        upload_file = UploadFile(
            filename="20231201_123456_document.pdf",
            original_filename="重要文档.pdf",
            file_path="/uploads/2023/12/01/20231201_123456_document.pdf",
            file_size=1024000,
            file_type="document",
            mime_type="application/pdf",
            category="document",
            uploader_id=user.id,
            is_active=True,
            download_count=5
        )
        
        test_db_session.add(upload_file)
        test_db_session.commit()
        
        assert upload_file.id is not None
        assert upload_file.filename == "20231201_123456_document.pdf"
        assert upload_file.original_filename == "重要文档.pdf"
        assert upload_file.file_path == "/uploads/2023/12/01/20231201_123456_document.pdf"
        assert upload_file.file_size == 1024000
        assert upload_file.file_type == "document"
        assert upload_file.mime_type == "application/pdf"
        assert upload_file.category == "document"
        assert upload_file.uploader_id == user.id
        assert upload_file.is_active is True
        assert upload_file.download_count == 5
    
    def test_upload_file_relationship(self, test_db_session):
        """测试上传文件与用户关系"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        upload_file = UploadFile(
            filename="test.jpg",
            original_filename="测试图片.jpg",
            file_path="/uploads/test.jpg",
            uploader_id=user.id
        )
        
        test_db_session.add(upload_file)
        test_db_session.commit()
        
        # 验证关系
        assert upload_file.uploader == user
    
    def test_upload_file_default_values(self, test_db_session):
        """测试上传文件默认值"""
        upload_file = UploadFile(
            filename="test.txt",
            original_filename="test.txt",
            file_path="/uploads/test.txt"
        )
        
        test_db_session.add(upload_file)
        test_db_session.commit()
        
        assert upload_file.file_size == 0  # 默认文件大小
        assert upload_file.category == "general"  # 默认分类
        assert upload_file.is_active is True  # 默认有效
        assert upload_file.download_count == 0  # 默认下载次数
    
    def test_upload_file_str_representation(self, test_db_session):
        """测试上传文件字符串表示"""
        upload_file = UploadFile(
            filename="test.jpg",
            original_filename="测试图片.jpg",
            file_path="/uploads/test.jpg"
        )
        test_db_session.add(upload_file)
        test_db_session.commit()
        
        assert str(upload_file) == "测试图片.jpg"
    
    def test_upload_file_categories(self, test_db_session):
        """测试不同文件分类"""
        files = [
            UploadFile(filename="doc.pdf", original_filename="文档.pdf", file_path="/doc.pdf", category="document"),
            UploadFile(filename="img.jpg", original_filename="图片.jpg", file_path="/img.jpg", category="image"),
            UploadFile(filename="vid.mp4", original_filename="视频.mp4", file_path="/vid.mp4", category="video"),
            UploadFile(filename="file.zip", original_filename="压缩包.zip", file_path="/file.zip", category="archive"),
        ]
        
        test_db_session.add_all(files)
        test_db_session.commit()
        
        assert files[0].category == "document"
        assert files[1].category == "image"
        assert files[2].category == "video"
        assert files[3].category == "archive"


class TestSystemModelIndexes:
    """测试系统模型索引"""
    
    def test_menu_info_indexes(self):
        """测试菜单信息索引字段"""
        assert hasattr(MenuInfo, 'parent_id')
        assert hasattr(MenuInfo, 'menu_type')
        assert hasattr(MenuInfo, 'is_active')
    
    def test_system_config_indexes(self):
        """测试系统配置索引字段"""
        assert SystemConfig.key.unique is True
        assert hasattr(SystemConfig, 'category')
    
    def test_upload_file_indexes(self):
        """测试上传文件索引字段"""
        assert hasattr(UploadFile, 'uploader_id')
        assert hasattr(UploadFile, 'category')


class TestSystemModelIntegration:
    """测试系统模型集成功能"""
    
    def test_menu_hierarchy(self, test_db_session):
        """测试菜单层级结构"""
        # 创建菜单元数据
        meta1 = MenuMeta(title="系统管理")
        meta2 = MenuMeta(title="用户管理")
        meta3 = MenuMeta(title="用户列表")
        
        test_db_session.add_all([meta1, meta2, meta3])
        test_db_session.commit()
        
        # 创建菜单树：系统管理 -> 用户管理 -> 用户列表
        level1 = MenuInfo(name="System", path="/system", menu_type=0, meta_id=meta1.id)
        level2 = MenuInfo(name="UserManagement", path="/users", menu_type=1, meta_id=meta2.id)
        level3 = MenuInfo(name="UserList", path="/users/list", menu_type=1, meta_id=meta3.id)
        
        test_db_session.add_all([level1, level2, level3])
        test_db_session.commit()
        
        # 建立层级关系
        level2.parent_id = level1.id
        level3.parent_id = level2.id
        test_db_session.commit()
        
        # 验证层级关系
        assert level2.parent == level1
        assert level3.parent == level2
        assert level2 in level1.children
        assert level3 in level2.children
        assert len(level1.children) == 1
        assert len(level2.children) == 1
        assert level1.meta.title == "系统管理"
        assert level2.meta.title == "用户管理"
        assert level3.meta.title == "用户列表"
    
    def test_user_with_multiple_configs(self, test_db_session):
        """测试用户拥有多个个人配置"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        configs = [
            UserPersonalConfig(user_id=user.id, key="theme", name="主题", value="dark"),
            UserPersonalConfig(user_id=user.id, key="language", name="语言", value="zh-CN"),
            UserPersonalConfig(user_id=user.id, key="pageSize", name="分页大小", value="20"),
        ]
        
        test_db_session.add_all(configs)
        test_db_session.commit()
        
        # 验证配置
        for config in configs:
            assert config.user == user
        
        # 验证不同的配置键
        config_keys = {config.key for config in configs}
        assert config_keys == {"theme", "language", "pageSize"}
    
    def test_user_with_uploaded_files(self, test_db_session):
        """测试用户上传的多个文件"""
        user = UserInfo(username="testuser", password="password")
        test_db_session.add(user)
        test_db_session.commit()
        
        files = [
            UploadFile(filename="avatar.jpg", original_filename="头像.jpg", file_path="/avatar.jpg", uploader_id=user.id, category="image"),
            UploadFile(filename="resume.pdf", original_filename="简历.pdf", file_path="/resume.pdf", uploader_id=user.id, category="document"),
        ]
        
        test_db_session.add_all(files)
        test_db_session.commit()
        
        # 验证文件与用户关系
        for file in files:
            assert file.uploader == user
        
        # 验证不同文件类型
        file_categories = {file.category for file in files}
        assert file_categories == {"image", "document"}