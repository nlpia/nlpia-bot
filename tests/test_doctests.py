# test_doctests
import pytest  # noqa
import doctest

import nlpia_bot.skills.eliza_bots
import nlpia_bot.clibot
import nlpia_bot.etl.glossaries
import nlpia_bot.skills.glossary_bots


__author__ = "SEE AUTHORS.md"
__copyright__ = "Hobson Lane"
__license__ = "The Hippocratic License, see LICENSE.txt (MIT + Do no Harm)"


def test_eliza_bots():
    results = doctest.testmod(nlpia_bot.skills.eliza_bots, optionflags=doctest.ELLIPSIS |
                              doctest.NORMALIZE_WHITESPACE, verbose=True)
    assert results.failed < 1
    assert results.attempted > 0


def test_clibot():
    results = doctest.testmod(nlpia_bot.clibot, optionflags=doctest.ELLIPSIS |
                              doctest.NORMALIZE_WHITESPACE, verbose=True)
    assert results.failed < 1
    assert results.attempted > 0


def test_glossaries():
    results = doctest.testmod(nlpia_bot.etl.glossaries, optionflags=doctest.ELLIPSIS |
                              doctest.NORMALIZE_WHITESPACE, verbose=True)
    assert results.failed < 1
    assert results.attempted > 5


def test_glossary_bots():
    results = doctest.testmod(nlpia_bot.skills.glossary_bots, optionflags=doctest.ELLIPSIS |
                              doctest.NORMALIZE_WHITESPACE, verbose=True)
    assert results.failed < 1
    assert results.attempted > 2
