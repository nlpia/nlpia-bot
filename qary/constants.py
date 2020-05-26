import os
import sys
import logging
from collections import Counter

import nltk
import nltk.corpus
import spacy  # noqa
import configargparse
from environment import Environment

from . import __version__

# DO ACCESS KEY and SECRET need to be integrated into env
env = Environment(spacy_lang=str, loglevel=int, name=str)

SRC_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(SRC_DIR, 'data')
LOG_DIR = os.path.join(DATA_DIR, 'log')
HISTORY_PATH = os.path.join(DATA_DIR, 'history.json')
os.makedirs(LOG_DIR, exist_ok=True)
# with open(HISTORY_PATH, 'a') as fap:
#     pass
MIDATA_DOMAINNAME = 'tan.sfo2.digitaloceanspaces.com'
MIDATA_URL = f'https://{MIDATA_DOMAINNAME}'
MIDATA_QA_MODEL_DIR = 'midata/public/models/qa'
MIDATA_QA_MODEL_DIR_URL = f'{MIDATA_URL}{MIDATA_QA_MODEL_DIR}'

USE_CUDA = False
MAX_TURNS = 10000
EXIT_COMMANDS = set('exit quit bye goodbye cya'.split())

DEFAULT_CONFIG = {
    'name': 'bot',
    'persist': 'False',  # Yes, yes, 1, Y, y, T, t
    'bots': 'glossary',  # glossary,qa,parul,eliza,search_fuzzy'
    'spacy_lang': 'en_core_web_sm',
    'use_cuda': USE_CUDA,
    'loglevel': logging.FATAL,
    'num_top_replies': 10,
    'self_score': '.5',
    'semantic_score': '.5',
    'debug': True,
    'wiki_title_max_words': 4,
    'score_weights': '{"spell": .25, "sentiment": .25, "semantics": .5}',
    'qa_model': 'albert-large-v2-0.2.0'
}
DEFAULT_CONFIG.update(env.parsed)


LOGLEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]
# LOG_LEVELS = [         10,           20,              30,            40,            50]
LOGLEVEL_NAMES = 'DEBUG INFO WARNING ERROR FATAL'.split()
LOGLEVEL_ABBREVIATIONS = [s[:4].lower() for s in LOGLEVEL_NAMES]
LOGLEVEL_ABBR_DICT = dict(zip(LOGLEVEL_ABBREVIATIONS, LOGLEVELS))
# this is the LOGLEVEL for the top of this file, once args and .ini file are read, it will change
LOGLEVEL = getattr(env, 'loglevel', DEFAULT_CONFIG.get('loglevel', logging.WARNING))
USE_CUDA = getattr(env, 'use_cuda', DEFAULT_CONFIG.get('use_cuda', USE_CUDA))

