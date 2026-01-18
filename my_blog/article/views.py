# 09 导入markdown
import markdown
import json

from django.shortcuts import render,redirect

from django.conf import settings

# 05 导入HttpResponse模块
# 10 引入重定向模块
from django.http import HttpResponse, JsonResponse

# 10 引入ArticlePostForm表单类
from .forms import ArticlePostForm

# 10 引入User模型
from django.contrib.auth.models import User
# 17 引入登录检查装饰器
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# 06 导入数据模型
from .models import ArticlePost,ArticleColumn,TerminalMonitor

# 19 分页模块
from django.core.paginator import Paginator

# 22 用来查询的Q对象
from django.db.models import Q

# 24 评论模型
from comment.models import Comment

# 05 主页视图函数，返回HttpResponse对象或者抛出异常，request参数与请求类型有关
def article_list(request):
    # # 05 返回最简单的网页
    # return HttpResponse("Hello World!")
    order = request.GET.get('order')
    # 22 搜索参数
    search = request.GET.get('search')
    # 27 专栏参数
    column_id = request.GET.get('column')
    # 28 标签参数
    tag = request.GET.get('tag')
    # if search:
    #     if column_id:
    #         if order == 'total_views':
    #             article_list = ArticlePost.objects.filter(
    #                 # 22 忽略大小写查询数据库，标题或正文有关键词就被选出
    #                 Q(title__icontains=search)|
    #                 Q(body__icontains=search),
    #                 column = ArticleColumn.objects.get(id=column_id)
    #             ).order_by('-total_views')
    #         else:
    #             article_list = ArticlePost.objects.filter(
    #                 Q(title__icontains=search)|
    #                 Q(body__icontains=search),
    #                 column = ArticleColumn.objects.get(id=column_id)
    #             )
    #             order = 'normal'
    # else:
    #     # 22 没有搜索参数会返回None，此处将search置为空字符串，防止检索None这个字符串
    #     search = ''
    #     # 21 根据不同的参数返回不同顺序的列表
    #     if order == 'total_views':
    #         article_list = ArticlePost.objects.all().order_by('-total_views')
    #     else:
    #         article_list = ArticlePost.objects.all()
    #         order = 'normal'
    article_list = ArticlePost.objects.all()

    # 1. 搜索
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    # 2. 栏目
    if column_id == 'uncategorized':
        # 27 找到所有没有专栏的文章
        article_list = article_list.filter(column__isnull=True)
    elif column_id and column_id != 'None':
        article_list = article_list.filter(column=ArticleColumn.objects.get(id=column_id))


    if tag and tag != 'None':
        # 28 如果有文章标签的名称在给定的列表中
        article_list = article_list.filter(tags__name__in=[tag])

    # 3. 排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')
    else:
        article_list = article_list.order_by('-updated')
        order = 'normal'


    # 19 每页3篇文章
    paginator = Paginator(article_list,6)
    # 19 从url中'?page=value'中获取page的值，没有这个会直接返回None
    page = request.GET.get('page')
    # 19 将页码对应的文章返回给articles，page为None返回1
    articles = paginator.get_page(page)
    columns = ArticleColumn.objects.all()
    uncategorized_count = ArticlePost.objects.filter(column__isnull=True).count()
    # 28 获取所有标签
    all_tags = ArticlePost.tags.all()
    # 获取Thousand用户信息用于个人卡片展示
    try:
        profile_user = User.objects.get(id=6)
    except User.DoesNotExist:
        profile_user = None
    # 06 context字典定义了要传递给模板的上下文
    # 21 order用来传递给模板，在切换页时保持不同的排序
    context = {'articles':articles,
               'order':order,
               'search':search,
               'columns':columns,
               'column':column_id,
               'uncategorized_count':uncategorized_count,
               'profile_user':profile_user,
               'tag':tag,
               'all_tags':all_tags}
    # 06 render函数结合模板与上下文并返回渲染后的HttpResponse对象
    # 06 render的三个参数分别为固定的request，模板文件，传入模板文件的上下文（字典）
    return render(request,'article/list.html',context)

