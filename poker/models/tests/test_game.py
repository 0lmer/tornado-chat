# -*- coding: utf-8 -*-

import unittest
from poker.models.cards import HoldemDeck, Deck, Card, Suit, Heart
from poker.models.game import Hand, Gamer, Room


class HandTest(unittest.TestCase):
    def setUp(self):
        self.hand = Hand()
        self.cards = [Card.from_rank(Suit.get_hearts(), 10), Card.from_rank(Suit.get_hearts(), 11),
                      Card.from_rank(Suit.get_hearts(), 12)]

    def test_adding_card(self):
        for card in self.cards:
            self.hand.add_card(card=card)
        self.assertEqual(len(self.hand.cards), 3)

    def test_clean_cards(self):
        for card in self.cards:
            self.hand.add_card(card=card)
        self.assertEqual(len(self.hand.cards), 3)
        self.hand.clean()
        self.assertEqual(len(self.hand.cards), 0)


class RoomTest(unittest.TestCase):
    def setUp(self):
        self.room = Room()
        for step in xrange(0, 4):
            self.room.add_gamer(Gamer())

    def test_gamers_count(self):
        self.assertEqual(len(self.room.gamers), 4)

    def test_preflop_cards(self):
        self.room.preflop()
        for gamer in self.room.gamers:
            self.assertEqual(len(gamer.hand.cards), 2)
        self.assertEqual(len(self.room.board.cards), 0)

    def test_flop_cards(self):
        self.room.preflop()
        self.room.flop()
        for gamer in self.room.gamers:
            self.assertEqual(len(gamer.hand.cards), 2)
        self.assertEqual(len(self.room.board.cards), 3)

    def test_turn_cards(self):
        self.room.preflop()
        self.room.flop()
        self.room.turn()
        for gamer in self.room.gamers:
            self.assertEqual(len(gamer.hand.cards), 2)
        self.assertEqual(len(self.room.board.cards), 4)

    def test_river_cards(self):
        self.room.preflop()
        self.room.flop()
        self.room.turn()
        self.room.river()
        for gamer in self.room.gamers:
            self.assertEqual(len(gamer.hand.cards), 2)
        self.assertEqual(len(self.room.board.cards), 5)

    def test_gamers_limit_in_room(self):
        for step in xrange(0, 5):
            self.room.add_gamer(Gamer())
        self.assertRaises(OverflowError, self.room.add_gamer, Gamer())

    def test_bet(self):
        gamer = Gamer()
        amount = 100
        self.assertEqual(self.bet(gamer, amount), False)