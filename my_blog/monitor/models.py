from django.db import models
from django.utils import timezone
class TerminalMonitor(models.Model):
    """终端监控模型"""
    # IMEI
    imei = models.CharField(max_length=15)
    # 电量百分比
    percent = models.IntegerField()
    # 是否充电
    is_charging = models.BooleanField()
    # 忙碌时间 
    busy_time = models.IntegerField()
    # 运行时间
    up_time = models.IntegerField(default=0)
    # 记录时间
    created = models.DateTimeField(default=timezone.now)