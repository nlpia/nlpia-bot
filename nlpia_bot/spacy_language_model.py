import logging

from .constants import LANG

import spacy

log = logging.getLogger(__name__)


def load(lang=None):
    """ Load the specified language model or the small English model, if none specified

    >>> load_spacy_model()  # doctest: +ELLIPSIS
    <spacy.lang.en.English object at ...
    """
    model = None
    log.warn(f"Loading SpaCy model...")
    if lang:
        try:
            model = spacy.load(lang)
        except OSError:
            spacy.cli.download(lang)
            model = spacy.load(lang)
        return model
    for lang in ('en_core_web_sm', 'en_core_web_md', 'en_core_web_lg'):
        try:
            model = spacy.load(lang)
            break
        except OSError:
            pass
    if model is None:
        lang = 'en'
        spacy.cli.download(lang)
        model = spacy.load(lang)
    log.info(
        f"Finished loading SpaCy model: {model}\n"
        f"    with {model._meta['accuracy']['token_acc']:.2f}% token accuracy\n"
        f"     and {model._meta['accuracy']['ents_f']:.2f}% named entity recognition F1 score.\n"
    )
    return model


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


nlp = SpacyLM(LANG)
