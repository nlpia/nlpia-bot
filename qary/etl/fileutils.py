""" Low level file system utilities that import only `os` and `sys` (no constants.py)

>>> url_filename('http://whatever.com/abs/dir/name/')
'name'
>>> basename('http://example.com/abs/dir/name/')
'name'
>>> basename('http://www.example.com/basename.some.big.tar.gz')
'basename'
"""
import os


def url_filename(url):
    return url.rstrip('/').split('/')[-1]


def basename(filename):
    filename = url_filename(filename)
    ext = True
    while ext:
        base, ext = os.path.splitext(filename)
    return base
