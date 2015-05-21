# -*- coding: utf-8 -*-
from core.handlers.auth import AuthSockJSHandler
from core.handlers.base import BaseSockJSHandler, BaseHandler
from chatapp.models import Message
from core.handlers.subscribe import RabbitMQSubscribeHandler, RedisSubscribeHandler, TornadoSubscribeHandler
from tornado import gen
import json


class ChatPageHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        # db = self.application.db
        response = yield Message.find()
        messages = response
        self.render('chatapp/chat.html', messages=messages)


# class ChatAPIHandler(AuthSockJSHandler, BaseSockJSHandler):
class ChatAPIHandler(TornadoSubscribeHandler):
    CHANNEL = 'messages'
    JOIN_MESSAGE = json.dumps({"text": "Someone joined.", "user": "system"})
    LEAVE_MESSAGE = json.dumps({"text": "Someone left.", "user": "system"})