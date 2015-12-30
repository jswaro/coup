from collections import OrderedDict
from gamebot.coup.exceptions import GameInvalidOperation, GamePermissionError
from gamebot.game.player import BasePlayer


class BaseGame(object):
    def __init__(self, instance, game_creator, max_players, parameters):
        self.is_started = False
        self.instance = instance
        self.name = parameters.name
        self.password = parameters.password
        self.game_creator = game_creator
        self.max_players = max_players

        self.players = OrderedDict()

        self.current_player = 0

        self.events = list()

        self.stack = list()

        self.messages = list()
        self.messages_to_send = list()

        self.instance.msgqueue.append(("create room", self.name))

    def __del__(self):
        self.instance.msgqueue.append(("destroy room", self.name))

    def add_player(self, player, password):
        if not isinstance(player, BasePlayer):
            raise RuntimeError("player object is not of type BasePlayer or a subclass of")

        if self.password is not None and password != self.password:
            raise GamePermissionError("Incorrect password. You may not join this game.")

        if self.is_started:
            raise GameInvalidOperation("Game already started.")

        if player.name in self.players:
            raise GameInvalidOperation("Player {0} is already in the game.".format(player.name))

        if len(self.players) == self.max_players:
            raise GameInvalidOperation("No more room, already full.")

        self.players[player.name] = player
        self.instance.msgqueue.append(("invite", (player.name, self.name)))

    def is_creator(self, user):
        return user == self.game_creator

    def start(self):
        raise NotImplementedError

    def current_player_name(self):
        if len(self.players) == 0:
            raise GameInvalidOperation('There are no players in this game yet')
        return list(self.players.items())[self.current_player][0]

    def long_name(self):
        if self.password is None:
            return self.name

        return "{0} (private)".format(self.name)

    def find_player_by_name(self, name):
        if name not in self.players.keys():
            raise GameInvalidOperation("You are not part of this game.")

        return self.players[name]

    def my_turn(self, user):
        return user == list(self.players.items())[self.current_player][0]

    def advance_to_next_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)

    def progress_to_next_turn(self):
        alive_players = [x for x in self.players if not x.dead()]

        if len(alive_players) == 1:
            for player in self.players:
                self.add_message_to_queue(player.name, "Player {0} has won!".format(alive_players[0]))
        else:
            self.advance_to_next_player()
            while self.players[self.current_player_name()].dead():
                print("{0} is dead... skipping".format(self.current_player_name()))
                self.advance_to_next_player()

            self.add_message_to_queue(self.current_player_name(), "It is your turn. Please choose an action.")

    def add_message_to_queue(self, user, message):
        self.instance.msgqueue.append(("private message", (user, message)))

    def broadcast_message(self, message):
        self.instance.msgqueue.append(("game message", (self.name, message)))
