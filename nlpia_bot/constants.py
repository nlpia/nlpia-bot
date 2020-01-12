# constants.py
import os
import sys
# import re
import logging
from collections import Counter
# import json

# import pandas as pd
import nltk
import nltk.corpus
import spacy  # noqa
import configargparse
from environment import Environment

from nlpia_bot import __version__

env = Environment(spacy_lang=str, loglevel=int, name=str)

SRC_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(DATA_DIR, 'log')
os.makedirs(LOG_DIR, exist_ok=True)

MAX_TURNS = 10000
EXIT_COMMANDS = set('exit quit bye goodbye cya'.split())

DEFAULT_CONFIG = {
    'name': 'bot',
    'persist': 'False',  # Yes, yes, 1, Y, y, T, t
    'bots': 'glossary',  # ,parul,eliza,glossary,search_fuzzy',
    'spacy_lang': 'en_core_web_sm',
    'loglevel': logging.WARNING,
    'num_top_replies': 10,
    'self_score': '.5',
    'semantic_score': '.5',
    'score_weights': '{"spell": .25, "sentiment": .25, "semantics": .5}',
}
DEFAULT_CONFIG.update(env.parsed)


LOGLEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]
# LOG_LEVELS = [         10,           20,              30,            40,            50]
LOGLEVEL_NAMES = 'DEBUG INFO WARNING ERROR FATAL'.split()
LOGLEVEL_ABBREVIATIONS = [s[:4].lower() for s in LOGLEVEL_NAMES]
LOGLEVEL_ABBR_DICT = dict(zip(LOGLEVEL_ABBREVIATIONS, LOGLEVELS))
# this is the LOGLEVEL for the top of this file, once args and .ini file are read, it will change
LOGLEVEL = getattr(env, 'loglevel', None) or DEFAULT_CONFIG.get('loglevel', logging.WARNING)

