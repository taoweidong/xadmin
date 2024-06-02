"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from common.celery.flower import CeleryFlowerView
from common.core.utils import auto_register_app_url
from common.utils.media import serve

schema_view = get_schema_view(
    openapi.Info(
        title="项目的API",
        default_version="v1",
        description="描述XXXXXXXXXXXXXXXXXXXXXXX",
        terms_of_service="xxxx===terms_of_service",
        contact=openapi.Contact(email="taoweidong@outlook.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('system_api/', include('system.urls')),
    re_path(r'api/flower/(?P<path>.*)', CeleryFlowerView.as_view(), name='flower-view'),
    # media路径配置 开发环境可以启动下面配置，正式环境需要让nginx读取资源，无需进行转发
    re_path('^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}, ),
    # 文档
    re_path(r"swagger(?P<format>\.json|\.yaml)", schema_view.without_ui(cache_timeout=0), name="schema-json", ),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui", ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

auto_register_app_url(urlpatterns)
