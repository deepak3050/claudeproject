#!/bin/bash

echo "=================================================="
echo "Setting up Browser Automation for Flask App"
echo "=================================================="

# Navigate to project directory
cd /Users/deepakdas/Github3050/claude/agent_explore

# Activate venv
source ../.venv/bin/activate

# Install Playwright Python package
echo "Installing Playwright..."
pip install playwright

# Install Chromium browser
echo "Installing Chromium browser..."
playwright install chromium

echo "=================================================="
echo "✅ Setup complete!"
echo "=================================================="
echo ""
echo "Now you can run:"
echo "  python flask_app_browser.py"
echo ""
echo "Then open: http://localhost:5001"
echo "Try: 'Go to Google News and find top 5 headlines'"
echo "=================================================="
