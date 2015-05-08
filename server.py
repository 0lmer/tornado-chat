#!/usr/bin/env python
#!-*- coding: utf-8 -*-

import json
import tornado.web
import tornado.ioloop
import tornado.websocket
from tornado import template
import asyncmongo
import sockjs.tornado


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        db = self.application.db

        def _on_response(response, error):
            if error:
                raise tornado.web.HTTPError(500)
            self.render('index.html', messages=response)

        db.chat.find(callback=_on_response)


class SockJSHandler(sockjs.tornado.SockJSConnection):
    participants = set()
    application = None

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


class Application(tornado.web.Application):
    def __init__(self):
        settings = {
            'static_url_prefix': '/static/',
        }
        handlers = [
            (r'/', MainHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler,
             {'path': 'static/'}),
        ]

        SockJSHandler.application = self
        ChatRouter = sockjs.tornado.SockJSRouter(SockJSHandler, '/websocket')
        handlers += ChatRouter.urls

        tornado.web.Application.__init__(self, handlers)

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = asyncmongo.Client(pool_id='chat', host='127.0.0.1', port=27017, maxcached=10,
                                             maxconnections=50, dbname='chat')
        return self._db

application = Application()

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()