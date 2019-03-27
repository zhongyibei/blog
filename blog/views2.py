from django.shortcuts import render, render_to_response, get_object_or_404
from .models import BlogType, Blog#,ReadNum  #
from django.core.paginator import Paginator  # 引入分页器

from django.db.models import Count
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from read_sttistics.models import ReadNum

from read_sttistics.utils import read_statistics_once_read
from comment.models import Comment
from comment.forms import CommentForm
from user.forms import LoginForm
# Create your views here.

def get_blog_list_common_data(request, blogs_all_list):
    context = {}
    paginator = Paginator(blogs_all_list, 5)
    page_num = request.GET.get('page', 1)
    page_of_blogs = paginator.get_page(page_num)  # 得到相应页码对应的对象
    current_page_num = page_of_blogs.number  # 获取当前页码
    page_range = [current_page_num - 2, current_page_num - 1, current_page_num, current_page_num + 1,
                  current_page_num + 2]
    # 上面这样直接设置会出错，如果当前页为1，则出现负数页，所以要进行一个判断

    # 两个列表相加
    page_range = list(range(max(1, current_page_num - 2), current_page_num)) + list(
        range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    # 开始加省略号
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加首页和最后一页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取博客分类对应的博客数量
    # 第一种方法
    '''blog_types=BlogType.objects.all()
    blog_types_list=[]
    for blog_type in blog_types:
        blog_type.blog_count=Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)

    context['blog_types']=blog_types_list'''
    # 第二种方法  django给我们提供了annotate拓展查询字段
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))

    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range

    # 获取日期归档对应的博客
    # 第一种方法

    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month
                                         ).count()
        blog_dates_dict[blog_date] = blog_count  # 键值字典
    context['blog_dates'] = blog_dates_dict

    # 第二种方法
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC").annotate(blog_count=Count('created_time'))
    # 不好做
    return context


# 博客列表处理方法
def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_count'] = Blog.objects.all().count()  # 对博客数量进行计数
    return render(request,'blog/blog_list.html', context)
def music(request):
    return render(request,'blog/music.html')

def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)

    # 看看cookies里是否存在该博客，如果不存在该对象则执行阅读量加一操作
    """if not request.COOKIES.get('blog_%s_read' % blog_pk):
        ct=ContentType.objects.get_for_model(Blog)#获取类型
        if ReadNum.objects.filter(content_type=ct,object_id=blog.pk).count():
            #存在记录
            readnum=ReadNum.objects.get(content_type=ct,object_id=blog.pk)
            readnum.read_num+=1
            readnum.save()
        else:
            #不存在记录
            readnum=ReadNum(content_type=ct,object_id=blog.pk)
            readnum.read_num +=1
            readnum.save()
        '''if ReadNum.objects.filter(blog=blog).count():#如果存在博客记录
            readnum=ReadNum.objects.get(blog=blog)#取出该博客对应的数量
            #在这readnum是个一条对象
            readnum.read_num += 1
            readnum.save()
        else:
            #不存在该博客，则需要写博客的实例化
            readnum=ReadNum()
            readnum.read_num +=1
            readnum.blog=blog #给这个blog对着blog
            readnum.save()
          '''
    """
    read_cookie_key=read_statistics_once_read(request,blog)
    blog_content_type=ContentType.objects.get_for_model(blog)
    comments=Comment.objects.filter(content_type=blog_content_type,object_id=blog.pk)
    context = {}
    previous_blog = Blog.objects.filter(created_time__gt=blog.created_time).last()
    next_blog = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    #context['comments']=comments.order_by('-comment_time')
    context['comment_count']=comments.count()
    context['user']=request.user#得到请求中的user信息
    context['previous_blog'] = previous_blog
    context['next_blog'] = next_blog
    context['login_form']=LoginForm()
    #初始化关键的参数
    data={}
    data['content_type']=blog_content_type.model
    data['object_id']=blog_pk
    data['reply_comment_id']=0

    #context['comment_form']=CommentForm(initial=data)#初始化一个参数
    #后面用comment_tags来实现
    response = render(request,'blog/blog_detail.html', context)  # 响应
    # 写  记录到cookie信息 read_cookie_key='blog_%s_read' % blog_pk
    response.set_cookie(read_cookie_key, 'true', max_age=60)#阅读标记
    # 是一个字典,对于某一篇博客，读过设为真，有效期设为60s;在这也可以用expires=datetime来指定时间；两者不能同时存在
    return response


def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request, blogs_all_list)
    return render(request,'blog/blogs_with_type.html', context)


def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_data(request, blogs_all_list)
    # context['blog_types']=BlogType.objects.all()
    # context['blog_dates']=Blog.objects.dates('created_time','month',order="DESC")
    return render(request,'blog/blogs_with_date.html', context)


'''def blogs_with_type(request,blog_type_pk):
    blog_type=get_object_or_404(BlogType,pk=blog_type_pk)
    context={}
    context['blogs']=Blog.objects.filter(blog_type=blog_type)
    context['blog_types']=BlogType.objects.all()#为了给右侧分类使用
    return render_to_response('blog/blogs_with_type.html',context)
'''
