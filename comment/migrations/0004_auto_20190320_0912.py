# Generated by Django 2.0 on 2019-03-20 01:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0003_auto_20190320_0912'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reply',
            name='comment',
        ),
        migrations.DeleteModel(
            name='Reply',
        ),
    ]
