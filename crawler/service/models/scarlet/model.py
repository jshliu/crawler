# -*- coding: utf-8 -*-
from uuid import uuid1
from django.conf import settings

from context.context import Context

ContentModel = Context().get("search.ContentModel")
CassandraQueryApi = Context().get("CassandraQueryApi")


class SearchArticleModel(ContentModel):
    """docstring for SearchArticleModel"""

    #TYPE = "zjld.article"
    TYPE = "zjld.search"

    FIELDS = {
        "type": u"元搜索",
        "author": u"",
        "publisher": u"",
        "title": u"",
        "content": u"",
        "url": u"",
        "key": u"",
    }

    def __init__(self, dct={}):
        super(SearchArticleModel, self).__init__(dct)

    def find_dup(self):
        dup = []
        if self.get('url'):
            cql = """SELECT * FROM %s WHERE url='%s' and key='%s' and producer_id=%s LIMIT 1 allow filtering""" \
                % (self.TYPE.split(".")[1], self['url'], self['key'], self['producer_id'])
            dup = CassandraQueryApi(keyspace=settings.SITE.get("cassandra.db")).find(cql)
        return self.wrap(dup[0] if dup else None)

    def clean_value(self, field, value):
        return value  # leave original value

    def on_import(self):
        if self['source'] and self['url']:
            keyspace, column_family = self.TYPE.split(".")
            self._import_cassandra(keyspace=settings.SITE.get("cassandra.db"), 
                column_family=column_family)