# test_doctests
import pytest  # noqa
import doctest

import qary.clibot

import qary.skills.basebots
import qary.skills.eliza_bots
import qary.skills.glossary_bots
import qary.skills.qa_bots
import qary.skills.faq_bots

import qary.etl.glossaries
import qary.etl.scrape_wikipedia
import qary.etl.yml
import qary.etl.faqs
import qary.etl.elastic
import qary.etl.knowledge_extraction
import qary.etl.qa_datasets

import qary.scores.semantics_score
# import qary.template_generators


__author__ = "SEE AUTHORS.md"
__copyright__ = "Hobson Lane"
__license__ = "The Hippocratic License, see LICENSE.txt (MIT + Do no Harm)"

DOCTEST_KWARGS = dict(
    optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
    verbose=True)


################################################
# etl/*

def test_etl_glossaries():
    results = doctest.testmod(qary.etl.glossaries, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted > 4


def test_etl_qa_datasets():
    results = doctest.testmod(qary.etl.qa_datasets, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted > 0


def test_etl_scrape_wikipedia():
    results = doctest.testmod(qary.etl.scrape_wikipedia, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted > 2


def test_etl_faqs():
    results = doctest.testmod(qary.etl.faqs, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted > 0


def test_etl_elastic():
    results = doctest.testmod(qary.etl.elastic, **DOCTEST_KWARGS)
    assert results.failed == 0
    assert results.attempted >= 0


def test_etl_knowledge_extraction():
    results = doctest.testmod(qary.etl.knowledge_extraction, **DOCTEST_KWARGS)
    assert results.failed == 0
    assert results.attempted >= 0

# etl/*
################################################


########################################
# skills/*_bots


def test_basebots():
    results = doctest.testmod(qary.skills.basebots, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted > 0


def test_eliza_bots():
    results = doctest.testmod(qary.skills.eliza_bots, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted > 0


def test_faq_bots():
    results = doctest.testmod(qary.skills.faq_bots, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted > 0


def test_qa_bots():
    results = doctest.testmod(qary.skills.qa_bots, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted > 0

# def test_yml():
#     results = doctest.testmod(qary.etl.yml, optionflags=doctest.ELLIPSIS |
#                               doctest.NORMALIZE_WHITESPACE, verbose=True)
#     assert results.failed < 1
#     assert results.attempted > 2


# def test_template_generators():
#     results = doctest.testmod(qary.template_generators, **DOCTEST_KWARGS)
#     assert results.failed < 1
#     assert results.attempted >= 1


def test_glossary_bots():
    results = doctest.testmod(qary.skills.glossary_bots, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted > 2

# skills/*_bots
########################################


def test_semantics_score():
    results = doctest.testmod(qary.scores.semantics_score, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted >= 1


def test_clibot():
    results = doctest.testmod(qary.clibot, **DOCTEST_KWARGS)
    assert results.failed < 1
    assert results.attempted > 0
