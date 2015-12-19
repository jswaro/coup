import unittest
from argparse import Namespace

from gamebot.game import BaseGame
from gamebot.game.player import BasePlayer
from gamebot.game.instance import BaseInstance

from gamebot.coup.exceptions import GameInvalidOperation, GamePermissionError

base_parameters = {'name': 'testgame',
                   'password': 'pass'}

default_user = 'jim'
default_players = 6
args = Namespace(**base_parameters)


class BaseGameTester(unittest.TestCase):
    def test_create(self):
        instance = BaseInstance()
        game = BaseGame(instance, default_user, default_players, args)

        self.assertTrue(game.game_creator == default_user)
        self.assertTrue(game.name == args.name)
        self.assertTrue(game.password == args.password)

    def test_add_player(self):
        instance = BaseInstance()
        game = BaseGame(instance, default_user, default_players, args)

        player = BasePlayer(default_user)
        other_player = BasePlayer('some guy')

        game.add_player(player, args.password)

        with self.assertRaises(GamePermissionError) as exception:
            game.add_player(other_player, 'bad password')

        with self.assertRaises(GameInvalidOperation) as exception:
            game.add_player(player, args.password)

        with self.assertRaises(RuntimeError) as exception:
            game.add_player('x', args.password)

    def test_is_creator(self):
        instance = BaseInstance()
        game = BaseGame(instance, default_user, default_players, args)

        self.assertTrue(game.is_creator(default_user))

        self.assertFalse(game.is_creator('no one'))

    def test_current_player_name(self):
        instance = BaseInstance()
        game = BaseGame(instance, default_user, default_players, args)
        player = BasePlayer(default_user)

        with self.assertRaises(GameInvalidOperation) as e:
            game.current_player_name()

        game.add_player(player, args.password)

        self.assertEqual(default_user, game.current_player_name())

    def test_start(self):
        instance = BaseInstance()
        game = BaseGame(instance, default_user, default_players, args)

        with self.assertRaises(NotImplementedError) as e:
            game.start()

    def test_long_name(self):
        instance = BaseInstance()
        game = BaseGame(instance, default_user, default_players, args)

        name = game.long_name()
        self.assertTrue(isinstance(name, str))
        self.assertTrue(name != "")

    def test_find_player_by_name(self):
        instance = BaseInstance()
        game = BaseGame(instance, default_user, default_players, args)
        player = BasePlayer(default_user)

        game.add_player(player, args.password)

        with self.assertRaises(GameInvalidOperation) as e:
            game.find_player_by_name('not found')

        p = game.find_player_by_name(default_user)

        self.assertEqual(p, player)

    def test_my_turn(self):
        """ This tests both 'my_turn' and 'advance_to_next_players """
        instance = BaseInstance()
        game = BaseGame(instance, default_user, default_players, args)
        me = BasePlayer(default_user)
        other = BasePlayer('other player')

        game.add_player(me, args.password)

        self.assertTrue(game.my_turn(me.name))
        self.assertFalse(game.my_turn(other.name))

        game.add_player(other, args.password)
        game.advance_to_next_player()

        self.assertTrue(game.my_turn(other.name))
        self.assertFalse(game.my_turn(me.name))

