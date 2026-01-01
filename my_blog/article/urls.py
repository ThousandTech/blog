# 03article 自己的路由分发文件
from django.urls import path# 03引入path函数
from . import views

app_name = 'article'# 03设置命名空间

urlpatterns = [
    path('article-list',views.article_list,name='article_list')
    # 05 django根据url选择对应的视图函数，name相当于主键，使第一个参数即URL可以任意改变
]# 03定义一个空的路径映射列表