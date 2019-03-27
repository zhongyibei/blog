from django.shortcuts import render, reverse, redirect
from .models import Comment
from django.contrib.contenttypes.models import ContentType
from .forms import CommentForm
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import time

from django.shortcuts import render
# Create your views here.

def update_comment(request):
    '''user=request.user
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    if not user.is_authenticated:#未登录用户
        return render(request,'error.html',{'message':'用户未登录','redirect_to':referer})
    text=request.POST.get('text','').strip()#去掉空格
    if text =='':
        return render(request,'error.html',{'message':'评论内容为空！','redirect_to':referer})

    try:
        content_type=request.POST.get('content_type','')
        object_id=int(request.POST.get('object_id',''))
        models_class = ContentType.objects.get(model=content_type).model_class()  # 得到具体的model  class  如在这是Blog
        model_obj = models_class.objects.get(pk=object_id)
    except Exception as e:
        return render(request,"error.html",{'message':'评论对象不存在','redirect_to':referer})
    comment=Comment()
    comment.user=user
    comment.text=text
    #Blog.objects.get(pk=object_id)可以写死  但不好
    #所以要获取它的类型
    #content_type=ContentType.objects.get_for_model()
    comment.content_object=model_obj
    comment.save()
    return redirect(referer)'''
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    comment_form = CommentForm(request.POST, user=request.user)  # 将user对象传给forms表单
    if comment_form.is_valid():
        # 检查通过，保存数据
        comment = Comment()
        comment.user = request.user
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']

        # 判断父
        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()
        '''
        # 发送邮件通知
        if comment.parent is None:
            # 评论博客
            subject = '有人评论你的博客'
            content = '%s\n <a href="%s">%s</a>'%(comment.text,  comment.content_object.get_url(),'查看博客') # 用get_url()方便我们获取各种模型的url
            context1={}
            context1['comment_text']=comment.text
            context1['url']= comment.content_object.get_url()
            content = render(None, 'comment/send.html', context1).content.decode('utf-8')
            email = comment.content_object.get_email()
            if email != '':
                send_mail(subject,'' , 'zhongyibei101@sina.com', [email], fail_silently=False,html_message=content, )
        else:
            # 回复评论
            subject = '有人回复你的评论'
            email = comment.reply_to.email
            if email != '':
                content='%s\n <a href="%s">%s</a>' % (comment.text, comment.content_object.get_url(), '查看博客') # 用get_url()方便我们获取各种模型的url
                context1 = {}
                context1['comment_text'] = comment.text
                context1['url'] = comment.content_object.get_url()
                content = render(None,'comment/send.html', context1).content.decode('utf-8')
                send_mail(subject,'' , 'zhongyibei101@sina.com', [email], fail_silently=False, html_message=content,)

        '''
        comment.send_mail()
        # return redirect(referer)
        # 向前端js返回数据
        data = {}
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.username
        data['username'] = comment.user.get_nickname_or_username()
        # data['comment_time']=comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')#会出现时区错误
        data['comment_time'] = comment.comment_time.timestamp()
        data['text'] = comment.text
        data['content_type'] = ContentType.objects.get_for_model(comment).model
        if not parent is None:
            # data['reply_to']=comment.reply_to.username
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
        return JsonResponse(data)
    else:
        # return render(request,'error.html',{'message':comment_form.errors,'redirect_to':referer})
        data = {}
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]  # 返回错误信息
        return JsonResponse(data)
