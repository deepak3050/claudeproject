# Sliding Window Adventure Game

An interactive HTML game to teach kids how the sliding window technique works!

## How to Run

### Option 1: Double-click (Easiest)
1. Navigate to this folder
2. Double-click `index.html`
3. The game opens in your default browser

### Option 2: Terminal
```bash
cd /Users/deepakdas/Github3050/claude/dfs_claude/sliding_window_game
open index.html
```

### Option 3: Python Server (if double-click doesn't work)
```bash
cd /Users/deepakdas/Github3050/claude/dfs_claude/sliding_window_game
python -m http.server 8000
```
Then open: http://localhost:8000

## Game Modes

### 🎯 Fixed Window
- **Concept**: Find max sum of K consecutive elements
- **Story**: Collect the most coins from 3 boxes!
- **Learn**: How to slide a fixed-size window efficiently

### 🔄 Variable Window
- **Concept**: Find minimum subarray with sum ≥ target
- **Story**: Find the smallest bag to hold treasures!
- **Learn**: Two-pointer expand/contract technique

### ✨ Unique Characters
- **Concept**: Longest substring without repeating characters
- **Story**: Collect the longest chain of unique gems!
- **Learn**: HashMap + sliding window

### 👑 Window Maximum
- **Concept**: Find maximum in each sliding window
- **Story**: Find the king in each group!
- **Learn**: Monotonic deque technique

## Controls

- **Next ➡️**: Move to next step
- **⬅️ Back**: Go to previous step
- **🔄 Reset**: Start over
- **▶️ Auto**: Auto-play animation
- **Speed slider**: Adjust animation speed

## Color Guide

- 🟨 **Yellow**: Current window
- 🟩 **Teal/Green**: Best result found
- ⬜ **Gray**: Outside window
- 🟥 **Red**: Current maximum (in Window Max game)

## Learning Tips

1. Start with **Fixed Window** - it's the simplest
2. Watch the numbers change as the window slides
3. Pay attention to how we **reuse** previous calculations
4. Try to predict the next step before clicking!

Enjoy learning! 🎮
