from django.urls import path
from . import views

app_name = 'monitor'

urlpatterns = [
    path('info/', views.system_info, name='info'),
    path('state/', views.system_state_details, name='state'),
    # sp 终端上报路由
    path('terminal-receive/',views.terminal_status_receive,name='terminal_receive'),
    # sp 获取最新终端状态
    path('terminal-latest/',views.terminal_status_latest,name='terminal_latest'),
]
