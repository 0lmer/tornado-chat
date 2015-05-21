# -*- coding: utf-8 -*-
import random
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
    def __init__(self, suits=None, rate_range=None):
        self._cards = []
        suits = [] if suits is None else suits
        for suit in suits:
            if rate_range:
                for rate in xrange(*rate_range):
                    card = Card.from_rate(suit=suit, rate=rate)
                    self._cards.append(card)

    def pop_random_card(self):
        idx = random.randint(0, len(self._cards))
        card = self._cards.pop(idx)
        return card


class HoldemDeck(Deck):
    def __init__(self):
        suits = [Suit.from_type(suit_type) for suit_type in Suit.TYPES]
        super(HoldemDeck, self).__init__(suits=suits, rate_range=(2, 15, ))


class Card(object):
    DENOMINATION_TO_RATE = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    RATE_TO_DENOMINTAION = {rate: denomination for denomination, rate in DENOMINATION_TO_RATE.iteritems()}

    def __init__(self, suit):
        self.suit = suit
        self.denomination = None  # [2-10, J, Q, K, A]
        self.rate = None  # 2-14

    @classmethod
    def from_denomination(cls, suit, denomination):
        instance = cls(suit)
        instance.denomination = denomination
        instance.rate = cls.DENOMINATION_TO_RATE.get(denomination.upper())
        return instance

    @classmethod
    def from_rate(cls, suit, rate):
        instance = cls(suit)
        instance.rate = rate
        instance.denomination = cls.RATE_TO_DENOMINTAION.get(rate)
        return instance

    @property
    def description(self):
        return unicode(self)

    def __str__(self):
        return "%(suit)s%(denomination)s" % {'suit': self.suit.STRING_SYMBOL.encode("utf-8"), 'denomination': self.denomination}

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