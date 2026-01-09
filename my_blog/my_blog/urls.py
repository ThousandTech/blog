"""my_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include# 03引入include函数

urlpatterns = [
    path('admin/', admin.site.urls),
    # 03 告诉django怎样定位article应用
    # 03 'article/'参数分配了一个URL前缀给article应用
    # 03 include('article.urls', namespace='article')参数告诉Django去查找article应用下的urls.py文件
    # 03 namespace='article'参数为article应用指定了一个命名空间
    path('article/', include('article.urls', namespace='article')),
    # 13 用户管理根路由
    path('userprofile/',include('userprofile.urls',namespace='userprofile')),
    # 16 重置密码路由
    path('password-reset/',include('password_reset.urls')),
]
