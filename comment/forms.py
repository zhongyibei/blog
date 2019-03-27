from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget
from .models import Comment

class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput())  # 隐藏不显示
    object_id = forms.IntegerField(widget=forms.HiddenInput())
    text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'),
                            error_messages={'required':'评论内容不能为空！'})
    reply_comment_id=forms.IntegerField(widget=forms.HiddenInput(attrs={'id':'reply_comment_id'}))

    def clean_reply_comment_id(self):
        reply_comment_id=self.cleaned_data['reply_comment_id']
        if reply_comment_id <0:
            raise forms.ValidationError()
        elif reply_comment_id==0:
            self.cleaned_data['parent']=None
        elif Comment.objects.filter(pk=reply_comment_id).exists():
            self.cleaned_data['parent']=Comment.objects.get(pk=reply_comment_id)
        else:
            raise forms.ValidationError('回复出错')
        return reply_comment_id
    def __init__(self, *args, **kwargs):  # 用这个方法把user传过来了
        if 'user' in kwargs:
            self.user = kwargs.pop('user')  # 接收传过来的user
        super(CommentForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        # 评论对象验证
        content_type = self.cleaned_data['content_type']  # 获取content_type
        object_id = self.cleaned_data['object_id']
        try:
            models_class = ContentType.objects.get(model=content_type).model_class()  # 得到具体的model  class  如在这是Blog
            model_obj = models_class.objects.get(pk=object_id)
            self.cleaned_data['content_object'] = model_obj
        except  ObjectDoesNotExist:  # 对象不存在
            raise forms.ValidationError('评论对象不存在')
        return self.cleaned_data
