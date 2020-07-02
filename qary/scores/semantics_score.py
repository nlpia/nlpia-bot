import logging

from qary import spacy_language_model

log = logging.getLogger(__name__)
nlp = spacy_language_model.nlp
if nlp._meta['vectors']['width'] < 300:  # len(nlp('word vector').vector) < 300:
    log.warning(f"SpaCy Language model ({nlp._meta['name']}) doesn't contain 300D word2vec word vectors.")
    nlp = spacy_language_model.nlp = spacy_language_model.load('en_core_web_md')


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


def semantics(reply, stmt=None, **kwargs):
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
        self.nlp = nlp if nlp is not None else self.nlp
        self.text = text
        self.doc = nlp(text)
        self.vector = self.doc.vector

    def similarity(self, other_doc):
        return self.doc.similarity(other_doc)


def semantic_similarity(text1, text2):
    """ Similarity between two natural language texts (words, phrases, documents) 1 = 100%, -1 = -100%

    >>> semantic_similarity('Hello', 'hello') > 0.99
    True
    >>> .8 > semantic_similarity('Hello!', 'Hi?') > 0.75
    True
    """
    return Doc(text1).similarity(Doc(text2).doc)

    # log.debug(f"vector1 for text1 {vector1}")
    # question_vector /= np.linalg.norm(question_vector)
    # log.debug(f"faq['question_vectors'].shape is {self.faq['question_vectors'].shape}")
    # question_similarities = self.faq['question_vectors'].dot(question_vector.reshape(-1, 1))
