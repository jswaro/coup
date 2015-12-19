from collections import deque

from gamebot.coup.exceptions import GameInvalidOperation, GameNotFoundException


class BaseInstance(object):
    def __init__(self):
        self.games = dict()
        self.msgqueue = deque()

    def add_game(self, name, game):
        if not self.game_exists(name):
            self.games[name] = game
        else:
            raise GameInvalidOperation("A game with this name already exists")

    def game_exists(self, name):
        return name in self.games

    def find_game_by_name(self, name):
        if name not in self.games:
            raise GameNotFoundException("Game '{0}' not found".format(name))

        return self.games[name]

    def find_user_game(self, name):
        for game_name in self.games.keys():
            if name in self.games[game_name].players:
                return self.games[game_name]

        raise GameNotFoundException("User {0} does not appear to be in a game".format(name))

    def get_stats(self, player_name=None):
        pass  # TODO get statistics

    def print_games(self):
        if len(self.games.keys()) == 0:
            return ""

        games = [self.games[x].long_name() for x in self.games.keys()]
        return "\n".join(games)