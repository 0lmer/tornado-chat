# -*- coding: utf-8 -*-

import unittest
from core.models import User
from pokerapp.models.cards import HoldemDeck, Deck, Card, Suit, Heart
from pokerapp.models.game import Hand, Table, HoldemTable, Player as PlayerOrig


class Player(PlayerOrig):
    @property
    def id(self):
        if not hasattr(self, '_mocked_id'):
            self._mocked_id = None
        return self._mocked_id

    @id.setter
    def id(self, value):
        self._mocked_id = value


class HandTest(unittest.TestCase):
    def setUp(self):
        self.hand = Hand()
        self.cards = [Card.from_rank(Suit.get_hearts(), 10), Card.from_rank(Suit.get_hearts(), 11),
                      Card.from_rank(Suit.get_hearts(), 12)]

    def test_adding_card(self):
        for card in self.cards:
            self.hand.add_card(card=card)
        self.assertEqual(self.hand.length(), 3)

    def test_clean_cards(self):
        for card in self.cards:
            self.hand.add_card(card=card)
        self.assertEqual(self.hand.length(), 3)
        self.hand.clean()
        self.assertEqual(self.hand.length(), 0)

    def test_length(self):
        self.assertEqual(self.hand.length(), 0)
        for card in self.cards:
            self.hand.add_card(card=card)
        self.assertEqual(self.hand.length(), 3)

    def test_to_json(self):
        self.assertEqual(sorted(self.hand.to_json().keys()), sorted(['cards']))
        self.assertIsInstance(self.hand.to_json()['cards'], list)
        for card in self.cards:
            self.hand.add_card(card=card)
        self.assertIs(len(self.hand.to_json()['cards']), 3)


class PlayerTest(unittest.TestCase):
    def setUp(self):
        self.player = PlayerOrig()

    def test_has_enough_money(self):
        self.assertFalse(self.player.has_enough_money(amount=30))
        self.assertTrue(self.player.has_enough_money(amount=0))

    def test_add_card(self):
        self.assertEqual(self.player.hand.length(), 0)
        card = Card.from_code('Qd')
        self.player.add_card(card)

    def test_take_off_money(self):
        self.player._amount = 50
        self.player.take_off_money(amount=20)
        self.assertEqual(self.player._amount, 30)
        self.assertRaises(ValueError, self.player.take_off_money, 31)

    def test_to_json(self):
        self.assertEqual(sorted(self.player.to_json().keys()), sorted(['hand', 'amount', 'name', 'id']))
        self.player._amount = 30
        self.player.name = u"John"
        self.assertEqual(self.player.to_json()['amount'], 30)
        self.assertIsInstance(self.player.to_json()['hand'], dict)
        self.assertEqual(self.player.to_json()['name'], u"John")

    def test_create_player_from_user(self):
        user = User(login='test_login')
        user.name = 'test_name'
        player = PlayerOrig.from_user(user=user)
        self.assertEqual(player.name, user.name)
        self.assertEqual(player.user, user)
        self.assertEqual(player.id, user.id)

    def test_eq(self):
        user = User(login='test_login')
        user._id = 1
        user2 = User(login='test_login2')
        player = PlayerOrig.from_user(user=user)
        player2 = PlayerOrig.from_user(user=user)
        self.assertEqual(player, player2)
        player3 = PlayerOrig.from_user(user=user2)
        self.assertNotEqual(player, player3)
        self.assertNotEqual(player3, player3)
        self.assertNotEqual(player3, None)

    def test_ne(self):
        user = User(login='test_login')
        user._id = 1
        player = PlayerOrig.from_user(user=user)

        user2 = User(login='test_login')
        user2._id = 2
        player2 = PlayerOrig.from_user(user=user2)

        user3 = User(login='test_login2')
        player3 = PlayerOrig.from_user(user=user2)

        self.assertNotEqual(player, player2)
        self.assertNotEqual(player, player3)


