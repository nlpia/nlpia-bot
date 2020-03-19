from tqdm import tqdm
import yaml


from ..constants import DEFAULT_FAQ_DOMAINS

import logging
log = logging.getLogger(locals().get('__name__'))


def load(domains=DEFAULT_FAQ_DOMAINS):
    """ Load yaml file, use hashtags to create context tags as multihot columns

    Load faq*.yml into dictionary: question: answer

    >>> g = load(domains='dsdh'.split(','))
    >>> len(g['raw']) <= len(g['cleaned']) > 30
    True
    >>> sorted(g['cleaned']['Allele'])
    ['acronym', 'definition', 'hashtags', 'parenthetical']
    """
    faq_raw = {}
    for domain in tqdm(domains):
        faq_raw.update(yaml.load(open(f'faq-{domain}.yml')))
        pass
        #     glossary_raw.update(yaml.load(open(os.path.join(DATA_DIR, 'faq', f'glossary-{domain}.yml'))))
        # glossary = {}
        # for term_raw, definition_raw in glossary_raw.items():
        #     match = re.match(r'(?P<term>[^(]*)\s*(\((?P<parenthetical>[^)]*)\))?\s*$', term_raw)
        #     gd = match.groupdict()
        #     term = (gd['term'] or '').strip()
        #     paren = (gd['parenthetical'] or '').strip()
        #     # term_acros = possible_acronyms(term)
        #     # paren_acros = possible_acronyms(paren)
        #     acro = ''
        #     if len(paren) >= len(term) * 1.2:
        #         if term in paren_acros:
        #             term, acro, paren = paren, term, None
        #     elif len(paren) < len(term):
        #         if paren in term_acros or ((len(paren) > 1) and paren == paren.upper()):
        #             term, acro, paren = term, paren, None
        #     hashtag_dict = find_hashtags(definition_raw)
        #     if not term:
        #         continue
        #     # term_entry = glossary_entry(glossary, term)
        #     glossary[term_entry] = {
        #         'definition': hashtag_dict['cleaned'],
        #         'hashtags': hashtag_dict['hashtags']}
        #     glossary[term_entry]['acronym'] = acro
        #     glossary[term_entry]['parenthetical'] = paren
        #     if acro:
        #         acro_entry = glossary_entry(glossary, acro)
        #         glossary[acro_entry] = {
        #             'definition': term_entry,
        #             'hashtags': hashtag_dict['hashtags'],
        #             'acronym': acro_entry
        #         }
        #         # glossary[term_entry]['acronym'] = ''
        #     glossary[term_entry]['parenthetical'] = paren

    # return {'raw': glossary_raw, 'cleaned': glossary}
    #     if match:
    #         acronyms.append(match.groups())
    #     else:
    #         acronyms.append((None, None))
    # acronyms = pd.DataFrame(acronyms, columns='acronym acronym_expanded'.split())
    # cleaned_hashtags = [find_hashtags(s) for s in df['definition']]
    # cleaned_hashtags = pd.DataFrame(cleaned_hashtags)
    # return pd.concat([acronyms, df, cleaned_hashtags], axis=1)


# def parse_sentences(title, sentences, title_depths, see_also=True, exclude_headings=(), d=0, depth=0, max_depth=3):

#     return sentences, title_depths
