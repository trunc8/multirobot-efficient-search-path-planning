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
    '''
    Single searcher for the time being
    '''
    N = 100
    self.M = 1
    self.positions = [90]
    self.belief = np.zeros(N+1)
    self.belief[1] = 1

class Mespp:
  def __init__(self):
    '''
    Grid graphs for the time being
    '''
    N = 100
    self.g = ig.Graph.Lattice(dim=[10, 10], circular=False)
    self.target = Target()
    self.searchers = Searchers()

  def start(self):
    # print(self.has_captured())
    # self.plot()
    self.plan()

  def has_captured(self):
    '''
    Same vertex capture for the time being
    i.e. When searcher and target are on the same vertex
    The searcher declares "Captured!"
    '''
    return self.target.position in self.searchers.positions

  def plan(self):
    print("Planning routine in progress...")

    N = 100
    DISCOUNT = 1
    HORIZON = 12
    discount_series = np.array([DISCOUNT**t for t in range(HORIZON+1)])

    # To suppress gurobi optimize function's unnecessary output-
    with gp.Env() as env, gp.Model("planner", env=env) as m:
      beliefs = m.addMVar((N+1,HORIZON+1), lb=0, ub=1, vtype=GRB.CONTINUOUS)
      m.setObjective(discount_series@beliefs[0,:], GRB.MAXIMIZE)
      m.optimize()
      print(f"Objective value: {m.objVal}")

    

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
  print("\nWelcome to the Multi-robot Efficient Search Path Planning solver!\n")
  Mespp().start()