class TableTest(unittest.TestCase):
    def setUp(self):
        self.table = Table()
        for step in xrange(0, 4):
            player = Player()
            player.id = step
            self.table.add_player(player=player)

    def test_add_player(self):
        player = Player()
        player.id = 99
        self.assertEqual(len(self.table.players), 4)
        self.table.add_player(player=player)
        self.assertEqual(len(self.table.players), 5)

        # test duplicate user
        self.assertRaises(OverflowError, self.table.add_player, player)

    def test_has_player_at_the_table(self):
        player = Player()
        player.id = 99
        self.assertEqual(self.table.has_player_at_the_table(player), False)
        self.table.add_player(player=player)
        self.assertEqual(self.table.has_player_at_the_table(player), True)

    def test_add_and_remove_player(self):
        player1 = Player()
        player1.id = 98
        player1.name = 'Vasya'
        player2 = Player()
        player2.id = 99
        player2.name = 'Petya'
        self.table.add_player(player1)
        self.table.add_player(player2)
        self.assertEqual(len(self.table.players), 6)
        self.table.remove_player(player=player1)
        self.table.remove_player(player=player2)
        self.assertEqual(len(self.table.players), 4)
        self.assertRaises(ValueError, self.table.remove_player, player1)

    def test_next_step(self):
        self.table.next_step()
        self.assertEqual(self.table.current_step, 1)
        self.table.next_step()
        self.assertEqual(self.table.current_step, 1)

    def test_to_json(self):
        self.assertIsInstance(self.table.to_json(), dict)
        self.assertEqual(sorted(self.table.to_json().keys()), sorted(['_id', 'active_players', 'board', 'circle_pot',
                                                                      'current_step', 'players', 'pot']))
        self.assertIsInstance(self.table.to_json()['players'], list)
        self.assertIsInstance(self.table.to_json()['active_players'], list)
        self.assertEqual(self.table.to_json()['pot'], 0)
        self.assertEqual(self.table.to_json()['circle_pot'], 0)
        self.assertEqual(self.table.to_json()['current_step'], 0)
        self.assertIsInstance(self.table.to_json()['board'], dict)


