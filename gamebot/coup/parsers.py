import argparse

from gamebot.coup.exceptions import MalformedCLICommand


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise MalformedCLICommand(message)

create_parser = ThrowingArgumentParser(prog='.create', add_help=False, description="Creates a new game")
create_parser.add_argument('name', help='The game\'s name. Used for joining')
create_parser.add_argument('-p', '--password', dest='password', help='Set password for private game')
group = create_parser.add_mutually_exclusive_group()
group.add_argument('-i', '--inq', dest='inquisitor', action='store_true', default=True,
                   help='Use Inquisitor instead of Ambassador (Default)')
group.add_argument('-a', '--amb', dest='ambassador', action='store_true', default=False,
                   help='Use Ambassador instead of Inquisitor')
create_parser.add_argument('-t', '--teams', dest='teams', action='store_true', default=False,
                           help='Use Teams/Allegiances and the Treasury Reserve')
create_parser.add_argument('-g', '--guess', dest='guessing', action='store_true', default=False,
                           help='Requires guessing an opponent\'s card to coup or assassinate')

start_parser = ThrowingArgumentParser(prog='.start', add_help=False, description="Starts a game you own")

join_parser = ThrowingArgumentParser(prog='.join', add_help=False, description="Joins a game")
join_parser.add_argument('name', help='The game name to join')
join_parser.add_argument('-p', '--password', dest='password', help='The game\'s password')

list_parser = ThrowingArgumentParser(prog='.list', add_help=False, description="Lists available games")

stats_parser = ThrowingArgumentParser(prog='.stats', add_help=False, description="Lists a players stats")
stats_parser.add_argument('player', help='The player name to lookup', nargs='?')

help_parser = ThrowingArgumentParser(prog='.help', add_help=False, description="Help info on a command or action")
help_parser.add_argument('command', help='The command or action to lookup', nargs='?')

do_parser = ThrowingArgumentParser(prog='.do', add_help=False, description="Main turn actions")
do_subparser = do_parser.add_subparsers()

income_parser = do_subparser.add_parser('income', add_help=False)
foreign_aid_parser = do_subparser.add_parser('foreign_aid', add_help=False)
tax_parser = do_subparser.add_parser('tax', add_help=False)
embezzle_parser = do_subparser.add_parser('embezzle', add_help=False)
exchange_parser = do_subparser.add_parser('exchange', add_help=False)

steal_parser = do_subparser.add_parser('steal', add_help=False)
steal_parser.add_argument('player')

examine_parser = do_subparser.add_parser('examine', add_help=False)
examine_parser.add_argument('player')

convert_parser = do_subparser.add_parser('convert', add_help=False)
convert_parser.add_argument('player')

assassinate_parser = do_subparser.add_parser('assassinate', add_help=False)
assassinate_parser.add_argument('player')
assassinate_parser.add_argument('guess', nargs='?')

coup_parser = do_subparser.add_parser('coup', add_help=False)
coup_parser.add_argument('player')
coup_parser.add_argument('guess', nargs='?')

counter_parser = ThrowingArgumentParser(prog='.counter', add_help=False)
counter_parser.add_argument('with_role', nargs='?')

challenge_parser = ThrowingArgumentParser(prog='.challenge', add_help=False)
challenge_parser.add_argument('player')

accept_parser = ThrowingArgumentParser(prog='.accept', add_help=False)

keep_parser = ThrowingArgumentParser(prog='.keep', add_help=False)
keep_parser.add_argument('cards', nargs='*')

change_parser = ThrowingArgumentParser(prog='.change', add_help=False)

status_parser = ThrowingArgumentParser(prog='.status', add_help=False)

forfeit_parser = ThrowingArgumentParser(prog='.forfeit', add_help=False)
