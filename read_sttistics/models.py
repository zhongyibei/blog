from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
# Create your models here.
from django.db.models.fields import exceptions


class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()  # 字段类型为数值类型
    content_object = GenericForeignKey('content_type', 'object_id')  # 变成一个通用的外键


class ReadNumExpandMethod():
    def get_read_num(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)
            return readnum.read_num
        except exceptions.ObjectDoesNotExist:
            return 0


class ReadDetail(models.Model):
    date = models.DateField(default=timezone.now)  # 日期字段，默认为当天
    read_num = models.IntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)  # 获取类型
    object_id = models.PositiveIntegerField()  # 字段类型为数值类型，是一种模型下的一个ID值
    content_object = GenericForeignKey('content_type', 'object_id')  # 变成一个通用的外键
