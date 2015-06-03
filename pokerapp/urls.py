# -*- coding: utf-8 -*-


from pokerapp.handlers import holdem
import sockjs.tornado

url_patterns = [
    (r"/poker/table/([a-zA-Z0-9]+)", holdem.PokerTablePageHandler),
    (r"/poker/table/", holdem.PokerRoomHandler),
]

PokerRouter = sockjs.tornado.SockJSRouter(holdem.PokerHandler, '/poker/ws')
url_patterns += PokerRouter.urls