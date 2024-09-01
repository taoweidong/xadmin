#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : common
# author : ly_13
# date : 6/7/2024
import uuid

from django.utils import translation
from drf_spectacular.plumbing import build_object_type, build_basic_type, build_array_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiRequest
from rest_framework.generics import GenericAPIView

from common.cache.storage import CommonResourceIDsCache
from common.core.response import ApiResponse
from common.swagger.utils import get_default_response_schema
from common.utils.country import COUNTRY_CALLING_CODES, COUNTRY_CALLING_CODES_ZH


class ResourcesIDCacheApi(GenericAPIView):
    """资源ID 缓存"""

    @extend_schema(
        description='将资源数据临时保存到服务器',
        request=OpenApiRequest(
            build_object_type(
                properties={'resources': build_array_type(build_basic_type(OpenApiTypes.STR))},
                required=['resources'],
                description="主键列表"
            )
        ),
        responses=get_default_response_schema({'spm': build_basic_type(OpenApiTypes.STR)})
    )
    def post(self, request, *args, **kwargs):
        spm = str(uuid.uuid4())
        resources = request.data.get('resources')
        if resources is not None:
            CommonResourceIDsCache(spm).set_storage_cache(resources, 300)
        return ApiResponse(spm=spm)


class CountryListApi(GenericAPIView):
    """城市列表"""
    permission_classes = []

    @extend_schema(
        description="获取城市手机号列表",
        responses=get_default_response_schema(
            {
                'data': build_array_type(
                    build_object_type(
                        properties={
                            'name': build_basic_type(OpenApiTypes.STR),
                            'phone_code': build_basic_type(OpenApiTypes.STR),
                            'flag': build_basic_type(OpenApiTypes.STR),
                            'code': build_basic_type(OpenApiTypes.STR)
                        }
                    )
                )
            }
        )
    )
    def get(self, request, *args, **kwargs):
        current_lang = translation.get_language()
        if current_lang == 'zh-hans':
            return ApiResponse(data=COUNTRY_CALLING_CODES_ZH)
        else:
            return ApiResponse(data=COUNTRY_CALLING_CODES)
