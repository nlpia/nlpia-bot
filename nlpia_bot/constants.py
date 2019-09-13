# constants.py
import os
import logging
import logging.handlers
from collections import Counter
import json

import nltk
import nltk.corpus
import spacy  # noqa


SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)
LOG_DIR = os.path.join(DATA_DIR, 'log')
if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)


LOG_LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]
LOG_LEVEL_NAMES = 'DEBUG INFO WARNING ERROR FATAL'.split()
LOG_LEVEL_ABBREVIATIONS = [s[:4].lower() for s in LOG_LEVEL_NAMES]

root_logger = logging.getLogger()
root_logger.setLevel(logging.WARN)

log = logging.getLogger(__name__)
# handler = logging.handlers.TimedRotatingFileHandler(os.path.join(LOG_DIR, 'nlpia_bot.constants.log'), when='midnight')
# handler.setLevel(logging.INFO)
# log.addHandler(handler)
log.setLevel(logging.INFO)

try:
    STOPWORDS_DICT = Counter(nltk.corpus.stopwords.words('english'))
except LookupError:
    log.info('Downloading NLTK stopwords and punkt corpora')
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    STOPWORDS_DICT = Counter(nltk.corpus.stopwords.words('english'))
STOPWORDS = set(STOPWORDS_DICT)


def load_spacy_model(lang=None):
    """ Load the specified language model or the small English model, if none specified

    >>> load_spacy_model()  # doctest: +ELLIPSIS
    <spacy.lang.en.English object at ...
    """
    model = None
    log.warning("Loading SpaCy model...")
    if lang:
        try:
            model = spacy.load(lang)
        except OSError:
            log.warning(f"Downloading {lang} SpaCy model...")
            spacy.cli.download(lang)
            model = spacy.load(lang)
    else:
        for lang in ('en_core_web_lg', 'en_core_web_md', 'en_core_web_sm'):
            if model is None:
                try:
                    model = spacy.load(lang)
                    log.info(f"Successfully loaded SpaCy model named {lang}")
                except OSError:
                    pass
    if model is None:
        lang = 'en'
        spacy.cli.download(lang)
        model = spacy.load(lang)
    log.warning(f"Finished loading SpaCy model named {lang}: {model}.")
    return model


nlp = load_spacy_model('en_core_web_md')

TFHUB_USE_MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder-large/3"
SENTENCE_SPEC_PATH = os.path.join(os.path.dirname(__file__), 'data', 'medical_sentences.json')
SENTENCE_SPEC = json.load(open(SENTENCE_SPEC_PATH, 'r'))


# Universal Sentence Encoder's TF Hub module for creating USE Embeddings from
USE = None
