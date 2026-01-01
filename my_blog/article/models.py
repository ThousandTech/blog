from django.db import models
from django.contrib.auth.models import User
# 04 导入内置的User模型
from django.utils import timezone
# 04 导入timezone模块以处理时间相关操作

class ArticlePost(models.Model):
    ## 04 定义文章表的结构
    # 04 文章作者，外键，on_delete参数使文章作者注销时一并删除此文章
    author = models.ForeignKey(User,on_delete=models.CASCADE)

    # 04 文章标题，charField为短字符串字段，max_length指定最大长度
    title = models.CharField(max_length=100)

    # 04 文章正文，textField保存大量文本
    body = models.TextField()

    # 04 文章创建时间，参数default指定创建时写入当前时间
    created = models.DateTimeField(default=timezone.now)

    # 04 文章更新时间，参数auto_now指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)

    ## 04 规范表行为
    # 04 内部类class meta用来给model定义元数据
    # 04 元数据是**“任何不是字段的东西”**，例如排序选项ordering、数据库表名db_table、单数和复数名称verbose_name和 verbose_name_plural。这些信息不是某篇文章私有的数据，而是整张表的共同行为。
    class meta:
        # 表示按创建顺序倒序输出
        ordering = ('-created')

    # 04 函数__str__定义返回值内容，在将对象转为字符串时自动调用
    def __str__(self):
        # 04 返回文章标题
        return self.title