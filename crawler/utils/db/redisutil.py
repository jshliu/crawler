# -*- coding: utf-8 -*-
import redis
from django.conf import settings


class RedisClient(object):

    """docstring for RedisClient"""
    def __init__(self):
        pass

    def connect(self):
        pool = redis.ConnectionPool(
            host=settings.SITE.get('redis.host'),
            port=settings.SITE.get('redis.port'),
            db=settings.SITE.get('redis.db'),
            password=settings.SITE.get('redis.password'))
        return redis.Redis(connection_pool=pool)


def get_instance():
    return RedisClient().connect()


class RedisQueryApi(object):
    """Redis Query Api"""
    instance = None

    def __init__(self):
        self.instance = get_instance()

    def rpop(self, name):
        return self.instance.rpop(name)

    def delete(self, name):
        return self.instance.delete(name)

    def lindex(self, name, index):
        return self.instance.lindex(name, index)

    def llen(self, name):
        return self.instance.llen(name)

    def lpush(self, name, values):
        return self.instance.lpush(name, values)

    def lrange(self, name, start, end):
        return self.instance.lrange(name, start, end)

    def hset(self, name, key, value):
        self.instance.hset(name, key, value)

    def hget(self, name, key):
        return self.instance.hget(name, key)

    def hgetall(self, name):
        return self.instance.hgetall(name)

    def hexists(self, name, key):
        return self.instance.hexists(name, key)

    def scard(self, name):
        return self.instance.scard(name)

    def sort(self, name, start=None, num=None, by=None, get=None, desc=False, alpha=False, store=None):
        return self.instance.sort(name, start, num, by, get, desc, alpha, store)

    def set(self, key, value):
        return self.instance.set(key, value)

    def get(self, key):
        return self.instance.get(key)

    def expire(self, key, value):
        return self.instance.expire(key, value)

    def keys(self, key):
        return self.instance.keys(key)