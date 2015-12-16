import unittest
from argparse import Namespace

from gamebot.game import BaseGame

base_parameters = {'name': 'testgame',
                   'password': 'pass'}

default_user = 'jim'
default_players = 6
args = Namespace(**base_parameters)


class BaseGameTester(unittest.TestCase):
    def test_create(self):
        instance = 'x'
        game = BaseGame(instance, default_user, default_players, args)

        self.assertTrue(game.game_creator == default_user)
        self.assertTrue(game.name == args.name)
        self.assertTrue(game.password == args.password)

