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
        controllers = {
            'table': TableController
        }
        controller_cls = controllers.get(self._message_json.get('type'))
        if controller_cls:
            controller = controller_cls(handler=self)
            action = controller.get_action(self._message_json['action'])
            yield action()


class TableController(object):

    def __init__(self, handler=None):
        self.handler = handler
        self.ACTION_MAP = {
            'join': self._join_table,
            'leave': self._leave_table,
            'bet': self._bet,
            'fold': self._fold
        }

    def get_action(self, action):
        return self.ACTION_MAP.get(action, lambda: 1)

    # @gen.coroutine
    # def receive_player_card(self, user):
    #     player = Player.from_user(user=user)
    #     table = yield self._get_table()
    #
    #     card = table.deck.pop_random_card()
    #     table.save()
    #     self._send_message({
    #         'action': 'receive_player_card',
    #         'data': {
    #             'player': player.to_json(),
    #             'card': card.to_json()
    #         }
    #     })

    @gen.coroutine
    def _join_table(self):
        table = yield self._get_table()
        player = Player.from_user(user=self.handler.current_user)
        table.add_player(player=player)
        yield table.save()
        self._send_message({
            'action': 'join',
            'data': {
                'player': player.to_json()
            }
        })

    @gen.coroutine
    def _leave_table(self):
        table = yield self._get_table()
        player = Player.from_user(user=self.handler.current_user)
        table.remove_player(player=player)
        yield table.save()
        self._send_message({
            'action': 'leave',
            'data': {
                'player': player.to_json()
            }
        })

    @gen.coroutine
    def _bet(self):
        amount = self.handler._message_json['data']['amount']
        table = yield self._get_table()
        player = Player.from_user(user=self.handler.current_user)
        yield table.save()

        self._send_message({
            'action': 'bet',
            'data': {
                'player': player.to_json(),
                'amount': amount
            }
        })

    @gen.coroutine
    def _fold(self):
        table = yield self._get_table()
        player = Player.from_user(user=self.handler.current_user)
        yield table.save()

        self._send_message({
            'action': 'fold',
            'data': {
                'player': player.to_json()
            }
        })

    @gen.coroutine
    def _get_table(self):
        table_id = self.handler._message_json['data']['table_id']
        tables = yield HoldemTable.find(_id=str(table_id))
        table = tables[0]
        raise gen.Return(table)

    def _send_message(self, message_dict):
        response_dict = message_dict.copy()
        default_data = {
            'type': 'table'
        }
        response_dict.update(default_data)
        self.handler.send_message(json.dumps(response_dict))