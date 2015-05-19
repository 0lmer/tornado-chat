# -*- coding: utf-8 -*-
import json
from core.handlers.auth import AuthSockJSHandler
from core.handlers.base import BaseSockJSHandler, BaseHandler
from tornado import gen


class ChatPageHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        db = self.application.db
        response, error = yield gen.Task(db.chat.find)
        messages = response[0]
        self.render('chat/chat.html', messages=messages)


class ChatAPIHandler(AuthSockJSHandler, BaseSockJSHandler):
    participants = set()

    def on_open(self, request):
        super(ChatAPIHandler, self).on_open(request)
        self.broadcast(self.participants, json.dumps({"text": "Someone joined.", "user": "system"}))
        self.participants.add(self)

    @gen.coroutine
    def on_message(self, message):
        super(ChatAPIHandler, self).on_message(message)
        db = self.application.db
        message_dict = json.loads(message)

        yield gen.Task(db.chat.insert, message_dict)
        for key, value in enumerate(self.participants):
                if value != self:
                    participants = (value, )
                    self.broadcast(participants, message)

    def on_close(self, message=None):
        self.participants.remove(self)
        self.broadcast(self.participants, json.dumps({"text": "Someone left.", "user": "system"}))