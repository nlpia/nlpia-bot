#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
[options.entry_points] section in setup.cfg:

    console_scripts =
         fibonacci = nlpia_bot.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""

import argparse
import logging
import sys

# from nlpia_bot.use_demo import reply as use_reply

# from chatbot.bots import Bot
# from chatbot.contrib import (
#     ChoiceFeature,
#     DiceFeature,
#     DictionaryFeature,
#     PyPIFeature,
#     SlapbackFeature,
#     WikipediaFeature
# )

from nlpia_bot import __version__

from nlpia_bot.patterns import greeting
from nlpia_bot.search_fuzzy import MovieBot


__author__ = "hobs"
__copyright__ = "hobs"
__license__ = "mit"

_logger = logging.getLogger(__name__)

BOT = None
moviebot = MovieBot()


def normalize_replies(replies):
    if isinstance(replies, str):
        replies = [(1e-10, replies)]
    if isinstance(replies, tuple) and len(replies, 2) and isinstance(replies[0], float):
        replies = [(replies[0], str(replies[1]))]
    return sorted([
        ((1e-10, r) if isinstance(r, str) else tuple(r))
        for r in replies
        ], reverse=True)


class CLIBot:
    def __init__(self, repliers=(greeting, moviebot.reply)):
        self.repliers = repliers

    def reply(self, statement=''):
        replies = []
        for replier in self.repliers:
            bot_replies = []
            try:
                bot_replies = normalize_replies(replier(statement))
            except Exception as e:
                _logger.error(str(e))
                try:
                    bot_replies = normalize_replies(replier.reply(statement))
                except AttributeError as e:
                    _logger.debug(str(e))
                except Exception as e:
                    _logger.error(str(e))
            replies.extend(bot_replies)
        if len(replies):
            return sorted(replies, reverse=True)[0][1]
        # TODO: np.choice from list of more friendly random unknown error replies...
        return "Sorry, something went wrong. Not sure what to say..."


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Command line bot application, e.g. bot how do you work?")
    parser.add_argument(
        '--version',
        action='version',
        version='nlpia_bot {ver}'.format(ver=__version__))
    parser.add_argument(
        default="bot",
        dest="nickname",
        help="IRC nick or CLI command name for the bot",
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
    parser.add_argument(
        'words',
        type=str,
        nargs='*',
        help="Words to pass to bot as an utterance or conversational statement requiring a bot reply or action.")
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    global BOT
    args = parse_args(args)
    setup_logging(args.loglevel)
    if BOT is None:
        _logger.warn("Building a BOT...")
        BOT = CLIBot()
        print("Started a CLIBot: {}".format(BOT))
    _logger.warn("Computing a reply to {}...".format(args.words))
    print(BOT.reply(args.words))


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
