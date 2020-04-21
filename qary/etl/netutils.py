""" Transformer based chatbot dialog engine for answering questions """
import logging

from tqdm import tqdm

log = logging.getLogger(__name__)


class DownloadProgressBar(tqdm):
    """ Utility class that adds tqdm progress bar to urllib.request.urlretrieve """

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)
