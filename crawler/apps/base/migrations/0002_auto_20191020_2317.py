# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scarletonsell',
            name='buy_num',
            field=models.IntegerField(null=True, verbose_name='\u8d2d\u4e70\u6570\u91cf', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scarletonsell',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 20, 15, 17, 23, 411486), verbose_name='\u521b\u5efa\u65f6\u95f4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scarletonsell',
            name='name',
            field=models.TextField(null=True, verbose_name='\u540d\u79f0', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scarletonsell',
            name='origin',
            field=models.TextField(null=True, verbose_name='\u6570\u636e\u6765\u6e90', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scarletonsell',
            name='price',
            field=models.FloatField(null=True, verbose_name='\u4ef7\u683c', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scarletonsell',
            name='sell_num',
            field=models.IntegerField(null=True, verbose_name='\u5728\u552e\u6570\u91cf', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scarletonsell',
            name='steam_price',
            field=models.FloatField(null=True, verbose_name='steam \u4ef7\u683c', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scarletonsell',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 20, 15, 17, 23, 411509), verbose_name='\u66f4\u65b0\u65f6\u95f4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 20, 15, 17, 23, 410794), verbose_name='\u521b\u5efa\u65f6\u95f4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='next_run',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 20, 15, 17, 23, 410856), verbose_name='\u4e0b\u6b21\u8fd0\u884c\u65f6\u95f4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 20, 15, 17, 23, 410829), verbose_name='\u66f4\u65b0\u65f6\u95f4'),
            preserve_default=True,
        ),
    ]
