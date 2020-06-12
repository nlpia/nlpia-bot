""" Pattern and template based chatbot dialog engines """
import logging

# import pandas as pd

from qary.etl import glossaries
from qary import spacy_language_model
from qary.etl import knowledge_extraction as extract
from qary.skills.basebots import ContextBot

log = logging.getLogger(__name__)
nlp = spacy_language_model.load('en_core_web_md')


def capitalizations(s):
    return (s, s.lower(), s.upper(), s.title())


class Bot(ContextBot):
    """ Bot that can reply with definitions from glossary yml files in data/faq/glossary-*.yml

    >>> bot = Bot()
    >>> bot.reply('allele')
    [(0.05, "I don't understand...")]
    >>> bot.reply('What is an Allele?')
    [(1.0, 'A variant form of a given gene...')]
    >>> bot.reply('What is a nucleotide?')
    [(0.94, 'The basic building blocks of DNA and RNA...')]
    """

    def __init__(self, domains=('dsdh',)):
        """ Load glossary from yaml file indicated by list of domain names """
        global nlp
        super().__init__(self)
        self.nlp = nlp
        self.glossary = glossaries.load(domains=domains)['cleaned']
        self.vector = dict()
        self.vector['term'] = glossaries.term_vector_dict(self.glossary.keys())
        self.vector['definition'] = glossaries.term_vector_dict(self.glossary.values(), self.glossary.keys())

        self.synonyms = {term: term for term in self.glossary}
        # create reverse index of synonyms to canonical terms
        # for term, d in self.glossary.items():
        #     self.synonyms.update(dict(zip(capitalizations(term), [term] * 4)))
        #     acro = d['acronym']
        #     if acro:
        #         self.synonyms.update(dict(zip(capitalizations(acro), [term] * 4)))

    def reply(self, statement):
        """ Suggest responses to a user statement string with [(score, reply_string)..]"""
        responses = []
        extracted_term = extract.whatis(statement) or extract.whatmeans(statement) or ''
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
