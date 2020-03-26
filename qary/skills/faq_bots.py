""" Pattern and template based chatbot dialog engines """
import logging

import pandas as pd

from ..etl import faqs
from ..constants import DEFAULT_FAQ_DOMAINS
from .. import spacy_language_model
from ..etl import knowledge_extraction as extract

log = logging.getLogger(__name__)
nlp = spacy_language_model.load()  # 'en_core_web_md'


def capitalizations(s):
    return (s, s.lower(), s.upper(), s.title())


class Bot:
    r""" Bot that can reply with answers to frequently asked questions using data/faq/*.yml

    >>> bot = Bot()
    >>> bot.reply('What are the basic variable data types in python?')[0][-1]
    '`float`, `int`, `str`, and `bool`'
    """

    def __init__(self,
                 domains=DEFAULT_FAQ_DOMAINS):
        """ Load glossary from yaml file indicated by list of domain names """
        global nlp
        self.nlp = nlp
        self.faq = faqs.load(domains=domains)['cleaned']
        self.vector = dict()
        self.vector['term'] = pd.DataFrame(
            {term: nlp(term).vector for term in self.glossary})
        self.vector['definition'] = pd.DataFrame(
            {term: nlp(d['definition']).vector for term, d in self.glossary.items()})

        # self.synonyms = {term: term for term in self.glossary}
        # create reverse index of synonyms to canonical terms
        # for term, d in self.glossary.items():
        #     self.synonyms.update(dict(zip(capitalizations(term), [term] * 4)))
        #     acro = d['acronym']
        #     if acro:
        #         self.synonyms.update(dict(zip(capitalizations(acro), [term] * 4)))

    def reply(self, statement):
        """ Suggest responses to a user statement string with [(score, reply_string)..]"""
        responses = []
        extracted_term = extract.whatis(statement) or ''
        if extracted_term:
            for i, term in enumerate(capitalizations(extracted_term)):
                normalized_term = self.synonyms.get(term, term)
                if normalized_term in self.glossary:
                    responses.append((1 - .02 * i, self.glossary[normalized_term]['definition']))
        else:
            responses = [(0.05, "I don't understand. That doesn't sound like a question I can answer using my glossary.")]
        if not len(responses):
            responses.append((0.25, f"My glossaries and dictionaries don't seem to contain that term ('{extracted_term}')."))
        return responses
