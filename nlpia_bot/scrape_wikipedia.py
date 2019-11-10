# make sure you `pip install --upgrade git+https://github.com/lucasdnd/Wikipedia.git`
import time
import pandas as pd
from wikipediaapi import Wikipedia

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


# def parse_sentences(title, sentences, title_depths, see_also=True, exclude_headings=(), d=0, depth=0, max_depth=3):

#     return sentences, title_depths
