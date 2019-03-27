

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name="login"),
    path('login_for_modal/', views.login_for_modal, name="login_for_modal"),
    path('logout/', views.logout, name="logout"),
    path('register/', views.register, name="register"),
    path('user_info/', views.user_info, name='user_info'),
    path('ajax_val/', views.ajax_val, name="ajax_val"),
    path('change_nickname/',views.change_nickname,name="change_nickname"),
    path('bind_email/',views.bind_email,name="bind_email"),
    path('send_verfication_code/',views.send_verfication_code,name="send_verfication_code"),
    path('change_password/',views.change_password,name="change_password"),
    path('forgot_password/',views.forgot_password,name="forgot_password"),
    ]