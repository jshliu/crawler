# -*- coding: utf-8 -*-
import sys

from django.conf import settings

from context.context import Context
import jobtracker
import tasktracker


def run(*args):
    if args:
        if args[0] == 'start' or args[0] == 'stop':
            tasktracker.run(*args)
            jobtracker.run(*args)
        elif args[0] == 'jobtracker':
            jobtracker.run(*args[1:])
        elif args[0] == 'tasktracker':
            tasktracker.run(*args[1:])
        else:
            print 'Unknown command'
            sys.exit(2)
        sys.exit(0)
    else:
        print "bad arguments"
        sys.exit(2)
