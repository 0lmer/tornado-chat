# -*- coding: utf-8 -*-

import unittest
from poker.models.cards import HoldemDeck, Deck, Card, Suit, Heart


class DeckTest(unittest.TestCase):
    def setUp(self):
        self.deck = Deck()

    def test_deck_length(self):
        self.assertEqual(len(self.deck._cards), 0)

    def test_pop_card_from_deck(self):
        self.assertRaises(IndexError, self.deck.pop_random_card)


class HoldemDeckTest(unittest.TestCase):
    def setUp(self):
        self.deck = HoldemDeck()

    def test_deck_length(self):
        self.assertEqual(len(self.deck._cards), 52)

    def test_pop_card_from_deck(self):
        card = self.deck.pop_random_card()
        self.assertIsInstance(card, Card)
        self.assertEqual(len(self.deck._cards), 51)


class CardTest(unittest.TestCase):
    QUEEN_STR = 'Q'
    QUEEN_RATE = 12
    JACK_STR = 'J'
    JACK_RATE = 11

    def setUp(self):
        self.suit = Suit.from_type(Suit.HEARTS)

    def test_card_denomination_from_rate(self):
        card = Card.from_rate(suit=self.suit, rate=self.JACK_RATE)
        self.assertEqual(card.denomination, self.JACK_STR)

    def test_card_denomination_from_denomination(self):
        card = Card.from_denomination(suit=self.suit, denomination=self.QUEEN_STR)
        self.assertEqual(card.rate, self.QUEEN_RATE)

    def test_card_description(self):
        card = Card.from_denomination(suit=self.suit, denomination=self.QUEEN_STR)
        self.assertEqual(card.description, u"♥Q")

    def test_card_str(self):
        card = Card.from_denomination(suit=self.suit, denomination=self.QUEEN_STR)
        self.assertEqual(unicode(card), u"♥Q")
        self.assertEqual(str(card), "♥Q")


class SuitTest(unittest.TestCase):
    def test_fabric_method(self):
        suit = Suit.from_type(suit_type=Suit.HEARTS)
        self.assertIsInstance(suit, Heart)

    def test_suit_types_length(self):
        self.assertEqual(len(Suit.TYPES), 4)