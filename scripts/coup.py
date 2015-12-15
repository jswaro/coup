from __future__ import print_function
import sys
import os
import argparse
import logging

scripts_dir = os.path.dirname(__file__)
source_dir = os.path.abspath(os.path.join(scripts_dir, '..', 'gamebot'))
sys.path.append(source_dir)
base_directory = os.path.abspath(os.path.join(source_dir, '..'))
sys.path.append(base_directory)

import secrets

from gamebot.logging import log_to_file, log_to_stream
from gamebot.bots import irc_simple
from gamebot.coup.game import Instance
from gamebot.coup.cli import CoupCLIParser

__author__ = 'jswaro', 'dcolestock'
core = logging.getLogger('core')


def main(args):
    """
    Main Loop
    """
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    group = parser.add_argument_group('Bot Options', 'Options that are given directly to the bot')
    group.add_argument('-c', '--channels', action='store',
                       help='name of the IRC channels for the bot to join, comma delimited',
                       default=",".join(secrets.channellist))
    group.add_argument('-n', '--nickname', action='store', help='nickname for the bot to use',
                       default=secrets.botnick)
    group.add_argument('-p', '--password', action='store', help='password that the bot will use to authenticate',
                       default=secrets.botpass)
    group.add_argument('-s', '--server', action='store', help='IRC server address to connect to',
                       default=secrets.server)
    group.add_argument('-u', '--use-ssl', action='store_true', dest='ssl', help='enables the use of SSL',
                       default=secrets.usessl)

    group = parser.add_argument_group('Logging options', 'Options given to the logging framework')

    verbosity = group.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_true', help='enables verbose output to stdout')
    verbosity.add_argument('-d', '--debug', action='store_true', help='enables debug output to stdout')
    group.add_argument('-S', '--output-stream', action='store', dest='stream',
                           help='logs output to a provided stream. Choices are stdout or stderr',
                           default=None)

    group.add_argument('-f', '--output-file', action='store', dest='file',
                           help='logs output to the provided file name',
                           default='freenode.log')

    args = parser.parse_args(args)

    if args.verbose or args.debug:
        level = logging.INFO
        if args.debug:
            level = logging.DEBUG

        if args.file:
            log_to_file(args.file, level)

        if args.stream:
            stream = sys.stderr if args.stream.lower() == 'stderr' else sys.stdout

            log_to_stream(stream, level)

        if args.file:
            core.info('logging to file, file=%s', args.file)

        if args.stream:
            core.info('logging to stream, stream=%s', args.stream)

    instance = Instance()
    cliparser = CoupCLIParser(instance)

    connection = irc_simple.irc_connection(parser=cliparser,
                                           channellist=args.channels.split(','),
                                           botnick=args.nickname,
                                           botpass=args.password,
                                           server=args.server,
                                           usessl=args.ssl)
    connection.run()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

