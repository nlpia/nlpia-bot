""" Text search to retrieve a statement """
import logging
import sys
import os

import yaml
import pandas as pd
from fuzzywuzzy import process
from ..constants import DATA_DIR

log = logging.getLogger(__name__)


LIMIT = 1000000


def get_data(name):
    """ replacement for nlpia.loaders.get_data to avoid dependencies that result in version conflicts

    >>> get_data('movie_dialog').shape
    (64350, 2)
    """
    return pd.read_csv(os.path.join(DATA_DIR, name + '.csv'))


def normalize(text):
    return text.lower()


def scale_probability(p):
    """ Levenshtein similarity is only good when it's high, when it's low, the score should go down """
    return p ** 2


def load_faq(faq_path=os.path.join(DATA_DIR, 'dsfaq_plus_faq_data_science_and_machine_learning.yml')):
    faq = None
    with open(faq_path, 'r') as instream:
        try:
            faq = yaml.safe_load(instream)
        except yaml.YAMLError as e:
            print(e)
            raise(e)
    for i, qa in enumerate(faq):
        if not isinstance(qa, dict):
            faq[i] = {}
            log.warning(f'qa #{i} was not a dict')
            continue
        for k in qa:
            if k.lower() != k:
                qa[k.lower()] = qa.pop(k)
        # if 'q' not in qa:
        #     log.warning(f'qa #{i} had no Question: {list(qa)} {qa[list(qa)[0]]}')
        #     qa['q'] = qa.pop('q_student', qa.pop('q_student2', qa.pop('q_teacher')))
        # if 'a' not in qa:
        #     log.warning(f'qa #{i} had no Answer: {list(qa)} {qa[list(qa)[0]]}')
        #     qa['a'] = qa.pop('a_teacher', qa.pop('a_teacher2', qa.pop('a_student')))
        #     continue
    faq = pd.DataFrame(faq)
    faq = faq.dropna()
    return faq


class Bot:
    db = None

    def __init__(self, name='movie_dialog'):
        self.limit = LIMIT
        self.name = name
        # TODO: make this lazy, do it inside reply()
        self.db = self.load_dialog(name=name)

    def load_dialog(self, name='movie_dialog'):
        log.warning('Loading movie dialog...')
        if name == 'dsfaq':
            db = load_faq()
        else:
            db = get_data(name)
        log.info(f'Loaded {len(db)} {self.name} statement-reply pairs.')
        if self.limit <= len(db):
            log.info(f'Limiting {self.name} database to {self.limit} statement-reply pairs.')
            db = db.iloc[:self.limit]
        db = dict(zip(db[db.columns[0]], db[db.columns[1]]))
        return db

    def reply(self, statement, db=None):
        """ Use fuzzywuzzy to find the closest key in the dictionary then return the value for that key

        >>> bot = MovieBot()
        >>> reply = bot.reply
        >>> reply('hey', {'hello': 'world', 'goodbye': 'fantasy'})
        (0.3, 'fantasy')
        >>> reply("Hi!")
        (1.0, 'hey there. tired of breathing?')
        """
        if self.db is None:
            self.db = db
        if self.db is None:
            self.db = self.load_dialog()
        movie_statement, percent_match, movie_reply = process.extractOne(
            normalize(statement), choices=self.db)
        log.info(f'Closest movie_statement = {movie_statement}')
        return [((percent_match / 100.), movie_reply)]


# class FAQBot(Bot):
#     def __init__(self, name='dsfaq'):
#         self.limit = LIMIT
#         # TODO: make this lazy, do it inside reply()
#         self.db = self.load_dialog(name=name)
# BOTS = (Bot, FAQBot)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        bot = Bot()
        statement = "Hi!"
        statement = ' '.join(sys.argv[1:])
        print(bot.reply(statement))
