# Math Mario - BODMAS Adventure 🍄

A fun, Mario-themed mathematical game where you solve progressively challenging math problems to help Mario reach the finish line!

![Math Game](https://img.shields.io/badge/React-18.3-blue) ![Vite](https://img.shields.io/badge/Vite-6.0-purple) ![Tailwind](https://img.shields.io/badge/Tailwind-3.4-cyan)

## 🎮 Game Features

- **Progressive Difficulty System**
  - **Levels 1-3**: Simple operations (+, -, ×, ÷)
  - **Levels 4-6**: Two operations with BODMAS rules
  - **Levels 7+**: Complex BODMAS with parentheses

- **Engaging Gameplay**
  - Mario character moves with each correct answer
  - 3 lives (hearts) system
  - Score increases with level difficulty
  - Beautiful animations and modern UI

- **Educational Value**
  - Practice arithmetic operations
  - Learn BODMAS/PEMDAS order of operations
  - Progressive difficulty for skill building

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start the development server
npm run dev
```

Visit `http://localhost:5173` to play the game!

## 📖 How to Play

1. **Solve the Math Problem** displayed on screen
2. **Enter Your Answer** in the input field
3. **Press Enter or Click Submit** to check your answer
4. **Watch Mario Move** closer to the flag with each correct answer
5. **Reach the Flag** (5 correct answers) to level up!
6. **Don't Lose All Hearts** - wrong answers cost you a life ❤️

## 🎯 Game Mechanics

- **Movement**: Each correct answer moves Mario 15% toward the flag
- **Scoring**: Points = Level × 10 per correct answer
- **Level Up**: Answer 5 questions correctly to reach the flag
- **Lives**: Start with 3 hearts, lose one per wrong answer
- **Game Over**: Occurs when all lives are lost

## 🛠️ Tech Stack

- **React 18.3** - Modern React with hooks
- **Vite 6.0** - Lightning-fast build tool and dev server
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **Modern Design** - Gradients, glass-morphism, smooth animations

## 📁 Project Structure

```
mathematics/
├── src/
│   ├── App.jsx          # Main game component
│   ├── main.jsx         # React entry point
│   └── index.css        # Global styles with Tailwind
├── index.html           # HTML template
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind configuration
└── README.md           # This file
```

## 🎨 Features Highlights

- **Beautiful UI**: Modern gradients and glass-morphism effects
- **Smooth Animations**: Transitions and hover effects
- **Responsive Design**: Works on different screen sizes
- **Visual Feedback**: Immediate feedback on answers
- **Progress Tracking**: See your level, score, and lives at a glance

## 📚 BODMAS Rules Reminder

**B**rackets → **O**rders → **D**ivision/Multiplication → **A**ddition/Subtraction

The game enforces these rules, so remember to calculate in the correct order!

## 🔧 Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Create production build
npm run preview  # Preview production build
```

## 🐛 Troubleshooting

**Port already in use?**
- Vite will automatically use the next available port
- Default port is 5173

**Dependencies not installing?**
```bash
rm -rf node_modules package-lock.json
npm install
```

## 🎓 Learning Objectives

This game helps practice:
- Basic arithmetic operations
- Order of operations (BODMAS/PEMDAS)
- Mental math skills
- Problem-solving under pressure

## 🤝 Contributing

Feel free to modify the game! Key areas to customize:
- Question generation logic in `src/App.jsx`
- Styling in Tailwind classes
- Difficulty progression
- Scoring system

## 📝 License

This is an educational project - feel free to use and modify as needed!

---

**Enjoy the game and happy calculating!** 🎮✨
