#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest  # noqa

from nlpia_bot.spacy_language_model import nlp

__author__ = "SEE AUTHORS.md"
__copyright__ = "Hobson Lane"
__license__ = "The Hippocratic License"


def test_spacy_language_model():
    assert callable(nlp)
    assert len(list(nlp("Hello world!"))) == 3
