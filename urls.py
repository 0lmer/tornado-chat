# -*- coding: utf-8 -*-
from handlers import base, chat
import sockjs.tornado

url_patterns = [
    (r"/", base.MainHandler),
    (r"/chat", chat.ChatPageHandler),
]
ChatRouter = sockjs.tornado.SockJSRouter(chat.ChatAPIHandler, '/chat/ws')
url_patterns += ChatRouter.urls