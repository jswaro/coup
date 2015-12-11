"""
There are several different types of events. There are contestable events which occur when a player
makes a decision that can be contested by another player. There are incontestable events that cannot be
contested, only resolved.

Contestable events require resolution from every player, whether it is simply an accept or contest of the statement.

Interrogative events require resolution from only one player and are typically used to resolve a single decision.

Contestable events are limited the originating player, and the contesting player.

Countering events involve all players, but only one player can respond.

Examples:

An interrogative event is a question to a specific player, such as what action they may want to take this turn.

An incontestable event is a statement of fact that cannot be disputed, such as a coup. These actions are resolved
without any input from the other entities.

A contestable event is a statement of fact that can be disputed, such as an attempt of theft by one player against
another. Another player may dispute the fact that the original player had the role necessary to perform the action.
A counter can result in another contestable event, but only contestable in terms of possession rather than counter.

A counter can only be challenged, but a declaration can be countered or challenged.
"""
import random

from gamebot.coup.influence import ambassador, assassin, contessa, captain, duke, inquisitor
from gamebot.coup.actions import Income, ForeignAid, Coup, Embezzle, Convert
from gamebot.coup.cli import create_game_parser, join_parser
from gamebot.coup.player import Player
from gamebot.coup.exceptions import GameNotFoundException, GameInvalidOperation, GamePermissionError,\
    InvalidCLICommand, CoupException

__author__ = 'jswaro'


class Game(object):
    def __init__(self, instance, game_creator, parameters):
        self.isactive = False
        self.instance = instance
        self.name = parameters.name
        self.password = parameters.password
        self.game_creator = game_creator
        self.max_players = 10

        self.deck = list()
        self.court_deck = list()
        self.valid_player_actions = list()
        if parameters.teams:
            self.treasury = 0

        self.inquisitor = parameters.inquisitor
        self.teams = parameters.teams  # Todo: To implement
        self.guessing = parameters.guessing  # Todo: To implement

        self.players = dict()
        self.player_order = list()

        self.current_player = 0

        self.events = list()

        self.stack = list()

        self.messages = list()
        self.messages_to_send = list()

    def add_player(self, player, password):
        if self.password is not None and password != self.password:
            raise GamePermissionError("Incorrect password. You may not join this gamebot.")
        if player.name in self.players:
            raise GameInvalidOperation("Player {0} is already in the gamebot".format(player.name))

        self.players[player.name] = player

    def populate_deck_and_actions(self):
        cards = [contessa, duke, captain, assassin]
        self.valid_player_actions = [Income, ForeignAid, Coup]

        if self.use_inquisitor:
            cards.append(inquisitor)
        else:
            cards.append(ambassador)

        if self.use_treasury:
            self.valid_player_actions.extend([Embezzle, Convert])

        for card in cards:
            num_cards_each = 3
            if 6 < len(self.players) <= 8:
                num_cards_each = 4
            elif len(self.players) > 8:
                num_cards_each = 5

            for x in range(0, num_cards_each):
                self.deck.append(card)

            for action in card.actions:
                self.valid_player_ations.append(action)

    def is_creator(self, user):
        return user == self.game_creator

    def start(self):
        if len(self.players) < 2:
            raise GameInvalidOperation("Not enough players to start yet")

        # make a random player the first player
        self.current_player = random.randint(0, len(self.players) - 1)

        # create the deck
        self.populate_deck_and_actions()

        # shuffle the deck
        random.shuffle(self.deck)

        # deal each player two cards
        for name in self.players:
            current = self.players[name]

            # each player gets two cards
            current.give_card(self.deck.pop())
            current.give_card(self.deck.pop())

        # put the remaining cards into the court deck
        self.court_deck = list(self.deck)

        self.player_order = self.players.keys()

        turn_order = list()
        for x in range(0, len(self.players)):
            turn_order.append(self.player_order[(self.current_player + x) % len(self.players)])

        self.isactive = True
        self.broadcast_message("The gamebot has begun. Turn order is {0}.".format(", ".join(turn_order)))

        self.add_message_to_queue(self.current_player_name(), "You are the first player. "
                                                              "Please choose an action.")

        self.process_outbound_messages()

    def current_player_name(self):
        return self.player_order[self.current_player]

    def long_name(self):
        if self.password is None:
            return self.name

        return "{0} (private)".format(self.name)

    def get_action_by_name(self, name):
        for action in self.valid_player_actions:
            if name == action.name:
                return action
        return GameInvalidOperation("You have picked an invalid option. "
                                    "Please choose from {0}.".format(", ".join(self.valid_player_actions)))

    def find_player_by_name(self, name):
        if name not in self.players.keys():
            raise GameInvalidOperation("You are not part of this gamebot.")

        return self.players[name]

    def my_turn(self, user):
        return user == self.player_order[self.current_player]

    def advance_to_next_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)

    def progress_to_next_turn(self):
        alive_players = [x for x in self.player_order if not self.players[x].dead()]

        if len(alive_players) == 1:
            for name in self.player_order:
                self.add_message_to_queue(name, "Player {0} has won!".format(alive_players[0]))
        else:
            self.advance_to_next_player()
            while self.players[self.current_player_name()].dead():
                print("{0} is dead... skipping".format(self.current_player_name()))
                self.advance_to_next_player()

            self.add_message_to_queue(self.current_player_name(), "It is your turn. Please choose an action.")

    def face_up_cards(self):
        face_up = list()
        for name in self.player_order:
            face_up.extend(self.players[name].face_up_cards())

        return ", ".join(face_up)

    def do_income(self, player, arguments):
        player.modify_cash(1)
        self.broadcast_message("{0} took income. {0} has {1} coins.".format(player.name, player.cash()))
        self.progress_to_next_turn()

    def do_foreign_aid(self, player, arguments):
        pass  # TODO

    def do_tax(self, player, arguments):
        pass  # TODO

    def do_steal(self, player, arguments):
        pass  # TODO

    def do_assassinate(self, player, arguments):
        pass  # TODO

    def do_exchange2(self, player, arguments):
        pass  # TODO

    def do_exchange1(self, player, arguments):
        pass  # TODO

    def do_examine(self, player, arguments):
        pass  # TODO

    def do_coup(self, player, arguments):
        if len(arguments) < 2:
            raise InvalidCLICommand("You need to specify a target for the coup.")

        target = arguments[1]

        target_player = self.find_player_by_name(target)

        if player.cash() < 7:
            raise GameInvalidOperation("You do not have enough coins to coup. Pick another action.")

        if target_player.dead():
            raise GameInvalidOperation("Your target is already dead. Shame on you. Pick another action.")

        player.modify_cash(-7)
        if target_player.influence_remaining() == 1:
            target_player.kill()

            self.broadcast_message("{0} has lost all their influence. They are out of the gamebot.")
        else:
            # generate decision event
            # TODO: need to add an event for losing influence
            pass

        self.broadcast_message("The list of current face-up cards are '{0}'.".format(self.face_up_cards()))
        self.progress_to_next_turn()

    def do_convert(self, player, arguments):
        pass  # TODO

    def do_embezzle(self, player, arguments):
        pass  # TODO

    def no_action(self, player, arguments):
        raise CoupException("Not sure how we got here, but you picked an invalid option")


