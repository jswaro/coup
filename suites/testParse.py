import unittest

from gamebot.coup.game import Instance
from gamebot.coup.cli import CoupCLIParser


class GameInitialization(unittest.TestCase):
    def setUp(self):
        self.instance = Instance()
        self.cliparser = CoupCLIParser(self.instance)

    def parse(self, player, command):
        return self.cliparser.parse_input({'nick': player, 'command': command})

    def test_game_create(self):
        self.assertEqual(self.parse('TestPlayer1', 'create one'), "Game 'one' created")
        self.assertEqual(list(self.instance.games.keys()), ['one'])

    def test_game_join(self):
        self.parse('TestPlayer1', 'create one')
        self.assertTrue(self.parse('TestPlayer1', 'join one').startswith("Error:"))  # Already joined
        self.assertEqual(self.parse('TestPlayer2', 'join one'), "Joined game 'one'")
        self.assertEqual(list(self.instance.games['one'].players.keys()), ['TestPlayer1', 'TestPlayer2'])

    def test_game_start(self):
        self.parse('TestPlayer1', 'create one')
        self.assertTrue(self.parse('TestPlayer1', 'start').startswith("Error:"))  # Not enough players
        self.parse('TestPlayer2', 'join one')
        self.assertTrue(self.parse('TestPlayer2', 'start').startswith("Error:"))  # Doesn't own
        self.assertFalse(self.instance.games['one'].is_started)
        self.assertEqual(self.parse('TestPlayer1', 'start'), "Game 'one' started")
        self.assertTrue(self.instance.games['one'].is_started)


class GamePlay(unittest.TestCase):
    def setUp(self):
        self.instance = Instance()
        self.cliparser = CoupCLIParser(self.instance)
        self.parse('TestPlayer1', 'create one')
        self.parse('TestPlayer2', 'join one')
        self.parse('TestPlayer1', 'start')
        self.player1, self.player2 = self.instance.games['one'].players.keys()

    def parse(self, player, command):
        return self.cliparser.parse_input({'nick': player, 'command': command})

    @unittest.skip("Not yet implemented")
    def test_income(self):
        self.parse(self.player1, 'do income')
        #  Todo: Add event progression
        self.assertEqual(self.instance.games['one'].players[self.player1].coins, 3)

if __name__ == '__main__':
    unittest.main()





