from django.shortcuts import render, render_to_response, get_object_or_404
from .models import BlogType, Blog  #
from django.core.paginator import Paginator  # 引入分页器


# Create your views here.

# 博客列表处理方法
def blog_list(request):
    context = {}
    blogs_all_list = Blog.objects.all()
    paginator = Paginator(blogs_all_list, 5)  # 分页
    # 获取前端传来的页码
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

    context['blog_types'] = BlogType.objects.all()
    context['blog_count'] = Blog.objects.all().count()  # 对博客数量进行计数
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_dates']=Blog.objects.dates('created_time','month',order="DESC")
    return render_to_response('blog/blog_list.html', context)


def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    context = {}
    previous_blog=Blog.objects.filter(created_time__gt=blog.created_time).last()
    next_blog=Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    context['previous_blog']=previous_blog
    context['next_blog']=next_blog
    return render_to_response('blog/blog_detail.html', context)


def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    context = {}
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    paginator = Paginator(blogs_all_list, 5)
    page_num = request.GET.get('page', 1)
    page_of_blogs = paginator.get_page(page_num)  # 当前对应的页对象
    current_page_num = page_of_blogs.number  # 获取当前页
    page_range = list(range(max(1, current_page_num - 2), current_page_num)) + list(
        range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    context['blog_types'] = BlogType.objects.all()  # 为了给右侧分类使用
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_dates']=Blog.objects.dates('created_time','month',order="DESC")
    return render_to_response('blog/blogs_with_type.html', context)


def blogs_with_date(request, year, month):
    context = {}
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    paginator=Paginator(blogs_all_list,5)
    page_num=request.GET.get('page',1)
    page_of_blogs=paginator.get_page(page_num)
    current_num=page_of_blogs.number
    page_range=list(range(max(1,current_num-2),current_num))+list(range(current_num,min(current_num+2,paginator.num_pages)+1))
    if page_range[0]-1>=2:
        page_range.insert(0,'...')
    if paginator.num_pages-page_range[-1]>=2:
        page_range.append('...')
    if page_range[0]!=1:
        page_range.insert(0,1)
    if page_range[-1]!=paginator.num_pages:
        page_range.append(paginator.num_pages)
    context['page_of_blogs']=page_of_blogs
    context['page_range']=page_range
    context['blog_types']=BlogType.objects.all()
    context['blogs_with_date']='%s年%s月'%(year,month)
    context['blog_dates']=Blog.objects.dates('created_time','month',order="DESC")
    return render_to_response('blog/blogs_with_date.html', context)


'''def blogs_with_type(request,blog_type_pk):
    blog_type=get_object_or_404(BlogType,pk=blog_type_pk)
    context={}
    context['blogs']=Blog.objects.filter(blog_type=blog_type)
    context['blog_types']=BlogType.objects.all()#为了给右侧分类使用
    return render_to_response('blog/blogs_with_type.html',context)
'''