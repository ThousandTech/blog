from django.db import models
from django.contrib.auth.models import User
from article.models import ArticlePost

# Create your models here.
class Comment(models.Model):
    article = models.ForeignKey(
        ArticlePost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    body = models.TextField()
    # 24 自动设置为当前时间
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('created',)
    
    def __str__(self):
        # 24 返回前20个字符
        return self.body[:20]