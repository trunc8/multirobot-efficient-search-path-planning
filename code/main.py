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
  '''
  Inheriting functions from Helper class in helper.py
  '''
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
    target_initial_position = 45
    self.target = Target(self.g,
                         N=self.N,
                         initial_position=target_initial_position,
                         motion="uniform")
    # Single searcher example
    # self.searchers = Searchers(N=self.N, M=1, 
    #                            initial_positions=np.array([90]),
    #                            target_initial_position=target_initial_position)
    # Two searchers example
    self.searchers = Searchers(self.g,
                               N=self.N,
                               M=2,
                               initial_positions=np.array([93,79]),
                               target_initial_position=target_initial_position)

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
    self.m.update()
    self.addMILPConstraints()
    self.setMILPObjective()

    
    self.plan()

    for t in range(self.HORIZON+1):
      self.plot(t)
      self.target.updateTargetPosition()

    print("\n---------------Exiting----------------\n")


  def addMILPVariables(self):
    print("\n>> Adding MILP Variables...\n")

    start_time = time.time()

    ## Adding presence and transition design variables
    self.addTransitionVariables()
    
    ## Defining belief and propagated belief design variables
    self.addBeliefVariables()

    end_time = time.time()

    print(f"\n<< Finished adding MILP Variables in {end_time-start_time:.2f}s\n")


  def addMILPConstraints(self):
    print("\n>> Adding MILP Constraints...\n")
    start_time = time.time()

    ## Adding constraints on presence and transition 
    self.addTransitionConstraints()

    # print(time.time()-start_time)
    
    ## Adding constraints on beliefs
    self.addBeliefConstraints()

    end_time = time.time()
    print(f"\n<< Finished adding MILP Constraints in {end_time-start_time:.2f}s\n")


  def setMILPObjective(self):
    DISCOUNT = 0.8
    discount_series = np.array([DISCOUNT**t for t in range(self.HORIZON+1)])
    # self.beliefs[0,:] --> Capture beliefs over all time instances
    self.m.setObjective(discount_series@self.beliefs[0,:], GRB.MAXIMIZE)


  def plan(self):
    print("\n>> Planning routine started...\n")
    
    start_time = time.time()

    self.m.optimize()
    if self.m.status == GRB.OPTIMAL:
      print("Success!")
      print(f"Objective value: {self.m.objVal:.2f}")
      # print("Capture belief across all time steps:",
      #       [round(b.X[0],2) for b in self.beliefs[0,:]])
      # for t in range(self.HORIZON+1):
        # print(f"Capture at t={t}")
        # print(np.array([b.X[0] for b in self.capture[:,t]]).reshape(10,10))

        # print(f"Belief at t={t}")
        # print(np.array([b.x[0] for b in self.beliefs[1:,t]]).reshape(10,10))
        # print(f"Prop Belief at t={t}")
        # print(np.array([b.x[0] for b in self.prop_beliefs[:,t]]).reshape(10,10))
    else:
      print("Failed to optimize!")

    end_time = time.time()

    print(f"\n<< Finished planning routine in {end_time-start_time:.2f}s\n")


if __name__ == '__main__':
  print("\nWelcome to the Multi-robot Efficient Search Path Planning solver!\n")
  mespp_object = Mespp()
  mespp_object.start()
  print("\nThank you!\n")
