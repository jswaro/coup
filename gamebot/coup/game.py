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
from collections import OrderedDict

from gamebot.game import BaseGame
from gamebot.game.instance import BaseInstance

from gamebot.coup.influence import ambassador, assassin, contessa, captain, duke, inquisitor
from gamebot.coup.actions import Income, ForeignAid, Coup, Embezzle, Convert
from gamebot.coup.exceptions import GameInvalidOperation
from gamebot.coup.actions import response_action, game_action
from gamebot.coup.events import EventQueue


class CoupGame(BaseGame):
    PLAYER_LIMIT = 10

    def __init__(self, instance, game_creator, parameters):
        super().__init__(instance, game_creator, CoupGame.PLAYER_LIMIT, parameters)

        self.deck = list()
        self.court_deck = list()
        self.valid_player_actions = list()
        if parameters.teams:
            self.treasury = 0

        self.inquisitor = parameters.inquisitor
        self.teams = parameters.teams  # Todo: To implement
        self.guessing = parameters.guessing  # Todo: To implement

        self.action_time = 30
        self.event_queue = EventQueue(self.action_time)
        self.to_forfeit = []

    def populate_deck_and_actions(self):
        cards = [contessa, duke, captain, assassin]
        self.valid_player_actions = [Income, ForeignAid, Coup]

        if self.inquisitor:
            cards.append(inquisitor)
        else:
            cards.append(ambassador)

        if self.teams:
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
                    self.valid_player_actions.append(action)

    def start(self):
        if len(self.players) < 2:
            raise GameInvalidOperation("Not enough players to start yet")

        # Randomize player order
        player_items = list(self.players.items())
        random.shuffle(player_items)
        self.players = OrderedDict(player_items)
        self.current_player = 0

        # create the deck
        self.populate_deck_and_actions()

        # shuffle the deck
        random.shuffle(self.deck)

        # deal each player two cards
        for _, player in self.players.items():

            # each player gets two cards
            player.give_card(self.deck.pop())
            player.give_card(self.deck.pop())

            card_list_msg = " and ".join([card.short_description() for card in player.available_influence])
            self.add_message_to_queue(player.name, "You have {}.".format(card_list_msg))

        # put the remaining cards into the court deck
        self.court_deck = list(self.deck)

        self.is_started = True
        self.broadcast_message("The game has begun. Turn order is {0}.".format(", ".join(self.players)))

        self.add_message_to_queue(self.current_player_name(), "You are the first player. Please choose an action.")

    def long_name(self):
        if self.password is None:
            return self.name

        return "{0} (private)".format(self.name)

    def get_action_by_name(self, name):
        for action in self.valid_player_actions:
            if name.lower() == action.command_name():
                return action
        raise GameInvalidOperation("You have picked an invalid option. "
                                   "Please choose from {0}.".format(", ".join(self.valid_player_actions.command_name())))

    def find_player_by_name(self, name):
        if name not in self.players.keys():
            raise GameInvalidOperation("You are not part of this game.")

        return self.players[name]

    def my_turn(self, user):
        return user == list(self.players.items())[self.current_player][0]

    def advance_to_next_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)

    def progress_to_next_turn(self):
        # TODO: remove forfeit players
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

    def face_up_cards(self):
        face_up = list()
        for player in self.players:
            face_up.extend(player.face_up_cards())

        return ", ".join(face_up)

    def run_command(self, action, player, arguments):
        if action.lower() == 'do':
            if not self.my_turn(player.name):
                raise GameInvalidOperation("Not your turn")
            actionvar = self.get_action_by_name(arguments['do'])
            if actionvar not in self.valid_player_actions:
                raise GameInvalidOperation("Action not available given current rules")
        elif action in dict(response_action):
            actionvar = dict(response_action)[action]
        elif action in dict(game_action):
            actionvar = dict(game_action)[action]
        else:
            raise GameInvalidOperation
        additional = {x: y for x, y in arguments.items() if x not in ('command', 'do')}
        actionvar.run(self, player, **additional)

    def status(self):
        return "Status not implemented"  # TODO


class Instance(BaseInstance):
    pass
