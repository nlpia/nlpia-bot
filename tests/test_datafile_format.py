#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import pytest  # noqa
import yaml
import json

from qary.constants import DATA_DIR

__author__ = "SEE AUTHORS.md"
__copyright__ = "Hobson Lane"
__license__ = "The Hippocratic License, see LICENSE.txt (MIT + Do no Harm)"


def test_yaml_datafiles():
    for path in Path(DATA_DIR).rglob('*.yml'):
        with open(path, 'rt') as fin:
            assert len(yaml.full_load(fin)) >= 0


def test_json_datafiles():
    for path in Path(DATA_DIR).rglob('*.json'):
        with open(path, 'rt') as fin:
            assert len(json.load(fin)) >= 0
