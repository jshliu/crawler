# -*- coding: utf-8 -*-
import json
import time
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.db import transaction

from context.context import Context

CrawlerConf = Context().get("CrawlerConf")
Task = Context().get("Task")
RedisQueryApi = Context().get("RedisQueryApi")
time2str = Context().get("datetimeutil.time2str")

inject_logger = logging.getLogger("crawler.inject")
fetch_logger = logging.getLogger("crawler.fetch")
_CRAWLER_CONF = CrawlerConf()


class Status:
    """
    任务状态。
    """

    NotStart = 0
    Running = 1
    Succeed = 2
    Failed = -1
    Canceling = -2


class Priority:
    """
    任务优先级别。
    """

    High2 = 4
    High = 3
    Normal = 2
    Low = 1


class Handler(object):
    """
    相关任务逻辑处理的类。
    """


    @staticmethod
    def create(task):
        """
        根据任务创建出爬虫对象。

        @task：一个任务。
        """
        cls = _CRAWLER_CONF.enabled_crawlers.get(task.crawler)
        if not cls:
            return None
        return cls(task)


    @staticmethod
    def handle(type, key=None, data=None, producer_id=None, category=None, application=None,
            priority=Priority.Normal, interval=0, timeout=settings.TASK_TIMEOUT,
            status=Status.NotStart, reset=False):
        """
        根据参数生成新的爬虫任务。
        """
        if type:
            if data:
                time2str(data)
            task = Task(key=key, data=json.dumps(data), priority=priority, interval=interval,
                status=status, timeout=timeout, crawler=type, producer_id=producer_id,
                category=category, application=application)
            task.save()
            fetch_logger.info("general new task id=%d" % task.id)
        else:
            return


    @staticmethod
    def finish(crawler, success=True):
        """
        任务结束时调用的方法。
        """
        now = datetime.utcnow()
        task = crawler.task
        if crawler.data:
            time2str(crawler.data)
        task.data = json.dumps(crawler.data)
        if task.interval > 0:
            task.status = Status.NotStart 
            task.next_run = now + timedelta(seconds=task.interval)      
        elif success:
            task.status = Status.Succeed
        else:
            task.status = Status.Failed
        task.last_run = now
        task.save()


    @staticmethod
    def receive_task():
        """
        从任务队列中获取一个任务，执行任务进程需要调用。
        """
        data = RedisQueryApi().rpop('task')
        if data:
            data = Handler.redis_to_mysql(json.loads(data))
            task = Task.create(**data)
            return task
        return None

    @staticmethod
    def redis_to_mysql(task):
        """
        将redis中存放的任务数据转化成mysql中的一条任务数据。
        """
        data = {
            'id': task['id'],
            'create_time': datetime.fromtimestamp(task['create_time']),
            'update_time': datetime.fromtimestamp(task['update_time']),
            'last_run': datetime.fromtimestamp(task['last_run']),
            'next_run': datetime.fromtimestamp(task['next_run']),
            'timeout': task['timeout'],
            'status': task['status'],
            'priority': task['priority'],
            'interval': task['interval'],
            'crawler': task['crawler'],
            'key': task['key'],
            'data': task['data'],
            'producer_id': task['producer_id'],
            'category': task['category'],
            'application': task['application'],
        }

        return data    


    @staticmethod
    def inject_task(length): 
        """
        将mysql中符合要求的任务注入到redis中，个数最多为length。

        """ 
        for i in [Priority.High2, Priority.High, Priority.Normal, Priority.Low]:
            count = Handler.push_task(length, status=0, priority=i)
            if count >= length:
                break
            else:
                length -= count


    @staticmethod
    def push_task(length, status=Status.NotStart, priority=Priority.Normal):
        """
        根据状态和级别注入任务。
        """
        count = 0
        tasks = Task.objects.filter(status=status, next_run__lte=datetime.utcnow(),
            priority=priority).order_by('-next_run')[:length]
        if tasks:
            for task in tasks:
                with transaction.atomic():
                    task.status = Status.Running
                    task.save()
                    try:
                        RedisQueryApi().lpush('task', json.dumps(Handler.mysql_to_redis(task)))
                        count += 1
                    except Exception, e:
                        inject_logger.error("push task:"+e.message)
                        raise e
        inject_logger.info("inject task count=%d, priority=%d" % (count, priority))
        return count


    @staticmethod
    def mysql_to_redis(data):
        """
        将mysql中存放的任务数据转化成redis中的一条任务数据。
        """
        new_data = {
            "id": data.id,
            "create_time": int(time.mktime(data.create_time.timetuple())),
            "update_time": int(time.mktime(data.update_time.timetuple())),
            "last_run": int(time.mktime(data.last_run.timetuple())),
            "next_run": int(time.mktime(data.next_run.timetuple())),
            "timeout": data.timeout,
            "status": data.status,
            "priority": data.priority,
            "interval": data.interval,
            "crawler": data.crawler,
            "key": data.key,
            "data": data.data,
            "producer_id": data.producer_id,
            "category": data.category,
            "application": data.application,
        }
        return new_data        


if __name__ == '__main__':
    pass
