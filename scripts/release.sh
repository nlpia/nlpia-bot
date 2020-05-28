#!/usr/bin/env bash
# release.sh

# pip install -U twine wheel setuptools

git tag -l | cat
git tag -a "$1" -m "$2"
python setup.py sdist
python setup.py bdist_wheel
twine check dist/*
twine uplaod dist/"qary-$1"*
