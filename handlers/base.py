# -*- coding: utf-8 -*-
import tornado.web
import sockjs.tornado

class BaseHandler(tornado.web.RequestHandler):
    pass


class MainHandler(BaseHandler):

    #@tornado.web.authenticated
    def get(self):
        self.render('index.html')


class BaseSockJSHandler(sockjs.tornado.SockJSConnection):
    application = None