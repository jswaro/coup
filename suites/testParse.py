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
        self.parse('TestPlayer1', 'create one', resolve=False)
        self.parse('TestPlayer2', 'join one', resolve=False)
        self.parse('TestPlayer1', 'start', resolve=False)
        self.player1, self.player2 = self.instance.games['one'].players.keys()

    def parse(self, player, command, resolve=True):
        val = self.cliparser.parse_input({'nick': player, 'command': command})
        if resolve:
            self.instance.games['one'].event_queue.resolve("Default")
        return val

    @unittest.skip("Not yet implemented")
    def test_income(self):
        self.parse(self.player1, 'do income')
        self.assertEqual(self.instance.games['one'].players[self.player1].coins, 3)

    @unittest.skip("Not yet implemented")
    def test_foreign_aid(self):
        self.parse(self.player1, 'do foreign_aid')
        self.assertEqual(self.instance.games['one'].players[self.player1].coins, 4)

    @unittest.skip("Not yet implemented")
    def test_tax(self):
        self.parse(self.player1, 'do tax')
        self.assertEqual(self.instance.games['one'].players[self.player1].coins, 5)

    @unittest.skip("Not yet implemented")
    def test_steal(self):
        self.parse(self.player1, 'do steal {}'.format(self.player2))
        self.assertEqual(self.instance.games['one'].players[self.player1].coins, 4)
        self.assertEqual(self.instance.games['one'].players[self.player2].coins, 0)

    @unittest.skip("Not yet implemented")
    def test_assassinate(self):
        self.instance.games['one'].players[self.player1].modify_cash(1)
        self.parse(self.player1, 'do assassinate {}'.format(self.player2))
        self.assertEqual(len(self.instance.games['one'].players[self.player2].available_influence), 1)

    @unittest.skip("Incomplete check")
    def test_exchange(self):
        self.parse(self.player1, 'do exchange')
        self.parse(self.player1, 'select 1')
        # TODO: check results

    @unittest.skip("Incomplete check")
    def test_examine(self):
        pass  # TODO

    @unittest.skip("Not yet implemented")
    def test_coup(self):
        self.instance.games['one'].players[self.player1].modify_cash(5)
        self.parse(self.player1, 'do coup {}'.format(self.player2))
        self.assertEqual(len(self.instance.games['one'].players[self.player2].available_influence), 1)

    # Todo: Unchecked actions: exchange2, convert, embezzle, challenge, select, accept, counter, status, forfeit

    @unittest.skip("Not yet implemented")
    def test_full_game(self):
        self.parse(self.player1, 'do income')  # player's coins = (3, 2)
        self.parse(self.player2, 'do foreign_aid')  # player's coins = (3, 4)
        self.parse(self.player1, 'do tax')  # player's coins = (6, 4)
        self.parse(self.player2, 'do steal {}'.format(self.player1))  # player's coins = (4, 6)
        self.parse(self.player1, 'do tax')  # player's coins = (7, 6)
        self.parse(self.player2, 'do tax')  # player's coins = (7, 9)
        self.parse(self.player1, 'do assassinate {}'.format(self.player2))  # player's coins = (4, 9)
        self.parse(self.player2, 'do coup {}'.format(self.player1))  # player's coins = (4, 2)
        self.parse(self.player1, 'do assassinate {}'.format(self.player2))  # player's coins = (4, 9)
        self.assertTrue(self.instance.games['one'].is_complete)

if __name__ == '__main__':
    unittest.main()





