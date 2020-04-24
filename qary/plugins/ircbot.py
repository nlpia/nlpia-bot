#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
[options.entry_points] section in setup.cfg:

    console_scripts =
         qary = qary.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""

import argparse
import logging
import sys

from chatbot.bots import Bot
from chatbot.contrib import (
    ChoiceFeature,
    DiceFeature,
    DictionaryFeature,
    PyPIFeature,
    SlapbackFeature,
    WikipediaFeature
)

from . import __version__

__author__ = "See AUTHORS.md"
__copyright__ = "Hobson Lane"
__license__ = "The Hippocratic License (MIT + *Do No Harm*, see LICENSE.txt)"

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Just a Fibonnaci demonstration")
    parser.add_argument(
        '--version',
        action='version',
        version='qary {ver}'.format(ver=__version__))
    parser.add_argument(
        dest="nickname",
        help="IRC nick (nickname or username) for the bot",
        type=str,
        metavar="STR")
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def ircbot(args=None,
           nickname='nlpia',
           irc_server='chat.freenode.net',
           port=6665,
           server_password='my_bots_password',
           channels=('#freenode', '#python'),
           features=None):
    """Entry point for console_script for shell command `ircbot --nickname nlpia` ... """
    nickname = getattr(args, 'nickname', nickname)
    irc_server = getattr(args, 'irc_server', irc_server)
    port = int(float(getattr(args, 'port', port)))
    server_password = getattr(args, 'server_password', server_password)
    channels = eval(str(getattr(args, 'channels', channels)))
    features = features or (PyPIFeature(), WikipediaFeature(), DictionaryFeature(),
                            DiceFeature(), ChoiceFeature(), SlapbackFeature())
    bot = Bot(
        nickname=nickname,
        hostname=irc_server,
        port=port,
        server_password=server_password,
        channels=channels,
        features=features,
    )

    return bot.run()


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting crazy calculations...")
    print("The ircbot returned: {}".format(ircbot(args)))
    _logger.info("Script ends here")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
