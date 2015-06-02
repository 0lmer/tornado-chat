# -*- coding: utf-8 -*-

import tornadoredis
import redis
from settings import settings

redis_client = tornadoredis.Client()
redis_client_sync = redis.Redis()