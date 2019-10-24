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
import importlib

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

from nlpia_bot import __version__


__author__ = "hobs"
__copyright__ = "hobs"
__license__ = "mit"

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

BOT_PACKAGES = dict(pattern='pattern_bots', search_fuzzy='search_fuzzy_bots')
BOT = None
MAX_TURNS = 10000
EXIT_COMMANDS = set('exit quit bye goodbye cya'.split())


def normalize_replies(replies):
    if isinstance(replies, str):
        replies = [(1e-10, replies)]
    if isinstance(replies, tuple) and len(replies, 2) and isinstance(replies[0], float):
        replies = [(replies[0], str(replies[1]))]
    return sorted([
        ((1e-10, r) if isinstance(r, str) else tuple(r))
        for r in replies
        ], reverse=True)


def bots_from_personalities(personalities):
    if isinstance(personalities, str):
        personalities = ','.join(personalities.split()).split(',')
    bot_dict = BOT_PACKAGES
    globals_dict = globals()
    return [bot_dict.get(p, globals_dict.get(p)).Bot() for p in personalities]


class CLIBot:
    def __init__(self, bots=('pattern_bots', 'search_fuzzy_bots')):
        module_names = [m if m.endswith('_bots') else f'{m}_bots' for m in bots]
        modules = [importlib.import_module(f'nlpia_bot.{m}') for m in module_names]
        self.bots = [m.Bot() for m in modules]
        self.repliers = [bot.reply for bot in self.bots]

    def reply(self, statement=''):
        log.info(f'statement={statement}')
        replies = []
        for replier in self.repliers:
            bot_replies = []
            try:
                bot_replies = normalize_replies(replier(statement))
            except Exception as e:
                log.error(str(e))
                try:
                    log.debug(repr(replier))
                    bot_replies = normalize_replies(replier.reply(statement))
                except AttributeError as e:
                    log.warn(str(e))
                except Exception as e:
                    log.error(str(e))
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
        '--name',
        default="bot",
        dest="nickname",
        help="IRC nick or CLI command name for the bot",
        type=str,
        metavar="STR")
    parser.add_argument(
        '-p',
        '--persist',
        help="Don't exit. Retain language model in memory and maintain dialog until user says 'exit' or 'quit'",
        dest="persist",
        default=False,
        action='store_true')
    parser.add_argument(
        '-b',
        '--bots',
        default="pattern",
        dest="bots",
        help="comma-separated bot personalities to load into bot: search_movie,pattern_greet,search_ds,generate_spanish",
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
    return statements


def parse_argv(argv=sys.argv):
    """Entry point for console_scripts"""
    new_argv = []
    if len(argv) > 1:
        new_argv.extend(list(argv[1:]))
    args = parse_args(new_argv)
    log.setLevel(args.loglevel or logging.WARNING)

    global BOT
    setup_logging(args.loglevel)
    args.bots = args.bots or 'search_fuzzy,pattern'
    args.bots = [m.strip() for m in args.bots.split(',')]
    log.info(f"Building a BOT with: {args.bots}")
    if BOT is None:
        BOT = CLIBot(bots=args.bots)

    if args.persist:
        log.warn('Type "quit" or "exit" to end the conversation...')

    return args


def cli(args):
    user_statement = ' '.join(args.words)
    args.persist = args.persist or not len(user_statement)
    user_statements = []
    bot_statements = []
    for i in range(int(not args.persist) or MAX_TURNS):
        user_statements.append(user_statement)
        if user_statement:
            log.info(f"Computing a reply to {user_statement}...")
            # state = BOT.reply(statement, **state)
            bot_statement = BOT.reply(user_statement)
            bot_statements.append(bot_statement)
            print(f"BOT: {bot_statement}")
        if user_statement.lower().strip() in EXIT_COMMANDS:
            break
        if args.persist or not user_statement:
            user_statement = input("YOU: ")
        else:
            break
    statements = dict(user=user_statements, bot=bot_statements)
    ulen = len(statements['user'])
    blen = len(statements['bot'])
    maxlen = max(ulen, blen)
    statements['bot'] += [None] * max(maxlen - len(statements['bot']), 0)
    statements['user'] += [None] * max(maxlen - len(statements['user']), 0)
    return pd.DataFrame(statements)


if __name__ == "__main__":
    main()
