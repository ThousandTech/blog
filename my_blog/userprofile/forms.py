# 13 表单类
from django import forms
# 13 用户模型
from django.contrib.auth.models import User
# 17 用户资料
from .models import Profile

# 13 登录表单，继承forms.Form类，不对数据库进行修改，需手动配置每个字段的类型
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

# 14 注册表单，继承forms.ModelForm类，直接读取User表的字段
class UserRegisterForm(forms.ModelForm):
    # 14 额外定义字段，覆盖默认行为
    password = forms.CharField()
    password2 = forms.CharField()
    # 14 元信息
    class Meta:
        # 14 数据模型
        model = User
        # 14 表单要填写的字段，不包含被覆盖的，因此这里没password
        fields = ('username','email')

    # 14 钩子函数，在验证数据时的最后自动调用，由于password2不是用户表中
    # 的字段，没有自己的清洗函数，会被django当成简单的字符串验证，导致密码始终不一致
    def clean_password2(self):
        data = self.cleaned_data
        if data.get('password') == data.get('password2'):
            # 14 稳妥取值写法
            return data.get('password')
        else:
            raise forms.ValidationError("两次密码输入不一致，请重试")
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone','avatar','bio')