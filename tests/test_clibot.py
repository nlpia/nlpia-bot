#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest  # noqa

from nlpia_bot.clibot import CLIBot

__author__ = "SEE AUTHORS.md"
__copyright__ = "Hobson Lane"
__license__ = "The Hippocratic License"


def test_clibot():
    clibot = CLIBot()
    assert callable(clibot.reply)
    assert isinstance(clibot.reply('Hi'), str)
