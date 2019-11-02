# -*- coding: utf-8 -*-
import sys

from django.conf import settings

from context.context import Context

CrawlerDaemon = Context().get("CrawlerDaemon")


def run(*args):
	"""
	注入任务服务进程的执行入口。
	"""
	jobtracker = CrawlerDaemon(settings.CRAWLER_JOB_PID)
	if args[0] == 'start':
		jobtracker.start()
	elif args[0] == 'stop':
		jobtracker.stop()
