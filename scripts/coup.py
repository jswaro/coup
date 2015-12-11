from __future__ import print_function
import logging
import sys
import os

scripts_dir = os.path.dirname(__file__)
source_dir = os.path.abspath(os.path.join(scripts_dir, '..', 'gamebot'))
sys.path.append(source_dir)
base_directory = os.path.abspath(os.path.join(source_dir, '..'))
sys.path.append(base_directory)

from gamebot.bots import irc_simple
from secrets import channellist, botnick, botpass, server, usessl
from gamebot.coup.game import Instance
from gamebot.coup.cli import CoupCLIParser

__author__ = 'jswaro', 'dcolestock'

logging.basicConfig(filename='freenode.log', level=logging.INFO)


def main(channellist, botnick, botpass, server, usessl):
    """
    Main Loop
    """
    instance = Instance()
    parser = CoupCLIParser(instance)

    connection = irc_simple.irc_connection(parser=parser,
                                           channellist=channellist,
                                           botnick=botnick,
                                           botpass=botpass,
                                           server=server,
                                           usessl=usessl)
    connection.run()


if __name__ == "__main__":
    main(channellist, botnick, botpass, server, usessl)
