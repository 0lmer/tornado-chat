# -*- coding: utf-8 -*-


from pokerapp.handlers import poker
import sockjs.tornado

url_patterns = [
    (r"/poker/table/([a-zA-Z0-9]+)", poker.PokerTablePageHandler),
]