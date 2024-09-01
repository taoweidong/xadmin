#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : server
# filename : permission
# author : ly_13
# date : 6/16/2023
import logging

from django_filters import rest_framework as filters

from common.core.filter import BaseFilterSet
from common.core.modelset import BaseModelSet, ImportExportDataAction
from system.models import DataPermission
from system.serializers.permission import DataPermissionSerializer

logger = logging.getLogger(__name__)


class DataPermissionFilter(BaseFilterSet):
    pk = filters.UUIDFilter(field_name='id')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = DataPermission
        fields = ['pk', 'name', 'mode_type', 'is_active', 'description']


class DataPermissionView(BaseModelSet, ImportExportDataAction):
    """数据权限管理"""
    queryset = DataPermission.objects.all()
    serializer_class = DataPermissionSerializer
    ordering_fields = ['created_time']
    filterset_class = DataPermissionFilter
