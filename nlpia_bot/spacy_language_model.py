import logging

from .constants import LANG, LANGS

import spacy

log = logging.getLogger(__name__)
nlp = None


def load(lang=None):
    """ Load the specified language model or the small English model, if none specified

    >>> load_spacy_model()  # doctest: +ELLIPSIS
    <spacy.lang.en.English object at ...
    """
    global nlp
    model = None
    log.warn(f"Loading SpaCy model...")
    if lang:
        try:
            model = spacy.load(lang)
        except OSError:
            spacy.cli.download(lang)
            model = spacy.load(lang)
        return model
    for lang in LANGS:
        try:
            model = spacy.load(lang)
            break
        except OSError:
            pass
    if model is None:
        lang = LANG
        spacy.cli.download(lang)
        model = spacy.load(lang)
    log.info(
        f"Finished loading SpaCy model: {model}\n"
        f"    with {model._meta['accuracy']['token_acc']:.2f}% token accuracy\n"
        f"     and {model._meta['accuracy']['ents_f']:.2f}% named entity recognition F1 score.\n"
    )
    if nlp is None:
        nlp = model
    if nlp.lang == 'en':
        if nlp._meta['accuracy']['token_acc'] < model._meta['accuracy']['token_acc']:
            nlp = model
    return model


# FIXME: doesn't inherit from spacy.nlp so needs to be deleted in favor of load() function above
class SpacyLM:
    nlp = None
    lang = None

    def __init__(self, lang=None, eager=False):
        self.lang = lang
        if eager:
            self.nlp = load(self.lang)

    def __call__(self, *args, **kwargs):
        self.lang = kwargs.pop('lang', self.lang)
        if self.nlp is None:
            self.nlp = load(self.lang)
            # self.nlp.on_load()
        return self.nlp(*args)


nlp = load(LANG)
