import unittest

from gamebot.game.team import BaseTeam
from gamebot.game.player import BasePlayer

default_player_name = 'jim'


class TestTeam(BaseTeam):
    RED_TEAM = 1
    BLUE_TEAM = 2


class BasePlayerTester(unittest.TestCase):
    def test_create_player(self):
        player = BasePlayer(default_player_name)

        self.assertEqual(player.name, default_player_name)
        self.assertEqual(player.team, BaseTeam.UNASSIGNED)

    def test_set_team(self):
        player = BasePlayer(default_player_name, team=TestTeam.RED_TEAM)

        self.assertEqual(player.team, TestTeam.RED_TEAM)

        player.set_team(TestTeam.BLUE_TEAM)

        self.assertEqual(player.team, TestTeam.BLUE_TEAM)

        player.set_team(TestTeam.UNASSIGNED)

        self.assertEqual(player.team, TestTeam.UNASSIGNED)

