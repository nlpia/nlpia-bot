# make sure you `pip install --upgrade git+https://github.com/lucasdnd/Wikipedia.git`
import os
import time
import csv
import gzip
import copy
# from queue import Queue

from tqdm import tqdm
import pandas as pd
from wikipediaapi import Wikipedia

from .. import constants
from ..spacy_language_model import load
from .vectors import phrase_to_vec

import logging
log = logging.getLogger(locals().get('__name__', ''))

nlp = load('en_core_web_md')
TITLES = ['Chatbot', 'ELIZA', 'Turing_test', 'AIML', 'Chatterbot', 'Loebner_prize', 'Chinese_room']
EXCLUDE_HEADINGS = ['See also', 'References', 'Bibliography', 'External links']


class WikiIndex():
    """ Semantic and trigram index for wikipedia page titles  """
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
        log.warning(f'Computing title vectors for {len(self.df_titles)} titles. This will take a while.')
        filepath = os.path.join(constants.DATA_DIR, filename)
        start = sum((1 for line in gzip.open(filepath, 'rb')))
        total = len(self.df_titles) - start
        vec_batch = []
        with gzip.open(filepath, 'ta') as fout:
            csv_writer = csv.writer(fout)
            csv_writer.writerow(['page_title'] + [f'x{i}' for i in range(300)])
            for i, s in tqdm(enumerate(self.df_titles.index.values[start:]), total=total):
                vec = [s] + phrase_to_vec(str(s))  # s can sometimes (rarely) be a float because of pd.read_csv (df_titles)
                vec_batch.append(vec)
                if not (i % 1000) or i == total - 1:
                    csv_writer.writerows(vec_batch)
                    print(f"wrote {len(vec_batch)} rows")
                    try:
                        print(f'wrote {len(vec_batch), len(vec_batch[0])} values')
                    except IndexError:
                        pass
                    vec_batch = []
        time.sleep(1)
        dtypes = {f'x{i}': pd.np.float16 for i in range(300)}
        dtypes.update(page_title=str)
        self.df_vectors = pd.read_csv(filepath, dtype=dtypes)
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
                df = pd.read_csv(filepath, dtype=str)
            except (IOError, FileNotFoundError):
                log.info(f'No local copy of Wikipedia titles file was found at {filepath}')
        if not len(df):
            log.warning(f'Starting download of entire list of Wikipedia titles at {url}...')
            df = pd.read_table(url, dtype=str)  # , sep=None, delimiter=None, quoting=3, engine='python')
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
        """ Takes dot product of a doc vector with all wikipedia title doc vectors to find closest article titles """
        if isinstance(title, str):
            vec = nlp(title).vector
        else:
            vec = title
        vec /= pd.np.linalg.norm(vec) or 1.
        dot_products = vec.dot(self.df_vectors.values.T)
        if n == 1:
            return self.df_titles.index.values[dot_products.argmax()]
        sorted(dot_products, reverse=True)


class WikiNotFound:
    text = ''
    summary = ''


