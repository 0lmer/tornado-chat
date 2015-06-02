# -*- coding: utf-8 -*-
__author__ = 'kdvo'
from core.handlers import base, auth, main

url_patterns = [
    (r"/", main.MainHandler),
    (r"/login", auth.LoginHandler),
    (r"/register", auth.RegisterHandler),
]