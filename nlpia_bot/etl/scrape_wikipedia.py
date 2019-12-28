# make sure you `pip install --upgrade git+https://github.com/lucasdnd/Wikipedia.git`
import os
import time
import csv
import gzip

from tqdm import tqdm
import pandas as pd
from wikipediaapi import Wikipedia

from nlpia_bot import constants
from nlpia_bot.spacy_language_model import load

import logging
log = logging.getLogger(locals().get('__name__', ''))

nlp = load('en_core_web_md')
TITLES = ['Chatbot', 'ELIZA', 'Turing_test', 'AIML', 'Loebniz_prize', 'Chatterbot',
          'Loebner_prize', 'Chinese_room']
EXCLUDE_HEADINGS = ['See also', 'References', 'Bibliography', 'External links']


class WikiIndex():
    _url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz'

    def __init__(self, url=None, refresh=False, **pd_kwargs):
        self._url = url or self._url
        self.df_titles = self.load(url=self._url, refresh=refresh, **pd_kwargs)
        # self.title_slug = self.df_titles.to_dict()
        # self.df_vectors = pd.DataFrame(nlp(s).vector for s in self.df_titles.index.values)
        # self.vectors = dict(zip(range(len(self.df_titles)), ))
        self.title_row = dict(zip(self.df_titles.index.values, range(len(self.df_titles))))
        # AttributeError: 'tuple' object has no attribute 'lower
        # self.title_row.update({k.lower(): v for (k, v) in tqdm(self.title_row.items()) if k.lower() not in self.title_row})
        # self.df_vectors = self.compute_vectors()

    def compute_vectors(self, filename='wikipedia-title-vectors.csv.gz'):
        log.warn(f'Computing title vectors for {len(self.df_titles)} titles. This will take a while.')
        try:
            df = pd.read_csv(os.path.join(constants.DATA_DIR, filename))
        except (IOError, FileNotFoundError, pd.errors.EmptyDataError):
            df = pd.DataFrame([], columns=list(range(300)))
        start = len(df)
        total = len(self.df_titles)
        del df
        vec_batch = []
        with gzip.open(os.path.join(constants.DATA_DIR, filename), 'ta') as fout:
            csv_writer = csv.writer(fout)
            for i, s in tqdm(enumerate(self.df_titles.index.values[start:]), total=total):
                vec = nlp(s).vector
                vec /= pd.np.linalg.norm(vec) or 1.
                vec = vec.round(7)
                mask_zeros = pd.np.abs(vec) > 0
                if mask_zeros.sum() < len(mask_zeros):
                    log.error(f'BAD VEC: {s} {mask_zeros.sum()}')
                if not (i % 1000) or (i == total - 1):
                    vec_batch.append(vec)
                    csv_writer.writerows(vec_batch)
                    vec_batch = []
        time.sleep(1)
        self.df_vectors = pd.read_csv(os.path.join(constants.DATA_DIR, filename))
        return self.df_vectors

    def load(
            self,
            url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz',
            refresh=False,
            **pd_kwargs):
        url_dir, filename = os.path.split(url)
        filepath = os.path.join(constants.DATA_DIR, filename)
        df = None
        if not refresh:
            try:
                df = pd.read_csv(filepath)
            except (IOError, FileNotFoundError):
                log.info(f'No local copy of Wikipedia titles file was found at {filepath}')
        if not len(df):
            log.warn(f'Starting download of entire list of Wikipedia titles at {url}...')
            df = pd.read_table(url)  # , sep=None, delimiter=None, quoting=3, engine='python')
            log.info(f'Finished downloading {len(df)} Wikipedia titles from {url}.')

        df.columns = ['page_title']
        if df.index.name != 'natural_title':
            df.index = list(df['page_title'].str.replace('_', ' ').str.strip())
            df.index.name == 'natural_title'
            df.to_csv(filepath, index=False, compression='gzip')
            log.info(f'Finished saving {len(df)} Wikipedia titles to {filepath}.')
        self.df_titles = df
        return self.df_titles

    def find_similar_titles(self, title=None, n=1):
        if isinstance(title, str):
            vec = nlp(title).vector
        else:
            vec = title
        vec /= pd.np.linalg.norm(vec) or 1.
        dot_products = vec.dot(self.df_vectors.values.T)
        if n == 1:
            return self.df_titles.index.values[dot_products.argmax()]
        sorted(dot_products, reverse=True)


