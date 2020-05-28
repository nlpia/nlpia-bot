#!/usr/bin/env bash
# release.sh

# pip install -U twine wheel setuptools

git commit -am "$2"
git tag -l | cat
git tag -a "$1" -m "$2"
git push --tag
python setup.py sdist
python setup.py bdist_wheel
twine check dist/*
twine upload dist/"qary-$1"*
