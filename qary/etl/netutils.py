""" Transformer based chatbot dialog engine for answering questions """
import logging

import urllib
from tqdm import tqdm

from qary.constants import LARGE_FILES


log = logging.getLogger(__name__)


class DownloadProgressBar(tqdm):
    """ Utility class that adds tqdm progress bar to urllib.request.urlretrieve """

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_if_necessary(
        url_or_name,
        dest_path=None):
    url = LARGE_FILES.get(url_or_name, url_or_name)
    filename = url.split('/')[-1]
    if dest_path is None:
        dest_path = LARGE_FILES.get(url_or_name,
            LARGE_FILES.get(url, os.path.join(DATA_DIR, filename))

    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=filename) as dpb:
        urllib.request.urlretrieve(url, filename=dest_path, reporthook=dpb.update_to)
    return dest_path
