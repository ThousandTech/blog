# 09 导入markdown
import markdown

from django.shortcuts import render,redirect

# 05 导入HttpResponse模块
# 10 引入重定向模块
from django.http import HttpResponse,Http404  

# 10 引入ArticlePostForm表单类
from .forms import ArticlePostForm

# 10 引入User模型
from django.contrib.auth.models import User
# 17 引入登录检查装饰器
from django.contrib.auth.decorators import login_required

# 06 导入数据模型
from .models import ArticlePost

# 19 分页模块
from django.core.paginator import Paginator

# 22 用来查询的Q对象
from django.db.models import Q

# 05 主页视图函数，返回HttpResponse对象或者抛出异常，request参数与请求类型有关
def article_list(request):
    # # 05 返回最简单的网页
    # return HttpResponse("Hello World!")
    order = request.GET.get('order')
    # 22 搜索参数
    search = request.GET.get('search')
    if search:
        if order == 'total_views':
            article_list = ArticlePost.objects.filter(
                # 22 忽略大小写查询数据库，标题或正文有关键词就被选出
                Q(title__icontains=search)|
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search)|
                Q(body__icontains=search)
            )
            order = 'normal'
    else:
        # 22 没有搜索参数会返回None，此处将search置为空字符串，防止检索None这个字符串
        search = ''
        # 21 根据不同的参数返回不同顺序的列表
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()
            order = 'normal'

    # 19 每页3篇文章
    paginator = Paginator(article_list,3)
    # 19 从url中'?page=value'中获取page的值，没有这个会直接返回None
    page = request.GET.get('page')
    # 19 将页码对应的文章返回给articles，page为None返回1
    articles = paginator.get_page(page)
    # 06 context字典定义了要传递给模板的上下文
    # 21 order用来传递给模板，在切换页时保持不同的排序
    context = {'articles':articles,'order':order,'search':search}
    # 06 render函数结合模板与上下文并返回渲染后的HttpResponse对象
    # 06 render的三个参数分别为固定的request，模板文件，传入模板文件的上下文（字典）
    return render(request,'article/list.html',context)

# 08 文章详情视图函数，需要参数id以得到确切的文章
def article_detail(request,id):

    article = ArticlePost.objects.get(id=id)

    article.total_views += 1
    article.save(update_fields=['total_views'])

    # 09 将article.body由markdown转为html
    article.body = markdown.markdown(article.body,
                                    extensions=[
                                        'markdown.extensions.extra',
                                        'markdown.extensions.codehilite',
                                    ])

    context = {'article':article}

    return render(request,'article/detail.html',context)

# 10 写文章视图函数
@login_required(login_url='/userprofile/login/')
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
            # 17 指定作者id
            new_article.author = User.objects.get(id=request.user.id)
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
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request,id):
    if request.method == "POST":
        # 11 得到对应的文章
        article = ArticlePost.objects.get(id=id)
        # 17 仅允许作者或管理员删除
        if article.author == request.user or request.user.is_superuser:
            # 11 删除文章
            article.delete()
            # 11 重定向到文章列表页
            return redirect("article:article_list")
        else:
            return HttpResponse("删除操作仅允许作者本人和管理员使用")
    else:
        return HttpResponse("删除操作仅允许POST请求")
    
# 12 文章更新函数
@login_required(login_url='/userprofile/login/')
def article_update(request,id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """
    # 12 拿到要更改的文章对象
    article = ArticlePost.objects.get(id=id)

    if article.author == request.user or request.user.is_superuser:
        # 12 如果是POST请求
        if request.method == "POST":
            # 12 存储收到的表单数据
            article_post_form = ArticlePostForm(data=request.POST)
            # 12 如果数据均合法
            if article_post_form.is_valid():
                # 12 更新数据并保存
                article.title = request.POST['title']
                article.body = request.POST['body']
                article.save()
                # 12 重定向至对应id的文章详情页
                return redirect("article:article_detail",id=id)
            # 12 如果数据不合法
            else:
                return HttpResponse("表单内容有误，请重新填写")
        # 12 如果是get请求
        else:
            article_post_form = ArticlePostForm()
            context = {'article':article,'article_post_form':article_post_form}
            return render(request,'article/update.html',context)
    else:
            return HttpResponse("编辑操作仅允许作者本人和管理员使用")