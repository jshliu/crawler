# -*- coding: utf-8 -*-
"""
Django settings for yuqing project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import re
import datetime
import logging.config

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(BASE_DIR))
sys.path.append(BASE_DIR)

from utils.configutil import Config

SITE = Config(os.path.join(BASE_DIR, "settings/conf/core-site.xml"))

CRAWLER_JOB_PID = SITE.get("job.pid") #注入任务服务进程的pid文件。
CRAWLER_TASK_PID = SITE.get("task.pid") #执行任务服务进程的pid文件。

JOBTRACKER_COUNT = int(SITE.get("job.tracker.count"))

PROCESS_TIMEOUT = int(SITE.get("process.timeout"))

QUEUE_MAX_LEN = int(SITE.get("queue.max_len"))
QUEUE_MIN_LEN = int(SITE.get("queue.min_len"))

TASK_INJECT_INTERVAL = int(SITE.get("task.inject.interval"))
TASK_FETCH_INTERVAL = int(SITE.get("task.fetch.interval"))

TASK_TIMEOUT = int(SITE.get("task.timeout"))

TASKTRACKER_COUNT = int(SITE.get("task.tracker.count"))

#日志文件配置。
log_conf = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s %(name)s:%(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "importhandler": {
            "formatter": "simple",
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024*1024*10,
            "filename": os.path.join(SITE.get("log.dir"), "import.log"),
        },
        "injecthandler": {
            "formatter": "simple",
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024*1024*10,
            "filename": os.path.join(SITE.get("log.dir"), "inject.log"),
        },
        "fetchhandler": {
            "formatter": "simple",
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024*1024*10,
            "filename": os.path.join(SITE.get("log.dir"), "fetch.log"),
        },
        "crawlerhandler": {
            "formatter": "simple",
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024*1024*10,
            "filename": os.path.join(SITE.get("log.dir"), "crawler.log"),
        },
    },
    "loggers": {
        "crawler.import": {
            "handlers": ["importhandler",],
            "level": "INFO",
            "propagete": True,
        },
        "crawler.inject": {
            "handlers": ["injecthandler",],
            "level": "INFO",
            "propagete": True,
        },
        "crawler.fetch": {
            "handlers": ["fetchhandler",],
            "level": "INFO",
            "propagete": True,
        },
        "crawler": {
            "handlers": ["crawlerhandler",],
            "level": "INFO",
        }
    },
}
logging.config.dictConfig(log_conf)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6f-lqyij0+64*exps#yyni+%@)6aryv56ooe)2h+$$vvvkdcm8'

# Application definition
DEBUG = True

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.base',
    'django_extensions',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)



TIME_ZONE = 'Asia/Shanghai'

ROOT_URLCONF = 'crawler.urls'

WSGI_APPLICATION = 'crawler.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': SITE.get("mysql.host"),
        'NAME': SITE.get("mysql.db"),
        'USER': SITE.get("mysql.user"),
        'PASSWORD': SITE.get("mysql.password"),
    },
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, "static/build/"),
)


# TEMPLATE_DIRS = (
#     os.path.join(PROJECT_ROOT, "templates"),
# )


MEDIA_URL = '/media/'
