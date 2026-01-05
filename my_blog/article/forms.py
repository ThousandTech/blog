# 10 引入表单类
from django import forms
# 10 引入文章模型
from .models import ArticlePost

# 10 文章表单类
class ArticlePostForm(forms.ModelForm):
    class Meta:
        # 10 指明数据模型来源
        model = ArticlePost
        # 10 定义表单包含的字段
        # 10 就是给表单类指定一个模型，指定表单中可被修改的字段，被指定的字段会校验类型
        fields = ('title','body')
