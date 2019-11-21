# constants.py
import os
import logging
import logging.handlers
from collections import Counter
# import json

import nltk
import nltk.corpus
# import spacy  # noqa

LANG = 'en_core_web_sm'  # 'en_core_web_md' or 'en_core_web_lg' or maybe 'en'

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(SRC_DIR, 'data')
LOG_DIR = os.path.join(DATA_DIR, 'log')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]
LOG_LEVEL_NAMES = 'DEBUG INFO WARNING ERROR FATAL'.split()
LOG_LEVEL_ABBREVIATIONS = [s[:4].lower() for s in LOG_LEVEL_NAMES]

logging.basicConfig(
    format='%(asctime)s.%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.WARNING)
root_logger = logging.getLogger()

log = logging.getLogger(__name__)
# handler = logging.handlers.TimedRotatingFileHandler(os.path.join(LOG_DIR, 'nlpia_bot.constants.log'), when='midnight')
# handler.setLevel(logging.INFO)
# log.addHandler(handler)

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
