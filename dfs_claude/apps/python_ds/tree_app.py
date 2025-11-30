from flask import Flask, jsonify, send_file, request, render_template
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import inspect

app = Flask(__name__)

# Binary Tree Node class
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

# Global tree root
root = None

# Build tree from list representation
# Example: [1, 2, 3, None, 4, 5, None] represents:
#     1
#    / \
#   2   3
#    \ /
#    4 5
def build_tree_from_list(values):
    if not values or values[0] is None:
        return None

    root = TreeNode(values[0])
    queue = [root]
    i = 1

    while queue and i < len(values):
        node = queue.pop(0)

        # Left child
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1

        # Right child
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1

    return root

# Tree Traversals
def preorder_traversal(node, result=None):
    # Initialize result list on first call
    if result is None:
        result = []

    # Base case: if node is None, return
    if node is None:
        return result

    # Recursive case: Root → Left → Right
    result.append(node.value)              # Visit root first
    preorder_traversal(node.left, result)  # Then left subtree
    preorder_traversal(node.right, result) # Then right subtree
    return result

def inorder_traversal(node, result=None):
    # Initialize result list on first call
    if result is None:
        result = []

    # Base case: if node is None, return
    if node is None:
        return result

    # Recursive case: Left → Root → Right
    inorder_traversal(node.left, result)   # First left subtree
    result.append(node.value)              # Then visit root
    inorder_traversal(node.right, result)  # Then right subtree
    return result

def postorder_traversal(node, result=None):
    # Initialize result list on first call
    if result is None:
        result = []

    # Base case: if node is None, return
    if node is None:
        return result

    # Recursive case: Left → Right → Root
    postorder_traversal(node.left, result)  # First left subtree
    postorder_traversal(node.right, result) # Then right subtree
    result.append(node.value)               # Finally visit root
    return result

def level_order_traversal(node):
    if not node:
        return []

    result = []
    queue = [node]

    while queue:
        current = queue.pop(0)
        result.append(current.value)

        if current.left:
            queue.append(current.left)
        if current.right:
            queue.append(current.right)

    return result

# Tree properties
def tree_height(node):
    if not node:
        return 0
    return 1 + max(tree_height(node.left), tree_height(node.right))

def tree_size(node):
    if not node:
        return 0
    return 1 + tree_size(node.left) + tree_size(node.right)

def is_balanced(node):
    def check_balance(node):
        if not node:
            return 0, True

        left_height, left_balanced = check_balance(node.left)
        right_height, right_balanced = check_balance(node.right)

        balanced = (left_balanced and right_balanced and
                   abs(left_height - right_height) <= 1)

        return 1 + max(left_height, right_height), balanced

    _, balanced = check_balance(node)
    return balanced

# Improved visualization helper with better spacing
def get_tree_positions(node, x=0, y=0, level=1, pos=None):
    if pos is None:
        pos = {}

    if node:
        pos[node.value] = (x, -y)

        # Calculate horizontal offset based on tree height
        # This gives more space at higher levels
        offset = 2.0 ** (tree_height(node) - level - 1)

        if node.left:
            get_tree_positions(node.left, x - offset, y + 1, level + 1, pos)
        if node.right:
            get_tree_positions(node.right, x + offset, y + 1, level + 1, pos)

    return pos

@app.route('/')
def home():
    return render_template('tree_index.html')

@app.route('/api/tree/build', methods=['POST'])
def build_tree():
    global root
    data = request.json
    values_str = data.get('values', '')

    # Parse input: "1,2,3,null,4,5,null" -> [1,2,3,None,4,5,None]
    values = []
    for v in values_str.split(','):
        v = v.strip()
        if v.lower() in ['null', 'none', '']:
            values.append(None)
        else:
            try:
                values.append(int(v))
            except ValueError:
                values.append(v)  # Keep as string if not int

    root = build_tree_from_list(values)
    code = inspect.getsource(build_tree_from_list)

    if root:
        return jsonify({
            'message': f'Tree built successfully with {tree_size(root)} nodes',
            'height': tree_height(root),
            'balanced': is_balanced(root),
            'code': code
        })
    else:
        return jsonify({'message': 'Empty tree created', 'code': code})

@app.route('/api/tree/clear', methods=['POST'])
def clear_tree():
    global root
    root = None
    return jsonify({'message': 'Tree cleared'})

@app.route('/api/tree/info')
def tree_info():
    if not root:
        return jsonify({'error': 'No tree exists'}), 404

    return jsonify({
        'size': tree_size(root),
        'height': tree_height(root),
        'balanced': is_balanced(root),
        'root_value': root.value
    })

