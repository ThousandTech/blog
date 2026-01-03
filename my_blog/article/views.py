from django.shortcuts import render
# 05 导入HttpResponse模块
from django.http import HttpResponse

# 06 导入数据模型
from .models import ArticlePost

# 05 视图函数，返回HttpResponse对象或者抛出异常，request参数与请求类型有关
def article_list(request):
    # # 05 返回最简单的网页
    # return HttpResponse("Hello World!")
    # 06 从数据库取出所有的博客文章
    articles = ArticlePost.objects.all()
    # 06 context字典定义了要传递给模板的上下文
    context = {'articles':articles}
    # 06 render函数结合模板与上下文并返回渲染后的HttpResponse对象
    # 06 render的三个参数分别为固定的request，模板文件，传入模板文件的上下文（字典）
    return render(request,'article/list.html',context)