# 08 文章详情视图函数，需要参数id以得到确切的文章
def article_detail(request,id):

    article = ArticlePost.objects.get(id=id)
    # 24 取出所有此文章的评论
    comments = Comment.objects.filter(article=id)

    article.total_views += 1
    article.save(update_fields=['total_views'])

    # 09 将article.body由markdown转为html
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            # 23 目录扩展
            'markdown.extensions.toc',
        ])
    
    article.body = md.convert(article.body)

    context = {'article':article,'toc':md.toc,'comments':comments}

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
            # 27 如果有栏目信息
            if request.POST['column']!='none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 10 修改作者为1
            # 17 指定作者id
            new_article.author = User.objects.get(id=request.user.id)
            # 10 保存文件到数据库
            new_article.save()
            # 27 保存tags的多对多关系，new_article主键在save()后才生成，
            # 无法同时构建多对多关系，因此需要额外保存一次
            # 27 表单实例处理多对多关系
            article_post_form.save_m2m()
            # 10 重定向到文章列表
            return redirect("article:article_list")
        # 10 如果表单数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写")
    # 10 如果用户请求获取数据
    else:
        # 10 实例化表单类
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 10 上下文，模板会用前面的名字找后面的对象
        context = {'article_post_form':article_post_form,'columns':columns}
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
            # 12 存储收到的表单数据，绑定到现有的 article 实例
            article_post_form = ArticlePostForm(data=request.POST, instance=article)
            # 12 如果数据均合法
            if article_post_form.is_valid():
                # 12 更新数据但不立即保存到数据库
                article = article_post_form.save(commit=False)
                # 28 处理栏目
                if request.POST['column']!='none':
                    article.column = ArticleColumn.objects.get(id=request.POST['column'])
                else:
                    article.column = None
                article.save()
                # 28 保存多对多关系（tags），必须在 save() 之后调用
                article_post_form.save_m2m()
                # 12 重定向至对应id的文章详情页
                return redirect("article:article_detail",id=id)
            # 12 如果数据不合法
            else:
                return HttpResponse("表单内容有误，请重新填写")
        # 12 如果是get请求
        else:
            article_post_form = ArticlePostForm()
            columns= ArticleColumn.objects.all()
            
            # 28 将 tags 的 queryset 对象转换为字符串，传递到模板
            tags = ','.join([x for x in article.tags.names()])

            context = {'article':article,'article_post_form':article_post_form,'columns':columns,'tags':tags}
            return render(request,'article/update.html',context)
    else:
            return HttpResponse("编辑操作仅允许作者本人和管理员使用")

@csrf_exempt
def terminal_status_receive(request):
    if request.method == 'POST':
        terminal_status = json.loads(request.body)
        if terminal_status['imei'] in settings.ALLOWED_IMEI:
            TerminalMonitor.objects.create(
                imei = terminal_status['imei'],
                percent = terminal_status['percent'],
                is_charging = (str(terminal_status['charging'])=='1'),
                busy_time = terminal_status['busy'],
                up_time = terminal_status.get('uptime', 0)
            )

            return HttpResponse('ok')
        else:
            return HttpResponse('不接受此终端的上报,请联系管理员')
    else:
        return HttpResponse('终端状态上报仅允许POST请求')

from django.utils import timezone

def terminal_status_latest(request):
    latest_status = TerminalMonitor.objects.order_by('-created').first()
    if latest_status:
        # 转换为本地时间
        created_local = timezone.localtime(latest_status.created)
        
        # 计算是否超时（例如5分钟无上报视为离线）
        time_diff = (timezone.now() - latest_status.created).total_seconds()
        is_offline = time_diff > 300  # 300秒 = 5分钟
        
        data = {
            'percent': latest_status.percent,
            'is_charging': latest_status.is_charging,
            'busy_time': latest_status.busy_time,
            'up_time': latest_status.up_time,
            'created': created_local.strftime('%Y-%m-%d %H:%M:%S'),
            'is_offline': is_offline,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No data'}, status=404)