# -*- coding: utf-8 -*-
from core.handlers.auth import AuthSockJSHandler
from core.handlers.base import BaseSockJSHandler, BaseHandler
from chatapp.models import Message
from core.handlers.subscribe import RabbitMQSubscribeHandler, RedisSubscribeHandler, TornadoSubscribeHandler
from tornado import gen
import json
from bson.json_util import dumps as bson_dumps, loads as bson_loads


class ChatPageHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        # db = self.application.db
        messages = yield Message.find_raw()
        self.render('chatapp/chat.html', messages=messages)


class ChatAngularPageHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        # db = self.application.db
        messages = yield Message.find_raw()
        json_messages = bson_dumps(messages)
        self.render('chatapp/chat_angular.html', messages=json_messages)


# class ChatAPIHandler(AuthSockJSHandler, BaseSockJSHandler):
class ChatAPIHandler(TornadoSubscribeHandler):
    CHANNEL = 'messages'
    JOIN_MESSAGE = json.dumps({"text": "Someone joined.", "user": "system"})
    LEAVE_MESSAGE = json.dumps({"text": "Someone left.", "user": "system"})

    @gen.coroutine
    def on_message(self, message):
        super(self.__class__, self).on_message(message)
        if 'user' not in self._message_json.keys():
            self._message_json['user'] = 'Unknown'
            message = json.dumps(self._message_json)
        message_id = yield Message.insert(self._message_json)
        self.send_message(message)