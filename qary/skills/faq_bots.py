""" Pattern and template based chatbot dialog engines """
import logging

# import pandas as pd

from ..etl import faqs
from ..constants import FAQ_DOMAINS, FAQ_MIN_SIMILARITY, FAQ_MAX_NUM_REPLIES
from .. import spacy_language_model
from ..etl import knowledge_extraction as extract  # noqa
import numpy as np

log = logging.getLogger(__name__)

nlp = spacy_language_model.nlp
if nlp._meta['vectors']['width'] < 300:  # len(nlp('word vector').vector) < 300:
    log.warning(f"SpaCy Language model ({nlp._meta['name']}) doesn't contain 300D word2vec word vectors.")
    nlp = spacy_language_model.nlp = spacy_language_model.load('en_core_web_md')


def capitalizations(s):
    return (s, s.lower(), s.upper(), s.title())


class Bot:
    r""" Bot that can reply with answers to frequently asked questions using data/faq/*.yml

    >>> bot = Bot()
    >>> bot.reply('What are the basic variable data types in python?')[0][-1]
    '`float`, `int`, `str`, and `bool`'
    """

    def __init__(self, domains=FAQ_DOMAINS):
        """ Load glossary from yaml file indicated by list of domain names """
        global nlp
        self.nlp = nlp
        self.faq = faqs.load(domains=domains)

    def reply(self, statement):
        """ Suggest responses to a user statement string with [(score, reply_string)..]"""
        responses = []
        question_vector = nlp(statement).vector
        log.debug(f"question_vector is {question_vector}")
        question_vector /= np.linalg.norm(question_vector)
        log.debug(f"faq['question_vectors'].shape is {self.faq['question_vectors'].shape}")
        question_similarities = self.faq['question_vectors'].dot(question_vector.reshape(-1, 1))
        # responses.append((1.0, str(question_similarities)))
        idx = question_similarities.argmax()
        mask = np.array(question_similarities).flatten() >= FAQ_MIN_SIMILARITY
        if sum(mask) >= 1:
            responses.extend(list(zip(question_similarities[mask],
                                      (str(a) for a in self.faq['answers'][mask])
                                      )))
            responses = sorted(responses, reverse=True)[:FAQ_MAX_NUM_REPLIES]
        else:
            responses = [(
                0.10,
                f"I don't know. Here's a FAQ similar to yours that you might try: \"{self.faq['questions'][idx]}\". ")]
        return responses
