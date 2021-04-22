#!/usr/bin/env python3
# trunc8 did this

import gurobipy as gp
from gurobipy import GRB

import igraph as ig
import numpy as np

import os, sys
import time

from helper import Helper
from target import Target
from searchers import Searchers


class Mespp(Helper):
  def __init__(self):
    '''
    Initializing all objects and variables
    HORIZON: Time horizon for joint path planning
    N: Number of vertices
    g: Grid graphs for the time being of side length SIDE
    '''
    SIDE = 10
    self.HORIZON = 10
    self.N = SIDE*SIDE
    self.g = ig.Graph.Lattice(dim=[SIDE, SIDE], circular=False)

    # Creating required objects
    self.target = Target(N=self.N)
    self.searchers = Searchers(N=self.N, M=2)
    self.m = gp.Model("planner")

    # Initializing MILP design variables
    self.presence = {}        # "x" variable in the paper
    self.transition = {}      # "y" variable in the paper
    self.legal_V = {}         # "V(s,t)" in the paper (not design variable)

    self.beliefs = None       # "beta" variable in the paper
    self.prop_beliefs = None  # "alpha" variable in the paper
    self.capture = None       # "psi" variable in the paper


  def start(self):
    print("\n---------------MESPP started----------------\n")
    # print(self.has_captured())
    self.addMILPVariables()

    # print(self.m)
    self.m.update()
    # print("\nUpdated\n")
    # print(self.m)
    # Does updating model matter? #

    self.addMILPConstraints()
    self.setMILPObjective()
    self.plan()
    self.plot()
    print("\n---------------Exiting----------------\n")


  def addMILPVariables(self):
    print("\n>> Adding MILP Variables...\n")
    ## Adding presence and transition design variables
    for t in range(self.HORIZON+1):
      '''
      Time instant 0 to HORIZON
      '''
      # Store a list of length of m in legal_V[t]
      self.legal_V[t] = self.g.neighborhood(self.searchers.initial_positions,
                                            order=t)
      # print(self.legal_V)
      self.presence[t] = {}
      self.transition[t] = {}
      
      for s in range(self.searchers.M):
        self.presence[t][s] = {}
        self.transition[t][s] = {}

        for v in self.legal_V[t][s]:
          # x_v^{s,t}
          self.presence[t][s][v] = self.m.addMVar((1,), vtype=GRB.BINARY, 
                                                  name=f'x_{v}^{s},{t}')
        for u in self.legal_V[t][s]:
          self.transition[t][s][u] = {}
          if t < self.HORIZON:
            for v in self.g.neighborhood(u, order=1):
              # y_{uv}^{s,t}
              self.transition[t][s][u][v] = self.m.addMVar((1,), vtype=GRB.BINARY, 
                                                           name=f'y_{u},{v}^{s},{t}')
          elif t == self.HORIZON:
            # y_{uv_g}^{s,tau}
            self.transition[t][s][u] = self.m.addMVar((1,), vtype=GRB.BINARY, 
                                                      name=f'y_{u},vg^{s},tau')
          else:
            print("EXCEPTION. Exiting...")
            sys.exit(0)
    
    ## Defining belief and propagated belief design variables
    
    # Belief starts from t=0 to HORIZON
    # Row is a vertex (or capture belief)
    # Column is a time instant
    self.beliefs = self.m.addMVar((self.N+1, self.HORIZON+1), 
                                  lb=0, ub=1, 
                                  vtype=GRB.CONTINUOUS, 
                                  name='beta')
    # Prop_belief matters from t=1 to HORIZON. First column is pointless
    # but for convenience of indexing
    self.prop_beliefs = self.m.addMVar((self.N, self.HORIZON+1), 
                                       lb=0, ub=1, 
                                       vtype=GRB.CONTINUOUS, 
                                       name='alpha')
    # Similar to prop_belief. First column is only for easier bookkeeping
    self.capture = self.m.addMVar((self.N, self.HORIZON+1), 
                                  vtype=GRB.BINARY, 
                                  name='psi')

    print("\n<< Finished adding MILP Variables\n")

  def addMILPConstraints(self):
    print("\n>> Adding MILP Constraints...\n")
    start_time = time.time()

    ## Adding constraints on presence and transition 
    self.addTransitionConstraints()

    print(time.time()-start_time)
    
    ## Adding constraints on beliefs
    self.addBeliefConstraints()

    end_time = time.time()
    print(f"\n<< Finished adding MILP Constraints in {end_time-start_time}s\n")


  def setMILPObjective(self):
    DISCOUNT = 0.8
    discount_series = np.array([DISCOUNT**t for t in range(self.HORIZON+1)])
    # self.beliefs[0,:] --> Capture beliefs over all time instances
    self.m.setObjective(discount_series@self.beliefs[0,:], GRB.MAXIMIZE)


  def has_captured(self):
    '''
    Same vertex capture for the time being
    i.e. When searcher and target are on the same vertex
    The searcher declares "Captured!"
    '''
    return self.target.position in self.searchers.positions


  def plan(self):
    print("\n>> Planning routine started...\n")
    
    self.m.optimize()
    if self.m.status == GRB.OPTIMAL:
      print("Success!")
      print(f"Objective value: {self.m.objVal}")
      print("Capture belief across all time steps:",[b.x[0] for b in self.beliefs[0,:]])
      # for t in range(self.HORIZON+1):
        # print(f"Capture at t={t}")
        # print(np.array([b.X[0] for b in self.capture[:,t]]).reshape(10,10))

        # print(f"Belief at t={t}")
        # print(np.array([b.x[0] for b in self.beliefs[1:,t]]).reshape(10,10))
        # print(f"Prop Belief at t={t}")
        # print(np.array([b.x[0] for b in self.prop_beliefs[:,t]]).reshape(10,10))
    else:
      print("Failed to optimize!")


  def plot(self):
    visual_style = {}
    visual_style["vertex_size"] = 20
    visual_style["layout"] = self.g.layout("grid")
    visual_style["vertex_label"] = range(self.g.vcount())
    for t in range(self.HORIZON+1):
      self.g.vs["color"]="yellow"
      self.g.vs[self.target.position]["color"]="red"
      # for idx in self.searchers.positions:
      #   self.g.vs[idx]["color"] = "green"
      for idx in range(self.N):
        # print(self.capture[idx,t].X[0])
        if self.capture[idx,t].X[0]:
          self.g.vs[idx]["color"] = "green"      
      ig.plot(self.g,
              target=os.path.join(sys.path[0], f'../results/path_{t}.png'), 
              **visual_style)


if __name__ == '__main__':
  print("\nWelcome to the Multi-robot Efficient Search Path Planning solver!\n")
  mespp_object = Mespp()
  mespp_object.start()
  print("\nThank you!\n")
