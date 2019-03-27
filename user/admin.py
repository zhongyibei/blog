from django.contrib import admin
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class ProfileInline(admin.StackedInline):#行内连接
    model=Profile#指向Profile模型
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines=(ProfileInline,)
    list_display=['username','email','is_staff','is_active','is_superuser','nickname']

    def nickname(self,obj):
        return obj.profile.nickname
    nickname.short_description='昵称'
admin.site.unregister(User)
admin.site.register(User,UserAdmin)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','nickname']
admin.site.register(Profile,ProfileAdmin)