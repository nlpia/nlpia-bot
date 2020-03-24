""" Functions, regular expressions, and SpaCy patterns for extracting information and knowledge from natural language text """
import re


def whatis(statement):
    match = re.match(r"\b(what\s+(is|are)\s*(not|n't)?\s+(a|an|the)?)\s*\b([^\?]*)(\?*)", statement.lower())
    extracted_term = match.groups()[-2] if match else ''
    return extracted_term


def count_upper(s):
    return sum(1 for c in s if c.isupper())


def count_lower(s):
    return sum(1 for c in s if c.isupper())


def isacronym(term):
    """ Estimate the probability that a given term is an acronym based only on its capitalization

    >>> isacronym('ABC')
    1.0
    >>> isacronym('Cat')
    0
    >>> isacronym('Cy')
    0
    """
    if re.match(r'\s', term):
        return 0
    return min(max(
        sum(1 if c.isupper() else -1 if c.islower() else -2 for c in term) / len(term) - .6, 0) / .6, 1)
