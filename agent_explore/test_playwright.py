"""
Test script to verify Playwright MCP setup
Run this after configuring MCP to test browser automation
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
import os

# Playwright MCP tools that should be available
PLAYWRIGHT_TOOLS = [
    'mcp__playwright__browser_navigate',
    'mcp__playwright__browser_snapshot',
    'mcp__playwright__browser_click',
    'mcp__playwright__browser_take_screenshot',
]

async def test_playwright_setup():
    """Test if Playwright MCP is properly configured"""

    print("=" * 80)
    print("Testing Playwright MCP Setup")
    print("=" * 80)

    # Simple test prompt
    test_prompt = "Navigate to google.com and take a screenshot, save it as google_test.png"

    # Configure options
    options = ClaudeAgentOptions(
        allowed_tools=PLAYWRIGHT_TOOLS,
        # Use API key if available, otherwise uses Pro subscription
        api_key=os.getenv("ANTHROPIC_API_KEY") if os.getenv("ANTHROPIC_API_KEY") else None
    )

    print(f"\nTest Prompt: {test_prompt}")
    print(f"Allowed Tools: {', '.join(PLAYWRIGHT_TOOLS)}\n")
    print("-" * 80)

    try:
        async for msg in query(prompt=test_prompt, options=options):
            # Print message type
            msg_type = type(msg).__name__
            print(f"\n[{msg_type}]")

            # Print content if available
            if hasattr(msg, 'content') and isinstance(msg.content, list):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == 'TextBlock':
                        print(f"  Text: {block.text[:200]}...")
                    elif block_type == 'ToolUseBlock':
                        print(f"  Tool: {block.name}")
                    elif block_type == 'ToolResultBlock':
                        if not block.is_error:
                            print(f"  Result: Success")
                        else:
                            print(f"  Error: {block.content}")

            # Check for completion
            if hasattr(msg, 'subtype') and msg.subtype == 'success':
                print("\n" + "=" * 80)
                print("✅ TEST PASSED - Playwright MCP is working!")
                print("=" * 80)

                if hasattr(msg, 'usage'):
                    usage = msg.usage
                    print(f"\nToken Usage:")
                    print(f"  Input: {usage.get('input_tokens', 0)}")
                    print(f"  Output: {usage.get('output_tokens', 0)}")
                    print(f"  Cache Read: {usage.get('cache_read_input_tokens', 0)}")

                return True

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        print("\nPossible issues:")
        print("1. Playwright MCP server not configured in ~/.claude/config.json")
        print("2. Playwright not installed (run: npm install -D @playwright/test && npx playwright install)")
        print("3. MCP server not running")
        print("\nSee PLAYWRIGHT_SETUP.md for detailed setup instructions")
        return False

if __name__ == '__main__':
    print("\n🎭 Playwright MCP Test Script\n")

    # Run the test
    result = asyncio.run(test_playwright_setup())

    if result:
        print("\n✨ Your Flask app is ready for browser automation!")
        print("   Start the server: python flask_app.py")
        print("   Open browser: http://localhost:5000")
        print("   Try prompts from: example_prompts.txt")
    else:
        print("\n⚠️  Setup incomplete. Check PLAYWRIGHT_SETUP.md for configuration steps")
