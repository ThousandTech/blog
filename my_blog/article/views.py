from django.shortcuts import render
# 05 导入HttpResponse模块
from django.http import HttpResponse

# 05 视图函数，返回HttpResponse对象或者抛出异常，request参数与请求类型有关
def article_list(request):
    # 05 返回最简单的网页
    return HttpResponse("Hello World!")