#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest  # noqa

from qary.spacy_language_model import nlp

__author__ = "See AUTHORS.md"
__copyright__ = "Hobson Lane"
__license__ = "The Hippocratic License (MIT + *Do No Harm*, see LICENSE.txt)"


def test_spacy_language_model():
    assert callable(nlp)
    assert len(list(nlp("Hello world!"))) == 3
