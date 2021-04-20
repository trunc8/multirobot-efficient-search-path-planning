# References
### igraph debugging
Node labels in igraph-
https://stackoverflow.com/questions/37793254/python-igraph-infomap-node-labels-on-graph
Plotting as grid graph and saving-
https://igraph.org/python/doc/tutorial/visualisation.html
Generating lattice graph-
https://igraph.org/python/doc/tutorial/generation.html
Lots of stuff from here-
https://igraph.org/python/doc/tutorial/tutorial.html
Multi-dimensional numpy decision variable-
https://www.gurobi.com/documentation/9.1/refman/py_model_addmvar.html
Suppress gurobi optimizer output-
https://support.gurobi.com/hc/en-us/articles/360044784552-How-do-I-suppress-all-console-output-from-Gurobi-
Finding neigborhood-
https://igraph.org/python/doc/tutorial/analysis.html#vertices-and-edges

### gurobi
Understanding MIP-
https://www.gurobi.com/resource/mip-basics/


# Steps
1. Obtain Gurobi license
2. Install Gurobi (http://abelsiqueira.github.io/blog/installing-gurobi-7-on-linux/)

# Referred the repo for
- Input output
- Motion model


# Algorithm design decisions

### Networkx vs iGraph
https://www.reddit.com/r/Python/comments/4g9lp0/opinions_on_igraph_vs_netwrokx_in_python/d2i0r45?utm_source=share&utm_medium=web2x&context=3

    Use NetworkX for smaller networks and dynamic networks. NetworkX is pure Python, well documented and handles changes to the network gracefully.  
    iGraph is more performant in terms of speed and ram usage but less flexible for dynamic networks. iGraph is a C library with very smart indexing and storage approaches so you can load pretty large graphs in ram. The index needs to be updated whenever the graph changes, so dynamic graphs incur a lot of overhead.

Therefore, iGraph is best suited for our purpose


# Additional comments
1. Linear programming (LP) is in P and integer programming (IP) is NP-hard.