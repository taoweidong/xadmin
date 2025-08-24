"""
测试 app.schemas.base 模块
"""
import pytest
from typing import List, Dict, Any
from pydantic import ValidationError
from datetime import datetime
from app.schemas.base import (
    BaseSchema,
    TimestampSchema,
    BaseResponse,
    ListResponse,
    PaginationParams,
    SearchParams,
    IDRequest,
    IDListRequest,
    BatchDeleteRequest,
    ChoiceItem,
    ChoicesResponse,
    FieldInfo,
    SearchFieldsResponse,
    ColumnInfo,
    SearchColumnsResponse,
    StatusResponse,
    ExportParams,
    ImportParams,
)


class TestBaseSchema:
    """测试基础Schema"""
    
    def test_base_schema_creation(self):
        """测试基础Schema创建"""
        # 创建一个继承BaseSchema的测试类
        class TestModel(BaseSchema):
            name: str
            age: int
        
        data = {"name": "test", "age": 25}
        model = TestModel(**data)
        
        assert model.name == "test"
        assert model.age == 25
        assert model.model_config["from_attributes"] is True
        assert model.model_config["arbitrary_types_allowed"] is True
    
    def test_base_schema_from_attributes(self):
        """测试从属性创建"""
        class TestModel(BaseSchema):
            name: str
            value: int
        
        # 模拟一个对象
        class MockObject:
            def __init__(self):
                self.name = "test"
                self.value = 100
        
        obj = MockObject()
        model = TestModel.model_validate(obj)
        
        assert model.name == "test"
        assert model.value == 100


class TestTimestampSchema:
    """测试时间戳Schema"""
    
    def test_timestamp_schema_creation(self):
        """测试时间戳Schema创建"""
        now = datetime.now()
        schema = TimestampSchema(created_at=now, updated_at=now)
        
        assert schema.created_at == now
        assert schema.updated_at == now
    
    def test_timestamp_schema_optional_fields(self):
        """测试时间戳Schema可选字段"""
        schema = TimestampSchema()
        
        assert schema.created_at is None
        assert schema.updated_at is None


class TestBaseResponse:
    """测试基础响应模型"""
    
    def test_base_response_default_values(self):
        """测试基础响应默认值"""
        response = BaseResponse()
        
        assert response.code == 1000
        assert response.detail == "success"
        assert response.data is None
    
    def test_base_response_with_data(self):
        """测试带数据的基础响应"""
        data = {"id": 1, "name": "test"}
        response = BaseResponse[Dict[str, Any]](data=data)
        
        assert response.code == 1000
        assert response.detail == "success"
        assert response.data == data
    
    def test_base_response_custom_values(self):
        """测试自定义基础响应值"""
        response = BaseResponse(
            code=500,
            detail="error",
            data="error message"
        )
        
        assert response.code == 500
        assert response.detail == "error"
        assert response.data == "error message"
    
    def test_base_response_generic_typing(self):
        """测试基础响应泛型类型"""
        # 字符串类型
        str_response = BaseResponse[str](data="test string")
        assert str_response.data == "test string"
        
        # 列表类型
        list_response = BaseResponse[List[int]](data=[1, 2, 3])
        assert list_response.data == [1, 2, 3]
        
        # 字典类型
        dict_response = BaseResponse[Dict[str, str]](data={"key": "value"})
        assert dict_response.data == {"key": "value"}


class TestListResponse:
    """测试列表响应模型"""
    
    def test_list_response_default_values(self):
        """测试列表响应默认值"""
        response = ListResponse()
        
        assert response.code == 1000
        assert response.detail == "success"
        assert response.data is None
    
    def test_list_response_with_pagination_data(self):
        """测试带分页数据的列表响应"""
        data = {
            "results": [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}],
            "total": 2,
            "page": 1,
            "size": 20,
            "pages": 1
        }
        response = ListResponse(data=data)
        
        assert response.code == 1000
        assert response.detail == "success"
        assert response.data == data
        assert response.data["total"] == 2
        assert len(response.data["results"]) == 2


class TestPaginationParams:
    """测试分页参数"""
    
    def test_pagination_params_default_values(self):
        """测试分页参数默认值"""
        params = PaginationParams()
        
        assert params.page == 1
        assert params.size == 20
        assert params.ordering is None
    
    def test_pagination_params_custom_values(self):
        """测试自定义分页参数"""
        params = PaginationParams(
            page=2,
            size=50,
            ordering="-created_at"
        )
        
        assert params.page == 2
        assert params.size == 50
        assert params.ordering == "-created_at"
    
    def test_pagination_params_validation(self):
        """测试分页参数验证"""
        # 测试页码必须大于0
        with pytest.raises(ValidationError):
            PaginationParams(page=0)
        
        # 测试页面大小必须在1-100之间
        with pytest.raises(ValidationError):
            PaginationParams(size=0)
        
        with pytest.raises(ValidationError):
            PaginationParams(size=101)
    
    def test_pagination_params_valid_range(self):
        """测试分页参数有效范围"""
        # 最小值
        params_min = PaginationParams(page=1, size=1)
        assert params_min.page == 1
        assert params_min.size == 1
        
        # 最大值
        params_max = PaginationParams(page=999999, size=100)
        assert params_max.page == 999999
        assert params_max.size == 100


