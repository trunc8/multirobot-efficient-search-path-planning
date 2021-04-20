#!/usr/bin/env python3
# trunc8 did this

import gurobipy as gp
from gurobipy import GRB

import igraph as ig
import numpy as np

import os, sys

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
    self.plot(index=0)
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

      presence = {}   # x variable in paper
      transition = {} # y variable in paper
      legal_V = {}

      ## Adding presence and transition design variables
      for t in range(0,HORIZON+1):
        legal_V[t] = self.g.neighborhood(self.searchers.initial_positions,
                                        order=t)
        print(legal_V)
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
      # For t>0
      for t in range(1,HORIZON+1):
        for s in range(self.searchers.M):
          m.addConstrs(gp.quicksum(transition[t-1][s][u][v] for u in 
                       # Taking Intersection of the two sets
                       list( set(self.g.neighborhood(v, order=1)) & 
                             set(legal_V[t-1][s]) )
                       )
                       == presence[t][s][v] for v in legal_V[t][s])
          if t is not HORIZON:
            m.addConstrs(gp.quicksum(transition[t][s][u][v] for v in 
                         self.g.neighborhood(u, order=1))
                         == presence[t][s][u] for u in legal_V[t][s])
          else:
            m.addConstrs(transition[t][s][u]
                         == presence[t][s][u] for u in legal_V[t][s])

      ## Defining belief and propogated belief design variables
      # Belief starts from t=0 to HORIZON
      beliefs = m.addMVar((self.N+1,HORIZON+1), lb=0, ub=1, vtype=GRB.CONTINUOUS, name='beta')
      # Prop_belief starts from t=1 to HORIZON. Indexing this would be confusing
      prop_beliefs = m.addMVar((self.N,HORIZON), lb=0, ub=1, vtype=GRB.CONTINUOUS, name='alpha')
      print(beliefs)

      ## Adding constraints
      m.addConstr(beliefs[:,0] == self.searchers.belief)
      for t in range(1,HORIZON+1):
        # m.addConstr(gp.quicksum(self.target.motion_model[u,v]*beliefs[u+1,t-1] for u in range(self.N))
        #              == prop_beliefs[v,t-1] for v in range(self.N))
        m.addConstr(self.target.motion_model@beliefs[1:,t-1] == prop_beliefs[:,t-1])
        # Due to weird indexing, at t=1 above eqn implies
        # motion_model * belief at t=0 == prop_belief at t=1

      ## Adding capture design variables and constraints
      capture = m.addMVar((self.N,HORIZON), vtype=GRB.BINARY, name='psi')
      for t in range(1,HORIZON+1):
        m.addConstr(beliefs[1:,t] <= (np.ones(self.N) - capture[:,t-1]))
        m.addConstr(beliefs[1:,t] <= prop_beliefs[:,t-1])
        m.addConstr(beliefs[1:,t] <= (prop_beliefs[:,t-1] - capture[:,t-1]))

      for t in range(0,HORIZON+1):
        for v in range(self.N):
        # for s in range(self.searchers.M):
          valid_searchers = []
          for s in range(self.searchers.M):
            if v in legal_V[t][s]:
              valid_searchers.append(s)
          ## Getting ERROR!
          print(valid_searchers)
          m.addConstr(sum(presence[t][s][v] for s in 
                     valid_searchers) <= self.searchers.M*capture[v,t-1])



      m.setObjective(discount_series@beliefs[0,:], GRB.MAXIMIZE)
      m.optimize()
      # print(f"Model: {m.display()}")
      print(f"Objective value: {m.objVal}")
      # for v in m.getVars():
      #   print('%s %g' % (v.varName, v.x))

    
  def plot(self, index):
    self.g.vs["color"]="yellow"
    self.g.vs[self.target.position]["color"]="red"
    for idx in self.searchers.positions:
      self.g.vs[idx]["color"] = "green"

    visual_style = {}
    visual_style["vertex_size"] = 20
    visual_style["layout"] = self.g.layout("grid")
    visual_style["vertex_label"] = range(self.g.vcount())
    ig.plot(self.g,
            target=os.path.join(sys.path[0], f'path_{index}.png'), 
            **visual_style)


if __name__ == '__main__':
  print("\nWelcome to the Multi-robot Efficient Search Path Planning solver!\n")
  Mespp().start()