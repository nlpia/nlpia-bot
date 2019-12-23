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
        self.vector = dict()
        self.vector['term'] = pd.DataFrame({term: nlp(term or '').vector for term in self.glossary})
        self.vector['definition'] = pd.DataFrame({d['term']: nlp(d['definition']).vector for term, d in self.glossary.items()})

        self.synonyms = {}
        # create reverse index of synonyms to canonical terms
        for term, d in self.glossary.items():
            self.synonyms.update(dict(zip(capitalizations(term), [term] * 4)))
            acro = d['acronym']
            if acro:
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
                if normalized_term in self.glossary:
                    responses.append((1 - .02 * i, self.glossary[normalized_term]['definition']))
        else:
            responses = [(0.05, "I don't understand. That doesn't sound like a question I can answer using my glossary.")]
        if not len(responses):
            responses.append((0.25, "My glossaries and dictionaries don't seem to contain that term."))
        return responses
