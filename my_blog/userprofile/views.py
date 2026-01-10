from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
# 15 引入验证登录的装饰器
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import UserLoginForm,UserRegisterForm,ProfileForm
from .models import Profile

# Create your views here.

def user_login(request):
    # 13 如果是POST请求
    if request.method == 'POST':
        # 13 实例化表单并将所有post请求发来的字典对象装进去
        user_login_form = UserLoginForm(data=request.POST)
        # 13 如果字段都合法
        if user_login_form.is_valid():
            # 13 清洗数据，避免sql注入或者多余空格
            data = user_login_form.cleaned_data
            # 13 进入数据库验证用户名和密码对，匹配成功返回user对象，不成功返回None
            user = authenticate(username = data['username'],password = data['password'])
            # 13 如果匹配成功
            if user:
                # 13 保持登陆状态，服务端生成一个session并给客户端发一个含有session ID的Cookie
                login(request,user)
                # 13 重定向至文章列表页
                return redirect("article:article_list")
            else:
                return HttpResponse("账号或密码不正确，请重试")
        # 13 如果有字段不合法
        else:
            return HttpResponse("账号或密码输入不合法")
    # 13 如果是GET请求
    elif request.method == "GET":
        user_login_form = UserLoginForm()
        context = {'form':user_login_form}
        return render(request,'userprofile/login.html',context)
    else:
        return HttpResponse("请使用GET或POST请求数据")
        
def user_logout(request):
    # 13 除掉请求中的Session ID并让后端Session过期
    logout(request)
    return redirect("article:article_list")

def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            # 14 现在不能写入，密码是明文，先暂存
            new_user = user_register_form.save(commit=False)
            # 14 密码哈希
            new_user.set_password(user_register_form.cleaned_data['password'])
            # 14 写入数据库
            new_user.save()
            # 14 注册后立即登录并转到文章列表页
            login(request,new_user)
            return redirect("article:article_list")
        else:
            return HttpResponse("用户名，邮箱或密码不合法，请重试")
    elif request.method == 'GET':
        # 14 创建空表单并通过上下文传给模板
        user_register_form = UserRegisterForm()
        context = {'form':user_register_form}
        return render(request,'userprofile/register.html',context)
    else:
        return HttpResponse("请使用GET或POST请求数据")

# 15 装饰器，用户已登录则执行下面的删除函数，未登录则跳转至登录页
@login_required(login_url = '/userprofile/login/')
def user_delete(request,id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        # 15 仅能注销自己的帐号，request.user是django根据请求中的id自动从数据库查出来的User实例
        if request.user == user:
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("无删除权限")
    else:
        return HttpResponse("此操作仅接受POST请求")

# 17 修改用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request,id):
    user = User.objects.get(id=id)
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':

        if request.user != user:
            return HttpResponse("无修改此用户信息的权限")
        # 18 request.FILES上传的文件由此传递给表单类
        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            # 18 如果request.FILES中存在文件则保存文件地址
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd['avatar']
            profile.save()
            return redirect("userprofile:edit",id=id)
        else:
            return HttpResponse("电话，头像或简介不合法，请重试")
    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = { 'profile_form':profile_form,'profile':profile,'user':user}
        return render(request,'userprofile/edit.html',context)
    else:
        return HttpResponse("请使用GET或POST请求数据")