class HoldemTableTest(TableTest):
    def setUp(self):
        self.table = HoldemTable()
        for step in xrange(0, 4):
            player = Player()
            player.id = step
            self.table.add_player(player=player)

    def test_preflop_cards(self):
        self.table.preflop()
        for player in self.table.players:
            self.assertEqual(player.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 0)

    def test_flop_cards(self):
        self.table.preflop()
        self.table.flop()
        for player in self.table.players:
            self.assertEqual(player.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 3)

    def test_turn_cards(self):
        self.table.preflop()
        self.table.flop()
        self.table.turn()
        for player in self.table.active_players:
            self.assertEqual(player.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 4)

    def test_river_cards(self):
        self.table.preflop()
        self.table.flop()
        self.table.turn()
        self.table.river()
        for player in self.table.active_players:
            self.assertEqual(player.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 5)

    def test_players_limit_in_room(self):
        for step in xrange(0, 5):
            player = Player()
            player.id = 20 + step
            self.table.add_player(player=player)
        self.assertRaises(OverflowError, self.table.add_player, player)

    def test_next_step(self):
        pass

    def test_cards_in_next_step(self):
        vasya = Player()
        vasya.id = 97
        petya = Player()
        petya.id = 98
        dima = Player()
        dima.id = 99
        self.table.add_player(vasya)
        self.table.add_player(petya)
        self.table.add_player(dima)

        self.assertEqual(dima.hand.length(), 0)
        self.table.next_step()  # preflop
        self.assertEqual(dima.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 0)

        self.table.next_step()  # flop
        self.assertEqual(dima.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 3)

        self.table.next_step()  # turn
        self.assertEqual(dima.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 4)

        self.table.next_step()  # river
        self.assertEqual(dima.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 5)

        self.table.next_step()  # showdown
        self.assertEqual(dima.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 5)

        self.table.next_step()  # new preflop
        self.assertEqual(dima.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 0)

        self.table.next_step()  # new flop
        self.assertEqual(dima.hand.length(), 2)
        self.assertEqual(self.table.board.length(), 3)

    def test_bet_in_next_step(self):
        vasya = Player()
        vasya.id = 97
        petya = Player()
        petya.id = 98
        dima = Player()
        dima.id = 99
        self.table.add_player(vasya)
        self.table.add_player(petya)
        self.table.add_player(dima)
        dima._amount = 400

        self.table.next_step()  # preflop
        self.table._active_player = dima
        self.assertEqual(dima._amount, 400)
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(player=dima, amount=50)
        self.assertEqual(dima._amount, 350)
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.circle_pot, 50)


        self.table.next_step()  # flop
        self.table._active_player = dima
        self.assertEqual(dima._amount, 350)
        self.assertEqual(self.table.pot, 50)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(player=dima, amount=50)
        self.assertEqual(dima._amount, 300)
        self.assertEqual(self.table.pot, 50)
        self.assertEqual(self.table.circle_pot, 50)

        self.table.next_step()  # turn
        self.table._active_player = dima
        self.assertEqual(dima._amount, 300)
        self.assertEqual(self.table.pot, 100)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(player=dima, amount=25)
        self.assertEqual(dima._amount, 275)
        self.assertEqual(self.table.pot, 100)
        self.assertEqual(self.table.circle_pot, 25)

        self.table.next_step()  # river
        self.table._active_player = dima
        self.assertEqual(dima._amount, 275)
        self.assertEqual(self.table.pot, 125)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(player=dima, amount=25)
        self.assertEqual(dima._amount, 250)
        self.assertEqual(self.table.pot, 125)
        self.assertEqual(self.table.circle_pot, 25)

        self.table.next_step()  # showdown
        self.table._active_player = dima
        self.assertEqual(dima._amount, 250)
        self.assertEqual(self.table.pot, 150)
        self.assertEqual(self.table.circle_pot, 0)
        self.table.bet(player=dima, amount=150)
        self.assertEqual(dima._amount, 100)
        self.assertEqual(self.table.pot, 150)
        self.assertEqual(self.table.circle_pot, 150)

        self.table.next_step()  # showdown
        self.assertEqual(dima._amount, 100)
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.circle_pot, 0)

    def test_forbidden_bet_for_non_active_player(self):
        vasya = Player()
        vasya.id = 97
        vasya._amount = 400
        petya = Player()
        petya.id = 98
        petya._amount = 400
        dima = Player()
        dima.id = 99
        dima._amount = 400

        self.table.players = []
        self.table._active_player = None
        self.table.add_player(vasya)
        self.table.add_player(petya)
        self.table.add_player(dima)

        self.table.next_step()  # preflop
        self.assertRaises(ValueError, self.table.bet, dima, 50)
        self.assertRaises(ValueError, self.table.bet, petya, 50)
        self.table.bet(player=vasya, amount=50)

        self.assertRaises(ValueError, self.table.bet, vasya, 50)
        self.assertRaises(ValueError, self.table.bet, dima, 50)
        self.table.bet(player=petya, amount=50)

        self.assertRaises(ValueError, self.table.bet, vasya, 50)
        self.assertRaises(ValueError, self.table.bet, petya, 50)
        self.table.bet(player=dima, amount=50)

    def test_bet(self):
        self.table.players = []
        self.table._active_player = None
        player = Player()
        player._amount = 300
        player.id = 99
        amount = 100
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.circle_pot, 0)
        self.assertRaises(ValueError, self.table.bet, player, amount)

        self.table.add_player(player)
        self.table.clean()
        self.table.bet(player=player, amount=amount)
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.circle_pot, amount)


class EvaluatorTest(unittest.TestCase):
    pass