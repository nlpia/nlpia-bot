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

```bash
$ bot -b 'pattern,parul' -vv -p --num_top_replies=1
2019-12-09:20:21:46.404 WARNING  [spacy_language_model.py:14] Failed to import spaCyHunSpell. Substituting with fake . . .
2019-12-09:20:21:46.404 WARNING  [spacy_language_model.py:42] Loading SpaCy model...
2019-12-09:20:21:47.142 INFO     [clibot.py:285] Building a BOT with: ['pattern', 'parul']
2019-12-09:20:21:47.142 INFO     [clibot.py:109] Adding bot named pattern_bots
2019-12-09:20:21:47.143 INFO     [clibot.py:116] Adding a Bot class <class 'nlpia_bot.skills.pattern_bots.Bot'>
from module <module 'nlpia_bot.skills.pattern_bots' from '/Users/hobs/code/chatbot/nlpia-bot/nlpia_bot/skills/pattern_bots.py'>...
2019-12-09:20:21:47.143 INFO     [clibot.py:109] Adding bot named parul_bots
2019-12-09:20:21:50.911 INFO     [clibot.py:116] Adding a Bot class <class 'nlpia_bot.skills.parul_bots.Bot'>
from module <module 'nlpia_bot.skills.parul_bots' from '/Users/hobs/code/chatbot/nlpia-bot/nlpia_bot/skills/parul_bots.py'>...
2019-12-09:20:21:50.923 WARNING  [clibot.py:290] Type "quit" or "exit" to end the conversation...
YOU: Hello someone not a chatbot.
2019-12-09:20:22:55.741 INFO     [clibot.py:305] Computing a reply to Hello someone not a chatbot....
2019-12-09:20:22:55.741 INFO     [clibot.py:126] statement=Hello someone not a chatbot.
2019-12-09:20:22:55.748 INFO     [clibot.py:145] Found 4 suitable replies, limiting to 1...
{'replies': [(0.2, "Hey. That's a good one."), (0.1, 'Hello'), (0.05, 'Wuh?'),
(0.4588375897316045, 'hello barbie is an internet-connected version of the doll that uses a chatbot provided by the company toytalk,
which previously used the chatbot for a range of smartphone-based characters for children.')],
'self': <nlpia_bot.scores.quality_score.QualityScore object at 0x117c6b290>, 'stmt': 'Hello someone not a chatbot.'}
bot: hello barbie is an internet-connected version of the doll that uses a chatbot provided by the company toytalk, which previously
 used the chatbot for a range of smartphone-based characters for children.
YOU: Hello another chatbot.
2019-12-09:20:23:14.798 INFO     [clibot.py:305] Computing a reply to Hello another chatbot....
2019-12-09:20:23:14.799 INFO     [clibot.py:126] statement=Hello another chatbot.
2019-12-09:20:23:14.804 INFO     [clibot.py:145] Found 4 suitable replies, limiting to 1...
{'replies': [(0.2, "Hey. That's a good one."), (0.1, 'Hello'), (0.05, 'Wuh?'),
(0.4588375897316045, 'hello barbie is an internet-connected version of the doll that uses a chatbot provided by the company toytalk,
which previously used the chatbot for a range of smartphone-based characters for children.')],
'self': <nlpia_bot.scores.quality_score.QualityScore object at 0x117c6b290>, 'stmt': 'Hello another chatbot.'}
bot: hello barbie is an internet-connected version of the doll that uses a chatbot provided by the company toytalk,
which previously used the chatbot for a range of smartphone-based characters for children.
YOU: Hi
2019-12-09:20:23:21.182 INFO     [clibot.py:305] Computing a reply to Hi...
2019-12-09:20:23:21.182 INFO     [clibot.py:126] statement=Hi
2019-12-09:20:23:21.187 INFO     [clibot.py:145] Found 2 suitable replies, limiting to 1...
{'replies': [(1.0, 'Hello!'), (1e-10, "I am sorry! I don't understand you")],
'self': <nlpia_bot.scores.quality_score.QualityScore object at 0x117c6b290>, 'stmt': 'Hi'}
bot: Hello!
YOU: Looking good!
2019-12-09:20:23:33.617 INFO     [clibot.py:305] Computing a reply to Looking good!...
2019-12-09:20:23:33.617 INFO     [clibot.py:126] statement=Looking good!
2019-12-09:20:23:33.622 INFO     [clibot.py:145] Found 2 suitable replies, limiting to 1...
{'replies': [(0.05, 'Wuh?'), (0.31232662648349846, 'the internet) retrieving information about goods and services.')],
'self': <nlpia_bot.scores.quality_score.QualityScore object at 0x117c6b290>, 'stmt': 'Looking good!'}
bot: the internet) retrieving information about goods and services.
```
"""
import collections.abc
import importlib
import logging
import os
import sys

import numpy as np
import pandas as pd

from configargparse import ArgParser

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
from nlpia_bot.scores.quality_score import QualityScore


__author__ = "see AUTHORS.md and README.md: Travis, Nima, Erturgrul, Aliya, Xavier, Hobson, ..."
__copyright__ = "Hobson Lane"
__license__ = "The Hippocratic License (MIT + *Do No Harm*, see LICENSE.txt)"


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


BOT = None
MAX_TURNS = 10000
EXIT_COMMANDS = set('exit quit bye goodbye cya'.split())

DEFAULT_CONFIG = {
    'name': 'bot',
    'persist': 'True',  # Yes, yes, 1, Y, y, T, t
    'bots': 'pattern,parul,search_fuzzy,eliza',
    'loglevel': 'WARNING',
    'num_top_replies': 10,
    'self_score': '.5',
    'semantic_score': '.5',
}


def normalize_replies(replies=''):
    if isinstance(replies, str):
        replies = [(1e-10, replies)]
    elif isinstance(replies, tuple) and len(replies, 2) and isinstance(replies[0], float):
        replies = [(replies[0], str(replies[1]))]
    # TODO: this sorting is likely unnecessary, redundant with sort happening within CLIBot.reply()
    return sorted([
        ((1e-10, r) if isinstance(r, str) else tuple(r))
        for r in replies
    ], reverse=True)


class CLIBot:
    """ Conversation manager intended to interact with the user on the command line, but can be used by other plugins/

    >>> CLIBot(bots='parul,pattern'.split(','), num_top_replies=1).reply('Hi')
    """
    bot_names = []
    bot_modules = []
    bots = []

    def __init__(
            self,
            bots=constants.DEFAULT_BOTS,
            num_top_replies=None,
            **quality_kwargs):
        if not isinstance(bots, collections.Mapping):
            bots = dict(zip(bots, [None] * len(bots)))
        for bot_name, bot_kwargs in bots.items():
            bot_kwargs = {} if bot_kwargs is None else dict(bot_kwargs)
            self.add_bot(bot_name, **bot_kwargs)
        self.num_top_replies = DEFAULT_CONFIG['num_top_replies'] if num_top_replies is None else min(
            max(int(num_top_replies), 1), 10000)
        self.repliers = [bot.reply if hasattr(bot, 'reply') else bot for bot in self.bots]
        self.quality_score = QualityScore(**quality_kwargs)

    def add_bot(self, bot_name, **bot_kwargs):
        bot_name = bot_name if bot_name.endswith('_bots') else f'{bot_name}_bots'
        log.info(f'Adding bot named {bot_name}')
        self.bot_names.append(bot_name)
        bot_module = importlib.import_module(f'nlpia_bot.skills.{bot_name}')
        new_modules, new_bots = [], []
        if bot_module.__class__.__name__ == 'module':
            module_vars = tuple(vars(bot_module).items())
            for bot_class in (c for n, c in module_vars if n.endswith('Bot') and callable(getattr(c, 'reply', None))):
                log.info(f'Adding a Bot class {bot_class} from module {bot_module}...')
                new_bots.append(bot_class(**bot_kwargs))
                new_modules.append(bot_module)
        else:
            log.warn(f'FIXME: add feature to allow import of specific bot classes like "nlpia_bot.skills.{bot_name}"')
        self.bots.extend(new_bots)
        self.bot_modules.extend(new_modules)
        return new_bots

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
            log.info(f'Found {len(replies)} suitable replies, limiting to {self.num_top_replies}...')
            replies = self.quality_score.update_replies(replies, statement)
            # re-sorts the replies based on their updated scores
            replies = sorted(replies, reverse=True)[:self.num_top_replies]
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


# def parse_config(filepath='nlpia-bot.ini'):

#     config = ConfigParser()
#     config['DEFAULT'] = config_defaults
#     config['bitbucket.org'] = {}
#     config['bitbucket.org']['User'] = 'hg'
#     config['topsecret.server.com'] = {}
#     topsecret = config['topsecret.server.com']
#     topsecret['Port'] = '50022'     # mutates the parser
#     topsecret['ForwardX11'] = 'no'  # same here
#     config['DEFAULT']['ForwardX11'] = 'yes'
#     with open('example.ini', 'w') as configfile:
#         config.write(configfile)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = ArgParser(
        default_config_files=[
            '~/nlpia-bot.ini',
            '~/nlpia_bot.ini',
            '~/nlpiabot.ini',
            '~/nlpia.ini',
            os.path.join(os.path.dirname(constants.BASE_DIR), '*.ini'),
            os.path.join(os.path.dirname(constants.SRC_DIR), '*.ini'),
        ],
        description="Command line bot application, e.g. bot how do you work?")
    parser.add('-c', '--config', required=False, is_config_file=True,
               help="Config file path (default: ~/nlpia-bot.ini)")
    parser.add_argument(
        '--version',
        action='version',
        version='nlpia_bot {ver}'.format(ver=__version__))
    parser.add_argument(
        '--name',
        default=DEFAULT_CONFIG['name'],
        dest="nickname",
        help="IRC nick or CLI command name for the bot",
        type=str,
        metavar="STR")
    parser.add_argument(
        '-n',
        '--num_top_replies',
        default=DEFAULT_CONFIG['num_top_replies'],
        dest="num_top_replies",
        help="Limit on the number of top (high score) replies that are randomly selected from.",
        type=int,
        metavar="INT")
    parser.add_argument(
        '-p',
        '--persist',
        help="Don't exit. Retain language model in memory and maintain dialog until user says 'exit' or 'quit'",
        dest='persist',
        default=str(DEFAULT_CONFIG['persist'])[0].lower() in 'ty1p',
        action='store_true')
    parser.add_argument(
        '-b',
        '--bots',
        default=DEFAULT_CONFIG['bots'],  # None so config.ini can populate defaults
        dest="bots",
        help="Comma-separated list of bot personalities to load. Defaults: pattern,parul,search_fuzzy,time,eliza",
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


def parse_argv(argv=sys.argv):
    """Entry point for console_scripts"""
    global BOT

    new_argv = []
    if len(argv) > 1:
        new_argv.extend(list(argv[1:]))
    args = parse_args(new_argv)
    log.setLevel(args.loglevel or logging.WARNING)

    setup_logging(args.loglevel)
    # args.bots = args.bots or 'search_fuzzy,pattern,parul,time'
    args.bots = [m.strip() for m in args.bots.split(',')]
    log.info(f"Building a BOT with: {args.bots}")
    if BOT is None:
        BOT = CLIBot(bots=args.bots, num_top_replies=args.num_top_replies)

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
            print(f"{args.nickname}: {bot_statement}")
        if args.persist or not user_statement:
            user_statement = input("YOU: ")
            statements.append(dict(user=user_statement, bot=None, **state))
        else:
            break
    return pd.DataFrame(statements)


if __name__ == "__main__":
    main()
