from flask import Flask, jsonify, send_file, request, render_template
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Initialize graph
G = nx.Graph()
G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'), ('D', 'E')])

# Tree for tree traversals (directed graph)
T = nx.DiGraph()

# DFS implementation
def dfs(graph, start, visited=None):
    if visited is None:
        visited = []
    visited.append(start)
    for neighbor in graph.neighbors(start):
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    return visited

# BFS implementation
def bfs(graph, start):
    visited = []
    queue = [start]
    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.append(node)
            queue.extend([n for n in graph.neighbors(node) if n not in visited])
    return visited

# Tree traversals
def preorder(tree, node, visited=None):
    if visited is None:
        visited = []
    visited.append(node)  # Visit root first
    for child in tree.successors(node):
        preorder(tree, child, visited)
    return visited

def postorder(tree, node, visited=None):
    if visited is None:
        visited = []
    for child in tree.successors(node):
        postorder(tree, child, visited)
    visited.append(node)  # Visit root last
    return visited

def inorder(tree, node, visited=None):
    if visited is None:
        visited = []
    children = list(tree.successors(node))
    if len(children) > 0:
        inorder(tree, children[0], visited)  # Left child
    visited.append(node)  # Visit root
    if len(children) > 1:
        inorder(tree, children[1], visited)  # Right child
    return visited

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/graph/update', methods=['POST'])
def update_graph():
    global G, T
    data = request.json
    edges_text = data.get('edges', '')
    graph_type = data.get('type', 'graph')

    # Parse edges
    edges = []
    for line in edges_text.strip().split('\n'):
        parts = line.strip().split()
        if len(parts) == 2:
            edges.append(tuple(parts))

    if graph_type == 'tree':
        T = nx.DiGraph()
        T.add_edges_from(edges)
        return jsonify({'message': f'Tree updated with {len(edges)} edges', 'type': 'tree'})
    else:
        G = nx.Graph()
        G.add_edges_from(edges)
        return jsonify({'message': f'Graph updated with {len(edges)} edges', 'type': 'graph'})

@app.route('/api/graph/clear', methods=['POST'])
def clear_graph():
    global G, T
    G = nx.Graph()
    T = nx.DiGraph()
    return jsonify({'message': 'All graphs cleared'})

@app.route('/api/dfs/<start_node>')
def run_dfs(start_node):
    if start_node not in G.nodes():
        return jsonify({'error': f'Node {start_node} not found'}), 404
    path = dfs(G, start_node)
    return jsonify({
        'algorithm': 'DFS',
        'start_node': start_node,
        'path': path,
        'path_string': ' → '.join(path)
    })

@app.route('/api/bfs/<start_node>')
def run_bfs(start_node):
    if start_node not in G.nodes():
        return jsonify({'error': f'Node {start_node} not found'}), 404
    path = bfs(G, start_node)
    return jsonify({
        'algorithm': 'BFS',
        'start_node': start_node,
        'path': path,
        'path_string': ' → '.join(path)
    })

@app.route('/api/preorder/<root_node>')
def run_preorder(root_node):
    if root_node not in T.nodes():
        return jsonify({'error': f'Node {root_node} not found in tree'}), 404
    path = preorder(T, root_node)
    return jsonify({
        'algorithm': 'Pre-order',
        'root_node': root_node,
        'path': path,
        'path_string': ' → '.join(path)
    })

@app.route('/api/postorder/<root_node>')
def run_postorder(root_node):
    if root_node not in T.nodes():
        return jsonify({'error': f'Node {root_node} not found in tree'}), 404
    path = postorder(T, root_node)
    return jsonify({
        'algorithm': 'Post-order',
        'root_node': root_node,
        'path': path,
        'path_string': ' → '.join(path)
    })

@app.route('/api/inorder/<root_node>')
def run_inorder(root_node):
    if root_node not in T.nodes():
        return jsonify({'error': f'Node {root_node} not found in tree'}), 404
    path = inorder(T, root_node)
    return jsonify({
        'algorithm': 'In-order',
        'root_node': root_node,
        'path': path,
        'path_string': ' → '.join(path)
    })

@app.route('/api/visualize')
@app.route('/api/visualize/<algorithm>')
def visualize(algorithm=None):
    plt.figure(figsize=(10, 6))

    # Determine which graph to use
    if algorithm in ['preorder', 'postorder', 'inorder']:
        graph = T
        title = "Tree Structure"
    else:
        graph = G
        title = "Graph Structure"

    if graph.number_of_nodes() == 0:
        plt.text(0.5, 0.5, 'No graph data\nAdd edges to visualize',
                ha='center', va='center', fontsize=16, color='gray')
        plt.axis('off')
    else:
        if algorithm and algorithm in ['dfs', 'bfs', 'preorder', 'postorder', 'inorder']:
            start_node = request.args.get('start', list(graph.nodes())[0])

            if algorithm == 'dfs':
                path = dfs(graph, start_node)
                title = f"DFS from {start_node}: {' → '.join(path)}"
            elif algorithm == 'bfs':
                path = bfs(graph, start_node)
                title = f"BFS from {start_node}: {' → '.join(path)}"
            elif algorithm == 'preorder':
                path = preorder(graph, start_node)
                title = f"Pre-order from {start_node}: {' → '.join(path)}"
            elif algorithm == 'postorder':
                path = postorder(graph, start_node)
                title = f"Post-order from {start_node}: {' → '.join(path)}"
            elif algorithm == 'inorder':
                path = inorder(graph, start_node)
                title = f"In-order from {start_node}: {' → '.join(path)}"

            # Color nodes
            node_colors = []
            for node in graph.nodes():
                if node == start_node:
                    node_colors.append('lightgreen')
                elif node in path[1:3]:
                    node_colors.append('yellow')
                elif node in path[3:]:
                    node_colors.append('orange')
                else:
                    node_colors.append('lightgray')
        else:
            node_colors = 'lightblue'

        # Use hierarchical layout for trees
        if isinstance(graph, nx.DiGraph):
            try:
                pos = nx.spring_layout(graph, k=1, iterations=50)
            except:
                pos = nx.spring_layout(graph)
        else:
            pos = nx.spring_layout(graph)

        nx.draw(graph, pos, with_labels=True,
                node_color=node_colors,
                node_size=1500,
                font_size=16,
                font_weight='bold',
                edge_color='gray',
                width=2,
                arrows=isinstance(graph, nx.DiGraph),
                arrowsize=20)
        plt.title(title, fontsize=14, fontweight='bold')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
