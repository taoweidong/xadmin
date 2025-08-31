#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : modelset
# author : ly_13
# date : 12/24/2023
from django.utils.translation import gettext_lazy as _
from drf_spectacular.plumbing import build_object_type, build_basic_type, build_array_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiRequest
from rest_framework.decorators import action

from common.core.config import SysConfig, UserConfig
from common.core.response import ApiResponse
from common.swagger.utils import get_default_response_schema
from system.models import UserRole, SystemConfig


class ChangeRolePermissionAction(object):
    def get_object(self):
        raise NotImplementedError('get_object must be overridden')

    @extend_schema(
        description="分配角色",
        request=OpenApiRequest(
            build_object_type(
                required=['roles'],
                properties={
                    'roles': build_array_type(build_basic_type(OpenApiTypes.STR)),
                }
            )
        ),
        responses=get_default_response_schema()
    )
    @action(methods=['post'], detail=True)
    def empower(self, request, *args, **kwargs):
        instance = self.get_object()
        roles = request.data.get('roles')
        if roles is not None:
            instance.roles.set(
                UserRole.objects.filter(pk__in=[role.get('pk') for role in roles]).all())
            return ApiResponse()
        return ApiResponse(code=1004, detail=_(
            "Operation failed. Abnormal data"))


class InvalidConfigCacheAction(object):
    def get_object(self):
        raise NotImplementedError('get_object must be overridden')

    @extend_schema(
        description="使配置值缓存失效",
        request=None,
        responses=get_default_response_schema()
    )
    @action(methods=['post'], detail=True)
    def invalid(self, request, *args, **kwargs):
        instance = self.get_object()

        if isinstance(instance, SystemConfig):
            SysConfig.invalid_config_cache(key=instance.key)
            owner = '*'
        else:
            owner = instance.owner
        UserConfig(owner).invalid_config_cache(key=instance.key)
        return ApiResponse()
