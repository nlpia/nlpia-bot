#!/usr/bin/env bash
# release.sh

# set -e
# pip install -U twine wheel setuptools
git commit -am "$2"
git push
git tag -l | cat
git tag -a "$1" -m "$2"
python setup.py sdist
python setup.py bdist_wheel

if [ -z "$(which twine)" ] ; then
    echo 'Unable to find `twine` so installing it with pip.'
    pip install --upgrade pip
    pip install --upgrade twine
fi

twine check dist/*
twine upload dist/"qary-$1"* --verbose
git push --tag
