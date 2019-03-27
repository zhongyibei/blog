from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)#一对一
    nickname=models.CharField(max_length=20)

    def __str__(self):
        return '<Profile:%s for %s>' %(self.nickname,self.user.username)

def get_nickname(self):
    if Profile.objects.filter(user=self).exists():#看看是否存在昵称
        profile=Profile.objects.get(user=self)
        return profile.nickname
    else:
        return ''
def has_nickname(self):
    return Profile.objects.filter(user=self).exists()

def get_nickname_or_username(self):
    if Profile.objects.filter(user=self).exists():#看看是否存在昵称
        profile=Profile.objects.get(user=self)
        return profile.nickname
    else:
        return self.username
User.get_nickname=get_nickname
User.has_nickname=has_nickname#动态绑定
User.get_nickname_or_username=get_nickname_or_username

