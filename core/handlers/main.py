# -*- coding: utf-8 -*-
from core.handlers.base import BaseHandler


class MainHandler(BaseHandler):

    #@tornado.web.authenticated
    def get(self):
        self.render('core/index.html')