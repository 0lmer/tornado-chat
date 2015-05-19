# -*- coding: utf-8 -*-
from handlers.auth import AuthSockJSHandler
from handlers.base import BaseSockJSHandler, BaseHandler
import tornado.web
from tornado import gen
import sockjs.tornado
import json


class ChatPageHandler(BaseHandler):
    # @tornado.web.asynchronous
    # def get(self):
    #     db = self.application.db
    #
    #     def _on_response(response, error):
    #         if error:
    #             raise tornado.web.HTTPError(500)
    #         self.render('chat.html', messages=response)
    #
    #     db.chat.find(callback=_on_response)

    @gen.coroutine
    def get(self):
        db = self.application.db
        response, error = yield gen.Task(db.chat.find)
        messages = response[0]
        self.render('chat.html', messages=messages)


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