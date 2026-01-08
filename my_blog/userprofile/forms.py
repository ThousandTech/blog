# 13 表单类
from django import forms
# 13 用户模型
from django.contrib.auth.models import User

# 13 登录表单 继承forms.Form类，不对数据库进行修改，需手动配置每个字段的类型
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()