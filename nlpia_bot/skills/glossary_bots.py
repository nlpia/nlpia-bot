""" Pattern and template based chatbot dialog engines """
import re

import pandas as pd

from nlpia_bot.etl import glossaries
from nlpia_bot import spacy_language_model


nlp = spacy_language_model.load('en_core_web_md')


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
            try:
                responses.append((1, self.glossary['definition'][match.groups()[-2].strip().lower()]))
            except KeyError:
                responses.append((1, str(match.groups())))
        else:
            responses = [(1.0, "I don't understand")]
        return responses
