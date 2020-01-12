import sys
import logging

import spacy

from nlpia_bot.constants import LANG, LANGS, passthroughSpaCyPipe


log = logging.getLogger(__name__)
nlp = None

try:
    from spacy_hunspell import spaCyHunSpell
except ImportError:
    log.warning('Failed to import spaCyHunSpell. Substituting with fake . . .')
    spaCyHunSpell = passthroughSpaCyPipe


def add_hunspell_pipe(model):
    if sys.platform == 'linux' or sys.platform == 'linux2':
        hunspell = spaCyHunSpell(model, 'linux')
    elif sys.platform == 'darwin':
        hunspell = spaCyHunSpell(model, 'mac')
    else:  # sys.platform == 'win32':
        try:
            # TODO determine paths for en_US.dic and en_US.aff on windows
            hunspell = spaCyHunSpell(model, ('en_US.dic', 'en_US.aff'))
        except Exception:
            log.warning('Failed to locate en_US.dic and en_US.aff files. Substituting with fake . . .')
            hunspell = passthroughSpaCyPipe()
    model.add_pipe(hunspell)
    return model


def load(lang=LANG):
    """ Load the specified language model or the small English model, if none specified

    >>> load_spacy_model()  # doctest: +ELLIPSIS
    <spacy.lang.en.English object at ...
    """
    global nlp
    model = None
    log.warning(f"Loading SpaCy model...")
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
    model = add_hunspell_pipe(model)
    if nlp is None:
        nlp = model
    # load the highest accuracy model into the global singleton nlp variable (user can still override)
    if nlp.lang == 'en':
        if nlp._meta['accuracy']['token_acc'] < model._meta['accuracy']['token_acc']:
            nlp = model
    return model  # return value may be lower accuracy, so `nlp=load('en_web_core_sm')` will have lower accuracy `nlp`


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
