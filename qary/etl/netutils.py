""" Transformer based chatbot dialog engine for answering questions """
import logging
import os

import urllib
from tqdm import tqdm

from qary.constants import LARGE_FILES, DATA_DIR


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
    file_meta = LARGE_FILES.get(url_or_name) or {}
    url = url_or_name if not file_meta else file_meta['url']
    dest_path = dest_path or file_meta.get('path')
    if not dest_path:
        file_meta = LARGE_FILES.get(url_or_name, LARGE_FILES.get(url, {}))
        filename = urllib.Path(file_meta.get('filename', dest_path)).name
        dest_path = file_meta.get('path', os.path.join(DATA_DIR, filename))
    filename = file_meta.get('filename', urllib.Path(dest_path).name)

    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=filename) as dpb:
        urllib.request.urlretrieve(url, filename=dest_path, reporthook=dpb.update_to)
    return dest_path
