# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models


class Task(models.Model):
    create_time = models.DateTimeField(default=datetime.utcnow(), verbose_name=u'创建时间')
    update_time = models.DateTimeField(default=datetime.utcnow(), verbose_name=u'更新时间')
    last_run = models.DateTimeField(default=datetime.min, verbose_name=u'上次运行时间')
    next_run = models.DateTimeField(default=datetime.utcnow(), verbose_name=u'下次运行时间')
    timeout = models.IntegerField(blank=False, default=3600, verbose_name=u'可执行的最大时间')
    status = models.IntegerField(blank=False, default=0, verbose_name=u'任务状态')
    priority = models.IntegerField(blank=False, default=1, verbose_name=u'优先级')
    interval = models.IntegerField(blank=False, default=0, verbose_name=u'运行间隔')
    crawler = models.CharField(null=False, max_length=255, verbose_name=u'爬虫')
    key = models.TextField(null=True, verbose_name=u'关键字')
    data = models.TextField(null=True, verbose_name=u'任务数据')
    producer_id = models.IntegerField(blank=True, null=True, verbose_name=u'生产者id')
    category = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'分类')
    application = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'应用')

    class Meta:
        db_table = 'task'
        verbose_name_plural = u'爬虫任务'
        ordering = ['-create_time']

    def __unicode__(self):
        return str(self.key)

    @classmethod
    def create(cls, **kwargs):
        task = cls(**kwargs)
        return task

class ScarletOnsell(models.Model):
    create_time = models.DateTimeField(default=datetime.utcnow(), verbose_name=u'创建时间')
    update_time = models.DateTimeField(default=datetime.utcnow(), verbose_name=u'更新时间')
    name = models.TextField(blank=True, null=True, verbose_name=u'名称')
    buy_num = models.IntegerField(blank=True, null=True, verbose_name=u'购买数量')
    price = models.FloatField(blank=True, null=True, verbose_name=u'价格')
    steam_price = models.FloatField(blank=True, null=True, verbose_name=u'steam 价格')
    sell_num = models.IntegerField(blank=True, null=True, verbose_name=u'在售数量')
    origin = models.TextField(blank=True, null=True, verbose_name=u'数据来源')

    class Meta:
        db_table = 'scarlet_onsell'
        verbose_name_plural = u'饰品在售'
        ordering = ['-create_time']

    def __unicode__(self):
        return str(self.key)

    @classmethod
    def create(cls, **kwargs):
        model = cls(**kwargs)
        return model
