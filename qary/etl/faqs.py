import os
from pathlib import Path

from tqdm import tqdm
import yaml
from yaml.scanner import ScannerError

import numpy as np

from qary.constants import FAQ_DOMAINS, DATA_DIR
from qary.spacy_language_model import nlp, UNKNOWN_WORDVEC


import logging
log = logging.getLogger(locals().get('__name__'))


def normalize_docvectors(docvectors):
    """ Convert a table (2D matrix) of row-vectors into a table of normalized row-vectors

    >>> vecs = normalize_docvectors([[1, 2, 3], [4, 5, 6], [0, 0, 0], [-1, 0, +2]])
    >>> vecs.shape
    (4, 3)
    >>> np.linalg.norm(vecs, axis=1).round()
    array([1., 1., 0., 1.])
    """
    docvectors = np.array(docvectors)
    log.info(f'docvectors.shape: {docvectors.shape}')
    norms = np.linalg.norm(docvectors, axis=1)
    iszero = norms <= 0
    log.info(f'norms.shape: {norms.shape}')
    norms_reshaped = norms.reshape(-1, 1).dot(np.ones((1, docvectors.shape[1])))
    log.info(f'norms_reshaped.shape: {norms_reshaped.shape}')
    if np.any(iszero):
        log.warning(
            f'Some doc vectors are zero like this first one: docvectors[{iszero},:] = {docvectors[iszero,:]}')
    norms_reshaped[iszero, :] = 1
    normalized_docvectors = docvectors / norms_reshaped
    log.info(f'normalized_docvectors.shape: {normalized_docvectors.shape}')
    assert normalized_docvectors.shape == docvectors.shape
    return normalized_docvectors


def load(domains=FAQ_DOMAINS):
    """ Load yaml file, use hashtags to create context tags as multihot columns

    Load faq*.yml into dictionary: question: answer

    >>> g = load()
    >>> len(g['questions']) == len(g['answers']) > 30
    True
    """
    questions, answers, question_vectors = [], [], []

    faqdirpath = os.path.join(DATA_DIR, 'faq')
    for domain in tqdm(domains):
        for filepath in Path(faqdirpath).glob(f'faq*{domain}*.yml'):
            # filename = filepath.name
            try:
                filepointer = open(filepath)
            except FileNotFoundError as e:
                log.error(f"{e}\n    Unable to find the file path object: {filepath}")
                continue
            with filepointer:
                log.info(f"loading: {filepath.name}\n    with file pointer: {filepointer}")
                try:
                    qa_list = yaml.safe_load(filepointer)
                except ScannerError as e:
                    log.error(f"{e}\n    yaml.load unable to read {filepointer.name}")
                    continue
            for qa_dict in qa_list:
                questions.append(qa_dict.get('Q', qa_dict.get('q', '')))
                answers.append(qa_dict.get('A', qa_dict.get('a', '')))
                try:
                    question_vectors.append(list(nlp(questions[-1] or '').vector))
                except TypeError:
                    question_vectors.append(list(UNKNOWN_WORDVEC))
                    continue
                assert len(UNKNOWN_WORDVEC) == len(question_vectors[-1])

    log.debug(f'len(question_vectors): {len(question_vectors)}')

    questions = np.array(questions)
    log.debug(f'len(questions): {len(questions)}')
    answers = np.array(answers)
    log.debug(f'len(answers): {len(answers)}')
    mask = np.array([(bool(a) and bool(q) and len(str(a).strip()) > 0 and len(str(q).strip()) > 0)
                     for a, q in zip(questions, answers)])

    question_vectors = normalize_docvectors(question_vectors)

    # This should be a Kendra/gensim/annoy class (with methods like .find_similar)
    return dict(
        questions=questions[mask],
        answers=answers[mask],
        question_vectors=np.array([qv for qv, m in zip(question_vectors, mask) if m])
    )