logging.basicConfig(
    format='%(asctime)s.%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=LOGLEVEL)  # FIXME: read from config file like in clibot.py
root_logger = logging.getLogger()
log = logging.getLogger(__name__)


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
    """Parse command line parameters using nlpia-bot.ini for the default values

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = configargparse.ArgParser(
        default_config_files=[
            '~/nlpia-bot.ini',
            '~/nlpia_bot.ini',
            '~/nlpiabot.ini',
            '~/nlpia.ini',
            os.path.join(BASE_DIR, '*.ini'),
            os.path.join(DATA_DIR, '*.ini'),
        ],
        description="Command line bot application. Try `$ bot how do you work?`")
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
        default=str(DEFAULT_CONFIG['persist'])[0].lower() in 'fty1p',
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
        '-q',
        '--quiet',
        dest="loglevel",
        help="set loglevel to ERROR",
        action='store_const',
        const=logging.ERROR)
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
        '-l',
        '--loglevel',
        dest="loglevel",
        help="Raw integer loglevel (10=debug, 20=info, 30=warn, 40=error, 50=fatal)",
        type=int,
        default=DEFAULT_CONFIG['loglevel'])
    parser.add_argument(
        '--spacy_lang',
        default=DEFAULT_CONFIG['spacy_lang'],
        dest="spacy_lang",
        help="SpaCy language model: en_core_web_sm, en_core_web_md, or en_core_web_lg",
        type=str,
        metavar="STR")
    parser.add_argument(
        '-s',
        '--score_weights',
        default=DEFAULT_CONFIG['score_weights'],
        dest="score_weights",
        help='Dictionary of weights: {"spell": .5, "sentiment": .5, "semantics": .5}',
        type=str,
        metavar="DICT_STR")
    parser.add_argument(
        '--semantics',
        type=float,
        default=1.0,
        dest='semantics',
        metavar='FLOAT',
        help='set weight of the semantic quality score')
    parser.add_argument(
        '--sentiment',
        type=float,
        default=0.5,
        dest='sentiment',
        metavar='FLOAT',
        help='set weight of the sentiment quality score')
    parser.add_argument(
        '--spell',
        type=float,
        default=0.2,
        dest='spell',
        metavar='FLOAT',
        help='set weight of the spell quality score')
    parser.add_argument(
        'words',
        type=str,
        nargs='*',
        help="Words to pass to bot as an utterance or conversational statement requiring a bot reply or action.")
    parsed_args = parser.parse_args(args)
    return parsed_args


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def parse_argv(argv=sys.argv):
    """Entry point for console_scripts"""
    global BOT

    new_argv = []
    if len(argv) > 1:
        new_argv.extend(list(argv[1:]))
    args = parse_args(new_argv)
    args.loglevel = args.loglevel or logging.WARNING
    log.setLevel(args.loglevel)

    setup_logging(args.loglevel)
    # set the root logger to the same log level
    logging.getLogger().setLevel(args.loglevel)
    log.debug(f'RAW ARGS (including config file): {vars(args)}')

    # strip quotes in case ini file incorrectly uses single quotes that become part of the str
    args.nickname = str(args.nickname).strip().strip('"').strip("'")
    # args.bots = args.bots or 'search_fuzzy,pattern,parul,time'
    args.bots = [m.strip() for m in args.bots.split(',')]
    log.info(f"Building a BOT with: {args.bots}")
    log.info(f"Weights: {args.score_weights}")
    # log.info(f"Parsed Weights: {type(json.loads(args.score_weights))}")
    return args


args = parse_argv()

LOGLEVEL = args.loglevel or LOGLEVEL


# handler = logging.handlers.TimedRotatingFileHandler(os.path.join(LOG_DIR, 'nlpia_bot.constants.log'), when='midnight')
# handler.setLevel(logging.INFO)
# log.addHandler(handler)


LANGS = ['en_core_web_sm', 'en_core_web_md', 'en_core_web_lg']
LANGS_ABBREV = 'en enmd enlg'.split()
LANGS += 'de_core_news_sm de_core_news_md de_trf_bertbasecased_lg'.split()
LANGS_ABBREV += 'de demd delg'.split()

# FOREIGN_LANGS_DF = pd.read_csv(os.path.join(DATA_DIR, 'spacy_languages.csv'))
# for i, row in FOREIGN_LANGS_DF.iterrows():
#     match = re.match(r'(\d)+\b', row['Models'])
#     if match:
#         num_models = int(match.groups()[0])
#         LANGS.extend([row['Code']] * num_models)

# tuple('de de de'.split())  # df=pd.read_html('https://spacy.io/usage/models')[0]
LANGS_ABBREV = dict(zip(LANGS_ABBREV, LANGS))

LANG = env.parsed.get('spacy_lang') or getattr(args, 'spacy_lang', None) or DEFAULT_CONFIG.get('spacy_lang') or LANGS[0]
log.info(f'LANG=spacy_lang={LANG}')

try:
    STOPWORDS_DICT = Counter(nltk.corpus.stopwords.words('english'))
except LookupError:
    log.info('Downloading NLTK stopwords and punkt corpora')
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    STOPWORDS_DICT = Counter(nltk.corpus.stopwords.words('english'))
STOPWORDS = set(STOPWORDS_DICT)

ASCII_LOWER = 'abcdefghijklmnopqrstuvwxyz'
ASCII_UPPER = ASCII_LOWER.upper()


DEFAULT_BOTS = {
    'pattern_bots': None,
    'search_fuzzy_bots': None,
    'parul_bots': None,
    'eliza_bots': None,
}
DEFAULT_FAQ_DOMAINS = ('general-python-data-science', 'python-data_science-for-healthcare')
DEFAULT_GLOSSARY_DOMAINS = ('dsdh', )

TFHUB_USE_MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder-large/3"

# templates for medical sentences
# SENTENCE_SPEC_PATH = os.path.join(os.path.dirname(__file__), 'data', 'medical_sentences.json')
# SENTENCE_SPEC = json.load(open(SENTENCE_SPEC_PATH, 'r'))


# Universal Sentence Encoder's TF Hub module for creating USE Embeddings from
USE = None


class passthroughSpaCyPipe:
    """ Callable pass-through SpaCy Pipeline Component class (callable) for fallback if spacy_hunspell.spaCyHunSpell fails"""
    def __init__(*args, **kwargs):
        pass

    def __call__(self, doc):
        log.info(f"This passthroughSpaCyPipe component only logs the token count: {len(doc)}")
        return doc
