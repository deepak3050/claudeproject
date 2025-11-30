# Data Structure Visualizers

Two Flask applications for learning data structures:
1. **Tree Visualizer** (RECOMMENDED FOR BEGINNERS) - Simple, hierarchical trees
2. **Graph Visualizer** - Complex graphs with cycles

## 🌳 Tree Visualizer (START HERE!)

**Recommended for beginners!** Trees are simpler and easier to understand.

See [TREE_README.md](TREE_README.md) for full documentation.

### Quick Start:
```bash
python tree_app.py
# Open http://localhost:5001
```

---

## 🕸️ Graph & Tree Algorithms Visualizer

A single-page Flask application for visualizing graph algorithms (DFS, BFS) and tree traversals (Pre-order, Post-order, In-order) with interactive controls.

## 🚀 Quick Start

1. **Navigate to the directory:**
   ```bash
   cd /Users/deepakdas/Github3050/claude/dfs_claude/apps/python_ds
   ```

2. **Start the Flask app:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   ```
   http://localhost:5000
   ```

## ✨ Features

### Single-Page Interface
- **No page navigation** - all updates happen in place
- Add/update graph dynamically
- Run algorithms and see results instantly
- Visualization updates without refresh

### Graph Operations
- **Undirected Graphs**: For DFS and BFS algorithms
- **Directed Trees**: For Pre-order, Post-order, In-order traversals
- **Dynamic Updates**: Add edges via text input
- **Clear All**: Reset graph completely

### Algorithms Supported
1. **DFS** (Depth-First Search) - Graph traversal
2. **BFS** (Breadth-First Search) - Graph traversal
3. **Pre-order** - Tree traversal (Root → Left → Right)
4. **Post-order** - Tree traversal (Left → Right → Root)
5. **In-order** - Tree traversal (Left → Root → Right)

## 📖 How to Use

### 1. Update Graph

Choose graph type:
- **Undirected Graph** - for DFS/BFS
- **Directed Tree** - for Pre/Post/In-order

Enter edges (one per line):
```
A B
A C
B D
C D
D E
```

Click **Update Graph** to replace the entire graph.

### 2. Run Graph Algorithms

1. Enter a start node (e.g., `A`)
2. Click **Run DFS** or **Run BFS**
3. View the traversal path in the result box
4. Graph visualization updates automatically with colored nodes

### 3. Run Tree Traversals

1. Make sure you've created a directed tree first
2. Enter the root node (e.g., `A`)
3. Click **Pre-order**, **Post-order**, or **In-order**
4. View traversal results and visualization

### 4. Refresh View

Click **Refresh View** to reload the current graph visualization.

## 🎨 Color Coding

In visualizations after running algorithms:
- **Light Green**: Start/Root node
- **Yellow**: Nodes 2-3 in traversal
- **Orange**: Nodes 4+ in traversal
- **Light Gray**: Unvisited nodes
- **Light Blue**: Default (no algorithm run)

## 📝 Example Graphs

### Example 1: Simple Graph
```
A B
B C
C D
```

### Example 2: Tree Structure
```
A B
A C
B D
B E
C F
```

### Example 3: Complex Graph
```
A B
A C
A D
B E
C E
D F
E F
```

## 🔧 API Endpoints

All API calls return JSON and don't navigate away from the page:

- `POST /api/graph/update` - Update graph with edges
- `POST /api/graph/clear` - Clear all graphs
- `GET /api/dfs/<node>` - Run DFS from node
- `GET /api/bfs/<node>` - Run BFS from node
- `GET /api/preorder/<node>` - Run pre-order from node
- `GET /api/postorder/<node>` - Run post-order from node
- `GET /api/inorder/<node>` - Run in-order from node
- `GET /api/visualize` - Get current visualization
- `GET /api/visualize/<algorithm>?start=<node>` - Get visualization with algorithm path

## 💡 Tips

1. **Updating clears everything**: When you update the graph, all previous algorithm results are cleared
2. **Try different start nodes**: Run the same algorithm from different nodes to see how paths change
3. **Trees vs Graphs**: Use directed trees for tree traversals, undirected graphs for DFS/BFS
4. **Node names**: Can use any alphanumeric node names (A, B, C or node1, node2, etc.)

## 🐛 Troubleshooting

**"Node not found" error**: Make sure:
- You've updated the graph first
- The node name matches exactly (case-sensitive)
- You're using the right graph type for the algorithm

**Tree traversals not working**:
- Make sure you selected "Directed Tree" when updating
- Verify your edges form a valid tree structure
