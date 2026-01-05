# 03article 自己的路由分发文件
from django.urls import path# 03引入path函数
from . import views

app_name = 'article'# 03 设置命名空间

# 03定义一个空的路径映射列表
urlpatterns = [
    # 05 django根据url选择对应的视图函数，name相当于主键，使第一个参数即URL可以任意改变
    path('article-list/',views.article_list,name='article_list'),
    # 08 定义带参数的URL，用尖括号定义需要传递的参数，int限定参数类型，将值保存在id中并传递给后面的视图函数
    path('article-detail/<int:id>/',views.article_detail,name='article_detail'),
    # 10 写文章路由
    path('article-create/',views.article_create,name='article_create'),
    # 11 删除文章路由(不安全)
    # path('article-delete/<int:id>/',views.article_delete,name='article_delete'),
    # 11 删除文章路由(安全)
    path('article-safe-delete/<int:id>/',views.article_safe_delete,name='article_safe_delete'),
]