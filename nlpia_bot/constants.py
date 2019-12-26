# constants.py
import os
# import re
import logging
from collections import Counter
# import json

# import pandas as pd
import nltk
import nltk.corpus
import spacy  # noqa

SRC_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(SRC_DIR, 'data')
LOG_DIR = os.path.join(DATA_DIR, 'log')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]
LOG_LEVEL_NAMES = 'DEBUG INFO WARNING ERROR FATAL'.split()
LOG_LEVEL_ABBREVIATIONS = [s[:4].lower() for s in LOG_LEVEL_NAMES]
LOG_LEVEL_ABBR_DICT = dict(zip(LOG_LEVEL_ABBREVIATIONS, LOG_LEVELS))

logging.basicConfig(
    format='%(asctime)s.%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.WARNING)  # FIXME: read from config file like in clibot.py
root_logger = logging.getLogger()

log = logging.getLogger(__name__)
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
LANG = LANGS[0]


try:
    STOPWORDS_DICT = Counter(nltk.corpus.stopwords.words('english'))
except LookupError:
    log.info('Downloading NLTK stopwords and punkt corpora')
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    STOPWORDS_DICT = Counter(nltk.corpus.stopwords.words('english'))
STOPWORDS = set(STOPWORDS_DICT)

DEFAULT_BOTS = {
    'pattern_bots': None,
    'search_fuzzy_bots': None,
    'parul_bots': None,
    'eliza_bots': None,
}


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
