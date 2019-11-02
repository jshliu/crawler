# -*- coding: utf-8 -*-
import os
import socket
import signal
import time
import logging
import json
import re
from datetime import datetime, timedelta

from context.context import Context

ModelBase = Context().get("ModelBase")
str2time = Context().get("datetimeutil.str2time")


class Crawler(object):
    """
    业务爬虫的超类，所有业务爬虫都是该类的子类。

    每个业务爬虫都必须有一个唯一标识符，该标识符为名为type的成员属性。
    同时要重写crawl()方法。

    """

    type = "base.crawler"

    def __init__(self, task):
        self.task = task
        self.key = None
        self.data = None
        self._structure()

    def _structure(self):
        source, name = tuple(self.task.crawler.split('.'))
        if not self.task.data:
            data = {}
        else:
            data = json.loads(self.task.data)
            str2time(data)
        if not data.has_key('source'):
            data.update({'source': source}) 
        self.key = self.task.key
        self.data = data       

    @staticmethod
    def init(conf={}):
        pass

    def crawl(self):
        """
        该方法是爬取的入口，子类需要重写该方法。
        """
        raise NotImplemented

    def __str__(self):
        return "Crawler(%s, %s, %s)" % (self.type, self.key, self.data)


class CrawlerStatus:
    NewAdded = 0
    Enabled = 1
    Disabled = 2


class CrawlerConf(object):

    def __init__(self):
        self._processes = None
        self._crawlers = None
        self._enabled_crawlers = None
        self._disabled_crawlers = None
        self._crawler_confs = {}

    def _query_processes(self):
        return dict([
            (p['category'], int(p['count'])) for p in
            self._db['crawler_process'].find({})])

    @property
    def processes(self):
        if not self._processes:
            self._processes = self._query_processes()
        return self._processes

    @property
    def crawlers(self):
        if not self._crawlers:
            self._crawlers = self.query_crawlers()
        return self._crawlers

    @property
    def enabled_crawlers(self):
        if not self._enabled_crawlers:
            self._enabled_crawlers = self.query_crawlers(
                status=CrawlerStatus.Enabled)
        return self._enabled_crawlers

    @property
    def disabled_crawlers(self):
        if not self._disabled_crawlers:
            self._disabled_crawlers = self.query_crawlers(
                status=[CrawlerStatus.NewAdded, CrawlerStatus.Disabled])
        return self._disabled_crawlers

    def query_crawlers(self, status=None):
        crawler_types = self.find_crawlers() 
        return crawler_types

    def _find_crawlers(self, obj, depth=0):   
        crawler_types = {}
        if depth > 3:
            return
        if isinstance(obj, type) and issubclass(obj, Crawler) and \
                obj != Crawler:
            crawler_types[obj.type] = obj
        elif type(obj).__name__ == "module":
            for key in dir(obj):
                if not key.startswith("__"):
                    ctypes = self._find_crawlers(getattr(obj, key), depth + 1)
                    if ctypes:
                        crawler_types.update(ctypes)
        return crawler_types

    def find_crawlers(self):
        from service import crawlerimpl
        return self._find_crawlers(crawlerimpl)


def export(data):
    assert isinstance(data, ModelBase)
    return data.on_import()


if __name__ == "__main__":
    pass
