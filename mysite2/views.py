import datetime
from django.shortcuts import  render
from read_sttistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data, \
    get_seven_days_hot_data
from django.contrib.contenttypes.models import ContentType
from blog.models import Blog
from read_sttistics.utils import get_express_info, showResult
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache



def get_days_hot_blogs(days):  # 取天的博客
    today = timezone.now().date()  # 获取当前时间
    date = today - datetime.timedelta(days=days)  # 获取到天前的那个天数
    blogs = Blog.objects.filter(read_details__date__lte=today, read_details__date__gte=date) \
        .values('id', 'title').annotate(read_num_sum=Sum('read_details__read_num')) \
        .order_by('-read_num_sum')

    # .values('id','title')提取具体博客的id和title
    # .annotate（Sum('read_details__read_num'))将查询集合中相应的id和title进行聚合汇总计数
    return blogs[:5]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)

    dates, read_nums = get_seven_days_read_data(blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)

    # 获取7天热门博客的缓存数据
    hot_blogs_for_seven_days = cache.get('hot_blogs_for_seven_days')
    if hot_blogs_for_seven_days is None:
        hot_blogs_for_seven_days = get_days_hot_blogs(7)
        cache.set('hot_blogs_for_seven_days', hot_blogs_for_seven_days, 3600)

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = today_hot_data
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['get_seven_days_hot_data'] = get_seven_days_hot_data(blog_content_type)
    context['hot_blogs_for_seven_days'] = get_days_hot_blogs(7)
    context['hot_blogs_for_thirty_days'] = get_days_hot_blogs(30)
    return render(request,'home.html', context)


def get_express(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    context = {}
    dates, read_nums = get_seven_days_read_data(blog_content_type)
    if request.method == 'POST':
        company_name = request.POST.get('company', '')
        if company_name == '百世':
            company = 'huitongkuaidi'
        elif company_name == '德邦':
            company = 'debangwuliu'
        elif company_name == 'EMS':
            company = 'ems'
        elif company_name == '如风达':
            company = 'rufengda'
        elif company_name == '申通':
            company = 'shentong'
        elif company_name == '顺丰':
            company = 'shunfeng'
        elif company_name == '圆通':
            company = 'yuantong'
        elif company_name == '韵达':
            company = 'yunda'
        else:
            company = 'zhongtong'
        code = request.POST.get('code', '')
        jsonStr = get_express_info(company, code)

        info = showResult(jsonStr)
        context['info'] = info
        express_data = info.get('data')
        context['express_data'] = express_data
    dates, read_nums = get_seven_days_read_data(blog_content_type)
    context['dates'] = dates
    context['read_nums'] = read_nums

    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['get_seven_days_hot_data'] = get_seven_days_hot_data(blog_content_type)
    context['hot_blogs_for_seven_days'] = get_days_hot_blogs(7)
    return render(request, 'home.html', context)


