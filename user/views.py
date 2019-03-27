from django.shortcuts import render_to_response, render, redirect

from .forms import LoginForm, ReForm, ChangeNickForm, BindEmailForm, ChangePasswordForm,FogotPasswordForm
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
from django.http import JsonResponse
from django.core.mail import send_mail
import string
import random
import time
# 验证码
from django.http import JsonResponse
from captcha.models import CaptchaStore


def ajax_val(request):
    if request.is_ajax():
        cs = CaptchaStore.objects.filter(response=request.GET['response'], hashkey=request.GET['hashkey'])
        if cs:
            json_data = {'status': 1}
        else:
            json_data = {'status': 0}
        return JsonResponse(json_data)
    else:
        json_data = {'status': 0}
        return JsonResponse(json_data)


def login_for_modal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def login(request):
    '''username=request.POST.get('username','')
    password=request.POST.get('password','')
    user=auth.authenticate(request,username=username,password=password)
    referer=request.META.get('HTTP_REFERER',reverse('home'))#重定向页面
    if user is not None:
        auth.login(request,user)
        #如何返回到原来的页面，应该需要记录一下之前的页面
        return redirect(referer)
    else:
        return render(request,'error.html',{'message':'用户名或密码不正确'})
    '''
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():  # 是否验证通过
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:  # 非post请求
        login_form = LoginForm()  # 实例化
    context = {}
    context['login_form'] = login_form
    return render(request, 'user/login.html', context)


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))


def register(request):
    if request.method == 'POST':
        register_form = ReForm(request.POST, request=request)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password']
            email = register_form.cleaned_data['email']
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            # user=User.objects.create_user(username,email,password)
            user.save()
            # 清除session
            del request.session['bind_email_code']
            # 登录用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        register_form = ReForm()

    context = {}
    context['register_form'] = register_form
    return render(request, 'user/register.html', context)


def user_info(request):
    context = {}

    return render(request, 'user/user_info.html', context)


def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ChangeNickForm(request.POST, user=request.user)
        if form.is_valid():  # 对表单数据检验，检验通过
            nickname_new = form.cleaned_data['nickname_new']  # 获取新的昵称
            profile, created = Profile.objects.get_or_create(user=request.user)  # profile为一个对象；created为一个是否创建标记
            profile.nickname = nickname_new
            profile.save()
            auth.logout(request)
            return redirect(redirect_to)  # 返回到原来页面
    else:
        form = ChangeNickForm()  # GET请求
    context = {}
    context['form'] = form
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)


def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user, created = User.objects.get_or_create(username=request.user)
            user.set_password(new_password)
            user.save()
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()
    context = {}
    context['form'] = form
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)

def forgot_password(request):
    redirect_to = reverse('login')
    if request.method == 'POST':
        form = FogotPasswordForm(request.POST, request=request)
        if form.is_valid():  #
            email = form.cleaned_data['email']  # 获取email
            new_password=form.cleaned_data['new_password']
            user=User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            #清除session
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = FogotPasswordForm()
    context = {}
    context['form'] = form
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '重置'
    context['return_back_url'] = redirect_to
    return render(request, 'forgot_password.html', context)

def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():  #
            email = form.cleaned_data['email']  # 获取email
            request.user.email = email
            request.user.save()
            return redirect(redirect_to)
    else:
        form = BindEmailForm()
    context = {}
    context['form'] = form
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['return_back_url'] = redirect_to
    return render(request, 'bind_email.html', context)


# 发送验证码方法
def send_verfication_code(request):
    email = request.GET.get('email', '')  # 通过前端bind_email页面的js中ajax传过来
    send_for = request.GET.get('send_for', '')
    data = {}
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())  # 当前时间秒数

        send_code_time = request.session.get('send_code_time', 0)  # 获取send_code_time
        if now - send_code_time < 30:  # 如果两个相差在30s以内  不让他发送
            data['status'] = 'ERROR'
        else:
            request.session['bind_email_code'] = code  # 在session中记录验证码
            request.session['send_code_time'] = now
            # 发送邮件
            send_mail(
                '绑定邮箱',
                '验证码:%s' % code,
                'zhongyibei101@sina.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)
