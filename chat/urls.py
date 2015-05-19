# -*- coding: utf-8 -*-
__author__ = 'kdvo'

from chat.handlers import chat
import sockjs.tornado

url_patterns = [
    (r"/chat", chat.ChatPageHandler),
]
ChatRouter = sockjs.tornado.SockJSRouter(chat.ChatAPIHandler, '/chat/ws')
url_patterns += ChatRouter.urls