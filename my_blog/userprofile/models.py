from django.db import models
from django.contrib.auth.models import User
# 17 引入内置信号
from django.db.models.signals import post_save
# 17 引入信号接收器的装饰器
from django.dispatch import receiver

# Create your models here.
# 17 用户扩展信息
class Profile(models.Model):
    # 17 一对一关联到内置User，用user.profile访问，删除用户时级联删除用户资料
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    # 17 字符串，可留空
    phone = models.CharField(max_length=20,blank=True)
    # 17 头像，路径avatar/YYYYMMDD/，可留空
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/',blank=True)
    # 17 个人简介，可留空
    bio = models.TextField(max_length=500,blank=True)
    # 17 将此对象转为字符串时调用此函数，格式user <username>
    def __str__(self):
        return 'user {}'.format(self.user.username)

# # 17 在User.save()调用时自动触发，instance为用户实例
# @receiver(post_save,sender=User)
# def create_user_profile(sender,instance,created,**kwargs):
#     # 17 创建用户时同时创建用户资料
#     if created:
#         Profile.objects.create(user = instance)

# @receiver(post_save,sender=User)
# def save_user_profile(sender,instance,**kwargs):
#     # 17 更新用户时同时更新用户资料
#     instance.profile.save()