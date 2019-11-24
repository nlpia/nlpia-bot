#!/usr/bin/env bash
conda env create -n nlpia-bot -f environment.yml
conda install hunspell
pip install -e .
