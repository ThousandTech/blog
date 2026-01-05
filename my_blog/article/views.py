# 09 导入markdown
import markdown

from django.shortcuts import render,redirect

# 05 导入HttpResponse模块
# 10 引入重定向模块
from django.http import HttpResponse

# 10 引入ArticlePostForm表单类
from .forms import ArticlePostForm

# 10 引入User模型
from django.contrib.auth.models import User

# 06 导入数据模型
from .models import ArticlePost

# 05 主页视图函数，返回HttpResponse对象或者抛出异常，request参数与请求类型有关
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

# 08 文章详情视图函数，需要参数id以得到确切的文章
def article_detail(request,id):

    article = ArticlePost.objects.get(id=id)

    # 09 将article.body由markdown转为html
    article.body = markdown.markdown(article.body,
                                    extensions=[
                                        'markdown.extensions.extra',
                                        'markdown.extensions.codehilite',
                                    ])

    context = {'article':article}

    return render(request,'article/detail.html',context)

# 10 写文章视图函数
def article_create(request):
    # 10 如果用户提交数据
    if request.method == "POST":
        # 10 将收到的表单数据(类字典对象)存进article_post_form
        article_post_form = ArticlePostForm(data=request.POST)
        # 10 如果表单内容合法
        if article_post_form.is_valid():
            # 10 生成不写入数据库的ArticlePost实例
            new_article = article_post_form.save(commit=False)
            # 10 修改作者为1
            new_article.author = User.objects.get(id=1)
            # 10 保存文件到数据库
            new_article.save()
            # 10 重定向到文章列表
            return redirect("article:article_list")
        # 10 如果表单数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写")
    # 10 如果用户请求获取数据
    else:
        # 10 实例化表单类
        article_post_form = ArticlePostForm()
        # 10 上下文，模板会用前面的名字找后面的对象
        context = {'article_post_form':article_post_form}
        return render(request,'article/create.html',context)
    
# 11 删除文章视图函数(不安全)
# def article_delete(request,id):
#     # 11 得到对应的文章
#     article = ArticlePost.objects.get(id=id)
#     # 11 删除文章
#     article.delete()
#     # 11 重定向到文章列表页
#     return redirect("article:article_list")

# 11 删除文章视图函数(安全)
def article_safe_delete(request,id):
    if request.method == "POST":
        # 11 得到对应的文章
        article = ArticlePost.objects.get(id=id)
        # 11 删除文章
        article.delete()
        # 11 重定向到文章列表页
        return redirect("article:article_list")
    else:
        return HttpResponse("删除操作仅允许POST请求")