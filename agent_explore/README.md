# Claude Agent System - Architecture & Guide

A Flask-based web interface for Claude Agent SDK with browser automation capabilities.

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Available Agents](#available-agents)
4. [Quick Start](#quick-start)
5. [Browser Automation](#browser-automation)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This project provides two Flask applications for interacting with Claude AI:

### 1. **flask_app.py** - Basic Agent Interface
- Web-based chat interface for Claude Agent SDK
- Real-time WebSocket communication
- Permission management system
- Pre-approved tools for common operations

### 2. **flask_app_browser.py** - Browser Automation Agent ⭐
- All features from flask_app.py
- **Python Playwright integration** for browser automation
- Navigate websites, extract data, take screenshots
- Smart prompt detection for browser actions

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Browser Client (Port 5001)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Input Form  │  │  Chat Panel  │  │  Permission  │          │
│  │              │  │              │  │    Modal     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                          ↕ Socket.IO                             │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                     Flask Server (Python)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               Flask-SocketIO Handler                     │   │
│  │  • start_agent: Initiates agent query                    │   │
│  │  • permission_response: Handles tool permissions         │   │
│  │  • close_browser: Cleanup browser instance               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↕                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          Browser Automation Layer (Playwright)           │   │
│  │  • init_browser(): Launch Chromium                       │   │
│  │  • execute_browser_action(): Navigate, click, type       │   │
│  │  • process_browser_request(): Parse user intent          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↕                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │      Async Agent Runner (Background Thread + asyncio)    │   │
│  │  • Creates isolated event loop                           │   │
│  │  • Runs Claude Agent SDK query()                         │   │
│  │  • Streams messages via WebSocket                        │   │
│  │  • Graceful cleanup (no cancel scope errors)             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↕                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Claude Agent SDK (Python)                   │   │
│  │  • query(): Async generator for agent messages           │   │
│  │  • Tool execution: WebSearch, Read, Write, Bash, etc.    │   │
│  │  • Message formatting and streaming                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│              Claude AI (via Pro Subscription or API)             │
│  • Natural language understanding                                │
│  • Response generation                                           │
│  • Tool usage decisions                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input → Socket Event → Flask Handler → Browser Detection
                                                    ↓
                                         ┌──────────┴──────────┐
                                         ↓                     ↓
                              Browser Action          Claude Agent Query
                              (Playwright)            (Claude SDK)
                                    ↓                         ↓
                              Page Content            Agent Response
                                    ↓                         ↓
                              Screenshot (optional)    Tool Results
                                    ↓                         ↓
                                    └─────────┬───────────────┘
                                              ↓
                                    Combined Results
                                              ↓
                                    Format Message
                                              ↓
                                    Socket.IO Emit
                                              ↓
                                    Browser Display
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | HTML5 + CSS3 + JavaScript | User interface |
| **WebSocket** | Socket.IO | Real-time bidirectional communication |
| **Backend** | Flask + Flask-SocketIO | Web server and event handling |
| **Browser Automation** | Playwright (Python) | Web scraping and automation |
| **Async Runtime** | asyncio + threading | Concurrent task execution |
| **AI Agent** | Claude Agent SDK | Claude API integration |
| **Authentication** | Claude Pro / API Key | Claude access |

---

## Available Agents

### Agent 1: Basic Flask Agent (`flask_app.py`)

**Port:** 5000
**Purpose:** General-purpose Claude agent with permission management

**Pre-approved Tools:**
- `WebSearch` - Search the web
- `WebFetch` - Fetch web content
- `Read` - Read files
- `Glob` - Find files by pattern
- `Grep` - Search in files
- `Bash` - Execute bash commands
- `Write` - Write files
- `Edit` - Edit files

**Use Cases:**
- Code analysis and editing
- File system operations
- Web research
- General Q&A

**Start Command:**
```bash
python flask_app.py
# Open: http://localhost:5000
```

---

### Agent 2: Browser Automation Agent (`flask_app_browser.py`) ⭐ RECOMMENDED

**Port:** 5001
**Purpose:** Claude agent with automated web browsing capabilities

**Features:**
- ✅ All features from Agent 1
- ✅ **Browser automation** (Chromium via Playwright)
- ✅ Navigate to any website
- ✅ Extract page content and links
- ✅ Take screenshots
- ✅ Google search automation
- ✅ Smart prompt detection

**Browser Actions:**
| Action | Trigger Keywords | Example |
|--------|------------------|---------|
| Navigate | "navigate", "go to", "visit", "open" | "Navigate to imdb.com" |
| Screenshot | "screenshot", "capture" | "Take a screenshot" |
| Search Google | "google", "search" | "Search Google for news" |
| Extract Links | "movie", "film" (on IMDb) | "Show top movies" |

**Use Cases:**
- Web scraping and data extraction
- Screenshot automation
- Research and news gathering
- Price checking across websites
- Testing web applications

**Start Command:**
```bash
python flask_app_browser.py
# Open: http://localhost:5001
```

---

### Agent Comparison

| Feature | flask_app.py | flask_app_browser.py |
|---------|--------------|---------------------|
| Claude AI Integration | ✅ | ✅ |
| File Operations | ✅ | ✅ |
| Web Search | ✅ | ✅ |
| Browser Automation | ❌ | ✅ |
| Screenshot Capture | ❌ | ✅ |
| Navigate Websites | ❌ | ✅ |
| Extract Web Data | ❌ | ✅ |
| Port | 5000 | 5001 |
| Dependencies | Flask, SocketIO | Flask, SocketIO, Playwright |

---

## Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# Virtual environment
cd /Users/deepakdas/Github3050/claude/agent_explore
source ../.venv/bin/activate
```

### Option 1: Basic Agent (No Browser)

```bash
# Start the basic agent
python flask_app.py

# Open browser
# http://localhost:5000

# Try a prompt
"Search the web for latest AI news"
```

### Option 2: Browser Automation Agent (Recommended)

```bash
# Install Playwright (one-time setup)
pip install playwright
playwright install chromium

# Start the browser agent
python flask_app_browser.py

# Open browser
# http://localhost:5001

# Try a prompt
"Navigate to imdb.com and capture screenshot"
```

### Example Prompts

**For Basic Agent (Port 5000):**
```
"Search for Python tutorials"
"Read the file at ./flask_app.py"
"Find all Python files in this directory"
"What are the top tech news today?"
```

**For Browser Agent (Port 5001):**
```
"Navigate to imdb.com and capture screenshot"
"Search Google for 'best movies 2024'"
"Go to bbc.com and get the top headlines"
"Visit weather.com and get the forecast"
"Navigate to amazon.com and search for laptops"
```

---

## Browser Automation

### How It Works

1. **Prompt Detection**
   - System analyzes your prompt for keywords
   - Keywords: "navigate", "go to", "imdb", "screenshot", "capture", etc.

2. **Browser Launch**
   - Chromium browser opens (visible window)
   - Configured to run non-headless for debugging

3. **Action Execution**
   - Navigate to URL
   - Extract page content (text, links)
   - Take screenshots (saved to `/tmp/`)
   - Return results to Claude

4. **Agent Analysis**
   - Claude receives browser results
   - Analyzes and summarizes content
   - Presents formatted results

### Browser Actions

#### Navigate to Website
```python
# User prompt: "Go to imdb.com"
# System executes:
await page.goto("https://imdb.com")
content = await page.inner_text("body")
# Returns: Page title + content preview
```

#### Take Screenshot
```python
# User prompt: "Take a screenshot"
# System executes:
await page.screenshot(path="/tmp/imdb_com_screenshot.png")
# Returns: File path
```

#### Search Google
```python
# User prompt: "Search Google for movies"
# System executes:
await page.goto("https://google.com")
await page.fill("textarea[name='q']", "movies")
await page.press("textarea[name='q']", "Enter")
# Returns: Search results
```

#### Extract Links (IMDb)
```python
# User prompt: "Show top movies on IMDb"
# System executes:
links = await page.evaluate("""
    () => Array.from(document.querySelectorAll('a'))
        .map(a => ({text: a.innerText, href: a.href}))
        .filter(link => link.text && link.href)
""")
# Returns: List of movies
```

### Screenshot Location

Screenshots are saved to:
```
/tmp/<url>_screenshot.png
```

Examples:
- `/tmp/imdb_com_screenshot.png`
- `/tmp/bbc_com_screenshot.png`
- `/tmp/weather_com_screenshot.png`

**View Screenshot:**
```bash
open /tmp/imdb_com_screenshot.png
```

**Change Location** (edit flask_app_browser.py:110):
```python
filepath = os.path.join("/your/custom/path", filename)
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```
Error: Port 5000/5001 is in use
```

**Solution:**
```bash
# Kill existing process
pkill -f flask_app.py
# Or
pkill -f flask_app_browser.py

# Restart
python flask_app_browser.py
```

#### 2. Playwright Not Installed
```
Error: ModuleNotFoundError: No module named 'playwright'
```

**Solution:**
```bash
source ../.venv/bin/activate
pip install playwright
playwright install chromium
```

#### 3. Browser Doesn't Open
```
Browser window doesn't appear
```

**Solution:**
```bash
# Verify Playwright
python -c "from playwright.async_api import async_playwright; print('OK')"

# Reinstall browsers
playwright install chromium

# Check permissions (macOS)
# System Settings → Privacy & Security → Automation
```

#### 4. Screenshot Fails
```
Error saving screenshot
```

**Solution:**
```bash
# Check /tmp/ permissions
ls -la /tmp/

# Verify Playwright can access filesystem
touch /tmp/test.txt && rm /tmp/test.txt
```

#### 5. Async Cancel Scope Error (Should not appear!)
```
RuntimeError: Attempted to exit cancel scope in a different task
```

**Solution:**
This error is now suppressed in flask_app_browser.py. If you still see it:
```bash
# Hard restart
pkill -9 -f flask_app_browser.py
python flask_app_browser.py
```

---

## Configuration

### Browser Settings (flask_app_browser.py)

**Headless Mode** (Line 48):
```python
browser_instance = await playwright_instance.chromium.launch(
    headless=False  # Change to True to hide browser window
)
```

**Screenshot Directory** (Line 110):
```python
filepath = os.path.join("/tmp", filename)  # Change path here
```

**Browser Type**:
```python
# Chromium (default)
browser_instance = await playwright_instance.chromium.launch()

# Firefox
browser_instance = await playwright_instance.firefox.launch()

# WebKit (Safari)
browser_instance = await playwright_instance.webkit.launch()
```

### Authentication (Both apps)

**Line 34**: Choose authentication method
```python
USE_API = 0  # 0 = Pro Subscription, 1 = API Key
```

**For API Key**:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

---

## File Structure

```
agent_explore/
├── flask_app.py              # Basic agent (Port 5000)
├── flask_app_browser.py      # Browser agent (Port 5001) ⭐
├── templates/
│   └── index.html            # Web UI
├── agent.py                  # Standalone agent script
├── test_browser.py           # Browser test script
├── test_playwright.py        # Playwright test script
├── setup_browser.sh          # Setup script
├── example_prompts.txt       # Example prompts for testing
└── README.md                 # This file
```

---

## Key Technical Details

### Async Architecture

**Problem:** Flask (sync) + Claude Agent SDK (async) = Threading complexity

**Solution:**
1. Flask-SocketIO handles WebSocket events (sync)
2. Background thread created for each agent query
3. New event loop in thread for asyncio operations
4. Graceful cleanup to avoid cancel scope errors

**Implementation (flask_app_browser.py:493-533):**
```python
def run_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Suppress SDK internal errors
    sys.stderr = io.StringIO()

    try:
        loop.run_until_complete(run_agent(user_prompt))
    except Exception as e:
        # Filter out cancel scope errors
        if 'cancel scope' not in str(e).lower():
            socketio.emit('error', {'message': str(e)})
    finally:
        sys.stderr = old_stderr
        loop.close()
```

### Error Handling

**Suppressed Errors:**
- `GeneratorExit` - Normal async generator cleanup
- `RuntimeError` with "cancel scope" - SDK internal cleanup
- SDK tracebacks via stderr redirect

**Shown Errors:**
- Network failures
- Permission denials
- Invalid URLs
- Browser crashes

---

## Performance

### Response Times

| Action | Typical Time |
|--------|-------------|
| Basic Claude Query | 2-5 seconds |
| WebSearch + Analysis | 5-10 seconds |
| Navigate + Extract | 3-7 seconds |
| Screenshot | 2-4 seconds |
| Google Search | 4-8 seconds |

### Resource Usage

| Resource | Basic Agent | Browser Agent |
|----------|-------------|---------------|
| Memory | ~100MB | ~300MB |
| CPU | Low | Medium |
| Disk | Minimal | Screenshots (~500KB each) |

---

## Security Notes

⚠️ **Important:**
- Don't enter real passwords/credentials in browser automation
- Use test accounts for form filling
- Review URLs before navigation
- Screenshots may contain sensitive data
- Browser runs in visible mode for security

---

## Next Steps

1. **Start the browser agent:**
   ```bash
   python flask_app_browser.py
   ```

2. **Open the UI:**
   ```
   http://localhost:5001
   ```

3. **Try a test prompt:**
   ```
   Navigate to imdb.com and capture screenshot
   ```

4. **Check the screenshot:**
   ```bash
   open /tmp/imdb_com_screenshot.png
   ```

5. **Explore more prompts:**
   See `example_prompts.txt` for 50+ ready-to-use prompts

---

## Support

**Issues?**
- Check [Troubleshooting](#troubleshooting) section
- Verify Playwright: `playwright install chromium`
- Restart with clean state: `pkill -f flask_app_browser.py`

**Questions about Claude Agent SDK?**
- [Claude Agent SDK Documentation](https://github.com/anthropics/anthropic-sdk-python)

---

**Built with:**
- Flask + Flask-SocketIO
- Claude Agent SDK
- Playwright
- asyncio

**Last Updated:** January 2026