class WikiScraper:
    """ RAM caching of scraped wikipedia pages

    TODO: preserve cache between runs in a sqlite database or flatfile or h5 (hdf) file
    """

    def __init__(self,
                 sleep_empty_page=2.17,
                 sleep_downloaded_page=0.01,
                 sleep_nonexistent_page=0.02):
        self.sleep_empty_page = sleep_empty_page
        self.sleep_nonexistent_page = sleep_nonexistent_page
        self.sleep_downloaded_page = sleep_downloaded_page
        self.cache = {}
        self.section_titles = {}

    def get_article(self,
                    title: str,
                    exclude_headings=EXCLUDE_HEADINGS,
                    see_also=True,
                    prepend_section_headings=True,
                    prepend_title_text=True,
                    ):
        """ same as scrape_article_texts but for single article, and checks cache first """
        page_dict = self.cache.get(title)
        if page_dict and page_dict.get('text') and page_dict.get('summary'):
            return copy.copy(page_dict)
        self.wiki = Wikipedia()
        page = self.wiki.article(title)

        text, summary, see_also_links = '', '', []
        if page.exists():
            text = getattr(page, 'text', '')
            summary = getattr(page, 'summary', '')
        else:
            time.sleep(self.sleep_nonexistent_page)
            self.cache[title] = {}
            return {}

        # FIXME: this postprocessing of Article objects to compost a text string should be in separate funcition
        # TODO: see_also is unnecessary until we add another way to walk deeper, e.g. links within the article
        if see_also:
            # .full_text() includes the section heading ("See also"). .text does not
            section = page.section_by_title('See also')
            if section:
                for t in section.text.split('\n'):
                    log.info(f"  Checking _SEE ALSO_ link: {t}")
                    if t in page.links:
                        see_also_links.append(t)

        text = f'{page.title}\n\n' if prepend_title_text else ''
        # page.text
        for section in page.sections:
            if section.title.lower().strip() in exclude_headings:
                continue
            # TODO: use pugnlp.to_ascii() or nlpia.to_ascii()
            text += f'\n{section.title}\n' if prepend_section_headings else '\n'
            # spacy doesn't handle "latin" (extended ascii) apostrophes well.
            text += section.text.replace('’', "'") + '\n'
            self.section_titles[str(section.title).strip()] = str(section.title).lower().strip().replace('’', "'")
        page_dict = dict(title=page.title, text=text, summary=summary, see_also_links=see_also_links)
        self.cache[title] = page_dict
        return page_dict

    def scrape_article_pages(self,
                             titles=TITLES,
                             exclude_headings=EXCLUDE_HEADINGS,
                             see_also=True,
                             prepend_section_headings=True,
                             prepend_title_text=True,
                             max_articles=10_000,
                             max_depth=1):
        r""" Download text for an article and parse into sections and sentences

        TODO: add exclude_title_regexes to exclude page titles like "ELIZA (disambiguation)" with '.*\(disambiguation\)'

        >>> scraper = WikiScraper()
        >>> pages = scraper.scrape_article_pages(['ELIZA'], see_also=False)
        >>> hasattr(pages, '__next__')
        True
        >>> pages = list(pages)
        >>> len(pages)
        1
        >>> texts = list(p['text'] for p in scraper.scrape_article_pages(['Chatbot', 'ELIZA'], max_articles=10, max_depth=3))
        >>> len(texts)
        10
        """
        if isinstance(titles, str):
            log.error(f'DEPRECATED `titles` should be a list of strs, not titles="{titles}"')
            titles = find_titles(titles)
        exclude_headings = set([eh.lower().strip() for eh in (exclude_headings or [])])
        # depth starts at zero here, but as additional titles are appended the depth will increase
        title_depths = list(zip(titles, [0] * len(titles)))
        text_lens = []
        # FIXME: record title tree (see also) so that .2*title1+.3*title2+.5*title3 can be semantically appended to sentences
        titles_scraped = set([''])
        d, num_articles, queue_pos = 0, 0, 0
        # TODO: make this a while loop to consolidate d = depth should be able to use depth rather than d:
        for depth in range(max_depth):
            while num_articles < max_articles and d <= depth and queue_pos < len(title_depths):
                title = ''
                log.debug("title_depths:\n" + '\n'.join(f"{td[1]}: {td[0]}" for td in title_depths))

                # pop another title and keep popping until it's not a title already scraped
                while queue_pos < len(title_depths) and (not title.strip() or title in titles_scraped):
                    log.info(f"Skipping '{title}' (already scraped)")
                    try:
                        title, d = title_depths[queue_pos]
                        queue_pos += 1
                    except IndexError:
                        log.debug(f'Out of titles: {title_depths}')
                        break
                    title = title.strip()
                if d > max_depth or not title:
                    log.info(f"{d} > {max_depth} or title ('{title}') is empty")
                    continue
                if title in titles_scraped:
                    continue
                log.info(f'title: {title}')
                log.info(f'remaining len(title_depths): {len(title_depths)}, queue_pos: {queue_pos}')
                page_dict = self.get_article(
                    title,
                    see_also=see_also,
                    exclude_headings=exclude_headings,
                    prepend_section_headings=prepend_section_headings,
                    prepend_title_text=prepend_title_text) or dict(text='', summary='', see_also_links=[])
                titles_scraped.add(title)
                if not page_dict:
                    continue
                page_dict['title'] = title
                page_dict['depth'] = d
                log.info(f'len(titles_scraped): {len(titles_scraped)}')
                if not len(page_dict['text'] + page_dict['summary']):
                    log.warning(f"Unable to retrieve _{title}_ because article text and summary len are 0.")
                    time.sleep(self.sleep_empty_page)
                    continue
                title_depths.extend([(t, d + 1) for t in page_dict['see_also_links']])
                text_lens.append(len(page_dict['text']))
                num_articles += 1

                log.warning(f'Added article #{num_articles} "{title}" with {len(page_dict["text"])} chars.')
                log.info(f'  Total scraped {sum(text_lens)} chars')  # TODO: separate scraped from cache-retrieval counts
                log.warning(str([depth, d, num_articles, title]))
                yield page_dict

    def scrape_article_texts(self,
                             titles=TITLES,
                             exclude_headings=EXCLUDE_HEADINGS,
                             see_also=True,
                             prepend_section_headings=True,
                             prepend_title_text=True,
                             max_articles=10_000,
                             max_depth=1):
        r""" Download text for an article and parse into sections and sentences

        TODO: add exclude_title_regexes to exclude page titles like "ELIZA (disambiguation)" with '.*\(disambiguation\)'
        >>> nlp('hello')  # to eager-load spacy model
        hello
        >>> scraper = WikiScraper()
        >>> texts = scraper.scrape_article_texts(['ELIZA'], see_also=False)
        >>> texts = list(texts)
        >>> len(texts)
        1
        >>> texts = list(scraper.scrape_article_texts(['Chatbot', 'ELIZA'], max_articles=10, max_depth=3))
        >>> len(texts)
        10
        """
        for page_dict in self.scrape_article_pages(titles=titles,
                                                   exclude_headings=exclude_headings,
                                                   see_also=see_also,
                                                   prepend_section_headings=prepend_section_headings,
                                                   prepend_title_text=prepend_title_text,
                                                   max_articles=max_articles,
                                                   max_depth=max_depth):
            yield page_dict['text']

    def scrape_article_sentences(self,
                                 titles=TITLES,
                                 exclude_headings=EXCLUDE_HEADINGS,
                                 see_also=True,
                                 prepend_section_headings=True,
                                 prepend_title_text=True,
                                 max_articles=10_000,
                                 max_depth=1):
        """ Download text for an article and parse into sections and sentences

        >>> scraper = WikiScraper()
        >>> df = scraper.scrape_article_sentences(['ELIZA'], see_also=False)
        >>> df.shape[0] > 50
        True
        >>> df.columns
        Index(['title', 'see_also_links', 'depth', 'sentence', 'section_title', 'section_num'], dtype='object')
        """
        df = []
        for page_dict in self.scrape_article_pages(titles=titles,
                                                   exclude_headings=exclude_headings,
                                                   see_also=see_also,
                                                   prepend_section_headings=prepend_section_headings,
                                                   prepend_title_text=prepend_title_text,
                                                   max_articles=max_articles,
                                                   max_depth=max_depth):
            section_title, section_num = '', 0
            for sentence in nlp(page_dict['text']).sents:
                for s in sentence.text.split('\n'):
                    stripped = s.strip()
                    if not stripped:
                        continue
                    sentence_dict = dict([kv for kv in page_dict.items() if kv[0] not in ('text', 'summary')])
                    sentence_dict['sentence'] = s
                    if self.section_titles.get(stripped):
                        section_title = stripped
                        section_num += 1
                    sentence_dict['section_title'] = section_title
                    sentence_dict['section_num'] = section_num
                    df.append(sentence_dict)

        return pd.DataFrame(df)


