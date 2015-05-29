# -*- coding: utf-8 -*-
from chatapp.urls import url_patterns as chat_urls
from core.urls import url_patterns as core_urls
from pokerapp.urls import url_patterns as poker_urls

url_patterns = []
url_patterns += chat_urls
url_patterns += core_urls
url_patterns += poker_urls