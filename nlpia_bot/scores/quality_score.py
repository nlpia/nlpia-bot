import logging
import nltk
import sys
import importlib


from .semantics_score import semantics  # noqa
from .sentiment_score import sentiment  # noqa
from .spell_score import spell  # noqa

from nlpia_bot.constants import passthroughSpaCyPipe
from nlpia_bot import spacy_language_model
from nltk.sentiment.vader import SentimentIntensityAnalyzer

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

try:
    from spacy_hunspell import spaCyHunSpell
except ImportError:
    log.warn('Failed to import spaCyHunSpell. Substituting with fake . . .')
    spaCyHunSpell = passthroughSpaCyPipe


class QualityScore:
    def __init__(self, metrics=['spell', 'sentiment', 'semantics'], weights=None):
        self.metrics = metrics
        self.modules = {metric: importlib.import_module(f'nlpia_bot.scores.{metric}_score') for metric in metrics}
        self.weights = weights if weights is not None else [1.0] * len(metrics)
        self.nlp = spacy_language_model.nlp
        if sys.platform == 'linux' or sys.platform == 'linux2':
            hunspell = spaCyHunSpell(self.nlp, 'linux')
        elif sys.platform == 'darwin':
            hunspell = spaCyHunSpell(self.nlp, 'mac')
        else:  # sys.platform == 'win32':
            try:
                # TODO determine paths for en_US.dic and en_US.aff on windows
                hunspell = spaCyHunSpell(self.nlp, ('en_US.dic', 'en_US.aff'))
            except Exception:
                log.warn('Failed to locate en_US.dic and en_US.aff files. Substituting with fake . . .')
                hunspell = passthroughSpaCyPipe()
        self.nlp.add_pipe(hunspell)
        try:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except LookupError:
            nltk.download('vader_lexicon')
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.kwargs = {'nlp': self.nlp, 'sentiment_analyzer': self.sentiment_analyzer}

    def update_replies(self, replies, stmt=None):
        print(locals())
        metrics_scores = [[reply[0] for reply in replies]]
        for i in range(len(self.metrics)):
            metric = self.metrics[i]
            metrics_scores.append([getattr(self.modules[metric], metric)(reply[1], stmt, self.kwargs) for reply in replies])
            metrics_scores[-1] = [float(score + 1) / (max(metrics_scores[-1]) + 1) * self.weights[i]
                                  for score in metrics_scores[-1]]

        updated_replies = list()
        replies_scores = list(map(list, zip(*metrics_scores)))
        for i, reply in enumerate(replies):
            updated_replies.append(((reply[0] * sum(replies_scores[i])) / (len(self.metrics) + 1), reply[1]))

        return updated_replies
