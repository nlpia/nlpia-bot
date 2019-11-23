#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from nlpia_bot.ircbot import ircbot

__author__ = "hobs"
__copyright__ = "hobs"
__license__ = "mit"


def test_ircbot():
    assert callable(ircbot)
