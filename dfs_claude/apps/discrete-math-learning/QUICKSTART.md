# Quick Start Guide

## 🚀 Three Ways to Run the Application

### Method 1: Automatic Start Script (Easiest)

```bash
cd discrete-math-learning
./start.sh
```

The script will automatically:
- Check if Docker is running
- Build and start the container if Docker is available
- Fall back to Python HTTP server if Docker is not available

### Method 2: Docker Compose (Recommended)

```bash
cd discrete-math-learning

# Start the application
docker-compose up -d

# View in browser
open http://localhost:8080

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Method 3: Simple Python Server (No Docker Required)

```bash
cd discrete-math-learning/src

# Python 3
python3 -m http.server 8080

# Or Python 2
python -m SimpleHTTPServer 8080

# Open browser
open http://localhost:8080
```

## 📱 Access the Application

Once running, open your web browser and navigate to:
```
http://localhost:8080
```

## 🎯 What You'll See

1. **Landing Page**: Beautiful animated index with all 8 topics
2. **Topic Cards**: Each topic has its own card with progress tracking
3. **Interactive Content**: Currently, "Logic & Proofs" is fully functional with:
   - Interactive truth tables
   - Live logic gate simulator
   - Proof examples with code
   - Quick quiz questions
   - Progress tracking

## 🔧 For Developers

### Project Structure
```
discrete-math-learning/
├── src/
│   ├── index.html           # Main landing page
│   ├── css/
│   │   ├── styles.css       # Landing page styles
│   │   └── content.css      # Content page styles
│   ├── js/
│   │   ├── main.js         # Landing page logic
│   │   └── content.js      # Content page interactions
│   └── pages/
│       └── logic.html      # Full content (other pages are placeholders)
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Orchestration config
├── nginx.conf             # Web server config
└── start.sh              # Auto-start script
```

### Development Mode

Edit files in `src/` directory and refresh your browser. If using Docker Compose with volume mounts, changes appear immediately.

### Adding New Content

1. Copy `src/pages/logic.html` as a template
2. Modify the content sections
3. Update navigation links
4. Add interactive elements in `src/js/content.js`

## 🎨 Features

- ✅ Fully responsive design
- ✅ Smooth animations and transitions
- ✅ Progress tracking (saved in browser)
- ✅ Interactive demos and quizzes
- ✅ Code examples in Python
- ✅ Mathematical proofs with step-by-step explanations
- ✅ Clean, modern UI

## 📚 Current Content Status

- ✅ **Logic & Proofs**: Complete with interactive demos
- 🚧 **Sets & Relations**: Placeholder
- 🚧 **Combinatorics**: Placeholder
- 🚧 **Graph Theory**: Placeholder
- 🚧 **Recurrence Relations**: Placeholder
- 🚧 **Algorithm Analysis**: Placeholder
- 🚧 **Number Theory**: Placeholder
- 🚧 **Probability**: Placeholder

## 🐛 Troubleshooting

**Docker not starting?**
- Make sure Docker Desktop is running
- Check if port 8080 is already in use
- Try: `docker-compose down` then `docker-compose up -d`

**Page not loading?**
- Clear browser cache
- Check if the server is running: `docker ps` or `lsof -i :8080`
- Try a different port by editing `docker-compose.yml`

**Progress not saving?**
- Make sure browser localStorage is enabled
- Check browser privacy settings
- Try a different browser

## 🎓 Learning Path

**Recommended order for beginners:**
1. Logic & Proofs ← Start here
2. Sets & Relations
3. Combinatorics
4. Number Theory
5. Graph Theory
6. Recurrence Relations
7. Algorithm Analysis
8. Probability

**For algorithm focus:**
1. Logic & Proofs
2. Algorithm Analysis
3. Recurrence Relations
4. Graph Theory
5. Combinatorics
6. Probability

---

**Happy Learning! 🚀**

Need help? Check the main README.md for more detailed information.
