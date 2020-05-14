# -*- coding: utf-8 -*-
"""
Created on Wed May 13 10:48:32 2020

@author: Philip Ciunkiewicz
"""

import numpy as np
import networkx as nx


class Terrain:
    """
    Terrain class for defining RGB pixel values
    associated with various terrain types.
    """    
    OPEN = np.array([1,1,1])
    WALL = np.array([0,0,0])
    START = np.array([0,0,1])
    TARGET = np.array([0,1,0])
    QUARANTINE = np.array([1,0,0])


def random_idx(mask):
    """
    Get random `(x,y)` index tuple from valid points in boolean mask.

    Parameters
    ----------
    mask : ndarray
        Boolean mask in 2 dimensions

    Returns
    -------
    (int, int)
        Tuple of `(x,y)` indices.
    """    
    idx = np.argwhere(mask)
    rand = np.random.randint(0, idx.shape[0] - 1)
    return tuple(idx[rand])


def dist(a, b):
    """
    Euclidian distance metric.

    Parameters
    ----------
    a : (int, int)
        Tuple of coordinates for distance computation.
    b : (int, int)
        Tuple of coordinates for distance computation.

    Returns
    -------
    float
        Euclidian distance between two 2d points.
    """    
    (x1, y1) = a
    (x2, y2) = b
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def create_graph(walls):
    """
    Create networkx graph from boolean mask.

    Parameters
    ----------
    walls : ndarray
        Boolean mask in 2d of invalid points (walls).

    Returns
    -------
    Graph
        networkx graph; edges connected to wall nodes have
        effectively infinite cost associated with them.
    """    
    M, N = walls.shape
    G = nx.grid_2d_graph(M, N)
    
    weights = {}
    for e in G.edges():
        if walls[e[0]] or walls[e[1]]:
            weights[e] = walls.size
        else:
            weights[e] = 1

    nx.set_edge_attributes(G, weights, 'cost')
    
    return G