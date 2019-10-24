# make sure you `pip install --upgrade git+https://github.com/lucasdnd/Wikipedia.git`
import time
import pandas as pd
import wikipedia

from nlpia_bot.spacy_language_model import nlp

import logging
log = logging.getLogger(locals().get('__name__'))

TITLES = ['Chatbot', 'ELIZA', 'Turing_test', 'AIML', 'Loebniz_prize', 'Chatterbot',
          'Loebner_prize', 'Chinese_room']
EXCLUDE_HEADINGS = ['See also', 'References', 'Bibliography', 'External links']


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
    depths = list([0] * len(titles))
    title_depths = list(zip(titles, depths))
    sentences = []
    # FIXME: breadth-first search so you can do a tqdm progress bar for each depth
    # FIXME: record title tree (see also) so that .2*title1+.3*title2+.5*title3 can be semantically appended to sentences
    titles_scraped = set([''])
    title, d = '', 0
    for depth in range(max_depth):
        for i in range(max_articles):
            try:
                title, d = title_depths.pop()
            except IndexError:
                log.warn(f'Out of titles: {title_depths}')
                break
            if title.strip():
                while title in titles_scraped:
                    log.warn(f"Skipping {title} (already scraped)")
                    try:
                        title, d = title_depths.pop()
                    except IndexError:
                        log.warn(f'Out of titles: {title_depths}')
                        break
            else:
                continue
            if d > max_depth:
                log.info(f"{d} > {max_depth}")
                break
            if not len(title.strip()):
                continue
            titles_scraped.add(title)

            retval = parse_sentences(
                title=title, sentences=sentences, title_depths=title_depths, see_also=see_also,
                exclude_headings=exclude_headings, d=d, depth=depth, max_depth=max_depth)
            if retval is None:
                continue
            else:
                sentences, title_depths = retval
            log.info(str([depth, d, i, title]))
            if d > depth:
                log.info(f"{d} > {depth}")
                break

    return pd.DataFrame(sentences, columns='depth title section sentence'.split())


def parse_sentences(title, sentences, title_depths, see_also=True, exclude_headings=(), d=0, depth=0, max_depth=3):
    try:
        page = wikipedia.WikipediaPage(title)
    except (wikipedia.PageError, KeyError) as e:
        log.error(f"Unable to retrieve {title}")
        log.error(e)
        time.sleep(3)
        return None
    for heading in page.sections:
        if heading in exclude_headings:
            return None
        text = page.section(heading)
        # TODO: use pugnlp.to_ascii() or nlpia.to_ascii()
        text = text.replace('’', "'")  # spacy doesn't handle "latin" (extended ascii) apostrophes well.
        # FIXME: need to rejoin short names before colons, like 'ELIZA:' 'Tell me...', and 'Human:' 'What...'
        # FIXME: need to split on question marks without white space but where next word is capitalized: ...to be unhappy?Though designed strictly...
        sentences.extend([
            (d, title, heading, s.text) for s in nlp(text).sents if (
                len(s.text.strip().strip('"').strip("'").strip()) > 1)
            ])
    if see_also and depth < max_depth:
        title_depths.extend((t, d + 1) for t in (page.section('See also') or '').split('\n'))
        # log.warn(f'title_depths: {title_depths}')
    return sentences, title_depths
