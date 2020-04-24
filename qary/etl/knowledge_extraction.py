""" Functions, regular expressions, and SpaCy patterns for extracting information and knowledge from natural language text """
import re


def whatis(statement):
    """ Extract the target noun phrase phrase for "What is ... " questions.

    >>> whatis("What is a Secretary Bird?")
    'Secretary Bird'
    """
    match = re.match(
        pattern=r"\b(what\s+(is|are)\s*(not|n't)?\s+(a|an|the)?)\s*\b([^\?]*)(\?*)",
        string=statement.strip(),
        flags=re.IGNORECASE)
    extracted_term = match.groups()[-2] if match else ''
    return extracted_term.strip()


def whatmeans(statement):
    """ Extract the target noun phrase for questions like "What does RMSE mean?"

    >>> whatmeans("What does rmse mean?")
    'rmse'
    """
    pattern = (r"\b(what\s+(is|are)\s*(not|n't)?\s+(a|an|the|those|this|that)?)\s*\b"
               r"((meaning|definition|significance|origin|interpretation|translation)[s]*\s*|"
               r"((mean|define|signifie|originate|interpret|translate)[s]*\s*))"
               r"(of|for|to|in|on)?\s*((a|an|the|those|this|that)?[s]*)?\s*"
               r"((tech|technology|science|biology|medicine|health|healthcare|genomic|data[ ]?science|machine[ ]?learning|dl|ml|ds|it|is|ir|nlp)?[es])*\s*"
               r"((phrase|quote|term|terminology|word|token|n[-]?gram?)[es]*)?\s*"
               r"([^\?]*)(\?*)"
               )
    match = re.match(
        pattern=pattern,
        string=statement.strip(),
        flags=re.IGNORECASE)
    extracted_term = match.groups()[-2] if match else ''
    if not extracted_term:
        match = match or re.match(
            pattern=(r"\b(what\s+(does)?\s*(a|an|the)?)\s*"
                     r"([^\?\s]+\s+)+"
                     r"\b(mean|signify|represent|translate|stand)?\s*(for|to|as|in)?\s*(\?*)"),
            string=statement.strip(),
            flags=re.IGNORECASE)
        extracted_term = match.groups()[-4] if match else ''
    return extracted_term.strip()


def count_upper(s):
    return sum(1 for c in s if c.isupper())


def count_lower(s):
    return sum(1 for c in s if c.isupper())


def isacronym(term):
    """ Estimate the probability that a given term is an acronym based only on its capitalization

    >>> isacronym('ABC')
    0.6666...
    >>> isacronym('Cat')
    0.0
    >>> isacronym('Cy')
    0.0
    """
    if re.match(r'\s', term):
        return 0
    return min(max(
        sum(1 if c.isupper() else -1 if c.islower() else -2 for c in term) / len(term) - .6, 0) / .6, 1)
