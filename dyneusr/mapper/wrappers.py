""" 
Flexible, sklearn-style wrappers for External Mapper 
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import numpy as np
import pandas as pd

# Machine learning libraries
from sklearn.datasets.base import Bunch
from sklearn.base import BaseEstimator, TransformerMixin, ClusterMixin
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, MDS 
from sklearn.cluster import DBSCAN

###############################################################################
### Optional imports
###############################################################################
# UMAP
try:
    from umap.umap_ import UMAP
except ImportError as e:
    print("[warning]", e)

# HDBSCAN
try:
    from hdbscan import HDBSCAN
except ImportError as e:
    print("[warning]", e)
    

# External mapper tools
try:
    from kmapper import KeplerMapper
    from kmapper.cover import Cover
except ImportError as e:
    print("[warning]", e)


# everything else should be in utils
from .utils import optimize_cover, optimize_dbscan 



###############################################################################
### Base MapperWrapper
###############################################################################
class BaseMapperWrapper(BaseEstimator, TransformerMixin, ClusterMixin):

    def fit(self, data, y=None):
        pass

    def fit_transform(self, data, y=None):
        """ Transform data into lens 
        """
        return self.fit(data).lens_
    
    def fit_map(self, data, y=None):
        """ Fit lens, map data into graph.
        """
        return self.fit(data).graph_


###############################################################################
### External MapperWrappers
###############################################################################
class KMapperWrapper(BaseMapperWrapper):

    def __init__(
            self, 
            projection=PCA(2), scaler=MinMaxScaler(), 
            cover=None, clusterer=None, 
            verbose=1
            ):
        """ Wraps KeplerMapper 

        Usage
        -----
            mapper = KMapperWrapper(projection=PCA(3), cover=dict(r=10, g=2))
            l = mapper.fit(X)
            g = mapper.map(l, X)

            # or 
            g = mapper.fit_map(X)
        """     
        try:
            from kmapper import KeplerMapper
            from kmapper.cover import Cover
        except ImportError as e:
            print("[warning]", e)

        # init mapper
        self.mapper = KeplerMapper()
        self.verbose = verbose

        # [1] fit params
        self.projection = projection
        self.scaler = scaler

        # [2] map params
        self.clusterer = clusterer
        self.cover = cover 

    
    def fit_lens(self, data, projection=None, scaler=None, **kwargs):
        """ Fit a lens over data.
         """
        # init params
        self.mapper = KeplerMapper(verbose=self.verbose-1)
        self.projection = projection or self.projection 
        self.scaler = scaler or self.scaler

         # fit lens
        lens = self.mapper.fit_transform(
            data, 
            projection=self.projection, 
            scaler=self.scaler
            )

        # save variables
        self.data_ = np.copy(data)
        self.lens_ = np.copy(lens)
        return self


    def fit_graph(self, lens, data=None, clusterer=None, cover=None, **kwargs):
        """ Fit a lens over data, map data into graph.
        """
        # init params
        self.mapper = KeplerMapper(verbose=self.verbose)
        self.clusterer = clusterer or self.clusterer or optimize_dbscan(data)
        self.cover = cover or self.cover or optimize_cover(data)
        optimize_cover(data)

        # fit graph
        graph = self.mapper.map(
            lens, X=data,
            clusterer=self.clusterer,
            cover=self.cover
            )

        # save variables
        self.data_ = np.copy(data)
        self.lens_ = np.copy(lens)
        self.graph_ = dict(graph)
        return self


    def fit(self, data, lens=None, **kwargs):
        """ Fit a lens over data, map data into graph.
        """
        # [1] fit lens
        if lens is None:
            self.fit_lens(data, **kwargs)
            lens = self.lens_
     
        # [2] map graph
        self.fit_graph(lens, data, **kwargs)
        return self


###############################################################################
### wrappers as functions
###############################################################################
def fit_kmapper(data, **params):
    mapper = KMapperWrapper(**params)
    return mapper.fit(data, **params)


def run_kmapper(data, **params):
    mapper = KMapperWrapper(**params)
    mapper.fit(data, **params)
    # save as bunch
    result = Bunch(
        data=mapper.data_,
        lens=mapper.lens_,
        graph=mapper.graph_,
        params=params,
        )
    return result


    
   
   