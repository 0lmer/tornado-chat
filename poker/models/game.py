# -*- coding: utf-8 -*-
from poker.models.cards import HoldemDeck
import copy

"""
    Термины
    http://ru.pokerstrategy.com/strategy/others/566/1/
    http://www.uapoker.info/glossary-poker-1.html
"""

class Hand(object):
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def clean(self):
        del self.cards[:]

    def __str__(self):
        return "%s" % [str(card) for card in self.cards]

    def __unicode__(self):
        return u", ".join([unicode(card) for card in self.cards])

    def __repr__(self):
        return self.__unicode__()


class Gamer(object):
    def __init__(self):
        self.hand = Hand()
        # self.

    def clean_hand(self):
        self.hand.clean()

    def add_card(self, card):
        self.hand.add_card(card=card)


class Table(object):
    def __init__(self):
        self.gamers = []
        self.active_gamers = []
        self.board = Hand()
        self.max_gamers_count = 9
        self.deck = HoldemDeck()
        self.pot = 0
        self.buy_in = 0
        self.rake = 0  # Comission
        self.PLAN = {
            1: self.preflop,
            2: self.flop,
            3: self.turn,
            4: self.river,
            5: self.showdown,
        }
        self.current_step = 0

    def add_gamer(self, gamer):
        if len(self.gamers) < self.max_gamers_count:
            self.gamers.append(gamer)
        else:
            raise OverflowError("Room is full")

    def next_step(self):
        if self.current_step == 5:
            self.clean()
        self.current_step += 1
        self.PLAN.get(self.current_step)()

    def preflop(self):
        self.active_gamers = copy.copy(self.gamers)
        for gamer in self.active_gamers:
            gamer.add_card(card=self.deck.pop_random_card())
            gamer.add_card(card=self.deck.pop_random_card())

    def flop(self):
        for el in xrange(0,3):
            self.board.add_card(self.deck.pop_random_card())

    def turn(self):
        self.board.add_card(self.deck.pop_random_card())

    def river(self):
        self.board.add_card(self.deck.pop_random_card())

    def showdown(self):
        pass

    def clean(self):
        self.active_gamers = self.gamers[:]
        self.pot = 0
        self.deck = HoldemDeck()
        self.board.clean()
        self.current_step = 0