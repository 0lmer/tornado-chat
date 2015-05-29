# -*- coding: utf-8 -*-
from core.handlers.auth import AuthSockJSHandler
from core.handlers.base import BaseSockJSHandler, BaseHandler
from chatapp.models import Message
from core.handlers.subscribe import RabbitMQSubscribeHandler, RedisSubscribeHandler, TornadoSubscribeHandler
from pokerapp.models.game import HoldemTable
from tornado import gen
import json
from bson import json_util as bson_util
from tornado.web import HTTPError


class PokerTablePageHandler(BaseHandler):

    @gen.coroutine
    def get(self, room_id):
        resp = yield HoldemTable.find(_id=str(room_id))
        if not len(resp):
            raise HTTPError(404)
        table = HoldemTable.unserialize(struct=resp[0])
        table = bson_util.dumps(table.to_json())
        self.render('pokerapp/room.html', table=table)


# class PokerHandler(AuthSockJSHandler, BaseSockJSHandler):
class PokerHandler(TornadoSubscribeHandler):
    CHANNEL = 'messages'
    # JOIN_MESSAGE = json.dumps({"text": "Someone joined.", "user": "system"})
    # LEAVE_MESSAGE = json.dumps({"text": "Someone left.", "user": "system"})

    def join_table(self):
        pass