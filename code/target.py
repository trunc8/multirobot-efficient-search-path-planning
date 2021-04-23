#!/usr/bin/env python3
# trunc8 did this

import numpy as np
import random

class Target:
  def __init__(self, g, N=100, initial_position=45, motion="uniform"):
    '''
    g: Graph of environment
    N: Number of vertices
    initial_positions: Starting position of target
    motion: Motion model of target
    '''
    self.N = N
    self.initial_position = initial_position
    self.position = self.initial_position
    self.g = g
    self.motion_model = np.zeros((N,N))
    if motion == "stationary":
      # Stationary motion model
      self.motion_model = np.eye(N)
    elif motion == "uniform":
      # Uniform probability in all directions
      neighbourhood_list = g.neighborhood(np.arange(N),
                                          order=1)
      for v in range(N):
        neighbours = neighbourhood_list[v]
        self.motion_model[v,neighbours] = 1./len(neighbours)
    else:
      print("Exception! Motion model not recognized, assuming stationary")
      self.motion_model = np.eye(N)

  def updateTargetPosition(self):
    '''
    Target moves to any vertex in the neighborhood based on motion model
    '''
    neighborhood = self.g.neighborhood(self.position,
                                       order=1)
    self.position = random.choice(neighborhood)
