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
        instance._amount = user.total_amount
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
            'id': self.id,
        }

    def __eq__(self, other):
        try:
            return self.id == other.id and self.id is not None
        except AttributeError, ex:
            return False

    def __ne__(self, other):
        try:
            return (not (self.id == other.id)) or (None in [self.id, other.id])
        except AttributeError, ex:
            return True

    def __str__(self):
        return '<Player %s %s>' % (self.name, self.id, )

    def __unicode__(self):
        return u'<Player %s %s>' % (self.name, self.id, )


class Table(MongoModel, Jsonify):

    def __init__(self):
        super(Table, self).__init__()
        self.PLAN = {}
        self.players = []
        self.active_players = []
        self._active_player = None
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
                if not len(self.players):
                    self._set_next_active_player(player)
                self.players.append(player)
            else:
                raise OverflowError("Player %s already at the table" % (str(player.id) + ' ' + player.name))
        else:
            raise OverflowError("Table is full")

    def remove_player(self, player):
        try:
            player_idx = self.players.index(player)
            try:
                if self._active_player == player:
                    self._set_next_active_player(current_player=player)
            except ValueError, ex:
                self._active_player = None
            self.players.pop(player_idx)
        except ValueError, ex:
            raise ValueError("Player does not exist")

    def has_player_at_the_table(self, player):
        return player in self.players

    def bet(self, player, amount):
        if self._active_player != player:
            raise ValueError("%s is not active player (%s)" % (player, self._active_player, ))
        player.take_off_money(amount=amount)
        self.circle_pot += amount
        self._set_next_active_player(current_player=player)

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
        self._active_player = self.active_players[0] if len(self.active_players) else None

    def _merge_cirlce_pot(self):
        self.pot += self.circle_pot
        self.circle_pot = 0

    def _set_next_active_player(self, current_player):
        if self._active_player is None:
            self._active_player = current_player
            return

        active_player_idx = self.active_players.index(self._active_player)
        if (active_player_idx + 1) < len(self.active_players):
            self._active_player = self.active_players[active_player_idx+1]
        else:
            self._active_player = self.players[0]

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
