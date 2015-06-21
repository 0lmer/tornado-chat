# -*- coding: utf-8 -*-
from core.models import User, MongoModel

__author__ = 'kdvo'

import unittest
import tornado
import tornado.gen
from bson import ObjectId

class ModelTest(unittest.TestCase):
    def setUp(self):
        self.mongo_model = MongoModel

    def tearDown(self):
        yield tornado.gen.Task(self.mongo_model._collection().remove, {})

    def test_find(self):
        models = yield self.mongo_model.find()
        self.assertEqual(len(models), 0)

    def test_id(self):
        model_obj = self.mongo_model(login='test_login')
        model_obj._id = ObjectId('5586edb39cd28238533e109f')
        self.assertEqual(str(model_obj._id), model_obj.id)


# class UserTest(unittest.TestCase):
#     def test_set_password(self):
#         user = User()
#         raw_password = 'testpassword'
#         user.set_password(raw_password)
#         self.assertEqual(user.password, 'sdfasdfasdfa')
#
#     def test_get_by_login_password(self):
#         user = User()
#         user.login = 'testlogin'
#         user.set_password('testpassword')
#         user.save()
#         self.assertEqual(True, False)
#         user.delete()


if __name__ == '__main__':
    unittest.main()