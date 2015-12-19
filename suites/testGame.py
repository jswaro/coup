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

