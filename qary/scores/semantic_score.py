import logging

from qary import spacy_language_model

log = logging.getLogger(__name__)
nlp = spacy_language_model.nlp

try:
    assert nlp._meta['vectors']['width'] == 300  # len(nlp('word vector').vector) < 300:
except AssertionError:
    log.warning(f"SpaCy Language model ({nlp._meta['name']}) doesn't contain 300D word2vec word vectors.")
    nlp = spacy_language_model.nlp = spacy_language_model.load('en_core_web_md')
assert nlp._meta['vectors']['width'] == 300


def iou(a, b):
    """ Crude character vector overlap measure of string similarity

    >>> iou('Hello', 'World')
    0.285...
    """
    a, b = set(a.lower().strip()), set(b.lower().strip())
    return len(a & b) / len(a | b)


def rouge1():
    raise NotImplementedError()


def rouge2():
    raise NotImplementedError()


def bleu():
    raise NotImplementedError()


def score(reply, stmt=None, **kwargs):
    """ Compute word2vec docvec cosine similarity (fall back to character IOU)

    >>> semantics('Hello world!', 'Goodbye big earth!') > .5
    True
    """
    global nlp
    nlp = kwargs.get('nlp', nlp)
    if kwargs is None or nlp is None or not stmt or not reply:
        return 0.0

    reply_doc, stmt_doc = nlp(str(reply)), nlp(str(stmt))

    if not reply_doc or not stmt_doc or not reply_doc.has_vector or not stmt_doc.has_vector:
        # FIXME: levenshtien would be better or fuzzywuzzy
        return iou(reply, stmt)

    cos_sim = reply_doc.similarity(stmt_doc)
    log.debug(f'cos_sim={cos_sim}')
    return cos_sim


class Doc:
    global nlp

    def __init__(self, text='', nlp=nlp):
        """ Create a Doc object with an API similar to spacy.Doc

        >>> d = Doc('Hello').vector
        >>> len(d)
        300
        >>> d.doc.similarity(d.doc) > .99
        True
        """
        self.nlp = nlp if nlp is not None else self.nlp
        self.text = text
        self.doc = nlp(text)
        self.vector = self.doc.vector

    def similarity(self, other_doc):
        """ Similarity of self Doc object meaning to the meaning of another Doc object

        >>> doc = Doc('USA')
        >>> doc.similarity(Doc('United States'))
        0.5...
        """
        if hasattr(other_doc, 'vector_norm'):
            return self.doc.similarity(other_doc)
        else:
            return self.doc.similarity(getattr(other_doc, 'doc', other_doc))


def similarity(text1, text2):
    """ Similarity between two natural language texts (words, phrases, documents) 1 = 100%, -1 = -100%

    >>> similarity('Hello', 'hello') > 0.99
    True
    >>> .8 > similarity('Hello!', 'Hi?') > 0.75
    True
    """
    return Doc(text1).similarity(Doc(text2).doc)

    # log.debug(f"vector1 for text1 {vector1}")
    # question_vector /= np.linalg.norm(question_vector)
    # log.debug(f"faq['question_vectors'].shape is {self.faq['question_vectors'].shape}")
    # question_similarities = self.faq['question_vectors'].dot(question_vector.reshape(-1, 1))
