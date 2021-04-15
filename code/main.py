#!/usr/bin/env python3
# trunc8 did this

import gurobipy as gp
from gurobipy import GRB

import igraph as ig
import numpy as np


class Target:
  def __init__(self):
    N = 100
    self.position = 0
    self.motion_model = np.eye(N) # Not being used yet

class Searchers:
  def __init__(self):
    N = 100
    self.M = 1
    self.positions = [90]
    self.belief = np.zeros(N+1)
    self.belief[1] = 1

class Mespp:
  def __init__(self):
    N = 100
    self.g = ig.Graph.Lattice(dim=[10, 10], circular=False)
    self.target = Target()
    self.searchers = Searchers()

  def start(self):
    print(self.has_captured())
    self.plot()

  def has_captured(self):
    # Same vertex capture for the time being
    return self.target.position in self.searchers.positions

  def plot(self):
    self.g.vs["color"]="yellow"
    self.g.vs[self.target.position]["color"]="red"
    for idx in self.searchers.positions:
      self.g.vs[idx]["color"] = "green"

    visual_style = {}
    visual_style["vertex_size"] = 20
    visual_style["layout"] = self.g.layout("grid")
    visual_style["vertex_label"] = range(self.g.vcount())
    ig.plot(self.g, **visual_style)


if __name__ == '__main__':
  print("Welcome to the Multi-robot Efficient Search Path Planning solver!")
  Mespp().start()