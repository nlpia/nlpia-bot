from nlpia_bot.constants import DATA_DIR
import os
import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

import logging
log = logging.getLogger(locals().get('__name__', ''))

from nlpia_bot.spacy_language_model import load
nlp = load('en_core_web_md')

default_vector_file=os.path.join(DATA_DIR, 'wikipedia-title-vectors_sample.csv')

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

class VectorCollection():
    # eventually incorporate features from wiki index
    def __init__(self, filename=default_vector_file):
        #check on setting other= float
        self.vector_df=pd.read_csv(filename, dtype={'index':int}).set_index('index')
    
    def add_phrase(self, phrase):
        vec = phrase_to_vec(phrase)
        self.vector_df.append(pd.DataFrame(vec, index=[phrase]))

    def brute_find_nearest(self, input_vector, n=1):
        # add test for dims
        sims = cosine_similarity(self.vector_df.values, [input_vector]).flatten()
        print('similarities\n', sims, sims.shape)

        sim_pd = pd.Series(sims).sort_values()
        indexes=sim_pd[:n].index.values
        return indexes

'''
In [1]: from nlpia_bot.etl.vectors import phrase_to_vec, VectorCollection

In [2]: vc= VectorCollection()

In [4]: vc.brute_find_nearest([1]*300)
similarities
 [ 0.05691113  0.10072965  0.07687775 ...  0.1001407   0.05286667
 -0.02163353] (10000,)
Out[4]: array([9846])

In [5]: vc.brute_find_nearest([1]*300,5)
similarities
 [ 0.05691113  0.10072965  0.07687775 ...  0.1001407   0.05286667
 -0.02163353] (10000,)
Out[5]: array([9846, 8070, 5492, 2998, 6317])

'''
#  class vector_cluster(size, factor=10):
#     self.size=size
#     self.factor=factor
#     self.root_vec = [0*size]
#     self.children = []
    
#     def add_vectors(self, vectors):
#         n = len(vectors[0])
#         n_clusters= n//self.factor
#         labels = AgglomerativeClustering(n_clusters=n_clusters).fit_predict()
