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
import configparser
import logging
import sys
import importlib
import collections.abc

import numpy as np
import pandas as pd

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

from nlpia_bot import constants

from nlpia_bot import __version__


__author__ = "see AUTHORS.md and README.md: Travis, Nima, Erturgrul, Aliya, Xavier, Hobson, ..."
__copyright__ = "Hobson Lane"
__license__ = "The Hippocratic License (MIT + *Do No Harm*, see LICENSE.txt)"


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


BOT = None
MAX_TURNS = 10000
EXIT_COMMANDS = set('exit quit bye goodbye cya'.split())


def normalize_replies(replies=''):
    if isinstance(replies, str):
        replies = [(1e-10, replies)]
    elif isinstance(replies, tuple) and len(replies, 2) and isinstance(replies[0], float):
        replies = [(replies[0], str(replies[1]))]
    return sorted([
        ((1e-10, r) if isinstance(r, str) else tuple(r))
        for r in replies
    ], reverse=True)


class CLIBot:
    bot_names = []
    bot_modules = []
    bots = []

    def __init__(
            self,
            bots=constants.DEFAULT_BOTS):
        if not isinstance(bots, collections.Mapping):
            bots = dict(zip(bots, [None] * len(bots)))
        for bot_name, bot_kwargs in bots.items():
            bot_kwargs = {} if bot_kwargs is None else dict(bot_kwargs)
            self.add_bot(bot_name, **bot_kwargs)
        self.repliers = [bot.reply if hasattr(bot, 'reply') else bot for bot in self.bots]

    def add_bot(self, bot_name, **bot_kwargs):
        bot_name = bot_name if bot_name.endswith('_bots') else f'{bot_name}_bots'
        self.bot_names.append(bot_name)
        bot_module = importlib.import_module(f'nlpia_bot.{bot_name}')
        self.bot_modules.append(bot_module)
        self.bots.append(bot_module.Bot(**bot_kwargs))
        return self.bots[-1]

    def reply(self, statement=''):
        log.info(f'statement={statement}')
        replies = []
        for replier in self.repliers:
            bot_replies = []
            try:
                bot_replies = replier(statement)
            except Exception as e:
                log.error(f'Error trying to run {replier.__self__.__class__}.{replier.__name__}("{statement}")')
                log.error(str(e))
                try:
                    log.debug(repr(replier))
                    bot_replies = normalize_replies(replier.reply(statement))
                except AttributeError as e:
                    log.warn(str(e))
                except Exception as e:
                    log.error(str(e))
            bot_replies = normalize_replies(bot_replies)
            replies.extend(bot_replies)
        if len(replies):
            log.info(f'Found {len(replies)} suitable replies...')
            cumsum = 0
            cdf = list()
            for reply in replies:
                cumsum += reply[0]
                cdf.append(cumsum)
            roll = np.random.rand() * cumsum
            for i, threshold in enumerate(cdf):
                if roll < threshold:
                    return replies[i][1]

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
        '--name',
        default="bot",  # None so config.ini can populate defaults
        dest="nickname",
        help="IRC nick or CLI command name for the bot",
        type=str,
        metavar="STR")
    parser.add_argument(
        '-p',
        '--persist',
        help="Don't exit. Retain language model in memory and maintain dialog until user says 'exit' or 'quit'",
        dest="persist",
        default=False,  # None so config.ini can populate defaults
        action='store_true')
    parser.add_argument(
        '-b',
        '--bots',
        default="pattern,parul,search_fuzzy,eliza",  # None so config.ini can populate defaults
        dest="bots",
        help="comma-separated list of bot personalities to load into bot: pattern,parul,search_fuzzy,time",
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


def main():
    args = parse_argv(argv=sys.argv)
    statements = cli(args)
    if len(statements) > 1 and args.loglevel in 'DEBUG INFO'.split():
        return statements


def config_update(config, args):
    """ based on https://stackoverflow.com/a/48539074/623735 """
    config = configparser.ConfigParser()
    config.read('config.ini')
    defaults = dict(config['default'])

    argsdict = vars(args)
    defaults.update({k: v for k, v in argsdict.items() if v is not None})
    return defaults


def parse_argv(argv=sys.argv):
    """Entry point for console_scripts"""
    new_argv = []
    if len(argv) > 1:
        new_argv.extend(list(argv[1:]))
    args = parse_args(new_argv)
    log.setLevel(args.loglevel or logging.WARNING)

    global BOT
    setup_logging(args.loglevel)
    # args.bots = args.bots or 'search_fuzzy,pattern,parul,time'
    args.bots = [m.strip() for m in args.bots.split(',')]
    log.info(f"Building a BOT with: {args.bots}")
    if BOT is None:
        BOT = CLIBot(bots=args.bots)

    if args.persist:
        log.warn('Type "quit" or "exit" to end the conversation...')

    return args


def cli(args):
    state = {}
    statements = []
    user_statement = ' '.join(args.words)
    statements.append(dict(user=user_statement, bot=None, **state))
    args.persist = args.persist or not len(user_statement)
    for i in range(int(not args.persist) or MAX_TURNS):
        if user_statement.lower().strip() in EXIT_COMMANDS:
            break
        if user_statement:
            log.info(f"Computing a reply to {user_statement}...")
            # state = BOT.reply(statement, **state)
            bot_statement = BOT.reply(user_statement)
            statements[-1]['bot'] = bot_statement
            print(f"BOT: {bot_statement}")
        if args.persist or not user_statement:
            user_statement = input("YOU: ")
            statements.append(dict(user=user_statement, bot=None, **state))
        else:
            break
    return pd.DataFrame(statements)


if __name__ == "__main__":
    main()
