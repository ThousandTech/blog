from django.urls import path
from . import views

app_name = 'user_profile'

urlpatterns = [
    # 13 用户登录路由
    path('login/',views.user_login,name='login'),
    # 13 用户退出路由
    path('logout/',views.user_logout,name='logout'),
    # 14 用户注册路由
    path('register/',views.user_register,name='register'),
]