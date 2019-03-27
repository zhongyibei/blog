import datetime
from django.contrib.contenttypes.models import ContentType
from .models import ReadNum, ReadDetail
from django.db.models import Sum  # 引入求和函数
from django.utils import timezone


def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)  # 获取类型
    key = "%s_%s_read" % (ct.model, obj.pk)
    if not request.COOKIES.get(key):
        '''if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
            # 存在记录
            readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk)
            readnum.read_num += 1
            readnum.save()
        else:
            # 不存在记录
            readnum = ReadNum(content_type=ct, object_id=obj.pk)
            readnum.read_num += 1
            readnum.save()'''
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        # 下面的同样的道理，可以自己修改
        date = timezone.now().date()
        if ReadDetail.objects.filter(content_type=ct, object_id=obj.pk, date=date).count():
            readDetail = ReadDetail.objects.get(content_type=ct, object_id=obj.pk, date=date)
        else:
            readDetail = ReadDetail(content_type=ct, object_id=obj.pk, date=date)
        readDetail.read_num += 1  # 给明细记录加1
        readDetail.save()
    return key


# 获取前7天的阅读数
def get_seven_days_read_data(content_type):
    today = timezone.now().date()  # 今天
    # today - datetime.timedelta(days=1)#得到日期的差量1天，即获取昨天的数据
    read_nums = []
    dates = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)  # 进行加总，用聚合
        result = read_details.aggregate(read_num_sum=Sum('read_num'))  # 对read_num字段进行求和
        read_nums.append(result['read_num_sum'] or 0)  # 如果为none的话返回0
        dates.append(date.strftime("%m/%d"))
    return dates, read_nums


def get_today_hot_data(content_type):
    today = timezone.now().date()  # 获取今日的时间
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')  # 对其进行倒序排序
    return read_details[:5]  # 去前5条数据


def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)#计算出分类的时间
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday)\
        .order_by('-read_num')  # 对其进行倒序排序
    return read_details[:5]


def get_seven_days_hot_data(content_type):
    today = timezone.now().date()  # 获取当前日期
    seven_day = today - datetime.timedelta(days=7)  # 获取前7天的日期
    read_details = ReadDetail.objects \
        .filter(content_type=content_type, date__lt=today, date__gt=seven_day) \
        .values('content_type', 'object_id').annotate(read_num_sum=Sum('read_num')) \
        .order_by('-read_num_sum')
    return read_details[:5]


import urllib.request
import json


def get_express_info(company, code):
    url = 'http://www.kuaidi100.com/query?type=%s&postid=%s' % (company, code)
    page = urllib.request.urlopen(url)  # 打开连接，请求快递数据
    return page.read().decode('utf8')


def showResult(jsonStr):
    jsonObj = json.loads(jsonStr)
    print('当前状态：%s' % jsonObj.get('message'))
    print('\n')
    # status=jsonObj.get('status')
    # if status=='200':
    return jsonObj
