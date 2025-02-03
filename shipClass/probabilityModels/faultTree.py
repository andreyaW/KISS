# desired input : [1,(2,3),(4,5,6),7]

# notional system from the paper (Patel 2022)

# USING NETWORKX
# Top Level Failure : Node 1
# System A : Node 2 
# System B : Node 3
# ---------------------
    # Comp A : Node 4
    # Comp B : Node 5
    # Comp C : Node 6
    # Comp D : Node 7
    # Comp E : Node 8
    # Comp F : Node 9

# ---------------------
#system A : (AND gate) Comp A, Comp B
#system B : (OR gate) Comp C, Comp D, Comp E
#system C : (AND gate) system A, system B, Comp F

import networkx as nx
import matplotlib.pyplot as plt

# Create a directed graph for the fault tree
G = nx.DiGraph()

# Add nodes (events) to the graph
# G.add_node("Top Event")
# G.add_node("System A")
# G.add_node("System B")
# G.add_node("Component F")

# G.add_node("Component A")
# G.add_node("Component B")
# G.add_node("Component C")
# G.add_node("Component D")
# G.add_node("Component E")

# Add edges (relationships) between nodes
G.add_edge("System A", "Top Event")
G.add_edge("System B", "Top Event")
G.add_edge("Component F", "Top Event")

G.add_edge("Component A", "System A")
G.add_edge("Component B", "System A")

G.add_edge("Component C", "System B")
G.add_edge("Component D", "System B")
G.add_edge("Component E", "System B")

# Draw the fault tree
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10)
plt.show()