""" Add text documents and json data records to ElasticSearch using nboost proxy """
import os
from nlpia_bot import constants  # noqa


def index_dir(path=os.path.expanduser('~')):
    """ Add all text files in subdirectories of `path` to ElasticSearch index

    >>> index_dir(path=constants.DATA_DIR)
    0
    """
    paths = []
    return len(paths)