wikiscraper = WikiScraper()

scrape_article_texts = wikiscraper.scrape_article_texts


def count_nonzero_vector_dims(self, strings, nominal_dims=1):
    r""" Count the number of nonzero values in a sequence of vectors

    Used to compare the doc vectors normalized as Marie_Curie vs "Marie Curie" vs "marie curie",
    and found that the spaced version was more complete (almost twice as many title words had valid vectors).

    >> count_nonzero_vector_dims(df[df.columns[0]].values[:100]) / 300
    264.0
    >> df.index = df['page_title'].str.replace('_', ' ').str.strip()
    >> count_nonzero_vector_dims(df.index.values[:100]) / 300
    415.0
    """
    tot = 0
    for s in strings:
        tot += (pd.DataFrame([t.vector for t in nlp(s)]).abs() > 0).T.sum().sum()
    return tot


def list_ngrams(token_list, n=3, sep=' '):
    r""" Return list of n-grams from a list of tokens (words)

    >>> ','.join(list_ngrams('Hello big blue marble'.split(), n=3))
    'Hello,Hello big,Hello big blue,big,big blue,big blue marble,blue,blue marble,marble'
    >>> ','.join(list_ngrams('Hello big blue marble'.split(), n=3, sep='_'))
    'Hello,Hello_big,Hello_big_blue,big,big_blue,big_blue_marble,blue,blue_marble,marble'
    """
    if isinstance(token_list, str):
        token_list = [tok.text for tok in nlp(token_list)]
    ngram_list = []

    for i in range(len(token_list)):
        for j in range(n):
            if i + j < len(token_list):
                ngram_list.append(sep.join(token_list[i:i + j + 1]))

    return ngram_list


