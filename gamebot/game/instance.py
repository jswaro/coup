import time
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

    def find_user_game(self, user):
        for _, game in self.games.items():
            if user in game.players:
                return game

        raise GameNotFoundException("User {0} does not appear to be in a game".format(user))

    def get_stats(self, player_name=None):
        pass  # TODO get statistics

    def print_games(self):
        games = [game.long_name() for _, game in self.games]
        return "\n".join(games)

    def checkevents(self):
        for _, game in self.games.item():
            if time.time() > game.event_queue.next_event:
                game.event_queue.trigger()
