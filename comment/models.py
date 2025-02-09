from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
# Create your models here.
import threading
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render

class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject= subject
        self.text= text
        self.email= email
        self.fail_silently= fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.text, settings.EMAIL_HOST_USER, [self.email], fail_silently=False)


class Comment(models.Model):
    # 评论对象的创建
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)  # 获取类型
    object_id = models.PositiveIntegerField()  # 字段类型为数值类型，是一种模型下的一个ID值
    content_object = GenericForeignKey('content_type', 'object_id')  # 变成一个通用的外键

    text = models.TextField()  # 评论内容
    comment_time = models.DateTimeField(auto_now_add=True)  # 评论时间
    user = models.ForeignKey(User, related_name='comments', on_delete=models.DO_NOTHING)  # 评论者

    # parent_id=models.IntegerField(default=0)#看他的上一级是谁
    # related_name 为反向关系，方向解析  如user.replies.all()    user.comments.all()
    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.DO_NOTHING)
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.DO_NOTHING)
    reply_to = models.ForeignKey(User, related_name='replies', null=True, on_delete=models.DO_NOTHING)

    def send_mail(self):
        # 发送邮件通知
        if self.parent is None:
            # 评论我的博客
            subject = '有人评论你的博客'
            email = self.content_object.get_email()
        else:
            # 回复评论
            subject = '有人回复你的评论'
            email = self.reply_to.email
        if email != '':
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = self.text + self.content_object.get_url()
            text = render(None, 'comment/send.html', context).content.decode('utf-8')
            send_mail = SendMail(subject, text, email)
            send_mail.start()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['comment_time']
