# -*- coding: utf-8 -*-
from core.connection.mongo import mongo_client
from tornado import gen


class MongoModel(object):
    db = mongo_client
    collection_name = None

    @classmethod
    @gen.coroutine
    def insert(cls, message_dict=None):
        if message_dict is None:
            message_dict = {}
        response, error = yield gen.Task(cls._collection().insert, message_dict)
        object_id = response[0][0].get('connectionId')
        raise gen.Return(object_id)

    @classmethod
    @gen.coroutine
    def find(cls, query_dict=None):
        if query_dict is None:
            query_dict = {}
        response, error = yield gen.Task(cls._collection().find, query_dict)
        raise gen.Return(response[0])

    @classmethod
    def _collection(cls):
        return getattr(cls.db, cls.collection_name or '%ss' % cls.__name__.lower())


class Jsonify(object):
    def to_json(self):
        raise NotImplementedError


class User(MongoModel):
    pass