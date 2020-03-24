from ..constants import DATA_DIR
import os
import logging

import pandas as pd
import numpy as np

from sklearn.cluster import AgglomerativeClustering  # noqa
from sklearn.metrics.pairwise import cosine_similarity
from ..spacy_language_model import load

log = logging.getLogger(locals().get('__name__', ''))

nlp = load('en_core_web_md')

default_vector_file = os.path.join(DATA_DIR, 'wikipedia-title-vectors_sample.csv')


def phrase_to_vec(phrase):
    ''' transform doc to vector via nlp model. Returns [float]
    '''
    vec = nlp(phrase).vector
    vec /= pd.np.linalg.norm(vec) or 1.
    vec = vec.round(7)
    mask_zeros = pd.np.abs(vec) > 0
    if mask_zeros.sum() < len(mask_zeros):
        log.error(f'BAD VEC: {phrase} [0]*{mask_zeros.sum()}')
    return list(vec)


class vector_collection():
    def __init__(self, filename=default_vector_file):
        self.vector_df = pd.read_csv(filename).set_index('index')

    def add_phrase(self, phrase):
        vec = phrase_to_vec(phrase)
        self.vector_df.append(pd.DataFrame(vec, index=[phrase]))

    def brute_find_nearest(self, input_vector):
        sims = cosine_similarity(self.vector_df.values, [input_vector])
        print('similarities\n', sims, sims.shape)
        assert sims.shape == (len(self.vector_df), 1), "Distance calculation error"

        arg = np.argmax(sims)

        nearest = self.vector_df.iloc[arg]
        log.info(f'Match found with cosim of {sims[arg]}.')
        return nearest

#  class vector_cluster(size, factor=10):
#     self.size=size
#     self.factor=factor
#     self.root_vec = [0*size]
#     self.children = []

#     def add_vectors(self, vectors):
#         n = len(vectors[0])
#         n_clusters= n//self.factor
#         labels = AgglomerativeClustering(n_clusters=n_clusters).fit_predict()
