from django.contrib import admin

# 05 导入模型供后台管理
from .models import ArticlePost

# 05 注册ArticlePost到admin
admin.site.register(ArticlePost)