@app.route('/api/traversal/preorder')
def run_preorder():
    if not root:
        return jsonify({'error': 'No tree exists'}), 404

    result = preorder_traversal(root)
    code = inspect.getsource(preorder_traversal)

    return jsonify({
        'algorithm': 'Pre-order (Root → Left → Right)',
        'path': result,
        'path_string': ' → '.join(map(str, result)),
        'code': code
    })

@app.route('/api/traversal/inorder')
def run_inorder():
    if not root:
        return jsonify({'error': 'No tree exists'}), 404

    result = inorder_traversal(root)
    code = inspect.getsource(inorder_traversal)

    return jsonify({
        'algorithm': 'In-order (Left → Root → Right)',
        'path': result,
        'path_string': ' → '.join(map(str, result)),
        'code': code
    })

@app.route('/api/traversal/postorder')
def run_postorder():
    if not root:
        return jsonify({'error': 'No tree exists'}), 404

    result = postorder_traversal(root)
    code = inspect.getsource(postorder_traversal)

    return jsonify({
        'algorithm': 'Post-order (Left → Right → Root)',
        'path': result,
        'path_string': ' → '.join(map(str, result)),
        'code': code
    })

@app.route('/api/traversal/levelorder')
def run_levelorder():
    if not root:
        return jsonify({'error': 'No tree exists'}), 404

    result = level_order_traversal(root)
    code = inspect.getsource(level_order_traversal)

    return jsonify({
        'algorithm': 'Level-order (Breadth-First)',
        'path': result,
        'path_string': ' → '.join(map(str, result)),
        'code': code
    })

@app.route('/api/visualize')
@app.route('/api/visualize/<algorithm>')
def visualize(algorithm=None):
    fig, ax = plt.subplots(figsize=(14, 10))

    if not root:
        ax.text(0.5, 0.5, 'No tree data\nBuild a tree to visualize',
                ha='center', va='center', fontsize=16, color='gray',
                transform=ax.transAxes)
        ax.axis('off')
    else:
        # Get node positions
        pos = get_tree_positions(root)

        # Get traversal path if algorithm specified
        if algorithm == 'preorder':
            path = preorder_traversal(root)
            title = f"Pre-order: {' → '.join(map(str, path))}"
        elif algorithm == 'inorder':
            path = inorder_traversal(root)
            title = f"In-order: {' → '.join(map(str, path))}"
        elif algorithm == 'postorder':
            path = postorder_traversal(root)
            title = f"Post-order: {' → '.join(map(str, path))}"
        elif algorithm == 'levelorder':
            path = level_order_traversal(root)
            title = f"Level-order: {' → '.join(map(str, path))}"
        else:
            path = []
            title = "Binary Tree Structure"

        # Draw edges
        def draw_edges(node, pos):
            if node:
                if node.left:
                    x1, y1 = pos[node.value]
                    x2, y2 = pos[node.left.value]
                    ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, zorder=1)
                    draw_edges(node.left, pos)

                if node.right:
                    x1, y1 = pos[node.value]
                    x2, y2 = pos[node.right.value]
                    ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, zorder=1)
                    draw_edges(node.right, pos)

        draw_edges(root, pos)

        # Draw nodes
        def draw_nodes(node, pos, path):
            if node:
                x, y = pos[node.value]

                # Color based on traversal order
                if path:
                    idx = path.index(node.value) if node.value in path else -1
                    if idx == 0:
                        color = 'lightgreen'
                    elif idx == 1:
                        color = 'yellow'
                    elif idx == 2:
                        color = 'orange'
                    elif idx > 2:
                        color = 'lightcoral'
                    else:
                        color = 'lightgray'
                else:
                    color = 'lightblue'

                circle = plt.Circle((x, y), 0.3, color=color, ec='black',
                                   linewidth=2.5, zorder=2)
                ax.add_patch(circle)
                ax.text(x, y, str(node.value), ha='center', va='center',
                       fontsize=16, fontweight='bold', zorder=3)

                draw_nodes(node.left, pos, path)
                draw_nodes(node.right, pos, path)

        draw_nodes(root, pos, path)

        ax.set_aspect('equal')
        ax.axis('off')

        # Add padding around the plot
        x_vals = [p[0] for p in pos.values()]
        y_vals = [p[1] for p in pos.values()]
        x_margin = (max(x_vals) - min(x_vals)) * 0.15 if len(x_vals) > 1 else 1
        y_margin = (max(y_vals) - min(y_vals)) * 0.15 if len(y_vals) > 1 else 1
        ax.set_xlim(min(x_vals) - x_margin - 0.5, max(x_vals) + x_margin + 0.5)
        ax.set_ylim(min(y_vals) - y_margin - 0.5, max(y_vals) + y_margin + 0.5)

        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
