# -*- coding: utf-8 -*-

import unittest
from pokerapp.models.cards import HoldemDeck, Deck, Card, Suit, Heart
import copy


class DeckTest(unittest.TestCase):
    def setUp(self):
        self.empty_deck = Deck()
        self.full_deck = Deck(suits=[Suit.from_type(suit_type) for suit_type in Suit.TYPES], rank_range=(2, 15, ))

    def test_length(self):
        self.assertEqual(self.empty_deck.length(), 0)
        full_deck_length = 52
        self.assertEqual(self.full_deck.length(), full_deck_length)

    def test_pop_card_from_deck(self):
        self.assertRaises(IndexError, self.empty_deck.pop_random_card)

    def test_shuffle(self):
        deck = Deck(suits=[Suit.from_type(suit_type) for suit_type in Suit.TYPES], rank_range=(2, 15, ))
        unshuffled_cards = copy.copy(deck._cards)
        deck.shuffle()
        self.assertNotEqual(unshuffled_cards, deck._cards)


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
        self.suit = Suit.get_hearts()

    def test_card_denomination_from_rank(self):
        card = Card.from_rank(suit=self.suit, rank=self.JACK_RATE)
        self.assertEqual(card.denomination, self.JACK_STR)

    def test_card_denomination_from_denomination(self):
        card = Card.from_denomination(suit=self.suit, denomination=self.QUEEN_STR)
        self.assertEqual(card.rank, self.QUEEN_RATE)

    def test_card_description(self):
        card = Card.from_denomination(suit=self.suit, denomination=self.QUEEN_STR)
        self.assertEqual(card.description, u"Q♥")

    def test_card_str(self):
        card = Card.from_denomination(suit=self.suit, denomination=self.QUEEN_STR)
        self.assertEqual(unicode(card), u"Q♥")
        self.assertEqual(str(card), "Q♥")

    def test_code(self):
        card = Card.from_denomination(suit=self.suit, denomination=self.QUEEN_STR)
        self.assertEqual(card.code, u'Qh')

    def test_create_card_from_code(self):
        card = Card.from_code('Qd')
        self.assertEqual(unicode(card), u"Q♦")
        self.assertEqual(str(card), "Q♦")

    def test_to_json(self):
        card = Card.from_denomination(suit=Suit.get_diamonds(), denomination=self.QUEEN_STR)
        self.assertIsInstance(card.to_json(), dict)
        self.assertEqual(card.to_json()['description'], u'Q♦')
        self.assertEqual(card.to_json()['denomination'], u'Q')
        self.assertEqual(card.to_json()['rank'], self.QUEEN_RATE)
        self.assertEqual(card.to_json()['code'], u'Qd')
        self.assertIsInstance(card.to_json()['suit'], dict)


class SuitTest(unittest.TestCase):
    def test_fabric_method(self):
        suit = Suit.get_hearts()
        self.assertIsInstance(suit, Heart)

    def test_suit_types_length(self):
        self.assertEqual(len(Suit.TYPES), 4)

    def test_to_json(self):
        suit = Suit.get_hearts()
        self.assertIsInstance(suit.to_json(), dict)
        self.assertEqual(suit.to_json()['type'], 1)
        self.assertEqual(suit.to_json()['type_str'], u'h')
        self.assertEqual(suit.to_json()['user_str'], u"♥")
        self.assertEqual(suit.to_json()['user_str_white'], u"♡")