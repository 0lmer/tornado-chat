# -*- coding: utf-8 -*-
from core.connection.mongo import mongo_client
from tornado import gen
from bson.objectid import ObjectId
import bson
import datetime
import cPickle as pickle
import hashlib
from settings import settings


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
    def bson_properties(self):
        """ List of object properties for saving to mongo
        :return: List of strings
        """
        return []

    @classmethod
    def unserialize(cls, struct):
        clz = pickle.loads(str(struct['_class']))
        instance = clz()
        for key, value in struct.iteritems():
            if key == '_class':
                continue

            if isinstance(value, list):
                value = [cls.unserialize(el) for el in value]

            if isinstance(value, dict) and '_class' in value.keys():
                setattr(instance, key, pickle.loads(str(value['_class'])).unserialize(value))
            else:
                setattr(instance, key, value)
        return instance

    @property
    def bson(self):
        """ Using for Mongo serialization
        :return: Dict with bson data
        """
        resp = {}
        for key in self.bson_properties:
            if hasattr(self, key):
                val = getattr(self, key)
                has_bson_type = False
                for tp in self.BSON_TYPES:
                    if isinstance(val, tp):
                        has_bson_type = True
                        if isinstance(val, list):
                            val = [el.bson for el in val]
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


class MongoModel(Jsonify, object):
    db = mongo_client
    collection_name = None

    def __init__(self, *args, **kwargs):
        self._id = None

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
        resp = yield cls.find_raw(**kwargs)
        raise gen.Return([cls.unserialize(struct=model_raw) for model_raw in resp])

    @classmethod
    @gen.coroutine
    def find_raw(cls, **kwargs):
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

    @gen.coroutine
    def delete(self):
        response, error = yield gen.Task(self.__class__._collection().remove, {'_id': ObjectId(self._id)})
        print("Deleted! %s" % self._id)
        print("Response %s. Error: %s" % (response, error, ))

    @classmethod
    def _collection(cls):
        return getattr(cls.db, cls.collection_name or '%ss' % cls.__name__.lower())


class User(MongoModel):
    def __init__(self, login=''):
        super(User, self).__init__()
        self.login = login
        self.password = None
        self.name = self.login
        self.age = 0
        self.created = datetime.datetime.now()
        self.updated = datetime.datetime.now()
        self.last_visited = datetime.datetime.now()

    @classmethod
    @gen.coroutine
    def get_by_login_password(cls, login, password):
        password = hashlib.md5(''.join([settings["cookie_secret"], password, settings["cookie_secret"]])).hexdigest()
        users = yield cls.find(login=login, password=unicode(password))
        try:
            user = users[0]
        except IndexError, ex:
            raise ValueError("User not found")
        raise gen.Return(user)

    def set_password(self, new_password):
        password = hashlib.md5(''.join([settings["cookie_secret"], new_password, settings["cookie_secret"]]))\
                   .hexdigest()
        self.password = password

    @property
    def bson_properties(self):
        return ['login', 'name', 'password', 'age', 'created', 'updated', 'last_visited']