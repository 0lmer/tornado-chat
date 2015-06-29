# -*- coding: utf-8 -*-
from core.models import Jsonify, MongoModel
from pokerapp.models.cards import HoldemDeck, Deck
import copy

"""
    Термины
    http://ru.pokerstrategy.com/strategy/others/566/1/
    http://www.uapoker.info/glossary-poker-1.html
"""


class Hand(Jsonify):
    def __init__(self):
        self._cards = []

    def add_card(self, card):
        self._cards.append(card)

    def clean(self):
        del self._cards[:]

    def length(self):
        return len(self._cards)

    def to_json(self):
        return {
            'cards': [card.to_json() for card in self._cards]
        }

    @property
    def bson_properties(self):
        return ['_cards']

    def __str__(self):
        return "%s" % [str(card) for card in self._cards]

    def __unicode__(self):
        return u", ".join([unicode(card) for card in self._cards])

    def __repr__(self):
        return self.__unicode__()


class Player(Jsonify):
    def __init__(self):
        self.hand = Hand()
        self.name = u''
        self._amount = 0
        self.user = None

    @classmethod
    def from_user(cls, user):
        instance = cls()
        instance.user = user
        instance.name = user.name
        return instance

    @property
    def id(self):
        return self.user.id if self.user else None

    def clean_hand(self):
        self.hand.clean()

    def add_card(self, card):
        self.hand.add_card(card=card)

    def take_off_money(self, amount):
        if not self.has_enough_money(amount):
            raise ValueError("Player hasn't enough money!")
        self._amount -= amount

    def has_enough_money(self, amount):
        return self._amount >= amount

    @property
    def amount(self):
        return self._amount

    @property
    def bson_properties(self):
        return ['name', '_amount', 'hand', 'user']

    def to_json(self):
        return {
            'amount': self.amount,
            'hand': self.hand.to_json(),
            'name': self.name,
            'id': self.user.id if self.user else None,
        }

class Table(MongoModel, Jsonify):

    def __init__(self):
        super(Table, self).__init__()
        self.PLAN = {}
        self.players = []
        self.active_players = []
        self.board = Hand()
        self.max_players_count = 9
        self.deck = Deck()
        self.pot = 0
        self.circle_pot = 0
        self.buy_in = 0
        self.rake = 0  # Comission
        self.current_step = 0
        self.current_player = None
        self.name = None

    @property
    def bson_properties(self):
        return ['players', 'active_players', 'board', 'max_players_count', 'deck', 'pot', 'circle_pot', 'buy_in', 'rake',
                'current_step', 'current_player', 'name']

    def add_player(self, player):
        if len(self.players) < self.max_players_count:
            if not self.has_player_at_the_table(player=player):
                self.players.append(player)
            else:
                raise OverflowError("Player %s already at the table" % (str(player.id) + ' ' + player.name))
        else:
            raise OverflowError("Table is full")

    def remove_player(self, player):
        for idx, gmr in enumerate(self.players):
            if gmr.id == player.id:
                self.players.pop(idx)
                return
        raise ValueError("Player does not exist")

    def has_player_at_the_table(self, player):
        return player.id in (player.id for player in self.players)

    def bet(self, player, amount):
        player.take_off_money(amount=amount)
        self.circle_pot += amount

    def next_step(self):
        if self.current_step >= len(self.PLAN.keys()):
            self.clean()
        self.current_step += 1
        self.PLAN.get(self.current_step, (lambda: 1))()

    def clean(self):
        self.active_players = self.players[:]
        self.pot = 0
        self.circle_pot = 0
        self.deck = HoldemDeck()
        self.deck.shuffle()
        self.board.clean()
        self.current_step = 0
        for player in self.players:
            player.hand.clean()

    def _merge_cirlce_pot(self):
        self.pot += self.circle_pot
        self.circle_pot = 0

    def to_json(self):
        return {
            'players': [player.to_json() for player in self.players],
            'active_players': [player.to_json() for player in self.active_players],
            'pot': self.pot,
            'circle_pot': self.circle_pot,
            'board': self.board.to_json(),
            'current_step': self.current_step,
            '_id': str(self._id)
        }


class HoldemTable(Table):
    def __init__(self):
        super(HoldemTable, self).__init__()
        self.deck = HoldemDeck()
        self.deck.shuffle()
        self.PLAN = {
            1: self.preflop,
            2: self.flop,
            3: self.turn,
            4: self.river,
            5: self.showdown,
        }

    def preflop(self):
        self._merge_cirlce_pot()
        self.active_players = copy.copy(self.players)
        for player in self.active_players:
            player.add_card(card=self.deck.pop_random_card())
            player.add_card(card=self.deck.pop_random_card())

    def flop(self):
        self._merge_cirlce_pot()
        for el in xrange(0,3):
            self.board.add_card(self.deck.pop_random_card())

    def turn(self):
        self._merge_cirlce_pot()
        self.board.add_card(self.deck.pop_random_card())

    def river(self):
        self._merge_cirlce_pot()
        self.board.add_card(self.deck.pop_random_card())

    def showdown(self):
        self._merge_cirlce_pot()
        pass
