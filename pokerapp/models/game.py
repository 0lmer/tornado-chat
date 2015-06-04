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
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def clean(self):
        del self.cards[:]

    def to_json(self):
        return {
            'cards': [card.to_json() for card in self.cards]
        }

    @property
    def bson_properties(self):
        return ['cards']

    def __str__(self):
        return "%s" % [str(card) for card in self.cards]

    def __unicode__(self):
        return u", ".join([unicode(card) for card in self.cards])

    def __repr__(self):
        return self.__unicode__()


class Gamer(Jsonify):
    def __init__(self):
        self.hand = Hand()
        self.name = u''
        self._amount = 0

    def clean_hand(self):
        self.hand.clean()

    def add_card(self, card):
        self.hand.add_card(card=card)

    def take_off_money(self, amount):
        if not self.has_enough_money(amount):
            raise ValueError("Gamer hasn't enough money!")
        self._amount -= amount

    def has_enough_money(self, amount):
        return self._amount >= amount

    @property
    def amount(self):
        return self._amount

    @property
    def bson_properties(self):
        return ['name', '_amount', 'hand']

    def to_json(self):
        return {
            'amount': self.amount,
            'hand': self.hand.to_json(),
            'name': self.name
        }

class Table(MongoModel, Jsonify):

    def __init__(self):
        super(Table, self).__init__()
        self.PLAN = {}
        self.gamers = []
        self.active_gamers = []
        self.board = Hand()
        self.max_gamers_count = 9
        self.deck = Deck()
        self.pot = 0
        self.circle_pot = 0
        self.buy_in = 0
        self.rake = 0  # Comission
        self.current_step = 0
        self.current_gamer = None
        self.name = None

    @property
    def bson_properties(self):
        return ['gamers', 'active_gamers', 'board', 'max_gamers_count', 'deck', 'pot', 'circle_pot', 'buy_in', 'rake',
                'current_step', 'current_gamer', 'name']

    def add_gamer(self, gamer):
        if len(self.gamers) < self.max_gamers_count:
            self.gamers.append(gamer)
        else:
            raise OverflowError("Table is full")

    def remove_gamer(self, gamer):
        for idx, gmr in enumerate(self.gamers):
            if gmr.name == gamer.name:
                self.gamers.pop(idx)
                return
        raise ValueError("Gamer does not exist")

    def bet(self, gamer, amount):
        gamer.take_off_money(amount=amount)
        self.circle_pot += amount

    def next_step(self):
        if self.current_step >= len(self.PLAN.keys()):
            self.clean()
        self.current_step += 1
        self.PLAN.get(self.current_step, (lambda: 1))()

    def clean(self):
        self.active_gamers = self.gamers[:]
        self.pot = 0
        self.circle_pot = 0
        self.deck = HoldemDeck()
        self.deck.shuffle()
        self.board.clean()
        self.current_step = 0
        for gamer in self.gamers:
            gamer.hand.clean()

    def _merge_cirlce_pot(self):
        self.pot += self.circle_pot
        self.circle_pot = 0

    def to_json(self):
        return {
            'gamers': [gamer.to_json() for gamer in self.gamers],
            'active_gamers': [gamer.to_json() for gamer in self.active_gamers],
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
        self.active_gamers = copy.copy(self.gamers)
        for gamer in self.active_gamers:
            gamer.add_card(card=self.deck.pop_random_card())
            gamer.add_card(card=self.deck.pop_random_card())

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
