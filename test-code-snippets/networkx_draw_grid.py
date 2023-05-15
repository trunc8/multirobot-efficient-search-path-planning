#!/usr/bin/env python3
# trunc8 did this

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

L=10

G = nx.grid_2d_graph(L,L)
nx.draw(G,node_size=20)
plt.show()