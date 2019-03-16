# Initial attempt of getting networkx graph by loading from a shp file, edges were not mapped and took a long time to wrong - > switched to osmnx!

import networkx as nx
import matplotlib.pyplot as plt

G=nx.read_shp('Chicago.shp')

pos = {k: v for k,v in enumerate(G.nodes())}
X=nx.Graph()
X.add_nodes_from(pos.keys()) #Add nodes preserving coordinates
l=[set(x) for x in G.edges()] #To speed things up in case of large objects

edg=[tuple(k for k,v in pos.items() if v in sl) for sl in l]
nx.draw_networkx_nodes(X,pos,node_size=100,node_color='b')
X.add_edges_from(edg)
nx.draw_networkx_edges(X,pos)

