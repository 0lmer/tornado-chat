# -*- coding: utf-8 -*-
from core.handlers.auth import AuthSockJSHandler
from core.handlers.base import BaseSockJSHandler, BaseHandler
from chatapp.models import Message
from core.handlers.subscribe import RabbitMQSubscribeHandler, RedisSubscribeHandler, TornadoSubscribeHandler
from tornado import gen
import json
from bson import json_util as bson_util


class PokerTablePageHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        # db = self.application.db
        messages = yield Message.find()
        messages = bson_util.dumps(messages)
        self.render('poker/room.html', messages=messages)


# class PokerHandler(AuthSockJSHandler, BaseSockJSHandler):
class PokerHandler(TornadoSubscribeHandler):
    CHANNEL = 'messages'
    # JOIN_MESSAGE = json.dumps({"text": "Someone joined.", "user": "system"})
    # LEAVE_MESSAGE = json.dumps({"text": "Someone left.", "user": "system"})

    def join_table(self):
        pass