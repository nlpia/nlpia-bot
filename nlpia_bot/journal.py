import os
import logging

from tqdm import tqdm
import numpy as np
import pandas as pd
import spacy

from constants import nlp
from nlpia.futil import find_files

log = logging.getLogger(__name__)

# from spacy.matcher import Matcher
nlp = spacy.load('en_core_web_md') if nlp is None else nlp


def get_files(path, size_limit=100000, excludes=['.DS_Store']):
    allfiles = find_files(path)
    df = pd.DataFrame(allfiles)
    df['accessed'] = pd.to_datetime(df.accessed)
    df['modified'] = pd.to_datetime(df.modified)
    df['changed_any'] = pd.to_datetime(df['changed_any'])
    df['ext'] = df.name.apply(lambda s: os.path.splitext(s)[1])
    df['basename'] = df.name.apply(lambda s: os.path.splitext(s)[0])
    df.index = list(range(len(df)))
    df.index.name = 'file_id'
    return df


def is_journal(df, extensions='txt rst md text'.split() + [''], size_limit=100000, excludes=['.DS_Store']):
    extensions = [extensions] if isinstance(extensions, str) else extensions
    extensions = [ext.lower().lstrip('.') for ext in extensions]
    mask = pd.Series([False] * len(df), index=df.index)
    for ext in extensions:
        mask = mask | (df['ext'].str.lower().str.lstrip('.') == ext)
    for excl in excludes:
        mask = mask & (df['name'].str.strip() != excl)
    if size_limit:
        mask = mask & (df['size'] <= size_limit)

    return mask


def get_sentences(df, size_limit=50000, vector_dim=None):
    vector_dim = len(nlp('word').vector) if vector_dim is None else int(vector_dim)
    sents = []
    docvecs = np.zeros((len(df), vector_dim))
    encodings = []
    for file_id, row in tqdm(df.iterrows(), total=len(df)):
        sentvecs = []
        encodings.append('utf8')
        if row['size'] <= size_limit and row['is_journal']:
            try:
                with open(row['path'], 'rb') as fin:
                    bintext = fin.read()
                try:
                    text = bintext.decode()
                except UnicodeDecodeError:
                    encodings[-1] = 'latin'
                    log.warning(f"LATIN?: {row['path']}")
                    text = bintext.decode('latin')
                doc = nlp(text)
            except UnicodeDecodeError:
                log.error(f"UnicodeDecodeError: {row['path']}")
                continue
            docvecs[file_id, :] = np.array(list(doc.vector))
            docsents = [dict(sentence_pos=f'{file_id}-{j}', file_id=file_id, text=s.text) for j, s in enumerate(doc.sents)]
            log.info(f"Read {len(docsents)} sentences: {row['path']}")
            # print(doc.vector)
            sents.extend(docsents)
            sentvecs.extend([s.vector for s in doc.sents])
        else:
            log.warn(f"skipped {row['path']}")

    df['encoding'] = encodings
    df = pd.concat([df, pd.DataFrame(np.array(docvecs))], axis=1)
    df_sents = pd.DataFrame(sents, index=list(range(len(sents))))
    df_sents = pd.concat([df_sents, pd.DataFrame(np.array(sentvecs))], axis=1)
    df_sents.index.name = 'sentence_id'
    return df, df_sents


if __name__ == '__main__':
    df = get_files('~/Dropbox/notes/journal')
    df['is_journal'] = is_journal(df)
    df, df_sents = get_sentences(df)
    df.to_csv('files.csv')
    df_sents.to_csv('sentences.csv')
