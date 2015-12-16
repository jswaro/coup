from collections import OrderedDict

from six import with_metaclass

from gamebot.coup.parsers import create_parser, start_parser, join_parser, list_parser, stats_parser, help_parser
from gamebot.coup.exceptions import GamePermissionError, InvalidCLICommand, MalformedCLICommand, GameInvalidOperation
from gamebot.coup.player import Player
from gamebot.coup.game import CoupGame
from gamebot.coup.actions import do_action, response_action, game_action

command_list = OrderedDict()


class RegisterCommand(type):
    def __init__(cls, name, bases, clsdict):
        if len(cls.mro()) > 2:
            command_list[name.lower()] = cls
        super(RegisterCommand, cls).__init__(name, bases, clsdict)


class BaseCommand(with_metaclass(RegisterCommand, object)):
    parser = None

    @classmethod
    def __str__(cls):
        return cls.__name__.lower()

    @classmethod
    def run(cls, instance, user, arguments):
        args = cls.parser.parse_args(arguments)
        return cls.process_args(instance, user, args)

    @staticmethod
    def process_args(instance, user, args):
        pass

    @classmethod
    def help(cls):
        return cls.parser.format_help()

    @classmethod
    def usage(cls):
        return cls.parser.format_usage()[7:]


class Create(BaseCommand):
    parser = create_parser

    @staticmethod
    def process_args(instance, user, args):
        if instance.game_exists(args.name):
            raise InvalidCLICommand("A game with this name already exists")

        game = CoupGame(instance, user, args)
        instance.add_game(args.name, game)

        player = Player(user)
        game.add_player(player, args.password)

        return "Game '{0}' created".format(args.name)


class Start(BaseCommand):
    parser = start_parser

    @staticmethod
    def process_args(instance, user, args):
        game = instance.find_user_game(user)

        if not game.is_creator(user):
            raise GamePermissionError("Only the owner of the game may start the game")

        game.start()
        return "Game '{0}' started".format(game.name)


class Join(BaseCommand):
    parser = join_parser

    @staticmethod
    def process_args(instance, user, args):
        game = instance.find_game_by_name(args.name)
        if game.is_started:
            return GameInvalidOperation("Game already started")

        player = Player(user)
        game.add_player(player, args.password)

        game.broadcast_message(
            "Game '{}', players ({}): {}".format(args.name, len(game.players), ", ".join(game.players.keys())))

        return "Joined game '{}'".format(args.name, ", ".join(game.players.keys()))


class List(BaseCommand):
    parser = list_parser

    @staticmethod
    def process_args(instance, user, args):
        return instance.print_games()


class Stats(BaseCommand):
    parser = stats_parser

    @staticmethod
    def process_args(instance, user, args):
        if args.player is None:
            return instance.get_stats(user)
        else:
            return instance.get_stats(args.player)


class Help(BaseCommand):
    parser = help_parser

    @staticmethod
    def process_args(instance, user, args):
        if args.command is None:
            output_list = ["Bot for playing Coup. Use .help <command> for more information",
                           "Commands:"]
            for command_name, command in command_list.items():
                output_list.append(" "*3 + command.usage())
            output_list.append("In-game actions:")
            output_list.append("   Turn actions:")
            for action in do_action:
                output_list.append(" "*6 + ".do " + action.name.lower().replace(" ", "_"))
            output_list.append("   Response actions:")
            for action in response_action:
                output_list.append(" "*6 + "." + action.name.lower().replace(" ", "_"))
            output_list.append("   Game actions:")
            for action in game_action:
                output_list.append(" "*6 + "." + action.name.lower().replace(" ", "_"))
            return "\n".join(output_list)
        else:
            if args.command not in command_list:
                raise MalformedCLICommand("Command {} not recognized".format(args.command))
            return command_list[args.command].help()