class Instance(object):
    def __init__(self):
        self.games = dict()

    def add_game(self, name, game):
        if not self.game_exists(name):
            self.games[name] = game
        else:
            raise GameInvalidOperation("A gamebot with this name already exists")

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

        raise GameNotFoundException("User {0} does not appear to be in a gamebot".format(name))

    def print_games(self):
        if len(self.games.keys()) == 0:
            return ""

        games = [self.games[x].long_name() for x in self.games.keys()]
        return "\n".join(games)

    def run_command(self, action, user, msg_func, arguments):
        if action == 'create':
            ret = self.parse_base_create(user, msg_func, arguments)
        elif action == 'start':
            ret = self.parse_base_start(user, msg_func, arguments)
        elif action == 'join':
            ret = self.parse_base_join(user, msg_func, arguments)
        elif action == 'list':
            ret = self.parse_base_list(user, msg_func, arguments)
        elif action == 'help':
            ret = self.parse_base_help(user, msg_func, arguments)
        else:
            raise InvalidCLICommand("Unrecognized command: {}. Type .help for available options".format(action))
        return ret

    def parse_base_create(self, user, msg_func, arguments):
        args = create_game_parser.parse_args(arguments)

        if self.game_exists(args.name):
            raise InvalidCLICommand("A gamebot with this name already exists")

        game = Game(self, user, args)
        self.add_game(args.name, game)

        player = Player(user)
        game.add_player(player, args.password)

        return "Game '{0}' created".format(args.name)

    def parse_base_start(self, user, msg_func, arguments):

        game = self.find_user_game(user)

        if not game.is_creator(user):
            raise GamePermissionError("Only the owner of the gamebot may start the gamebot")

        game.start()

        return "Game '{0}' started".format(game.name)

    def parse_base_join(self, user, msg_func, arguments):
        args = join_parser.parse_args(arguments)

        game = self.find_game_by_name(args.name)

        player = Player(user)
        game.add_player(player, args.password)

        game.broadcast_message(
            "Game '{}', players ({}): {}".format(args.name, len(game.players), ", ".join(game.players.keys())))

        return "Joined game '{}'".format(args.name, ", ".join(game.players.keys()))

    def parse_base_list(self, user, msg_func, arguments):
        return self.print_games()

    def parse_base_help(self, user, msg_func, arguments):  # Todo Add other helps
        if len(arguments) == 0:
            ret = list([
                "Bot for playing Coup. Use .help <command> for more information",
                "Global commands:",
                " .create <name> [-p password]",
                " .list",
                " .join <name> [-p password]",
                " .start",
                "Game commands:",
                " .do income",
                " .do foreign_aid",
                " .do coup <player>",
                " .do tax",
                " .do steal <player>",
                " .do assassinate <player>",
                " .do exchange",
                " .counter <player> with <role>",
                " .challenge <player>",
                " .accept",
                " .status",
                " .forfeit"
            ])
            return "\n".join(ret)

        if arguments[0][0] == ".":
            arguments[0] = arguments[0][1:]

        if arguments[0] == 'create':
            return create_game_parser.format_help()
        elif arguments[0] == 'list':
            return "Lists available games"
        elif arguments[0] == 'join':
            return join_parser.format_help()
        elif arguments[0] == 'start':
            return "starts the gamebot you own"
        else:
            return "help not implemented for this command"  # TODO
