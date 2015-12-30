import unittest

from gamebot.coup.game import Instance
from gamebot.coup.cli import CoupCLIParser


class MyTestCase(unittest.TestCase):
    def test_something(self):
        instance = Instance()
        cliparser = CoupCLIParser(instance)

        def parse(player, command):
            return cliparser.parse_input({'nick': player, 'command': command})

        self.assertTrue(parse('TestPlayer1', 'create').startswith("Error:"))  # Need game name
        self.assertEqual(parse('TestPlayer1', 'create one'), "Game 'one' created")
        self.assertEqual(instance.msgqueue.popleft(), ('create room', 'one'))
        self.assertEqual(instance.msgqueue.popleft(), ('invite', ('TestPlayer1', 'one')))
        self.assertTrue(parse('TestPlayer1', 'join one').startswith("Error:"))  # Already joined

        self.assertEqual(parse('TestPlayer2', 'join one'), "Joined game 'one'")
        print(instance.msgqueue)
        self.assertEqual(instance.msgqueue.popleft(), ('invite', ('TestPlayer2', 'one')))
        self.assertTrue(parse('TestPlayer2', 'start').startswith("Error:"))  # Doesn't own
        self.assertEqual(parse('TestPlayer1', 'start'), "Game 'one' started")
        while instance.msgqueue:
            msg_type, msg = instance.msgqueue.popleft()
        self.assertTrue(parse('TestPlayer1', 'start one').startswith("Error:"))  # no argument

        game = instance.find_game_by_name('one')
        current = game.current_player_name()
        other = list(game.players.items())[1][0]
        self.assertTrue(parse('Not_in_game', 'do income').startswith("Error:"))  # not in game
        self.assertTrue(parse(other, 'do income').startswith("Error:"))  # not his turn
        print(parse(current, 'do income'))
        self.assertEqual(instance.msgqueue.popleft(), ('game message',
                                                       ('one', '{} takes income for 1 coin'.format(current))))

if __name__ == '__main__':
    unittest.main()