def scrape_articles(titles=TITLES, exclude_headings=EXCLUDE_HEADINGS,
                    see_also=True, max_articles=10000, max_depth=3):
    """ Download text for an article and parse into sections and sentences

    >>> nlp('hello')  # to eager-load spacy model
    hello
    >>> df = scrape_articles(['ELIZA'], see_also=False)
    >>> df.shape
    (87, 3)
    >>> df.columns
    Index(['title', 'section', 'sentence'], dtype='object')
    """

    titles = list([titles] if isinstance(titles, str) else titles)
    exclude_headings = set([eh.lower().strip() for eh in (exclude_headings or [])])
    depths = list([0] * len(titles))
    title_depths = list(zip(titles, depths))
    sentences = []
    # FIXME: breadth-first search so you can do a tqdm progress bar for each depth
    # FIXME: record title tree (see also) so that .2*title1+.3*title2+.5*title3 can be semantically appended to sentences
    titles_scraped = set([''])
    title, d = '', 0
    wiki = Wikipedia()
    for depth in range(max_depth):
        for i in range(max_articles):
            title = None
            while not title or title in titles_scraped:
                # log.warn(f"Skipping {title} (already scraped)")
                try:
                    title, d = title_depths.pop()
                except IndexError:
                    log.warn(f'Out of titles: {title_depths}')
                    break
                title = title.strip()
            if d > max_depth or not title:
                log.info(f"{d} > {max_depth} or title ('{title}') is empty")
                continue
            titles_scraped.add(title)
            page = wiki.article(title)
            if not (len(page.text) + len(page.summary)):
                log.error(f"Unable to retrieve {title}")
                time.sleep(2.17)
                continue
            if see_also and d + 1 < max_depth:
                # .full_text() includes the section heading ("See also"). .text does not
                section = page.section_by_title('See also')
                if not section:
                    continue
                for t in section.text.split('\n')[1:]:
                    if t in page.links:
                        title_depths.append((t, d + 1))
                log.debug(f'extended title_depths at depth {d}: {title_depths}')
            for section in page.sections:
                if section.title.lower().strip() in exclude_headings:
                    continue
                # TODO: use pugnlp.to_ascii() or nlpia.to_ascii()
                text = section.text.replace('’', "'")  # spacy doesn't handle "latin" (extended ascii) apostrophes well.
                # FIXME: need to rejoin short names before colons, like 'ELIZA:' 'Tell me...', and 'Human:' 'What...'
                # FIXME: need to split on question marks without white space but where next word is capitalized: ...to be unhappy?Though designed strictly...
                sentences.extend([
                    (d, title, section.title, s.text) for s in nlp(text).sents if (
                        len(s.text.strip().strip('"').strip("'").strip()) > 1)
                ])
            log.debug(f'Parsed {len(sentences)} sentences.')

            # retval = parse_sentences(
            #     title=title, sentences=sentences, title_depths=title_depths, see_also=see_also,
            #     exclude_headings=exclude_headings, d=d, depth=depth, max_depth=max_depth)
            # if retval is None:
            #     continue
            # else:
            #     sentences, title_depths = retval
            log.info(str([depth, d, i, title]))
            if d > depth:
                log.info(f"{d} > {depth}")
                break

    return pd.DataFrame(sentences, columns='depth title section sentence'.split())


def count_nonzero_vector_dims(self, strings, nominal_dims=1):
    """ Count the number of nonzero values in a sequence of vectors

    Used to compare the doc vectors normalized as Marie_Curie vs "Marie Curie" vs "marie curie",
    and found that the spaced version was more complete (almost twice as many title words had valid vectors).
    >>> count_nonzero_vector_dims(df[df.columns[0]].values[:100]) / 300
    264.0

    >>> df.index = df['page_title'].str.replace('_', ' ').str.strip()
    >>> count_nonzero_vector_dims(df.index.values[:100]) / 300
    415.0

    """
    tot = 0
    for s in strings:
        tot += (pd.DataFrame([t.vector for t in nlp(s)]).abs() > 0).T.sum().sum()
    return tot

# def parse_sentences(title, sentences, title_depths, see_also=True, exclude_headings=(), d=0, depth=0, max_depth=3):

#     return sentences, title_depths
