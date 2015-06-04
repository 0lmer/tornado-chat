# -*- coding: utf-8 -*-

import unittest
from pokerapp.models.cards import HoldemDeck, Deck, Card, Suit, Heart
from pokerapp.models.game import Hand, Gamer, Table, HoldemTable


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

    def test_to_json(self):
        self.assertEqual(sorted(self.hand.to_json().keys()), sorted(['cards']))
        self.assertIsInstance(self.hand.to_json()['cards'], list)
        for card in self.cards:
            self.hand.add_card(card=card)
        self.assertIs(len(self.hand.to_json()['cards']), 3)


class GamerTest(unittest.TestCase):
    def setUp(self):
        self.gamer = Gamer()

    def test_has_enough_money(self):
        self.assertFalse(self.gamer.has_enough_money(amount=30))
        self.assertTrue(self.gamer.has_enough_money(amount=0))

    def test_add_card(self):
        self.assertEqual(len(self.gamer.hand.cards), 0)
        card = Card.from_code('Qd')
        self.gamer.add_card(card)

    def test_take_off_money(self):
        self.gamer._amount = 50
        self.gamer.take_off_money(amount=20)
        self.assertEqual(self.gamer._amount, 30)
        self.assertRaises(ValueError, self.gamer.take_off_money, 31)

    def test_to_json(self):
        self.assertEqual(sorted(self.gamer.to_json().keys()), sorted(['hand', 'amount', 'name']))
        self.gamer._amount = 30
        self.gamer.name = u"John"
        self.assertEqual(self.gamer.to_json()['amount'], 30)
        self.assertIsInstance(self.gamer.to_json()['hand'], dict)
        self.assertEqual(self.gamer.to_json()['name'], u"John")


class TableTest(unittest.TestCase):
    def setUp(self):
        self.table = Table()
        for step in xrange(0, 4):
            self.table.add_gamer(Gamer())

    def test_add_gamer(self):
        self.assertEqual(len(self.table.gamers), 4)
        self.table.add_gamer(Gamer())
        self.assertEqual(len(self.table.gamers), 5)

    def test_add_gamer(self):
        gamer1 = Gamer()
        gamer1.name = 'Vasya'
        gamer2 = Gamer()
        gamer2.name = 'Petya'
        self.table.add_gamer(gamer1)
        self.table.add_gamer(gamer2)
        self.assertEqual(len(self.table.gamers), 6)
        self.table.remove_gamer(gamer=gamer1)
        self.table.remove_gamer(gamer=gamer2)
        self.assertEqual(len(self.table.gamers), 4)

    def test_next_step(self):
        self.table.next_step()
        self.assertEqual(self.table.current_step, 1)
        self.table.next_step()
        self.assertEqual(self.table.current_step, 1)

    def test_to_json(self):
        self.assertIsInstance(self.table.to_json(), dict)
        self.assertEqual(sorted(self.table.to_json().keys()), sorted(['_id', 'active_gamers', 'board', 'circle_pot',
                                                                      'current_step', 'gamers', 'pot']))
        self.assertIsInstance(self.table.to_json()['gamers'], list)
        self.assertIsInstance(self.table.to_json()['active_gamers'], list)
        self.assertEqual(self.table.to_json()['pot'], 0)
        self.assertEqual(self.table.to_json()['circle_pot'], 0)
        self.assertEqual(self.table.to_json()['current_step'], 0)
        self.assertIsInstance(self.table.to_json()['board'], dict)


class HoldemTableTest(TableTest):
    def setUp(self):
        self.table = HoldemTable()
        for step in xrange(0, 4):
            self.table.add_gamer(Gamer())

    def test_preflop_cards(self):
        self.table.preflop()
        for gamer in self.table.gamers:
            self.assertEqual(len(gamer.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 0)

    def test_flop_cards(self):
        self.table.preflop()
        self.table.flop()
        for gamer in self.table.gamers:
            self.assertEqual(len(gamer.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 3)

    def test_turn_cards(self):
        self.table.preflop()
        self.table.flop()
        self.table.turn()
        for gamer in self.table.gamers:
            self.assertEqual(len(gamer.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 4)

    def test_river_cards(self):
        self.table.preflop()
        self.table.flop()
        self.table.turn()
        self.table.river()
        for gamer in self.table.gamers:
            self.assertEqual(len(gamer.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 5)

    def test_gamers_limit_in_room(self):
        for step in xrange(0, 5):
            self.table.add_gamer(Gamer())
        self.assertRaises(OverflowError, self.table.add_gamer, Gamer())

    def test_next_step(self):
        pass

    def test_cards_in_next_step(self):
        vasya = Gamer()
        petya = Gamer()
        dima = Gamer()
        self.table.add_gamer(vasya)
        self.table.add_gamer(petya)
        self.table.add_gamer(dima)

        self.assertEqual(len(dima.hand.cards), 0)
        self.table.next_step()  # preflop
        self.assertEqual(len(dima.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 0)

        self.table.next_step()  # flop
        self.assertEqual(len(dima.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 3)

        self.table.next_step()  # turn
        self.assertEqual(len(dima.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 4)

        self.table.next_step()  # river
        self.assertEqual(len(dima.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 5)

        self.table.next_step()  # showdown
        self.assertEqual(len(dima.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 5)

        self.table.next_step()  # new preflop
        self.assertEqual(len(dima.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 0)

        self.table.next_step()  # new flop
        self.assertEqual(len(dima.hand.cards), 2)
        self.assertEqual(len(self.table.board.cards), 3)

    def test_bet_in_next_step(self):
        vasya = Gamer()
        petya = Gamer()
        dima = Gamer()
        self.table.add_gamer(vasya)
        self.table.add_gamer(petya)
        self.table.add_gamer(dima)
        dima._amount = 400

        self.table.next_step()  # preflop
        self.assertEqual(dima._amount, 400)
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(gamer=dima, amount=50)
        self.assertEqual(dima._amount, 350)
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.circle_pot, 50)


        self.table.next_step()  # flop
        self.assertEqual(dima._amount, 350)
        self.assertEqual(self.table.pot, 50)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(gamer=dima, amount=50)
        self.assertEqual(dima._amount, 300)
        self.assertEqual(self.table.pot, 50)
        self.assertEqual(self.table.circle_pot, 50)

        self.table.next_step()  # turn
        self.assertEqual(dima._amount, 300)
        self.assertEqual(self.table.pot, 100)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(gamer=dima, amount=25)
        self.assertEqual(dima._amount, 275)
        self.assertEqual(self.table.pot, 100)
        self.assertEqual(self.table.circle_pot, 25)

        self.table.next_step()  # river
        self.assertEqual(dima._amount, 275)
        self.assertEqual(self.table.pot, 125)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(gamer=dima, amount=25)
        self.assertEqual(dima._amount, 250)
        self.assertEqual(self.table.pot, 125)
        self.assertEqual(self.table.circle_pot, 25)

        self.table.next_step()  # showdown
        self.assertEqual(dima._amount, 250)
        self.assertEqual(self.table.pot, 150)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(gamer=dima, amount=150)
        self.assertEqual(dima._amount, 100)
        self.assertEqual(self.table.pot, 150)
        self.assertEqual(self.table.circle_pot, 150)

        self.table.next_step()  # showdown
        self.assertEqual(dima._amount, 100)
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.circle_pot, 0)

    def test_bet(self):
        gamer = Gamer()
        gamer._amount = 300
        amount = 100
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(gamer, amount)
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.circle_pot, amount)


class EvaluatorTest(unittest.TestCase):
    pass