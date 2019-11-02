# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScarletOnsell',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime(2019, 10, 20, 13, 33, 36, 982650), verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_time', models.DateTimeField(default=datetime.datetime(2019, 10, 20, 13, 33, 36, 982674), verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('name', models.TextField(verbose_name='\u540d\u79f0')),
                ('buy_num', models.IntegerField(verbose_name='\u8d2d\u4e70\u6570\u91cf')),
                ('price', models.FloatField(verbose_name='\u4ef7\u683c')),
                ('steam_price', models.FloatField(verbose_name='steam \u4ef7\u683c')),
                ('sell_num', models.IntegerField(verbose_name='\u5728\u552e\u6570\u91cf')),
                ('origin', models.TextField(verbose_name='\u6570\u636e\u6765\u6e90')),
            ],
            options={
                'ordering': ['-create_time'],
                'db_table': 'scarlet_onsell',
                'verbose_name_plural': '\u9970\u54c1\u5728\u552e',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime(2019, 10, 20, 13, 33, 36, 981940), verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_time', models.DateTimeField(default=datetime.datetime(2019, 10, 20, 13, 33, 36, 981967), verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('last_run', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0), verbose_name='\u4e0a\u6b21\u8fd0\u884c\u65f6\u95f4')),
                ('next_run', models.DateTimeField(default=datetime.datetime(2019, 10, 20, 13, 33, 36, 982001), verbose_name='\u4e0b\u6b21\u8fd0\u884c\u65f6\u95f4')),
                ('timeout', models.IntegerField(default=3600, verbose_name='\u53ef\u6267\u884c\u7684\u6700\u5927\u65f6\u95f4')),
                ('status', models.IntegerField(default=0, verbose_name='\u4efb\u52a1\u72b6\u6001')),
                ('priority', models.IntegerField(default=1, verbose_name='\u4f18\u5148\u7ea7')),
                ('interval', models.IntegerField(default=0, verbose_name='\u8fd0\u884c\u95f4\u9694')),
                ('crawler', models.CharField(max_length=255, verbose_name='\u722c\u866b')),
                ('key', models.TextField(null=True, verbose_name='\u5173\u952e\u5b57')),
                ('data', models.TextField(null=True, verbose_name='\u4efb\u52a1\u6570\u636e')),
                ('producer_id', models.IntegerField(null=True, verbose_name='\u751f\u4ea7\u8005id', blank=True)),
                ('category', models.CharField(max_length=255, null=True, verbose_name='\u5206\u7c7b', blank=True)),
                ('application', models.CharField(max_length=255, null=True, verbose_name='\u5e94\u7528', blank=True)),
            ],
            options={
                'ordering': ['-create_time'],
                'db_table': 'task',
                'verbose_name_plural': '\u722c\u866b\u4efb\u52a1',
            },
            bases=(models.Model,),
        ),
    ]
