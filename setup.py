#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for qary.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys
from pkg_resources import VersionConflict, require
from setuptools import setup

try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)

# Mapping from package name to a list of relative path names that should be copied into the package.
# The paths are interpreted as relative to the directory containing the package.
package_data = {
    'qary': [
        'qary/data/qary.ini',
        'qary/data/*.json',
        'qary/data/*.csv',
        'qary/data/*.txt',
        'qary/data/eliza_doctor.txt',
        'qary/data/movie_dialog.csv',
        'qary/data/medical_sentences.json',
        'qary/data/faq/glossary-dsdh.yml',
        'qary/data/faq/glossary-business.yml',
        'faq-general-python-data-science-and-machine-learning.yml',
    ]
}

# Each (directory, files) pair in the sequence specifies the installation directory and the files to install there.
# The directory must be a relative path (although this may change in the future, see wheel Issue #92).
# The directory path is relative to the installation prefix (Python’s sys.prefix for a default installation; site.USER_BASE for a user installation).
# Each file name in files is interpreted relative to the setup.py script at the top of the project source distribution.
data_files = [
    ('my_data', ['data/data_file'])
]

if __name__ == "__main__":
    setup(
        use_pyscaffold=True,
        package_data=package_data
    )
    # data_files=data_files)
