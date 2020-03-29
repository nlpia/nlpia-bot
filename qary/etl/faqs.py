from tqdm import tqdm
import yaml

import numpy as np

from ..constants import DEFAULT_FAQ_DOMAINS
from ..spacy_language_model import nlp

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
    # faq_raw = {}
    # q_vectors = pd.DataFrame()
    questions, answers, question_vectors = [], [], []

    for domain in tqdm(domains):
        qa_list = yaml.load(open(f'faq-{domain}.yml'))
        for qa_dict in qa_list:
            questions.append(qa_dict.get('Q', qa_dict.get('q', '')))
            answers.append(qa_dict.get('A', qa_dict.get('a', '')))
            question_vectors.append(list(nlp(questions[-1]).vector))
    # faq_raw = dict(zip(questions, answers))

    # This should be a Kendra/gensim/annoy class (with methods like .find_similar)
    return dict(
        questions=questions,
        answers=answers,
        question_vectors=np.array(question_vectors)
    )
