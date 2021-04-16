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
    self.initial_positions = np.array([90])
    self.positions = self.initial_positions.copy()
    self.belief = np.zeros(N+1)
    self.belief[1] = 1

class Mespp:
  def __init__(self):
    '''
    Grid graphs for the time being
    '''
    self.N = 100
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

    DISCOUNT = 1
    HORIZON = 2
    discount_series = np.array([DISCOUNT**t for t in range(HORIZON+1)])

    # To suppress gurobi optimize function's unnecessary output-
    with gp.Env() as env, gp.Model("planner", env=env) as m:
      beliefs = m.addMVar((self.N+1,HORIZON+1), lb=0, ub=1, vtype=GRB.CONTINUOUS)
      print(beliefs)

      presence = {}   # x variable in paper
      transition = {} # y variable in paper
      # del_prime = self.g.neighborhood(self.searchers.initial_positions,
      #                                 order=1)
      legal_V = {}

      ## Adding design variables
      for t in range(0,HORIZON+1):
        legal_V[t] = self.g.neighborhood(self.searchers.initial_positions,
                                        order=t)
        print(legal_V)
        # print(del_prime)
        presence[t] = {}
        transition[t] = {}
        
        for s in range(self.searchers.M):
          presence[t][s] = {}
          transition[t][s] = {}
          for v in legal_V[t][s]:
            presence[t][s][v] = m.addVar(vtype=GRB.BINARY, name=f'x_{v}^{s},{t}')
          for u in legal_V[t][s]:
            transition[t][s][u] = {}
            if t is not HORIZON:
              for v in self.g.neighborhood(u, order=1):
                transition[t][s][u][v] = m.addVar(vtype=GRB.BINARY, name=f'y_{u},{v}^{s},{t}')
            else:
              transition[t][s][u] = m.addVar(vtype=GRB.BINARY, name=f'y_{u},vg^{s},tau')
        # break
      
      ## Adding constraints
      
      for s in range(self.searchers.M):
        # t=0
        m.addConstrs(presence[0][s][v] == 1 for v in legal_V[0][s])
        m.addConstrs(gp.quicksum(transition[0][s][u][v] for v in 
                     self.g.neighborhood(u, order=1)) == 1 for u in 
                     legal_V[0][s])
        # t=tau
        m.addConstr(gp.quicksum(transition[HORIZON][s][u] for u in 
                     legal_V[HORIZON][s]) == 1)
      
      


      m.setObjective(discount_series@beliefs[0,:], GRB.MAXIMIZE)
      m.optimize()
      # print(f"Model: {m.display()}")
      print(f"Objective value: {m.objVal}")
      # for v in m.getVars():
      #   print('%s %g' % (v.varName, v.x))

    

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