class TestSearchParams:
    """测试搜索参数"""
    
    def test_search_params_inheritance(self):
        """测试搜索参数继承"""
        params = SearchParams(
            page=2,
            size=30,
            ordering="name",
            search="test"
        )
        
        # 继承的分页参数
        assert params.page == 2
        assert params.size == 30
        assert params.ordering == "name"
        
        # 新增的搜索参数
        assert params.search == "test"
    
    def test_search_params_default_search(self):
        """测试搜索参数默认搜索值"""
        params = SearchParams()
        assert params.search is None


class TestIDRequest:
    """测试ID请求模型"""
    
    def test_id_request_creation(self):
        """测试ID请求创建"""
        request = IDRequest(id=123)
        assert request.id == 123
    
    def test_id_request_validation(self):
        """测试ID请求验证"""
        # 必须提供ID
        with pytest.raises(ValidationError):
            IDRequest()


class TestIDListRequest:
    """测试ID列表请求模型"""
    
    def test_id_list_request_creation(self):
        """测试ID列表请求创建"""
        request = IDListRequest(ids=[1, 2, 3])
        assert request.ids == [1, 2, 3]
    
    def test_id_list_request_empty_list(self):
        """测试空ID列表请求"""
        request = IDListRequest(ids=[])
        assert request.ids == []
    
    def test_id_list_request_validation(self):
        """测试ID列表请求验证"""
        # 必须提供IDs列表
        with pytest.raises(ValidationError):
            IDListRequest()


class TestBatchDeleteRequest:
    """测试批量删除请求模型"""
    
    def test_batch_delete_request_creation(self):
        """测试批量删除请求创建"""
        request = BatchDeleteRequest(pks=[1, 2, 3, 4, 5])
        assert request.pks == [1, 2, 3, 4, 5]
    
    def test_batch_delete_request_validation(self):
        """测试批量删除请求验证"""
        # 必须提供pks列表
        with pytest.raises(ValidationError):
            BatchDeleteRequest()


class TestChoiceItem:
    """测试选择项模型"""
    
    def test_choice_item_creation(self):
        """测试选择项创建"""
        item = ChoiceItem(
            label="启用",
            value=True,
            disabled=False
        )
        
        assert item.label == "启用"
        assert item.value is True
        assert item.disabled is False
    
    def test_choice_item_default_disabled(self):
        """测试选择项默认禁用状态"""
        item = ChoiceItem(label="选项", value="value")
        assert item.disabled is False
    
    def test_choice_item_any_value_type(self):
        """测试选择项支持任意值类型"""
        items = [
            ChoiceItem(label="字符串", value="string"),
            ChoiceItem(label="数字", value=123),
            ChoiceItem(label="布尔", value=True),
            ChoiceItem(label="列表", value=[1, 2, 3]),
            ChoiceItem(label="字典", value={"key": "value"}),
        ]
        
        assert items[0].value == "string"
        assert items[1].value == 123
        assert items[2].value is True
        assert items[3].value == [1, 2, 3]
        assert items[4].value == {"key": "value"}


class TestChoicesResponse:
    """测试选择项响应模型"""
    
    def test_choices_response_creation(self):
        """测试选择项响应创建"""
        data = {
            "gender": [
                ChoiceItem(label="男", value=1),
                ChoiceItem(label="女", value=2),
            ],
            "status": [
                ChoiceItem(label="启用", value=True),
                ChoiceItem(label="禁用", value=False),
            ]
        }
        
        response = ChoicesResponse(data=data)
        
        assert response.code == 1000
        assert response.detail == "success"
        assert "gender" in response.data
        assert "status" in response.data
        assert len(response.data["gender"]) == 2
        assert len(response.data["status"]) == 2


class TestFieldInfo:
    """测试字段信息模型"""
    
    def test_field_info_creation(self):
        """测试字段信息创建"""
        choices = [
            ChoiceItem(label="选项1", value=1),
            ChoiceItem(label="选项2", value=2),
        ]
        
        field = FieldInfo(
            name="status",
            label="状态",
            field_type="select",
            required=True,
            choices=choices
        )
        
        assert field.name == "status"
        assert field.label == "状态"
        assert field.field_type == "select"
        assert field.required is True
        assert field.choices == choices
    
    def test_field_info_optional_fields(self):
        """测试字段信息可选字段"""
        field = FieldInfo(
            name="description",
            label="描述",
            field_type="text"
        )
        
        assert field.required is False  # 默认非必填
        assert field.choices is None  # 默认无选择项


