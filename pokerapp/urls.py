# -*- coding: utf-8 -*-


from pokerapp.handlers import poker
import sockjs.tornado

url_patterns = [
    (r"/poker/table", poker.PokerTablePageHandler),
]