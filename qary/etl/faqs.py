import os

from tqdm import tqdm
import yaml

import numpy as np

from ..constants import FAQ_DOMAINS, DATA_DIR
from ..spacy_language_model import nlp, UNKNOWN_WORDVEC

import logging
log = logging.getLogger(locals().get('__name__'))


def load(domains=FAQ_DOMAINS):
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
        qa_list = yaml.load(open(os.path.join(DATA_DIR, 'faq', f'faq-{domain}.yml')))
        for qa_dict in qa_list:
            questions.append(qa_dict.get('Q', qa_dict.get('q', '')))
            answers.append(qa_dict.get('A', qa_dict.get('a', '')))
            try:
                question_vectors.append(list(nlp(questions[-1] or '').vector))
            except TypeError:
                question_vectors.append(list(UNKNOWN_WORDVEC))

    question_vectors = np.array(question_vectors)
    question_vectors /= np.linalg.norm(
        question_vectors, axis=1).reshape(-1, 1).dot(np.ones((1, question_vectors.shape[1])))
    questions = np.array(questions)
    answers = np.array(answers)
    mask = np.array([(bool(a) and bool(q) and len(str(a).strip()) > 0 and len(str(q).strip()) > 0)
                     for a, q in zip(questions, answers)])

    # This should be a Kendra/gensim/annoy class (with methods like .find_similar)
    return dict(
        questions=questions[mask],
        answers=answers[mask],
        question_vectors=np.array([qv for qv, m in zip(question_vectors, mask) if m])
    )
