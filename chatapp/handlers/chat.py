# -*- coding: utf-8 -*-
import json
from core.connection.rabbitmq import PikaClient
from core.handlers.auth import AuthSockJSHandler
from core.handlers.base import BaseSockJSHandler, BaseHandler
from chatapp.models import Message
from tornado import gen
import tornado.ioloop


class ChatPageHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        # db = self.application.db
        response = yield Message.find()
        messages = response
        self.render('chatapp/chat.html', messages=messages)


# class ChatAPIHandler(AuthSockJSHandler, BaseSockJSHandler):
class ChatAPIHandler(BaseSockJSHandler):
    participants = set()
    pika_client = PikaClient('messages')

    def on_open(self, request):
        super(ChatAPIHandler, self).on_open(request)
        self.broadcast(self.participants, json.dumps({"text": "Someone joined.", "user": "system"}))
        self.participants.add(self)
        tornado.ioloop.IOLoop.instance().add_timeout(1, self.pika_client.connect)

    @gen.coroutine
    def on_message(self, message):
        super(ChatAPIHandler, self).on_message(message)
        message_dict = json.loads(message)

        message_id = yield Message.insert(message_dict)
        self.pika_client.websocket = self
        self.pika_client.sample_message(message)  # self.write_message()

    def write_message(self, message):
        for key, value in enumerate(self.participants):
            if value != self:
                participants = (value, )
                self.broadcast(participants, message)
        #@TODO fix last websocket!
        self.pika_client.websocket = None

    def on_close(self, message=None):
        self.participants.remove(self)
        self.broadcast(self.participants, json.dumps({"text": "Someone left.", "user": "system"}))
        # self.pika_client.connection.close()