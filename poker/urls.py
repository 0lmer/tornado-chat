# -*- coding: utf-8 -*-


from poker.handlers import poker
import sockjs.tornado

url_patterns = [
    (r"/poker/table", poker.PokerTablePageHandler),
]