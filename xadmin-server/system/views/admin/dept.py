#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : server
# filename : dept
# author : ly_13
# date : 6/16/2023
import logging

from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema

from common.base.utils import get_choices_dict
from common.core.modelset import BaseModelSet
from common.core.pagination import DynamicPageNumber
from common.core.response import ApiResponse
from system.models import DeptInfo
from system.utils.modelset import ChangeRolePermissionAction
from system.utils.serializer import DeptSerializer

logger = logging.getLogger(__name__)


class DeptFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    pk = filters.CharFilter(field_name='id')

    class Meta:
        model = DeptInfo
        fields = ['pk', 'is_active', 'code', 'mode_type', 'auto_bind']


# 导入django装饰器
from django.utils.decorators import method_decorator


@method_decorator(name='list',
                  decorator=swagger_auto_schema(operation_summary='查询数据', operation_description='查询所有数据'))
@method_decorator(name='create',
                  decorator=swagger_auto_schema(operation_summary='新增数据', operation_description='新增数据'))
@method_decorator(name='destroy',
                  decorator=swagger_auto_schema(operation_summary='删除数据', operation_description='删除指定数据'))
class DeptView(BaseModelSet, ChangeRolePermissionAction):
    """
    部门信息管理
    """
    queryset = DeptInfo.objects.all()
    serializer_class = DeptSerializer
    pagination_class = DynamicPageNumber(1000)

    ordering_fields = ['created_time', 'rank']
    filterset_class = DeptFilter

    def list(self, request, *args, **kwargs):
        data = super().list(request, *args, **kwargs).data
        return ApiResponse(**data, choices_dict=get_choices_dict(DeptInfo.ModeChoices.choices))
