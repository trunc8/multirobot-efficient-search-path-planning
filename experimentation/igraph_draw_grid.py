#!/usr/bin/env python3
# trunc8 did this

from igraph import *
import igraph as ig
import matplotlib.pyplot as plt

g = Graph()
g.add_vertices(3)
g.add_edges([(0,1), (1,2)])
g.add_edges([(2, 0)])
g.add_vertices(3)
g.add_edges([(2, 3), (3, 4), (4, 5), (5, 3)])
g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
print(g)

g = Graph.Lattice(dim=[10, 10], circular=False)
g.vs[0]["color"]="blue"
layout = g.layout("grid")
# g.vs["label"] = g.vs["name"]
visual_style = {}
visual_style["vertex_size"] = 20
visual_style["layout"] = layout
visual_style["vertex_label"] = range(g.vcount())
# visual_style["margin"] = 20
ig.plot(g, **visual_style)

# i=0
# ig.plot(g, target=f'path_{i}.png', **visual_style)


# fig, ax = plt.subplots()
# ig.plot(g, layout=layout, target=ax)
# plt.show()