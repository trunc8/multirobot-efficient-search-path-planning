#!/usr/bin/env python3
# trunc8 did this

import numpy as np

class Searchers:
  def __init__(self, N, M):
    '''
    Single searcher for the time being
    M: Number of searchers
    '''
    self.N = N
    self.M = M
    self.initial_positions = np.array([90,58])
    self.positions = self.initial_positions.copy()
    self.initial_belief = np.zeros(N+1)
    capture_offset = 1 # For less confusion while indexing
    self.initial_belief[7+capture_offset] = 1