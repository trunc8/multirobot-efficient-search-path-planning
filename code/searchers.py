#!/usr/bin/env python3
# trunc8 did this

import numpy as np

class Searchers:
  def __init__(self, g,
               N=100,
               M=2,
               initial_positions=np.array([90,58]),
               target_initial_position=45):
    '''
    g: Graph of environment
    N: Number of vertices
    M: Number of searchers
    initial_positions: Starting positions of searchers
    '''
    self.N = N
    self.M = M
    self.initial_positions = initial_positions
    self.positions = self.initial_positions.copy()
    self.initial_belief = np.zeros(N+1)
    capture_offset = 1 # For less confusion while indexing
    vertex = target_initial_position+capture_offset
    self.initial_belief[vertex] = 1


  def updatePositions(self):
    pass