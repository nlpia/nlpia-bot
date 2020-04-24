# TODO: add doc strings?
import logging
import nltk
import importlib
import sys

from nltk.sentiment.vader import SentimentIntensityAnalyzer

from .. import constants
from .. import spacy_language_model

sys.path.append(constants.BASE_DIR)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class QualityScore:
    def __init__(self, **kwargs):
        self.metrics = [metric_name for metric_name in kwargs.keys() if kwargs[metric_name]]
        self.weights = list(kwargs.values())
        self.modules = {metric: importlib.import_module(f'qary.scores.{metric}_score') for metric in self.metrics}
        self.nlp = spacy_language_model.nlp
        try:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except LookupError:
            nltk.download('vader_lexicon')
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.kwargs = {'nlp': self.nlp, 'sentiment_analyzer': self.sentiment_analyzer}

    def update_replies(self, replies, stmt=None):
        log.debug(replies)
        metrics_scores = [[reply[0] for reply in replies]]
        for i in range(len(self.metrics)):
            metric = self.metrics[i]
            metrics_scores.append([getattr(self.modules[metric], metric)(
                reply[1], stmt=stmt, **self.kwargs) for reply in replies])
            metrics_scores[-1] = [float(score + 1) / (max(metrics_scores[-1]) + 1) * self.weights[i]
                                  for score in metrics_scores[-1]]

        updated_replies = list()
        replies_scores = list(map(list, zip(*metrics_scores)))
        for i, reply in enumerate(replies):
            updated_replies.append(((reply[0] * sum(replies_scores[i])) / (len(self.metrics) + 1), reply[1]))

        return updated_replies
