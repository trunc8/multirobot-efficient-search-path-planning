#!/usr/bin/env python3
# trunc8 did this

import numpy as np

class Target:
  def __init__(self, N):
    self.N = N
    self.position = 7
    self.motion_model = np.eye(N) # Not being used yet