import logging

from ..spacy_language_model import nlp  # noqa

log = logging.getLogger(__name__)


def iou(a, b):
    """ Crude character vector overlap measure of string similarity

    >>> iou('Hello', 'World')
    0.285...
    """
    a, b = set(a.lower().strip()), set(b.lower().strip())
    return len(a & b) / len(a | b)


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
