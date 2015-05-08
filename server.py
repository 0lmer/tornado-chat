#!/usr/bin/env python
#!-*- coding: utf-8 -*-

import json
import tornado.web
import tornado.ioloop
import tornado.websocket
from tornado import template
# import pymongo
import asyncmongo


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        db = self.application.db
        db.chat.find(callback=self._on_response)

    def _on_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)
        self.render('index.html', messages=response)


class WebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        self.application.webSocketsPool.append(self)

    def on_message(self, message):
        db = self.application.db
        message_dict = json.loads(message)

        def _send_to_another_people(response, error):
            if error:
                return
            for key, value in enumerate(self.application.webSocketsPool):
                if value != self:
                    value.ws_connection.write_message(message)

        db.chat.insert(message_dict, callback=_send_to_another_people)

    def on_close(self, message=None):
        for key, value in enumerate(self.application.webSocketsPool):
            if value == self:
                del self.application.webSocketsPool[key]


class Application(tornado.web.Application):
    def __init__(self):
        self.webSocketsPool = []

        settings = {
            'static_url_prefix': '/static/',
        }
        handlers = (
            (r'/', MainHandler),
            (r'/websocket/?', WebSocket),
            (r'/static/(.*)', tornado.web.StaticFileHandler,
             {'path': 'static/'}),
        )

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