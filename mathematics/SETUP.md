# Math Mario - BODMAS Adventure 🍄

A Mario-themed mathematical game where you solve math problems to help Mario reach the finish line!

## Features

- 🎮 **Progressive Difficulty**:
  - Levels 1-3: Simple operations (+, -, *, /)
  - Levels 4-6: Two operations with BODMAS rules
  - Levels 7+: Complex BODMAS with parentheses

- 🏆 **Scoring System**: Earn more points on higher levels
- ❤️ **Lives System**: 3 hearts - don't lose them all!
- 🏁 **Level Progression**: Answer 5 questions correctly to advance
- 🎨 **Modern UI**: Beautiful gradients and animations

## Setup Instructions

### Prerequisites

Make sure you have Node.js installed (version 16 or higher recommended).

### Installation

1. **Navigate to the project directory:**
   ```bash
  cd /Users/deepakdas/Github3050/claude/mathematics 
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

### Running the Game

**Start the development server:**
```bash
npm run dev
```

The game will be available at `http://localhost:5173` (Vite's default port)

### Building for Production

**Create a production build:**
```bash
npm run build
```

**Preview the production build:**
```bash
npm run preview
```

## How to Play

1. **Solve Math Problems**: Each level presents you with mathematical questions
2. **Type Your Answer**: Enter your answer in the input field
3. **Submit**: Click "Submit Answer" or press Enter
4. **Progress**: Correct answers move Mario closer to the flag 🏁
5. **Level Up**: Reach the flag to advance to the next level
6. **Survive**: You have 3 lives (hearts) - wrong answers cost you one!

## Game Mechanics

- **Mario Movement**: Each correct answer moves Mario 15% closer to the flag
- **Level Completion**: After 5 correct answers, you reach the flag and level up
- **Scoring**: Points = Level × 10 per correct answer
- **Game Over**: Lose all 3 lives and it's game over!

## Technical Stack

- **React 18**: Modern React with hooks
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Modern Gradients**: Beautiful visual design following modern UI patterns

## Tips

- Remember BODMAS order: Brackets, Orders, Division/Multiplication, Addition/Subtraction
- For decimals, the game accepts answers within 0.01 of the correct value
- Take your time - accuracy is more important than speed!
- Watch out for division problems - they're designed to have clean answers

## Troubleshooting

**Port already in use?**
- Vite will automatically try the next available port
- Or stop the other process using port 5173

**Dependencies not installing?**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Build errors?**
- Make sure you're using Node.js 16 or higher
- Try `npm cache clean --force` then reinstall

## Customization

Want to modify the game? Key files:

- `src/App.jsx`: Main game logic and UI
- `src/index.css`: Global styles
- `tailwind.config.js`: Tailwind customization

Enjoy the game! 🎮✨