logging.basicConfig(
    format='%(asctime)s.%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=LOGLEVEL)
root_logger = logging.getLogger()
log = logging.getLogger(__name__)


# FIXME: to avoid PYTHONPATH hack, use relative imports: `from .constants` not `from qary.constants`
def append_sys_path():
    pass
    # if BASE_DIR not in sys.path:
    #     log.warning(f'Package BASE_DIR ({BASE_DIR}) not in sys.path: {sys.path}')
    #     sys.path.append(BASE_DIR)
    # if SRC_DIR not in sys.path:
    #     log.warning(f'Package SRC_DIR ({SRC_DIR}) not in sys.path: {sys.path}')
    #     sys.path.append(SRC_DIR)

# append_sys_path()
# def parse_config(filepath='qary.ini'):
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
    """Parse command line parameters using qary.ini for the default values

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    print(f"args: {args}")
    parser = configargparse.ArgParser(
        default_config_files=[
            '~/qary.ini',
            # '~/qary.ini',
            # '~/nlpiabot.ini',
            # '~/nlpia.ini',
            # os.path.join(BASE_DIR, '*.ini'),
            os.path.join(DATA_DIR, '*.ini'),
        ],
        description="Command line bot application. Try `$ bot how do you work?`")
    parser.add('-c', '--config', required=False, is_config_file=True,
               help="Config file path (default: ~/qary.ini)")
    parser.add_argument(
        '-d', '--debug',
        help="Set DEBUG logging level and raise more exceptions immediately.",
        dest="debug",
        default=str(DEFAULT_CONFIG['debug'])[0].lower() in 'fty1p',
        action='store_true')
    parser.add_argument(
        '--version',
        action='version',
        version='qary {ver}'.format(ver=__version__))
    parser.add_argument(
        '--name',
        default=None,  # DEFAULT_CONFIG['name'],
        dest="nickname",
        help="IRC nick or CLI command name for the bot",
        type=str,
        metavar="STR")
    parser.add_argument(
        '-n',
        '--num_top_replies',
        default=None,  # DEFAULT_CONFIG['num_top_replies'],
        dest="num_top_replies",
        help="Limit on the number of top (high score) replies that are randomly selected from.",
        type=int,
        metavar="INT")
    parser.add_argument(
        '-u',
        '--use_cuda',
        help="Use CUDA and GPU to speed up transformer inference.",
        dest='use_cuda',
        default=USE_CUDA,
        action='store_true')
    parser.add_argument(
        '-p',
        '--persist',
        help="DEPRECATED: Don't exit. Retain language model in memory and maintain dialog until user says 'exit' or 'quit'",
        dest='persist',
        default=str(DEFAULT_CONFIG['persist'])[0].lower() in 'fty1p',
        action='store_true')
    parser.add_argument(
        '-b',
        '--bots',
        default=None,  # DEFAULT_CONFIG['bots'],  # None so config.ini can populate defaults
        dest="bots",
        help="Comma-separated list of bot personalities to load. Defaults: pattern,parul,search_fuzzy,time,eliza",
        type=str,
        metavar="STR")
    parser.add_argument(
        '-q',
        '--quiet',
        dest="verbosity",
        help="Quiet: set loglevel to ERROR",
        action='store_const',
        const=logging.ERROR)
    parser.add_argument(
        '-qq',
        '--very_quiet',
        dest="verbosity",
        help="Very quiet: set loglevel to FATAL",
        action='store_const',
        const=logging.FATAL)
    parser.add_argument(
        '-v',
        '--verbose',
        dest="verbosity",
        help="Verbose: set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very_verbose',
        dest="verbosity",
        help="Verty verbose: set loglevel to DEBUG",
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
        default=None,  # None allows ini to set default
        dest="spacy_lang",
        help="SpaCy language model: en_core_web_sm, en_core_web_md, or en_core_web_lg",
        type=str,
        metavar="STR")
    parser.add_argument(
        '--wiki_title_max_words',
        default=DEFAULT_CONFIG['wiki_title_max_words'],
        dest="wiki_title_max_words",
        help='Maximum n-gram length (in tokens) for wikipedia article title guesses.',
        type=int,
        metavar="INT")
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
    parser.add_argument(
        '--qa_model',
        help="Select which model qa_bots will use",
        dest='qa_model',
        default=DEFAULT_CONFIG['qa_model'],
        type=str,
        metavar='STR')
    parsed_args = parser.parse_args(args)
    print(parsed_args)
    return parsed_args


def setup_logging(loglevel=LOGLEVEL):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    global LOGLEVEL, log, root_logger

    logformat = '%(asctime)s.%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    logdatefmt = "%Y-%m-%d%H:%M:%S"
    root_logger.setLevel(loglevel)
    log.setLevel(loglevel)
    # FIXME: this doesn't seem to change things, the original format and level set at top of file rules
    logging.basicConfig(level=loglevel, stream=sys.stdout, format=logformat, datefmt=logdatefmt)
    # set the root logger to the same log level
    logging.getLogger().setLevel(loglevel)


def parse_argv(argv=sys.argv):
    """ Parse the command line args and ini file. Business logic to resolve conflicting arg values """
    global BOT, USE_CUDA, log

    new_argv = []
    if len(argv) > 1:
        command_line_path = str(argv[0]).lower().strip()
        if command_line_path.endswith('qary') or command_line_path.endswith('bot'):
            new_argv.extend(list(argv[1:]))
    else:
        log.error(f"It doesn't look like you're running this as a command line application. sys.argv: {argv}")
    args = parse_args(args=new_argv)

    # consolidate the 2 synonymous args, loglevel and verbosity, by using the minimum of the 2
    #   loglevel may be set by the ini file or the command line arg loglevel
    #   verbosity may only be set by the command line args -v/verbose -qq -vv and -q/quiet
    #   The more verbose of the 2 (lower loglevel value) wins

    loglevel = min(args.loglevel or logging.WARNING, args.verbosity or logging.WARNING)
    setup_logging(loglevel=loglevel)
    log.debug(f'RAW ARGS (including config file): {vars(args)}')
    args.loglevel = loglevel

    # strip quotes in case ini file incorrectly uses single quotes that become part of the str
    args.nickname = str(args.nickname).strip().strip('"').strip("'")
    args.bots = 'glossary,qa' if getattr(args, 'bots', None) is None else args.bots
    args.bots = [m.strip() for m in args.bots.split(',')]
    log.info(f"Building a BOT with: {args.bots}")
    log.info(f"Weights: {args.score_weights}")
    # log.info(f"Parsed Weights: {type(json.loads(args.score_weights))}")

    USE_CUDA = args.use_cuda

    return args


try:
    # This will fail if another application (like gunicorn) imports qary and redirects stdin without running it as a command line app
    print(f"sys.argv: {sys.argv}")
    args = parse_argv(argv=sys.argv)
except Exception as e:  # noqa
    log.error(e)
    log.error('Unable to parse command line arguments. Are you trying to import this into gunicorn?')
    # Workaround for the bug when Django app tries to import qary.constants:
    # `usage: gunicorn [-h] [-c CONFIG] ... gunicorn: error: unrecognized arguments
    args = parse_argv(argv=[])


LOGLEVEL = args.loglevel or LOGLEVEL


# handler = logging.handlers.TimedRotatingFileHandler(os.path.join(LOG_DIR, 'qary.constants.log'), when='midnight')
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

LANG = getattr(args, 'spacy_lang', None) or DEFAULT_CONFIG.get('spacy_lang') or LANGS[0]
log.info(f'LANG=spacy_lang={LANG}')

try:
    STOPWORDS_DICT = Counter(nltk.corpus.stopwords.words('english'))
except LookupError:
    log.info('Downloading NLTK stopwords and punkt corpora')
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    STOPWORDS_DICT = Counter(nltk.corpus.stopwords.words('english'))
STOPWORDS = set(STOPWORDS_DICT)

QUESTIONWORDS = set('who what when were why which how'.split() + ['how come', 'why does', 'can i', 'can you', 'which way'])
QUESTION_STOPWORDS = QUESTIONWORDS | STOPWORDS

ASCII_LOWER = 'abcdefghijklmnopqrstuvwxyz'
ASCII_UPPER = ASCII_LOWER.upper()


# clibot.py
DEFAULT_BOTS = ['pattern']  # 'search_fuzzy', 'parul', 'eliza', 'glossary', 'qa'

# faq_bots.py
FAQ_DOMAINS = (
    'python-data-science',
)
FAQ_MIN_SIMILARITY = 0.88
FAQ_MAX_NUM_REPLIES = 3

# glossary_bots.py
DEFAULT_GLOSSARY_DOMAINS = ('dsdh', )

TFHUB_USE_MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder-large/3"

# # templates for medical sentences
# SENTENCE_SPEC_PATH = os.path.join(DATA_DIR, 'medical_sentences.json')
# SENTENCE_SPEC = json.load(open(SENTENCE_SPEC_PATH, 'r'))


# Universal Sentence Encoder's TF Hub module for creating USE Embeddings from
USE = None


class passthroughSpaCyPipe:
    """ Callable pass-through SpaCy Pipeline Component class (callable) for fallback if spacy_hunspell.spaCyHunSpell fails"""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, doc):
        log.info(f"This passthroughSpaCyPipe component only logs the token count: {len(doc)}")
        return doc
