import networkx as nx
import matplotlib.pyplot as plt

# Same graph as before
G = nx.Graph()
G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'), ('D', 'E')])

# DFS implementation
def dfs(graph, start, visited=None):
    if visited is None:
        visited = []
    
    visited.append(start)
    print(f"Visiting: {start}")
    
    for neighbor in graph.neighbors(start):
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    
    return visited

# Run DFS starting from 'A'
print("DFS Traversal Order:")
path = dfs(G, 'A')
print(f"Final path: {path}")

# Visualize with colors showing the order
plt.figure(figsize=(10, 6))

# Color nodes based on visit order
node_colors = ['lightgreen' if node == 'A' else 
               'yellow' if node in path[1:3] else 
               'orange' if node in path[3:] else 'lightgray' 
               for node in G.nodes()]

nx.draw(G, with_labels=True, 
        node_color=node_colors,
        node_size=1500, 
        font_size=16, 
        font_weight='bold',
        edge_color='gray',
        width=2)
plt.title(f"DFS Path: {' → '.join(path)}")
plt.show()