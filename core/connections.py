# -*- coding: utf-8 -*-

import asyncmongo
import tornadoredis
from settings import settings


db_client = asyncmongo.Client(pool_id=settings["mongo_db_name"], host=settings["mongo_host"],
                                         port=settings["mongo_port"], maxcached=10, maxconnections=50,
                                         dbname=settings["mongo_db_name"])
redis_client = tornadoredis.Client()