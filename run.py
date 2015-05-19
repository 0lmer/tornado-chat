#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncmongo
from session import RedisSessionStore
import tornadoredis
from handlers.base import BaseSockJSHandler

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.autoreload
from tornado.options import options

from settings import settings
from urls import url_patterns


class TornadoApplication(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, url_patterns, **settings)
        self.session_store = RedisSessionStore(self.redis_client)

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = asyncmongo.Client(pool_id='chat', host='127.0.0.1', port=27017, maxcached=10,
                                             maxconnections=50, dbname='chat')
        return self._db

    @property
    def redis_client(self):
        if not hasattr(self, '_redis_client'):
            self._redis_client = tornadoredis.Client()
            self._redis_client.connect()
        return self._redis_client

def main():
    app = TornadoApplication()
    BaseSockJSHandler.application = app
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()