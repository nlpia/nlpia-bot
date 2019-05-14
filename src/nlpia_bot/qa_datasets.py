""" Question Answering dataset loaders """
import re

import numpy as np
import pandas as pd
import requests


def load_trec_taxonomy(url='http://cogcomp.org/Data/QA/QC/definition.html'):
    dfs = pd.read_html(url)
    df = dfs[3]
    df.columns = 'class description'.split()
    df['class'] = df['class'].str.replace('&nbsp ', '')
    df['class'] = df['class'].str.strip()
    df['description'] = df['description'].str.strip()
    df['subclass'] = [x if x != x.upper() else np.nan for x in df['class']]
    df['class'] = [x if x == x.upper() else np.nan for x in df['class']]
    df['class'] = df['class'].fillna(method='ffill')
    df = df.dropna()
    df = df['class subclass description'.split()]
    df.columns = 'label sublabel description'.split()
    df['label'] = df['label'].astype('category')
    df['sublabel'] = df['sublabel'].astype('category')
    taxonomy = dict(question_types=df)
    for k, u in [('profession', 'http://cogcomp.org/Data/QA/QC/lists/prof'),
                 ('mountain', 'http://cogcomp.org/Data/QA/QC/lists/mount'),
                 ('food', 'http://cogcomp.org/Data/QA/QC/lists/food')]:
        taxonomy[k] = requests.get(u).content.decode('latin').split('\n')

    return taxonomy


def load_trec_trainset(url='http://cogcomp.org/Data/QA/QC/train_5500.label'):
    lines = []
    for i in [5500]:  # [1000, 2000, 3000, 4000, 5500]:
        u = url.replace(str(5500), str(i))
        resp = requests.get(u)
        lines.extend(resp.content.decode('latin').split('\n'))
    r = re.compile(r'\s*([A-Z]+)\s*:\s*([a-z]+)\s*(.*)')
    rows = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            row = r.match(line).groups()
        except AttributeError:
            print(f'PROBLEM on line {i}/{len(lines)}:')
            print(line)
            row = line.split(':')
            row = row[0], ':'.join(row[1:]).split()
            try:
                row = row[0], row[1][0], ' '.join(row[1][1:])
            except IndexError:
                row = row[0], 'unknown', str(row[-1])
                break
        rows.append(row)
    df = pd.DataFrame(rows, columns='label sublabel text'.split())
    df['label'] = df['label'].astype('category')
    df['sublabel'] = df['sublabel'].astype('category')
    return df
