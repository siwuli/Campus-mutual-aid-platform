"""
URL configuration for campus_errand_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# myproject/urls.py

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from errands import views as errands_views
from backend import views as backend_views

# 默认首页视图
def index(request):
    return HttpResponse("<h1>欢迎访问华师校园悬赏系统</h1><p><a href='/api/'>访问 API</a></p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('errands.urls')),  # 包含 API 路由
    path('', errands_views.home, name='home'),  # 根路径默认视图
    path('backend/', include('backend.urls')),  # 后台管理路由
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:  # 仅在调试模式下启用
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)