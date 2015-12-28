from __future__ import print_function
import sys
import os
import argparse
import logging
import stat
import yaml

scripts_dir = os.path.dirname(__file__)
source_dir = os.path.abspath(os.path.join(scripts_dir, '..', 'gamebot'))
sys.path.append(source_dir)
base_directory = os.path.abspath(os.path.join(source_dir, '..'))
sys.path.append(base_directory)

from gamebot.logging import log_to_file, log_to_stream
from gamebot.bots import irc_simple
from gamebot.coup.game import Instance
from gamebot.coup.cli import CoupCLIParser

core = logging.getLogger('core')


def read_config_file(path):
    with open(path, 'r') as config_file:
        return yaml.load(config_file)


def write_config_file(args, path):
    try:
        os.unlink(path)
    except OSError:
        pass

    with open(path, 'w') as config_file:
        yaml.dump(args.__dict__, config_file, indent=2, default_flow_style=False)


def find_configuration_file(search_paths, filename):
    for path in search_paths:
        p = os.path.join(path, filename)

        core.info('searching path, path=%s', p)
        perm = stat.S_IRUSR
        if os.path.exists(p) and (os.stat(p).st_mode & perm):
            return p

    return None


def main(args):
    """
    Main Loop
    """
    default_search_paths = [os.path.abspath(os.path.expanduser(x)) for x in ['.', '~/']]

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    group = parser.add_argument_group('Bot Options', 'Options that are given directly to the bot')
    group.add_argument('-C', '--channels', action='store',
                       help='name of the IRC channels for the bot to join, comma delimited',
                       default="#coup")
    group.add_argument('-n', '--nickname', action='store', help='nickname for the bot to use',
                       default='coupbot')
    group.add_argument('-p', '--password', action='store', help='password that the bot will use to authenticate',
                       default='')
    group.add_argument('-s', '--server', action='store', help='IRC server address to connect to',
                       default='wilhelm.freenode.net')
    group.add_argument('-u', '--use-ssl', action='store_true', dest='ssl', help='enables the use of SSL',
                       default=False)

    group = parser.add_argument_group('Logging options', 'Options given to the logging framework')

    verbosity = group.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_true', help='enables verbose output to stdout')
    verbosity.add_argument('-d', '--debug', action='store_true', help='enables debug output to stdout')
    group.add_argument('-S', '--output-stream', action='store', dest='stream',
                       help='logs output to a provided stream. Choices are stdout or stderr',
                       default=None)

    group.add_argument('-f', '--output-file', action='store', dest='file',
                       help='logs output to the provided file name',
                       default=None)

    parser.add_argument('-c', '--config', action='store', help='config file to read', default='secrets.yaml')
    parser.add_argument('-W', '--write-config', action='store_true', dest='write_config',
                        help='write default config file to config path and exit')

    args = parser.parse_args(args)

    if args.write_config and args.config:
        core.info('writing config file, path=%s', args.config)
        write_config_file(args, args.config)
        return 0

    config_file = find_configuration_file(default_search_paths, args.config)
    if config_file:
        # read the configuration file
        core.info('reading config file, path=%s', config_file)
        config = read_config_file(config_file)

        arg_values = dict(args.__dict__)
        arg_defaults = dict([(x, parser.get_default(x)) for x in arg_values])
        for key in config:
            # check each value from the config against the parser defaults. Parser values that differ from
            # the defaults will take precedence over configuration file values
            if arg_values[key] != arg_defaults[key]:
                continue

            arg_values[key] = config[key]

        args = argparse.Namespace(**arg_values)

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

