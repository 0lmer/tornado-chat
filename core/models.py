# -*- coding: utf-8 -*-
from core.connection.mongo import mongo_client
from tornado import gen
from bson.objectid import ObjectId
import bson
import datetime
import cPickle as pickle


class Jsonify(object):
    BSON_TYPES = [
        None.__class__, bool, int, long,
        # bson.int64.Int64,
        float, str, unicode, list, dict, datetime.datetime,
        bson.regex.Regex, bson.binary.Binary, bson.objectid.ObjectId, bson.dbref.DBRef, bson.code.Code, bytes
    ]

    def to_json(self):
        raise NotImplementedError

    @property
    def bson(self):
        resp = {}
        for key in self.bson_properties:
            if hasattr(self, key):
                val = getattr(self, key)
                has_bson_type = False
                for tp in self.BSON_TYPES:
                    if isinstance(val, tp):
                        has_bson_type = True
                        break
                if has_bson_type:
                    resp[key] = val
                else:
                    resp[key] = val.bson
            else:
                resp[key] = None
        if type(self) not in self.BSON_TYPES:
            resp['_class'] = pickle.dumps(self.__class__)
        return resp

    @property
    def bson_properties(self):
        return []

    @classmethod
    def unserialize(cls, struct):
        clz = pickle.loads(str(struct['_class']))
        instance = clz()
        for key, value in struct.iteritems():
            if key == '_class':
                continue

            if isinstance(value, dict) and '_class' in value.keys():
                setattr(instance, key, pickle.loads(str(value['_class'])).unserialize(value))
            else:
                setattr(instance, key, value)
        return instance


class MongoModel(Jsonify, object):
    db = mongo_client
    collection_name = None

    @classmethod
    @gen.coroutine
    def insert(cls, document=None):
        if document is None:
            document = {}
        response, error = yield gen.Task(cls._collection().insert, document)

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
    @gen.coroutine
    def mongo_update(cls, query=None, update=None, override=False, or_create=False, multi=False):
        query = {} if query is None else query
        update = {} if update is None else update
        if not override:
            update = {'$set': update}

        response, error = yield gen.Task(cls._collection().update, query, update, upsert=or_create, multi=multi)
        raise gen.Return(None)

    @gen.coroutine
    def save(self):
        if not hasattr(self, '_id') or not getattr(self, '_id'):
            resp = yield self.__class__.insert(self.bson)
            print "Inserted! %s" % resp
        else:
            resp = yield self.__class__.mongo_update(query={'_id': self._id}, update=self.bson)
            print "Updated! %s" % resp

    @classmethod
    def _collection(cls):
        return getattr(cls.db, cls.collection_name or '%ss' % cls.__name__.lower())


class User(MongoModel):
    pass