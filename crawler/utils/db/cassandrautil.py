# -*- coding: utf-8 -*-
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory
from django.conf import settings

class CassandraClient(object):
    session = None
    conn = None

    def __init__(self):
        self.conn = {
            'hosts': settings.SITE.get('cassandra.host'),
            'port': settings.SITE.get('cassandra.port'),
            'username': '',
            'password': ''
        }

    def connect(self, keyspace):
        cluster = Cluster(contact_points=self.conn['hosts'].split(','),
            port=self.conn['port'], auth_provider=PlainTextAuthProvider(
            username=self.conn['username'], password=self.conn['password']))
        metadata = cluster.metadata
        self.session = cluster.connect(keyspace)

    def close(self):
        self.session.cluster.shutdown()
        self.session.shutdown()


def get_session(keyspace):
    client = CassandraClient()
    client.connect(keyspace)
    return client.session


def close_client(client):
    client.close()


_SESSION = None
_SPACELIST = {}

class CassandraQueryApi(object):
    """Cassandra Query API"""
    client = None
    session = None
    keyspace = None

    def __init__(self, keyspace=None):
        if not _SPACELIST.get(keyspace, ''):
            _SPACELIST[keyspace] = get_session(keyspace)
        _SESSION = _SPACELIST[keyspace]
        self.session = _SESSION
        self.session.row_factory = dict_factory

    def find(self, cql):
        """
        cassandra.query.select syntax
        """

        def result():
            result = self.session.execute(cql)
            return result

        return result()

    def save(self, cql, fields):
        """
        cassandra.query.insert syntax
        """

        def insert():
            self.session.execute(cql, fields)

        insert()


if __name__ == '__main__':
    pass
  #  print CASSA_CONN_STR
    # client = get_client("zjld")
    # session = get_session()
    # close_client(client)
