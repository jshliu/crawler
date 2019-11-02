# -*- coding: utf-8 -*-
import os
import signal
import time
import logging
from threading import Timer
from django.conf import settings

from context.context import Context

Crawler = Context().get("Crawler")
Handler = Context().get("Handler")
get_exception_info = Context().get("get_exception_info")


fetch_logger = logging.getLogger("crawler.fetch")
_RUNNING_CRAWLER = None
_TERMINATING = False


def procedure():
    """
    一个执行任务服务进程所需要做的事。
    """

    signal.signal(signal.SIGTERM, service_term_handler) #将正常终止信号与自定义方法绑定。
    signal.signal(signal.SIGALRM, task_term_handler) #将闹钟信号与自定义方法绑定。

    start_time = time.time()
    print "tasktracker pid=%s start done." % os.getpid()
    fetch_logger.info("tasktracker pid=%s START !" % os.getpid())
    while (True if settings.PROCESS_TIMEOUT > 0 else time.time() 
        <= start_time + settings.PROCESS_TIMEOUT) and not _TERMINATING: #判断该进程是否过期，是否接收到终止信号。
        task = Handler.receive_task() #获取一个爬虫任务。
        
        if not task:
            time.sleep(settings.TASK_FETCH_INTERVAL) 
            continue
        global _RUNNING_CRAWLER
        _RUNNING_CRAWLER = task
        fetch_logger.info("fetch task id=%d" % task.id)

        timer = Timer(
            task.timeout if task.timeout else settings.TASK_TIMEOUT, timeout_handler) #设置定时器。
        timer.start()
        try:
            c = Handler.create(task) #根据一个任务创建出一个爬虫对象，用来执行任务（不应该一个任务创建一个爬虫对象）。
            c.crawl() #执行爬虫任务。
            success = True
            fetch_logger.info("crawl task SUCCEED id=%d" % task.id)
        except Exception:
            msg = get_exception_info()
            success = False
            fetch_logger.error("crawle task FAILED id=%s, %s" % (task.id, msg))

        timer.cancel()

        _RUNNING_CRAWLER = None
        Handler.finish(c, success) #任务结束。
    print "tasktracker pid=%s stop done." % os.getpid()
    fetch_logger.info("tasktracker pid=%s STOP !" % os.getpid())


def service_term_handler(signum, frame):
    """
    正常终止进程。
    """
    global _TERMINATING
    _TERMINATING = True


def task_term_handler(signum, frame):
    """
    处理任务超时的方法，跑出一个运行时错误。
    """
    fetch_logger.info("task timeout id=%s !" % _RUNNING_CRAWLER.id)
    raise RuntimeError("task timeout id=%s !" % _RUNNING_CRAWLER.id)


def timeout_handler():
    """
    任务超时时调用的方法，对当前进程发送一个闹钟信号。
    """
    os.kill(os.getpid(), signal.SIGALRM)


if __name__ == '__main__':
    procedure()