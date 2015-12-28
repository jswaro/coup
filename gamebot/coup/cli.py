"""
Players may create a game by sending a message to coup-bot in the following syntax:

  create <name> [password]

  * create requests may fail if there is already a game with that name in progress

The game's creator may start the game by issuing the following message to coup-bot:

  start <name>

  * start requests may fail if there are not enough players or there is not a game
    with the provided name

Any player may join a game by sending the following message to coup-bot:

  join <name> [password]

  * join requests may fail if a game with the provided name does not exist, the password
    is incorrect, or the game is already in progress

Any player may leave a game at any point by issuing the following command:

  forfeit

  * quit may fail if the player is not in a game

Any player may request the list of games that are currently available to join with the
  following command:

  list

  * list may fail if the player is already in a game


Once a player is in a game, they may do any of the following commands on their turn, provided they have the necessary
  resources:

  status [player]

  do <action>
    where <action> can be any one of the following:

    - income
    - foreign aid
    - coup
    - tax
    - steal <player>
    - assassinate <player>
    - exchange

    * during an exchange, the player will be prompted for the cards they wish to keep. They will not be able to accept
      more cards than they had prior to the exchange

  * There will be no warning for actions taken that would require a bluff. It is assumed that if you do an illegal
    action, you know that you will lose an influence if someone calls you out on it.

  challenge <player> with <influence>

  * During another player's turn, you may challenge their action. If they have the ability to do the action and reveal
    the card, you will lose an influence.

  counter <player> with <influence>

  * During another player's turn, you may counter their action with an influence of your own. If you bluff
    the influence and are challenged, you will lose an influence accordingly.

A player loses once they have lost all of their influence. At this point, they may leave to join another game.
"""
from gamebot.coup.exceptions import InvalidCLICommand, GameNotFoundException, CoupException, MalformedCLICommand
from gamebot.coup.events import completion
from gamebot.coup.commands import command_list
from gamebot.coup.parsers import command_parser

__author__ = 'jswaro'


class CoupCLIParser(object):
    def __init__(self, instance):
        self.recognized_base_actions = command_list

        self.recognized_game_actions = ['do', 'challenge', 'counter', 'accept', 'status', 'forfeit']

        self.instance = instance

    @staticmethod
    def complete_command(arguments, game_active):
        try:
            command_namespace = command_parser.parse_args(arguments)
        except MalformedCLICommand as e:
            # TODO: Attempt to resolve by command completion
            raise e

        return command_namespace

    def parse_input(self, message):
        arguments = message['command'].lower().split()

        user = message['nick']
        try:
            game = self.instance.find_user_game(user)
            game_active = game.is_started
        except GameNotFoundException:
            game = None
            game_active = False

        try:
            command_namespace = self.complete_command(arguments, game_active)
            action = command_namespace.command
            if action in self.recognized_base_actions:
                ret = self.recognized_base_actions[action].run(self.instance, user, arguments[1:])
            elif action in self.recognized_game_actions:
                if game is None:
                    raise GameNotFoundException("You are not in a game and cannot use {}".format(action))
                ret = game.run_command(action, user, vars(command_namespace))
            else:
                raise InvalidCLICommand("Unrecognized command: {}. Type .help for available options".format(action))
        except CoupException as e:
            ret = "Error: {0} ".format(e.args[0])

        return ret
