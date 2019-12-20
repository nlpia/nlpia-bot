# make sure you `pip install --upgrade git+https://github.com/lucasdnd/Wikipedia.git`
import os
import re

from tqdm import tqdm
import pandas as pd
import yaml

# from nlpia_bot.spacy_language_model import nlp
from nlpia_bot.constants import DATA_DIR

import logging
log = logging.getLogger(locals().get('__name__'))


def find_hashtags(s, pattern=r'\s*#[\w\d_-]+'):
    s = s or ''
    hashtags = re.findall(pattern, s) or []
    hashtags = tuple(sorted(set([t.strip() for t in hashtags])))
    cleaned = re.sub(pattern, '', s)
    return {'cleaned': cleaned, 'hashtags': hashtags}


def load(domains=('dsdh',)):
    """ Load yaml file, use hashtags to create context tags as multihot columns

    >>> len(load(domains='dsdh'.split(','))) > 30
    True
    """
    dictionaries = []
    for domain in tqdm(domains):
        dictionaries.append(
            yaml.load(open(os.path.join(DATA_DIR, 'faq', f'glossary-{domain}.yml'))))
    df = pd.concat([pd.DataFrame(d.items(), columns='term definition'.split()) for d in dictionaries])
    acronyms = []
    for i, row in df.iterrows():
        match = re.match(r'([^(]*)\(([^)]*)\)$', row['term'])
        if match:
            acronyms.append(match.groups())
        else:
            acronyms.append((None, None))
    acronyms = pd.DataFrame(acronyms, columns='acronym acronym_expanded'.split())
    cleaned_hashtags = [find_hashtags(s) for s in df['definition']]
    cleaned_hashtags = pd.DataFrame(cleaned_hashtags)
    return pd.concat([acronyms, df, cleaned_hashtags], axis=1)


# def parse_sentences(title, sentences, title_depths, see_also=True, exclude_headings=(), d=0, depth=0, max_depth=3):

#     return sentences, title_depths
