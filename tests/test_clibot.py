#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest  # noqa

from qary.clibot import CLIBot

__author__ = "SEE AUTHORS.md"
__copyright__ = "Hobson Lane"
__license__ = "The Hippocratic License, see LICENSE.txt (MIT + Do no Harm)"


def test_clibot():
    clibot = CLIBot()
    assert callable(clibot.reply)
    assert isinstance(clibot.reply('Hi'), str)
