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


class Gamer(object):
    def __init__(self):
        self.hand = Hand()
        # self.

    def clean_hand(self):
        self.hand.clean()

    def add_card(self, card):
        self.hand.add_card(card=card)


class Room(object):
    def __init__(self):
        self.gamers = []
        self.active_gamers = []
        self.deck = HoldemDeck()
        self.board = Hand()
        self.max_gamers_count = 9
        self.pot = 0
        self.buy_in = 0
        self.rake = 0  # Comission

    def add_gamer(self, gamer):
        if len(self.gamers) < self.max_gamers_count:
            self.gamers.append(gamer)
        else:
            raise OverflowError("Room is full")

    def preflop(self):
        self.active_gamers = copy.copy(self.gamers)
        for gamer in self.active_gamers:
            gamer.add_card(card=self.deck.pop_random_card())
            gamer.add_card(card=self.deck.pop_random_card())

    def flop(self):
        for step in xrange(0,3):
            self.board.add_card(self.deck.pop_random_card())

    def turn(self):
        self.board.add_card(self.deck.pop_random_card())

    def river(self):
        self.board.add_card(self.deck.pop_random_card())

    def finish(self):
        self.active_gamers = self.gamers[:]
        self.pot = 0