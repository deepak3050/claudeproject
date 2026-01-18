# MCP Playwright Setup Guide

## Understanding MCP Architecture

### What is MCP?

**MCP (Model Context Protocol)** is a protocol that allows AI assistants to use external tools through standardized servers.

```
┌──────────────────────────────────────────────┐
│  Client (Your Python Script)                 │
│  ┌────────────────────────────────────────┐  │
│  │  Claude Agent SDK                      │  │
│  │  query(prompt, options)                │  │
│  └────────────────────────────────────────┘  │
│              ↕                                │
│              ↕ MCP Protocol (JSON-RPC)        │
│              ↕                                │
│  ┌────────────────────────────────────────┐  │
│  │  MCP Server (Playwright)               │  │
│  │  - Receives commands                   │  │
│  │  - Controls browser                    │  │
│  │  - Returns results                     │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### Why Your Script Doesn't Work

When you run `simple_browser.py`:

```python
playwright_tools = [
    'mcp__playwright__browser_navigate',  # ❌ Just a string!
    'mcp__playwright__browser_snapshot',   # ❌ Not connected to anything!
]

options = ClaudeAgentOptions(allowed_tools=playwright_tools)
```

**Problem**: These are just tool NAMES, not actual tool implementations!

**What's Missing**:
1. ❌ No MCP Playwright server running
2. ❌ No connection configured to the server
3. ❌ Claude Agent SDK doesn't know where to find the tools

### How Claude Code CLI Works

In the Claude Code CLI session (where you're talking to me):

1. ✅ **MCP servers are pre-configured** in Claude Code settings
2. ✅ **Servers start automatically** when Claude Code starts
3. ✅ **Tools are registered** and available to Claude
4. ✅ **Full bidirectional communication** via MCP protocol

That's why I can use `mcp__playwright__browser_navigate` - the server is already running!

---

## The Problem with Standalone Scripts

**Claude Agent SDK** currently does NOT support configuring external MCP servers in standalone scripts.

Looking at `ClaudeAgentOptions`:
```python
class ClaudeAgentOptions:
    def __init__(
        self,
        api_key: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        # ❌ NO mcp_servers parameter!
        # ❌ NO server_config parameter!
    ):
```

**The `allowed_tools` parameter only works with BUILT-IN tools** like:
- `WebSearch`
- `WebFetch`
- `Read`
- `Write`
- `Bash`
- `Glob`
- `Grep`
- `Edit`

It does NOT work with external MCP tools!

---

## Solutions

### Solution 1: Use Claude Code CLI (Recommended)

**Instead of `simple_browser.py`, just use Claude Code directly:**

```bash
# In this chat session, just ask me:
"Navigate to imdb.com and get top movies, take a screenshot"
```

I already have MCP Playwright configured and running!

### Solution 2: Direct Playwright (No MCP)

**Write browser automation yourself** - don't rely on MCP:

```python
# simple_browser.py
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://imdb.com")
        await page.screenshot(path="/tmp/imdb.png")

        # Your custom logic here

        await browser.close()
```

### Solution 3: Flask App (Already Working)

**Use `flask_app_browser.py`** - it implements custom browser automation:

```bash
python flask_app_browser.py
# Open http://localhost:5001
```

This gives you a web UI with browser automation!

---

## Technical Deep Dive: Why MCP Doesn't Work Here

### MCP Server Configuration

MCP servers need to be configured in a config file. For Claude Code, it's in:

```bash
~/.claude/claude_desktop_config.json
```

Example config:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    }
  }
}
```

### The Connection Flow

1. **Claude Code starts** → Reads config → Launches MCP servers
2. **MCP server starts** → Listens on stdio/HTTP
3. **Claude connects** → Establishes MCP protocol connection
4. **Tools registered** → Server announces available tools
5. **Claude uses tools** → Sends JSON-RPC requests

### What's Missing in Standalone Scripts

**Claude Agent SDK** doesn't have:
- Config file reading
- MCP server lifecycle management
- MCP protocol client implementation
- Tool discovery mechanism

It's designed to use **built-in tools only** or be used within Claude Code where MCP is already set up.

---

## Future Possibility

**If Anthropic adds MCP support to the SDK**, it might look like:

```python
# HYPOTHETICAL - This doesn't work yet!
from claude_agent_sdk import query, ClaudeAgentOptions, MCPServer

# Start MCP server
playwright_server = MCPServer(
    command="npx",
    args=["-y", "@executeautomation/playwright-mcp-server"]
)

options = ClaudeAgentOptions(
    mcp_servers=[playwright_server],  # ❌ Doesn't exist yet!
    allowed_tools=['mcp__playwright__*']
)

async for msg in query(prompt="Navigate to imdb.com", options=options):
    print(msg)
```

But this **is not currently possible**!

---

## Recommendation

For **learning MCP Playwright**:

1. **Use this Claude Code CLI session** - I already have MCP Playwright!
2. **Ask me directly** - Just say "Navigate to imdb.com"
3. **Explore capabilities** - Try different browser automation tasks
4. **See MCP in action** - Watch how I use the tools

For **standalone automation**:
1. **Use Playwright directly** - More control, simpler architecture
2. **Or use Flask app** - Already working with custom browser automation

---

## Example: Using MCP Playwright in This Session

Try asking me (in this chat):

```
"Navigate to https://imdb.com and take a screenshot"

"Go to https://github.com/anthropics and get the repository list"

"Open https://bbc.com, extract headlines, and summarize the news"
```

I will:
- ✅ Use `mcp__playwright__browser_navigate`
- ✅ Use `mcp__playwright__browser_screenshot`
- ✅ Use `mcp__playwright__browser_snapshot`
- ✅ Return results to you

**This is the easiest way to explore MCP Playwright!**

---

## Summary

| Approach | MCP Support | Complexity | Best For |
|----------|-------------|------------|----------|
| **Claude Code CLI** | ✅ Built-in | Low | Learning MCP, quick tasks |
| **Standalone Script** | ❌ Not supported | N/A | Not possible for MCP |
| **Direct Playwright** | N/A | Medium | Custom automation |
| **Flask App** | N/A | High | Web UI, multi-user |

**Bottom line**: To explore MCP Playwright, use Claude Code CLI (this session) instead of standalone scripts!
