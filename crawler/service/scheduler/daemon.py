# -*- coding: utf-8 -*-
import time
import os
import signal
import logging
from django.conf import settings

from context.context import Context

Daemon = Context().get("utils.Daemon")
RedisQueryApi = Context().get("RedisQueryApi")
Handler = Context().get("Handler")


_CRAWLER_TYPES = {}
_TERMINATING = False
inject_logger = logging.getLogger("crawler.inject")


class CrawlerDaemon(Daemon):
    """
    注入任务服务的类，继承了Daemon类。

    """

    def __init__(self, CRAWLER_PID):
        super(CrawlerDaemon, self).__init__(pidfile=CRAWLER_PID)

    def run(self):
        signal.signal(signal.SIGTERM, self.term_handler) #将正常终止信号绑定自定义方法。

        print "jobtracker pid=%s start done." % os.getpid()
        inject_logger.info("jobtracker pid=%s START !" % os.getpid())
        while not _TERMINATING: #判断是否要终止运行。
            length = RedisQueryApi().llen('task') #获取当前任务队列中待执行的任务数量。
            if length <= settings.QUEUE_MIN_LEN: #判断是否需要注入任务。
                Handler.inject_task(settings.QUEUE_MAX_LEN-length) #注入一定数量的任务。
            else:
                pass
            time.sleep(settings.TASK_INJECT_INTERVAL)

        print "jobtracker pid=%s stop done." % os.getpid()
        inject_logger.info("jobtracker pid=%s STOP !" % os.getpid())

    def term_handler(self, signum, frame):
        global _TERMINATING
        _TERMINATING = True








