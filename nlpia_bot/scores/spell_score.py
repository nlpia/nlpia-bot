def spell(reply, stmt=None, **kwargs):
    if kwargs is None or kwargs['nlp'] is None:
        return 0.0

    doc = kwargs['nlp'](reply)
    correct_count = sum(
        [(getattr(getattr(token, '_', token), 'hunspell_spell', 0) and not token.is_punct) for token in doc]
    )
    correct_ratio = (correct_count + 1) / (sum([1 if not token.is_punct else 0 for token in doc]) + 1)

    return correct_ratio