def count_ignorable_words(text, ignore=constants.QUESTION_STOPWORDS, min_len=2):
    r""" Count the number of words in a space-delimitted string that are not in set(words)

    >>> count_ignorable_words('what a hello world in')
    3
    >>> count_ignorable_words('what a hello world in', ignore=['what'], min_len=1)
    2
    >>> count_ignorable_words('what a hello world in', ignore=['what'], min_len=0)
    1
    """
    return sum(1 for w in text.split() if w in ignore or len(w) <= min_len)


def find_titles(query='What is a chatbot?', max_titles=30, ngrams=5, min_len=2, max_ignorable_pct=.5, ignore=True):
    r""" Search db of wikipedia titles for articles relevant to a statement or questions

    >>> set(find_titles('What is a chatbot?')) == set(TITLES)
    True
    >>> find_titles('What is a ELIZA?')
    ['ELIZA']
    """
    if not query or query.lower().strip().strip('?').strip().endswith('chatbot'):
        return TITLES[:max_titles]
    ignore = constants.QUESTION_STOPWORDS if ignore is True else ignore
    ignore = ignore if ignore is not None and ignore is not False else []
    log.info(f"ignoring {len(ignore)} stopwords")
    toks = list_ngrams(query, n=ngrams)
    ans = []
    for t in toks:
        if count_ignorable_words(t.lower().strip(), ignore=ignore, min_len=min_len) < max_ignorable_pct * len(t.strip().split()):
            ans.append(t)
            if len(ans) >= max_titles:
                return ans
    return ans


def find_titles_sorted(query='What is a chatbot?',
                       max_titles=50, ngrams=5, min_len=2,
                       max_ignorable_pct=.5,
                       ignore=True, reverse=True, score=len):
    r""" Use find_ngrams and ignore stopwords then sort the resulting list of titles with longest first

    >>> find_titles_sorted('What is a ELIZA?', max_titles=30, ngrams=3, min_len=2, ignore=False)
    ['ELIZA', 'What']
    >>> find_titles_sorted('What is a ELIZA?')
    ['ELIZA']
    """
    # TODO Kendra: sort by importance (TFIDF) rather than length of strings
    titles = find_titles(query, max_titles=max_titles, ngrams=ngrams, min_len=min_len, ignore=ignore,
                         max_ignorable_pct=max_ignorable_pct)
    titles = sorted(((score(t), t) for t in titles), reverse=reverse)
    log.debug(f"sorted titles ({ngrams}-grams): \n" + str(pd.DataFrame(titles)))
    return [t for (n, t) in titles]


def find_article_texts(query=None, max_depth=3,
                       max_articles=100, ngrams=5, min_len=2,
                       max_ignorable_pct=.5,
                       ignore=True, reverse=True, score=len,
                       **scrape_kwargs):
    r""" Retrieve Wikipedia article texts relevant to the query text

    >>> texts = list(find_article_texts(''))
    >>> len(texts) > 5
    True
    """
    if isinstance(query, str):
        query = query or "What is a prosocial chatbot, conversational ai, or dialog engine?"
        # TODO Kendra: sort by importance (TFIDF) rather than length of text
        titles = find_titles_sorted(query,
                                    max_titles=max_articles * ngrams * 2, ngrams=ngrams, min_len=min_len,
                                    max_ignorable_pct=max_ignorable_pct,
                                    ignore=True, reverse=reverse, score=score)
    else:
        log.error(f'DEPRECATED: query should be a str, not query={query}')
        titles = list(query)

    return scrape_article_texts(titles, max_depth=max_depth, max_articles=max_articles, **scrape_kwargs)


# def parse_sentences(title, sentences, title_depths, see_also=True, exclude_headings=(), d=0, depth=0, max_depth=3):

#     return sentences, title_depths
