""" Pattern and template based chatbot dialog engines """
import re
import logging

import pandas as pd

from nlpia_bot.etl import glossaries
from nlpia_bot import spacy_language_model

log = logging.getLogger(__name__)
nlp = spacy_language_model.load('en_core_web_md')


def capitalizations(s):
    return (s, s.lower(), s.upper(), s.title())


class Bot:
    """ Bot that can reply with definitions from glossary yml files in data/faq/glossary-*.yml

    >>> bot = Bot()
    >>> bot.reply('allele')
    [(1.0, "I don't understand")]
    >>> bot.reply('What is a nucleotide?')
    [(1,
     'The basic building blocks of DNA and RNA...
    """

    def __init__(self, domains=('dsdh',)):
        global nlp
        self.nlp = nlp
        self.glossary = glossaries.load(domains=domains)
        self.glossary.fillna('', inplace=True)
        self.glossary.index = self.glossary['term'].str.lower().str.strip()
        self.vector = dict()
        self.vector['term'] = pd.DataFrame({s: nlp(s or '').vector for s in self.glossary['term']})
        self.vector['definition'] = pd.DataFrame({s: nlp(s or '').vector for s in self.glossary['definition']})

        self.synonyms = {}
        # create reverse index of synonyms to canonical terms
        for term, row in self.glossary.iterrows():
            self.synonyms.update(dict(zip(capitalizations(term), [term] * 4)))
            if type(row['acronym']) == str and row['acronym'].strip():
                acro = row['acronym'].strip()
                self.synonyms.update(dict(zip(capitalizations(acro), [term] * 4)))

    def reply(self, statement):
        """ Suggest responses to a user statement string with [(score, reply_string)..]

        >>> bot = Bot()
        >>> bot.reply('allele')
        [(1.0, "I don't understand")]
        >>> bot.reply('What is a nucleotide?')
        [(1,
         'The basic building blocks of DNA and RNA...
        """
        responses = []
        match = re.match(r"\b(what\s+(is|are)\s*(not|n't)?\s+(a|an|the))\b([^\?]*)(\?*)", statement.lower())
        if match:
            log.info(str(match.groups()))
            for i, term in enumerate(capitalizations(match.groups()[-2])):
                normalized_term = self.synonyms.get(term, None)
                if normalized_term:
                    responses.append((1 - .02 * i, self.glossary['definition'][normalized_term]))
        else:
            responses = [(0.05, "I don't understand. That doesn't sound like a question I can answer using my glossary.")]
        if not len(responses):
            responses.append((0.25, "My glossaries and dictionaries don't seem to contain that term."))
        return responses
