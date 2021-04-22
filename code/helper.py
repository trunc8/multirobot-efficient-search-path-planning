#!/usr/bin/env python3
# trunc8 did this

import numpy as np

class Helper:
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
          # print(f"{t}: {v}: {valid_searchers}")
          # print(self.capture[v,t])
          # print(np.array(sum(self.presence[t][s][v] for s in valid_searchers)))
          # print(self.presence[t][valid_searchers[0]][v])

          # s = valid_searchers[0]
          # x_constr = self.presence[t][s][v]
          # self.m.addConstr(np.ones(1)*x_constr <= self.searchers.M*self.capture[v,t])

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