from django.db import models
from django.contrib.auth.models import User
from read_sttistics.models import ReadNumExpandMethod,ReadDetail
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from ckeditor.fields import RichTextField
# Create your models here.




#博客类型
class BlogType(models.Model):
    type_name=models.CharField(max_length=15)#博客类型

    def __str__(self):
        return self.type_name

#博客类
class Blog(models.Model,ReadNumExpandMethod):#继承了两个类
    title=models.CharField(max_length=60)#标题
    #类型用外键关联
    blog_type=models.ForeignKey(BlogType,on_delete=models.DO_NOTHING)
    content=RichTextField()
    #作者
    author=models.ForeignKey(User,on_delete=models.DO_NOTHING)
    #可以让Blog使用与之关联的ReadDetail中的内容
    read_details=GenericRelation(ReadDetail)#和ReadDetail关联起来
    #read_num=models.IntegerField(default=0)#阅读量
    created_time=models.DateTimeField(auto_now_add=True)
    last_updated_time=models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('blog_detail',kwargs={'blog_pk':self.pk})

    def get_email(self):
        return self.author.email
    def __str__(self):
        return "<Blog:%s>" % self.title
    #获取阅读量

    '''def get_read_num(self):
        #通过捕获异常来设置0
        try:
            return self.readnum.read_num
        except exceptions.ObjectDoesNotExist:
            return 0
    '''
    class Meta:
        ordering=['-created_time']#按创建时间排序---倒序
        verbose_name="博客"
        verbose_name_plural="博客"

'''class ReadNum(models.Model):
    read_num=models.IntegerField(default=0)
    blog=models.OneToOneField(Blog,on_delete=models.DO_NOTHING)#一对一关系
    '''
