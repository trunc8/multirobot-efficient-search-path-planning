#!/usr/bin/env python3
# trunc8 did this

from gurobipy import GRB
import igraph as ig
import numpy as np
import os, sys


class Helper:
  def addTransitionVariables(self):
    '''
    Adding presence and transition design variables
    '''
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


  def addBeliefVariables(self):
    '''
    Defining belief and propagated belief design variables
    '''
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


  def addTransitionConstraints(self):
    '''
    Adding constraints on presence and transition
    '''
    for s in range(self.searchers.M):
      # At t=0,
      # self.legal_V[0][s] will be a single element
      # Neighborhood at 0 distance will be the starting position itself
      v_0 = (self.legal_V[0][s])[0]
      self.m.addConstr(self.presence[0][s][v_0] == 1)
      self.m.addConstr(sum(self.transition[0][s][v_0][j] for j in 
                                   self.g.neighborhood(v_0, order=1)) == 1)
      # At t=tau, searcher must enter v_g from wherever it is possibly present
      self.m.addConstr(sum(self.transition[self.HORIZON][s][j] for j in 
                                   self.legal_V[self.HORIZON][s]) == 1)
    
    # For 0<t<tau, combining constraints 2 and 3 (refer blog)
    for t in range(1,self.HORIZON+1):
      for s in range(self.searchers.M):
        self.m.addConstrs(sum(self.transition[t-1][s][j][v] for j in 
                                      list( set(self.g.neighborhood(v, order=1)) & 
                                            set(self.legal_V[t-1][s]) )
                                      # An Intersection of the two sets
                                      )
            == self.presence[t][s][v] for v in self.legal_V[t][s])

        if t < self.HORIZON:
          self.m.addConstrs(sum(self.transition[t][s][v][i] for i in 
                       self.g.neighborhood(v, order=1))
              == self.presence[t][s][v] for v in self.legal_V[t][s])
        
        elif t == self.HORIZON:
          self.m.addConstrs(self.transition[t][s][v]
              == self.presence[t][s][v] for v in self.legal_V[t][s])

        else:
          print("EXCEPTION! Exiting")
          sys.exit(0)


  def addBeliefConstraints(self):
    '''
    Adding constraints on beliefs
    '''
    # Initializing the entire belief at t=0
    self.m.addConstr(self.beliefs[:,0] == self.searchers.initial_belief)
    for t in range(1, self.HORIZON+1):
      # Don't constrain capture belief
      self.m.addConstr(self.beliefs[1:, t-1]@self.target.motion_model
          == self.prop_beliefs[:,t])
      
      self.m.addConstr(self.beliefs[1:,t] 
          <= (np.ones(self.N) - self.capture[:,t]))
      
      self.m.addConstr(self.beliefs[1:,t] 
          <= self.prop_beliefs[:,t])
      
      self.m.addConstr(self.beliefs[1:,t] 
          >= (self.prop_beliefs[:,t] - self.capture[:,t]))
    
    for t in range(self.HORIZON+1):
      for v in range(self.N):
        valid_searchers = [s for s in range(self.searchers.M) 
                           if v in self.legal_V[t][s]]
        if valid_searchers:
          self.m.addConstr(sum(self.presence[t][s][v] for s in valid_searchers)
              <= self.searchers.M*self.capture[v,t])
          
          self.m.addConstr(self.capture[v,t]
              <= sum(self.presence[t][s][v] for s in valid_searchers))
        else:
          self.m.addConstr(self.capture[v,t] == 0)
    
    # print(self.beliefs[0,:])
    # print(np.ones(self.N)@self.beliefs[1:,0])
    # print(self.beliefs[1:,0])
    self.m.addConstrs((self.beliefs[0,t]
        == (1 - np.ones(self.N)@self.beliefs[1:,t]))
        for t in range(self.HORIZON+1))


  def has_captured(self):
    '''
    Same vertex capture for the time being
    i.e. When searcher and target are on the same vertex
    The searcher declares "Captured!"
    '''
    return self.target.position in self.searchers.positions


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
