# Discrete Mathematics for Programmers

An interactive, animated web-based learning platform for discrete mathematics, specifically designed to help programmers master the mathematical foundations of algorithms.

## Features

- **Interactive Learning**: Animated content with visual demonstrations
- **Programming-Focused**: Every concept connected to real programming scenarios
- **Progress Tracking**: Save your progress as you learn
- **Interactive Demos**: Truth tables, logic gates, and more
- **Clean UI**: Modern, responsive design with smooth animations

## Topics Covered

1. **Logic & Proofs** - Propositional logic, proof techniques, truth tables
2. **Sets & Relations** - Set theory, operations, functions
3. **Combinatorics** - Counting principles, permutations, combinations
4. **Graph Theory** - Graphs, trees, paths, network algorithms
5. **Recurrence Relations** - Solving recurrences, Master theorem
6. **Algorithm Analysis** - Big-O notation, complexity classes
7. **Number Theory** - Primes, modular arithmetic, cryptography
8. **Probability** - Probability basics, randomized algorithms

## Quick Start with Docker

### Prerequisites
- Docker installed on your system
- Docker Compose (optional, but recommended)

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and run the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Option 2: Using Docker directly

```bash
# Build the image
docker build -t discrete-math-learning .

# Run the container
docker run -d -p 8080:80 --name discrete-math discrete-math-learning

# Stop the container
docker stop discrete-math

# Remove the container
docker rm discrete-math
```

### Access the Application

Once running, open your browser and navigate to:
```
http://localhost:8080
```

## Development

### Project Structure

```
discrete-math-learning/
├── src/
│   ├── index.html              # Main index page with topic navigation
│   ├── css/
│   │   ├── styles.css          # Main page styles
│   │   └── content.css         # Content page styles
│   ├── js/
│   │   ├── main.js            # Main page JavaScript
│   │   └── content.js         # Content page JavaScript
│   └── pages/
│       ├── logic.html         # Logic & Proofs content
│       ├── sets.html          # Sets & Relations (placeholder)
│       ├── counting.html      # Combinatorics (placeholder)
│       ├── graphs.html        # Graph Theory (placeholder)
│       ├── recurrence.html    # Recurrence Relations (placeholder)
│       ├── algorithms.html    # Algorithm Analysis (placeholder)
│       ├── number-theory.html # Number Theory (placeholder)
│       └── probability.html   # Probability (placeholder)
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── README.md
```

### Local Development (without Docker)

Simply open `src/index.html` in your browser. However, for the best experience and to avoid CORS issues, use a local web server:

```bash
# Using Python
cd src
python -m http.server 8080

# Using Node.js
npx http-server src -p 8080
```

## Features by Page

### Index Page (index.html)
- Animated landing page
- 8 topic cards with progress tracking
- Responsive grid layout
- Local storage for progress persistence

### Logic & Proofs Page (logic.html)
- Interactive truth table demonstrations
- Live logic gate simulator
- Step-by-step proof examples
- Code examples in Python
- Quick quiz for self-assessment
- Progress tracking

## Customization

### Changing the Port

Edit `docker-compose.yml`:
```yaml
ports:
  - "YOUR_PORT:80"
```

### Development Mode

The docker-compose.yml includes a volume mount for live development:
```yaml
volumes:
  - ./src:/usr/share/nginx/html:ro
```

This allows you to edit files and see changes immediately without rebuilding.

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Web Server**: Nginx (Alpine Linux)
- **Container**: Docker
- **Styling**: Custom CSS with animations and gradients
- **Storage**: Browser LocalStorage for progress tracking

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Opera (latest)

## Future Enhancements

- [ ] Complete all 8 topic pages with full content
- [ ] Add more interactive visualizations
- [ ] Include practice problems with solutions
- [ ] Add video explanations
- [ ] Implement a search feature
- [ ] Add dark mode toggle
- [ ] Include downloadable cheat sheets
- [ ] Add user accounts and cloud sync

## Contributing

This is a learning resource. Feel free to:
- Add more content to existing pages
- Create additional interactive demos
- Improve animations and UI
- Fix bugs or improve documentation

## License

This project is created for educational purposes.

## Acknowledgments

Based on content from:
- "Discrete Mathematics with Applications" by Susanna S. Epp
- "Concrete Mathematics" by Graham, Knuth, and Patashnik
- "Mathematics for Computer Science" by Lehman, Leighton, and Meyer
- "Discrete Mathematics and Its Applications" by Kenneth Rosen

---

**Happy Learning! 🚀**
