# -*- coding: utf-8 -*-
from uuid import uuid1
from django.conf import settings

from context.context import Context

ContentModel = Context().get("zjld.ContentModel")
CassandraQueryApi = Context().get("CassandraQueryApi")


class ZjldArticleModel(ContentModel):
    """docstring for ZjldArticleModel"""

    TYPE = "zjld.article"

    FIELDS = {
        "type": u"文章",
        "author": u"",
        "publisher": u"",
        "title": u"",
        "content": u"",
        "url": u"",
    }

    def __init__(self, dct={}):
        super(ZjldArticleModel, self).__init__(dct)


    def find_dup(self):
        dup = []
        if self.get('url'):
            cql = """SELECT * FROM %s WHERE url='%s' LIMIT 1""" \
                % (self.TYPE.split(".")[1], self['url'])
            dup = CassandraQueryApi(settings.SITE.get("cassandra.db")).find(cql)

        return self.wrap(dup[0] if dup else None)

    def clean_value(self, field, value):
        return value  # leave original value

    def on_import(self):
        if self['source'] and self['url']:
            keyspace, column_family = self.TYPE.split(".")
            return self._import_cassandra(keyspace=settings.SITE.get("cassandra.db"),
                 column_family=column_family)