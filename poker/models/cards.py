# -*- coding: utf-8 -*-
import random
from random import shuffle
"""
    Suits (in playing cards) – Масти (игральные).
    Deck – колода
    Suit – масть
    Hearts – червы
    Diamonds – бубны
    Clubs – трефы
    Spades – пики
    Jack – валет
    Queen – дама
    King – король
    Ace – туз
    Joker – джокер
"""

class Deck(object):
    def __init__(self, suits=None, rank_range=None):
        self._cards = []
        suits = [] if suits is None else suits
        for suit in suits:
            if rank_range:
                for rank in xrange(*rank_range):
                    card = Card.from_rank(suit=suit, rank=rank)
                    self._cards.append(card)
        shuffle(self._cards)

    def pop_random_card(self):
        max_idx = len(self._cards) - 1
        max_idx = max_idx if max_idx >= 0 else 0
        idx = random.randint(0, max_idx)
        card = self._cards.pop(idx)
        return card


class HoldemDeck(Deck):
    def __init__(self):
        suits = [Suit.from_type(suit_type) for suit_type in Suit.TYPES]
        super(HoldemDeck, self).__init__(suits=suits, rank_range=(2, 15, ))


class Card(object):
    DENOMINATION_TO_RATE = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    RATE_TO_DENOMINTAION = {rank: denomination for denomination, rank in DENOMINATION_TO_RATE.iteritems()}

    def __init__(self, suit):
        self.suit = suit
        self.denomination = None  # [2-10, J, Q, K, A]
        self.rank = None  # 2-14

    @classmethod
    def from_denomination(cls, suit, denomination):
        instance = cls(suit)
        instance.denomination = denomination
        instance.rank = cls.DENOMINATION_TO_RATE.get(denomination.upper())
        return instance

    @classmethod
    def from_rank(cls, suit, rank):
        instance = cls(suit)
        instance.rank = rank
        instance.denomination = cls.RATE_TO_DENOMINTAION.get(rank)
        return instance

    @property
    def description(self):
        return unicode(self)

    def __str__(self):
        return "%(suit)s%(denomination)s" % {'suit': self.suit.STRING_SYMBOL.encode("utf-8"),
                                             'denomination': self.denomination}

    def __unicode__(self):
        return u"%(suit)s%(denomination)s" % {'suit': self.suit.STRING_SYMBOL, 'denomination': self.denomination}


class Suit(object):
    HEARTS = 1
    DIAMONDS = 2
    CLUBS = 3
    SPADES = 4

    TYPES = [HEARTS, DIAMONDS, CLUBS, SPADES]
    STRING_SYMBOL = u""
    STRING_SYMBOL_WHITE = u""

    @classmethod
    def get_hearts(cls):
        return cls.from_type(cls.HEARTS)

    @classmethod
    def get_diamonds(cls):
        return cls.from_type(cls.DIAMONDS)

    @classmethod
    def get_clubs(cls):
        return cls.from_type(cls.CLUBS)

    @classmethod
    def get_spades(cls):
        return cls.from_type(cls.SPADES)

    @classmethod
    def from_type(cls, suit_type):
        return {
            cls.HEARTS: Heart,
            cls.DIAMONDS: Diamond,
            cls.CLUBS: Club,
            cls.SPADES: Spade,
        }.get(suit_type)()


class Heart(Suit):
    TYPE = Suit.HEARTS
    STRING_SYMBOL = u"♥"
    STRING_SYMBOL_WHITE = u"♡"


class Diamond(Suit):
    TYPE = Suit.DIAMONDS
    STRING_SYMBOL = u"♦"
    STRING_SYMBOL_WHITE = u"♢"


class Club(Suit):
    TYPE = Suit.CLUBS
    STRING_SYMBOL = u"♣"
    STRING_SYMBOL_WHITE = u"♧"


class Spade(Suit):
    TYPE = Suit.SPADES
    STRING_SYMBOL = u"♠"
    STRING_SYMBOL_WHITE = u"♤"