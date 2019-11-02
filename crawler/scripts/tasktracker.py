# -*- coding: utf-8 -*-
import sys
import os
import signal

from django.conf import settings

from context.context import Context

_create_child = Context().get("processutil._create_child")
procedure = Context().get("procedure")


def start():
	pid_file = file(settings.CRAWLER_TASK_PID, "w+")
	for i in range(settings.TASKTRACKER_COUNT):
		pid = _create_child(procedure, [], {}).keys()[0]
		pid_file.write(str(pid)+"\n")
	pid_file.close()


def stop():
    pid_file = file(settings.CRAWLER_TASK_PID, "r")
    pids = pid_file.readlines()
    pid_file.close()
    for i in range(len(pids)):
        pids[i] = int(pids[i].strip())
        try:
            os.kill(pids[i], signal.SIGTERM)
        except:
            self.pids.pop(pid)
    os.remove(settings.CRAWLER_TASK_PID)


def run(*args):
    """
    执行任务服务进程的执行入口。
    """
    if args[0] == 'start':
        start()
    elif args[0] == 'stop':
        stop()
