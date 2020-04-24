""" Download wiktionary slang words glossary """
import os
from datetime import datetime as Datetime
from datetime import date as Date
import requests

import pandas as pd

from ..constants import DATA_DIR


def scrape_slang(url='https://bestlifeonline.com/2010s-slang/'):
    return requests.get(url).text


def find_latest_index(lang='en', date='20200101'):
    if isinstance(date, (Datetime, Date)):
        date = f'{date.year}{date.month}{date.day}'
    return f'https://dumps.wikimedia.org/{lang}wiktionary/{date}/' \
        f'{lang}wiktionary-{date}-pages-articles-multistream-index.txt.bz2'


def load_english_index(path='{lang}wiktionary-{date}-pages-articles-multistream-index.txt.bz2',
                       lang='en', date='20200101'):
    if '{' in path:
        path = path.format(lang=lang, date=date)
    for p in [path, os.path.join(DATA_DIR, path), find_latest_index]:
        p = p() if callable(p) else p
        try:
            return pd.read_csv(p, sep=':')
        except IOError:
            pass


def get_pageids(word, url='https://en.wiktionary.org/w/api.php', params=None):
    """ Get the page ID for a word, -1 if page/word doesn't exist

    >>> get_page_ids('testnotaword')
    [-1]
    """
    default_params = dict(
        action='query',
        format='json'
    )
    default_params.update(dict(title=str(word)))
    default_params.update(params or {})
    resp = requests.get('https://en.wiktionary.org/w/api.php?action=query&format=json)')
    return list(resp.json().get('query', {}).get('pages', {}).keys())
