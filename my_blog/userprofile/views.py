from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from .forms import UserLoginForm

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
    