class TestColumnInfo:
    """测试列信息模型"""
    
    def test_column_info_creation(self):
        """测试列信息创建"""
        column = ColumnInfo(
            prop="name",
            label="姓名",
            width=150,
            sortable=True,
            searchable=True,
            fixed="left"
        )
        
        assert column.prop == "name"
        assert column.label == "姓名"
        assert column.width == 150
        assert column.sortable is True
        assert column.searchable is True
        assert column.fixed == "left"
    
    def test_column_info_default_values(self):
        """测试列信息默认值"""
        column = ColumnInfo(prop="id", label="ID")
        
        assert column.width is None
        assert column.sortable is False
        assert column.searchable is False
        assert column.fixed is None


class TestStatusResponse:
    """测试状态响应模型"""
    
    def test_status_response_creation(self):
        """测试状态响应创建"""
        response = StatusResponse(
            code=200,
            detail="操作成功",
            success=True
        )
        
        assert response.code == 200
        assert response.detail == "操作成功"
        assert response.success is True
    
    def test_status_response_error(self):
        """测试错误状态响应"""
        response = StatusResponse(
            code=400,
            detail="操作失败",
            success=False
        )
        
        assert response.code == 400
        assert response.detail == "操作失败"
        assert response.success is False


class TestExportParams:
    """测试导出参数"""
    
    def test_export_params_default_values(self):
        """测试导出参数默认值"""
        params = ExportParams()
        
        assert params.export_type == "xlsx"
        assert params.fields is None
    
    def test_export_params_custom_values(self):
        """测试自定义导出参数"""
        params = ExportParams(
            export_type="csv",
            fields=["id", "name", "email"]
        )
        
        assert params.export_type == "csv"
        assert params.fields == ["id", "name", "email"]


class TestImportParams:
    """测试导入参数"""
    
    def test_import_params_default_action(self):
        """测试导入参数默认动作"""
        params = ImportParams(file_url="/uploads/data.xlsx")
        
        assert params.action == "check"
        assert params.file_url == "/uploads/data.xlsx"
    
    def test_import_params_custom_action(self):
        """测试自定义导入动作"""
        params = ImportParams(
            action="import",
            file_url="/uploads/data.xlsx"
        )
        
        assert params.action == "import"
        assert params.file_url == "/uploads/data.xlsx"
    
    def test_import_params_validation(self):
        """测试导入参数验证"""
        # 必须提供文件URL
        with pytest.raises(ValidationError):
            ImportParams()


class TestSchemaIntegration:
    """测试Schema集成功能"""
    
    def test_nested_response_models(self):
        """测试嵌套响应模型"""
        # 创建字段信息列表
        fields = [
            FieldInfo(name="id", label="ID", field_type="number"),
            FieldInfo(name="name", label="姓名", field_type="text", required=True),
        ]
        
        # 创建搜索字段响应
        response = SearchFieldsResponse(data=fields)
        
        assert response.code == 1000
        assert response.detail == "success"
        assert len(response.data) == 2
        assert response.data[0].name == "id"
        assert response.data[1].required is True
    
    def test_generic_response_with_complex_data(self):
        """测试泛型响应与复杂数据"""
        # 创建复杂的列表数据
        list_data = {
            "results": [
                {"id": 1, "name": "项目1", "status": "active"},
                {"id": 2, "name": "项目2", "status": "inactive"},
            ],
            "total": 2,
            "page": 1,
            "size": 20,
            "pages": 1
        }
        
        response = ListResponse[Dict[str, Any]](data=list_data)
        
        assert response.code == 1000
        assert response.data["total"] == 2
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["name"] == "项目1"
    
    def test_schema_serialization(self):
        """测试Schema序列化"""
        response = BaseResponse[Dict[str, Any]](
            code=1000,
            detail="success",
            data={"message": "test"}
        )
        
        # 转换为字典
        data = response.model_dump()
        
        assert data["code"] == 1000
        assert data["detail"] == "success"
        assert data["data"]["message"] == "test"
    
    def test_schema_json_serialization(self):
        """测试Schema JSON序列化"""
        params = PaginationParams(page=2, size=30, ordering="-created_at")
        
        # 转换为JSON字符串
        json_str = params.model_dump_json()
        
        # JSON应该包含所有字段
        assert '"page":2' in json_str
        assert '"size":30' in json_str
        assert '"-created_at"' in json_str