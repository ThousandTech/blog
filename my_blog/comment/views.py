from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from article.models import ArticlePost
from .models import Comment
from .forms import CommentForm

@login_required(login_url='/userprofile/login/')
def post_comment(request,article_id):
    # 24 找不到对应的文章对象时返回404而非500
    article = get_object_or_404(ArticlePost,id = article_id)
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user
            new_comment.save()
            # 24 重定向至对应文章的详情页，参数为model对象时会自动调用此对象的get_absolute_url函数
            return redirect(article)
        else:
            return HttpResponse("表单内容有误，请重新填写")
    else:
        return HttpResponse("此操作仅允许POST请求")
    
@login_required(login_url='/userprofile/login/')
def delete_comment(request,comment_id):
    comment = get_object_or_404(Comment,id = comment_id)
    article = get_object_or_404(ArticlePost,id = comment.article.id)
    if request.method == 'POST':
        if request.user == comment.user or request.user == article.author or request.user.is_superuser:
            comment.delete()
            return redirect(article)
        else:
            return HttpResponse('<script>alert("此操作仅允许评论者，文章作者与管理员使用");window.history.back();</script>')
    else:
        return HttpResponse('<script>alert("此操作仅允许POST请求");window.history.back();</script>')

