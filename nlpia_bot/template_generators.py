# template_generators
import re

import numpy as np

from .constants import SENTENCE_SPEC
from .spacy_language_model import nlp


def generate_sentence(spec=SENTENCE_SPEC, sentence_id=None):
    """ Generate random sentence using word probabilities specified in SENTENCE_SPEC

    >>> spec = {
    ...     "answers":[[{"HDL":0.95,"good_cholesterol":0.05}, {"150": 0.01,"145": 0.01,"unk": 0.98}],
    ...     "sentences":["Patient LDL level is 100, ________ level is 50, and the total is ______ .",]
    ...     }
    >>> s = generate_sentence(spec=spec, sentence_id=0)  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    >>> s
    'Patient LDL level is 100, ... level is 50, and the total is ... .'
    >>> s[26:42] in ('HDL level is 50,', 'good_cholesterol')
    True
    >>> s[60:63] in ('150', '145', 'unk')
    True
    """
    sentences = spec['sentences']
    if sentence_id is None:
        sentence_id = np.random.randint(0, len(sentences))
    sentence = sentences[sentence_id]
    answer = spec['answers'][sentence_id]
    i_unk = 0
    tokens = []
    for i, tok in enumerate(nlp(sentence)):
        if re.match(r'^(_+|unk|\[MASK\])$', tok.text):
            possible_tokens, p = list(zip(*answer[i_unk].items()))
            tokens.append(np.random.choice(a=possible_tokens, p=p))
            i_unk += 1
