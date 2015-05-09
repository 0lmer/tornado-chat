# -*- coding: utf-8 -*-
from handlers.base import BaseSockJSHandler
import tornado.web
import sockjs.tornado
import json

class ChatPageHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        db = self.application.db

        def _on_response(response, error):
            if error:
                raise tornado.web.HTTPError(500)
            self.render('chat.html', messages=response)

        db.chat.find(callback=_on_response)


class ChatAPIHandler(BaseSockJSHandler):
    participants = set()

    def on_open(self, request):
        self.broadcast(self.participants, json.dumps({"text": "Someone joined.", "user": "system"}))
        self.participants.add(self)

    def on_message(self, message):
        db = self.application.db
        message_dict = json.loads(message)

        def _send_to_another_people(response, error):
            if error:
                return
            for key, value in enumerate(self.participants):
                if value != self:
                    participants = (value, )
                    self.broadcast(participants, message)

        db.chat.insert(message_dict, callback=_send_to_another_people)

    def on_close(self, message=None):
        self.participants.remove(self)
        self.broadcast(self.participants, json.dumps({"text": "Someone left.", "user": "system"}))