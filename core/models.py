# -*- coding: utf-8 -*-
from core.connection.mongo import mongo_client
from tornado import gen
from bson.objectid import ObjectId


class MongoModel(object):
    db = mongo_client
    collection_name = None

    @classmethod
    @gen.coroutine
    def insert(cls, input_dict=None):
        if input_dict is None:
            input_dict = {}
        response, error = yield gen.Task(cls._collection().insert, input_dict)
        object_id = response[0][0].get('connectionId')
        raise gen.Return(object_id)

    @classmethod
    @gen.coroutine
    def find(cls, **kwargs):
        if '_id' in kwargs.keys() and isinstance(kwargs['_id'], str):
            kwargs['_id'] = ObjectId(kwargs['_id'])

        response, error = yield gen.Task(cls._collection().find, kwargs)
        raise gen.Return(response[0])

    @classmethod
    def _collection(cls):
        return getattr(cls.db, cls.collection_name or '%ss' % cls.__name__.lower())


class Jsonify(object):
    def to_json(self):
        raise NotImplementedError


class User(MongoModel):
    pass