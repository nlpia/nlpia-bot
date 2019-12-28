from nlpia_bot.spacy_language_model import nlp  # noqa


def semantics(reply, stmt=None, **kwargs):
    global nlp
    nlp = kwargs.get('nlp', nlp)
    if kwargs is None or kwargs['nlp'] is None or not stmt:
        return 0.0

    cos_sim = nlp(reply).similarity(nlp(stmt))

    return cos_sim
