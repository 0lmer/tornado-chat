# -*- coding: utf-8 -*-
from core.handlers.auth import AuthSockJSHandler
from core.handlers.base import BaseSockJSHandler, BaseHandler
from chatapp.models import Message
from core.handlers.subscribe import RabbitMQSubscribeHandler, RedisSubscribeHandler, TornadoSubscribeHandler
from pokerapp.models.game import HoldemTable, Player
from tornado import gen
from tornado import web
import json
from bson import json_util as bson_util
from tornado.web import HTTPError


class PokerRoomHandler(BaseHandler):

    @web.authenticated
    @gen.coroutine
    def get(self):
        tables = yield HoldemTable.find()
        self.render('pokerapp/room.html', tables=tables)


class PokerTablePageHandler(BaseHandler):

    @web.authenticated
    @gen.coroutine
    def get(self, room_id):
        tables = yield HoldemTable.find(_id=str(room_id))
        table = bson_util.dumps(tables[0].to_json())
        self.render('pokerapp/table.html', table=table, session_sid=self.get_cookie("user"))


class PokerHandler(AuthSockJSHandler, RedisSubscribeHandler):
# class PokerHandler(TornadoSubscribeHandler):
    CHANNEL = 'messages'
    # JOIN_MESSAGE = json.dumps({"text": "Someone joined.", "user": "system"})
    # LEAVE_MESSAGE = json.dumps({"text": "Someone left.", "user": "system"})

    @gen.coroutine
    def on_message(self, message):
        super(PokerHandler, self).on_message(message=message)
        type = {
            'table': {
                'join': self.join_table,
                'leave': self.leave_table,
                'bet': self.bet
            }
        }.get(self._message_json.get('type'), {})
        action = type.get(self._message_json['action'], lambda: 1)
        yield action()

    @gen.coroutine
    def join_table(self):
        table_id = self._message_json['data']['table_id']

        tables = yield HoldemTable.find(_id=str(table_id))
        table = tables[0]
        player = Player.from_user(user=self.current_user)
        table.add_player(player=player)
        yield table.save()
        self.send_message(json.dumps({
            'type': 'table',
            'action': 'join',
            'data': {
                'player': player.to_json()
            }
        }))

    @gen.coroutine
    def leave_table(self):
        table_id = self._message_json['data']['table_id']

        tables = yield HoldemTable.find(_id=str(table_id))
        table = tables[0]
        player = Player.from_user(user=self.current_user)
        table.remove_player(player=player)
        yield table.save()
        self.send_message(json.dumps({
            'type': 'table',
            'action': 'leave',
            'data': {
                'player': player.to_json()
            }
        }))

    @gen.coroutine
    def bet(self):
        table_id = self._message_json['data']['table_id']
        amount = self._message_json['data']['amount']

        tables = yield HoldemTable.find(_id=str(table_id))
        table = tables[0]
        player = Player.from_user(user=self.current_user)
        yield table.save()

        self.send_message(json.dumps({
            'type': 'table',
            'action': 'bet',
            'data': {
                'player': player.to_json(),
                'amount': amount
            }
        }))


    @gen.coroutine
    def receive_player_card(self):
        pass