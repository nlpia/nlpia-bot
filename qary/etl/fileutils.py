""" Low level file system utilities that import only `os` and `sys` (no constants.py)

FIXME: Use builtin pathlib.Path and URL classes

>>> url_filename('http://whatever.com/abs/dir/name/')
'name'
>>> path_filename('/whatever.com/abs/dir/name/')
'name'
>>> path_filename('/whatever.com/abs/dir/name.txt')
'name.txt'
>>> basename('http://example.com/abs/dir/name/')
'name'
>>> basename('http://www.example.com/basename.some.big.tar.gz')
'basename'
"""
import os
from pathlib import Path


def url_filename(url):
    """ Extract filename.ext from a url ([protocol] [fqdn] path)

    >>> url_filename('http://whatever.com/abs/dir/name/')
    'name'
    >>> url_filename('whatever.com/abs/dir/name.txt')
    'name.txt'
    """
    return Path(url).name


def path_filename(url):
    """ Extract filename.ext from a path

    >>> path_filename('/whatever.com/abs/dir/name/')
    'name'
    >>> path_filename('/whatever.com/abs/dir/name.txt')
    'name.txt'
    """
    return url_filename(url)


def basename(filename):
    """ Extract filename from a protocol://fqdn/path/filename.ext

    >>> basename('basename.some.big.tar.gz')
    'basename'
    >>> basename('http://www.example.com/basename.some.big.tar.gz')
    'basename'
    >>> basename('http://example.com/abs/dir/name/')
    'name'
    """
    filename = str(url_filename(filename))
    for i in range(256):
        filename, ext = os.path.splitext(filename)
        if not ext or not filename:
            return filename
    return filename
