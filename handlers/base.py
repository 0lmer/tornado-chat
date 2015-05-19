# -*- coding: utf-8 -*-
import json

from session import Session
import tornado.web
import sockjs.tornado


class ProjectSessionHandler(object):
    _sid = None
    application = None

    @property
    def project_session(self):
        if self._sid:
            return Session(self.application.session_store, self._sid)
        else:
            return None


class BaseHandler(ProjectSessionHandler, tornado.web.RequestHandler):
    pass


class BaseSockJSHandler(sockjs.tornado.SockJSConnection, ProjectSessionHandler):
    application = None

    def __init__(self, session):
        super(BaseSockJSHandler, self).__init__(session)
        self._message_json = None

    def on_open(self, request):
        super(BaseSockJSHandler, self).on_open(request)

    def on_message(self, message):
        try:
            self._message_json = json.loads(message)
        except ValueError, ex:
            pass
        print(message)


class MainHandler(BaseHandler):

    #@tornado.web.authenticated
    def get(self):
        self.render('index.html')