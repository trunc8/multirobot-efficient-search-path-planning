# Multi-robot Efficient Search Path Planning
Implementation of [MILP Models for Multi-Robot Non-Adversarial Search](https://arxiv.org/abs/2011.12480) paper

*Important Note: The entire project has been built from scratch with [references](references.md) duly credited. No code from the [author's implementation](https://github.com/basfora/milp_mespp) was borrowed or used.*

You can find my blog post [here](https://trunc8.github.io/2021/04/01/pr-mespp)

The references used while coding this project are listed [here](references.md)

### Demo
![t=7](results/double-searchers-moving-target/path_t=7.png)  
Searchers(green) and target(red) just before capture

![t=8](results/double-searchers-moving-target/path_t=8.png)  
Capture event(pink)


### How to Run
1. [Obtain Gurobi license](https://www.gurobi.com/downloads/end-user-license-agreement-academic/). There is a free academic license which is sufficient for our needs.
1. [Install Gurobi(for Linux)](http://abelsiqueira.github.io/blog/installing-gurobi-7-on-linux/)
1. `git clone https://github.com/trunc8/multirobot-efficient-search-path-planning.git`
1. `cd multirobot-efficient-search-path-planning`
1. `pip install -r requirements.txt`
1. `python3 code/main.py`

You can find the results in the `results` directory

### Author(s)

* **Siddharth Saha** - [trunc8](https://github.com/trunc8)

<p align='center'>Created with :heart: by <a href="https://www.linkedin.com/in/sahasiddharth611/">Siddharth</a></p>
