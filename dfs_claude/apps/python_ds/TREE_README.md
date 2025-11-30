# 🌳 Binary Tree Visualizer

A beginner-friendly Flask application for learning binary tree data structures and traversals. Simpler than graphs - focuses on hierarchical tree structures!

## 🚀 Quick Start

1. **Navigate to the directory:**
   ```bash
   cd /Users/deepakdas/Github3050/claude/dfs_claude/apps/python_ds
   ```

2. **Start the Tree app:**
   ```bash
   python tree_app.py
   ```

3. **Open in browser:**
   ```
   http://localhost:5001
   ```

   ⚠️ **Note:** Tree app runs on port **5001** (Graph app uses 5000)

## ✨ Why Trees Are Simpler Than Graphs

### Trees vs Graphs:
- **Trees**: Hierarchical, no cycles, one parent per node (except root)
- **Graphs**: Can have cycles, multiple connections, more complex

### Learning Path:
1. Start with Trees 🌳 ← You are here!
2. Then learn Graphs 🕸️

## 📖 How to Build a Tree

### Input Format:
Enter values **level-order** (left to right, top to bottom), separated by commas.

Use `null` or `none` for empty positions.

### Examples:

#### Example 1: Simple Tree
```
Input: 1,2,3

Tree:
    1
   / \
  2   3
```

#### Example 2: Balanced Binary Tree
```
Input: 1,2,3,4,5,6,7

Tree:
      1
     / \
    2   3
   / \ / \
  4  5 6  7
```

#### Example 3: Tree with Gaps
```
Input: 1,2,3,null,4,5,null

Tree:
    1
   / \
  2   3
   \ /
   4 5
```

#### Example 4: Left-Skewed Tree
```
Input: 1,2,null,3,null,null,null

Tree:
  1
 /
2
/
3
```

#### Example 5: Right-Skewed Tree
```
Input: 1,null,2,null,null,null,3

Tree:
1
 \
  2
   \
    3
```

## 🔄 Tree Traversals Explained

### 1. Pre-order (Root → Left → Right)
- Visit the **root first**
- Then traverse left subtree
- Finally traverse right subtree

**When to use:**
- Copying a tree
- Getting prefix notation
- Creating a copy of the tree structure

**Example:**
```
Tree:     1
         / \
        2   3
Result: 1 → 2 → 3
```

### 2. In-order (Left → Root → Right)
- Traverse left subtree first
- Visit the **root in middle**
- Then traverse right subtree

**When to use:**
- Getting sorted values from BST (Binary Search Tree)
- Expression evaluation

**Example:**
```
Tree:     2
         / \
        1   3
Result: 1 → 2 → 3  (sorted!)
```

### 3. Post-order (Left → Right → Root)
- Traverse left subtree first
- Then right subtree
- Visit the **root last**

**When to use:**
- Deleting a tree
- Getting postfix notation
- Calculating directory sizes

**Example:**
```
Tree:     3
         / \
        1   2
Result: 1 → 2 → 3
```

### 4. Level-order (BFS - Breadth-First)
- Visit nodes **level by level**
- Left to right on each level

**When to use:**
- Finding shortest path
- Level-by-level processing
- Breadth-First Search

**Example:**
```
Tree:     1
         / \
        2   3
       / \
      4   5
Result: 1 → 2 → 3 → 4 → 5
```

## 🎨 Color Coding

After running a traversal:
- **Light Green**: 1st node visited
- **Yellow**: 2nd node visited
- **Orange**: 3rd node visited
- **Light Coral**: 4th+ nodes visited
- **Light Blue**: Default (no traversal)

## 🎓 Learning Exercises

### Exercise 1: Identify Traversal Type
Given tree:
```
    1
   / \
  2   3
 / \
4   5
```

Which traversal gives: `4, 2, 5, 1, 3`?
<details>
<summary>Answer</summary>
In-order! (Left → Root → Right)
</details>

### Exercise 2: Build Balanced Tree
Build a balanced tree with values 1-7.
<details>
<summary>Answer</summary>
Input: <code>4,2,6,1,3,5,7</code>
</details>

### Exercise 3: Find the Pattern
Tree: `1,2,3,4,5,6,7`

Try all 4 traversals and compare!

## 📊 Tree Properties

The app shows:
- **Size**: Total number of nodes
- **Height**: Longest path from root to leaf
- **Balanced**: Whether the tree is balanced (height difference ≤ 1)

### Example:
```
Tree:     1
         / \
        2   3
       /
      4

Size: 4 nodes
Height: 3 levels
Balanced: No (left height=2, right height=1)
```

## 🎯 Common Tree Patterns to Try

### Pattern 1: Complete Binary Tree
```
1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
```
All levels fully filled

### Pattern 2: Binary Search Tree (BST)
```
5,3,7,2,4,6,8
```
Left < Root < Right

### Pattern 3: Single Path
```
1,2,null,3,null,null,null,4
```
Like a linked list

## 💡 Tips for Beginners

1. **Start Simple**: Try `1,2,3` first
2. **Add Complexity Gradually**: Then `1,2,3,4,5,6,7`
3. **Understand Null**: Use `null` to skip positions
4. **Compare Traversals**: Run all 4 on the same tree
5. **Watch the Colors**: See which nodes are visited in order

## 🐛 Common Mistakes

❌ **Wrong:** `1 2 3` (using spaces)
✅ **Right:** `1,2,3` (using commas)

❌ **Wrong:** `1,2,3,,5` (double comma for null)
✅ **Right:** `1,2,3,null,5`

❌ **Wrong:** Mixed types without considering structure
✅ **Right:** Sequential level-order filling

## 🔧 API Endpoints

- `POST /api/tree/build` - Build tree from values
- `POST /api/tree/clear` - Clear the tree
- `GET /api/tree/info` - Get tree properties
- `GET /api/traversal/preorder` - Pre-order traversal
- `GET /api/traversal/inorder` - In-order traversal
- `GET /api/traversal/postorder` - Post-order traversal
- `GET /api/traversal/levelorder` - Level-order traversal
- `GET /api/visualize` - Get tree visualization
- `GET /api/visualize/<algorithm>` - Get visualization with traversal

## 🎮 Try These Challenges

1. Build a tree with height 4
2. Create a perfectly balanced tree with 15 nodes
3. Build a tree where pre-order = post-order (reversed)
4. Create a BST and verify in-order gives sorted output

## 🆚 Graph App vs Tree App

| Feature | Tree App (Port 5001) | Graph App (Port 5000) |
|---------|---------------------|----------------------|
| Structure | Hierarchical, simple | Complex, cycles allowed |
| Input | Comma-separated values | Edge pairs |
| Best for | Learning basics | Advanced algorithms |
| Difficulty | ⭐⭐ Beginner | ⭐⭐⭐⭐ Advanced |

## 🚀 Next Steps

After mastering trees:
1. Try Binary Search Trees (BST)
2. Learn AVL Trees (self-balancing)
3. Move to Graphs (more complex)
4. Explore Graph algorithms (DFS, BFS on graphs)

---

**Start here, master trees, then conquer graphs! 🌟**
