from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from captcha.fields import CaptchaField


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label='用户名或邮箱',
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '请输入用户名或邮箱'}
        )
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': '请输入密码'}
        )
    )
    captcha = CaptchaField(label='验证码')

    def clean(self):  # 验证数据
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']

        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if not user is None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('用户名或密码错误')
        else:
            self.cleaned_data['user'] = user  # 传过去user
        return self.cleaned_data


class ReForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        max_length=30,
        min_length=3,
        widget=forms.TextInput({'class': 'form-control', 'placeholder': '请输入3-30位用户名'})
    )

    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'})
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )

    password = forms.CharField(
        label='密码',
        min_length=6,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': '请输入密码'}
        )
    )
    password_agin = forms.CharField(
        label='再输入一次密码',
        min_length=6,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': '再输入一次密码'}
        )
    )

    def __init__(self, *args, **kwargs):  # 用这个方法把user传过来了
        if 'request' in kwargs:
            self.request = kwargs.pop('request')  # 接收传过来的request
        super(ReForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 生成验证码
        code = self.request.session.get('bind_email_code', '')  # 系统生成的验证码
        verification_code = self.cleaned_data.get('verification_code', '')  # 用户输入的验证码
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    # 验证数据
    def clean_username(self):
        username = self.cleaned_data['username']
        # User.objects.filter(username=username).count()>0
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入密码不一致')
        return password

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被绑定')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code
        # 判断是否登录


class ChangeNickForm(forms.Form):
    nickname_new = forms.CharField(
        label='新的昵称',
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'}
        )
    )

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new', '').strip()  # 是否为空
        if nickname_new == '':
            raise forms.ValidationError('新的昵称不能为空')
        return nickname_new

    # 判断是否登录
    def __init__(self, *args, **kwargs):  # 用这个方法把user传过来了
        if 'user' in kwargs:
            self.user = kwargs.pop('user')  # 接收传过来的user
        super(ChangeNickForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data


# 绑定邮箱表单
class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': '请输入正确的邮箱'}
        )
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )

    # 判断是否登录
    def __init__(self, *args, **kwargs):  # 用这个方法把user传过来了
        if 'request' in kwargs:
            self.request = kwargs.pop('request')  # 接收传过来的request
        super(BindEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 判断是否已经绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('您已经绑定邮箱')

        # 生成验证码
        code = self.request.session.get('bind_email_code', '')  # 系统生成的验证码
        verification_code = self.cleaned_data.get('verification_code', '')  # 用户输入的验证码
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被绑定')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='旧的密码',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': '请输入旧的密码'}
        )
    )
    new_password = forms.CharField(
        label='新的密码',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': '请输入新的密码'}
        )
    )
    new_password_again = forms.CharField(
        label='请再次输入新的密码',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': '请再次输入新的密码'}
        )
    )

    # 获取处理方法传过来的user
    def __init__(self, *args, **kwargs):  # 用这个方法把user传过来了
        if 'user' in kwargs:
            self.user = kwargs.pop('user')  # 接收传过来的user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 验证新的密码是否一致
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次输入不一致')
        return self.cleaned_data

    # 验证旧的密码是否正确
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧的密码错误')
        return old_password

class FogotPasswordForm(forms.Form):
    email = forms.CharField(
        label='邮箱',
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': '请输入邮箱名'}
        )
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )
    new_password = forms.CharField(
        label='新的密码',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': '请输入新的密码'}
        )
    )


    # 判断是否登录
    def __init__(self, *args, **kwargs):  # 用这个方法把user传过来了
        if 'request' in kwargs:
            self.request = kwargs.pop('request')  # 接收传过来的request
        super(FogotPasswordForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email=self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱不存在')
        return email

    def clean_verification_code(self):
        verification_code=self.cleaned_data.get('verification_code','').strip()
        if verification_code =='':
            raise forms.ValidationError('验证码不能为空')

        # 判断验证码
        code = self.request.session.get('bind_email_code', '')  # 系统生成的验证码
        verification_code = self.cleaned_data.get('verification_code', '')  # 用户输入的验证码
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return verification_code
