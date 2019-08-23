# constants.py
import os
import logging
from collections import Counter
import json

import nltk
import nltk.corpus
import spacy


SRC_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

LOG_LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]
LOG_LEVEL_NAMES = 'DEBUG INFO WARNING ERROR FATAL'.split()
LOG_LEVEL_ABBREVIATIONS = [s[:4].lower() for s in LOG_LEVEL_NAMES]

root_logger = logging.getLogger()
root_logger.setLevel(logging.WARN)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

try:
    STOPWORDS_DICT = Counter(nltk.corpus.stopwords.words('english'))
except LookupError:
    log.info('Downloading NLTK stopwords and punkt corpora')
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    STOPWORDS_DICT = Counter(nltk.corpus.stopwords.words('english'))
STOPWORDS = set(STOPWORDS_DICT)

NLP = spacy.load('en_core_web_lg')
TFHUB_USE_MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder-large/3"
SENTENCE_SPEC_PATH = os.path.join(os.path.dirname(__file__), 'data', 'medical_sentences.json')
SENTENCE_SPEC = json.load(open(SENTENCE_SPEC_PATH, 'r'))


# Universal Sentence Encoder's TF Hub module for creating USE Embeddings from
USE = None
