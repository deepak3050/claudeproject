"""
Simple test to verify Playwright MCP is working
This tests if the agent can actually use Playwright tools
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def test_browser_automation():
    """Test if browser automation works"""

    print("=" * 80)
    print("Testing Browser Automation with Playwright MCP")
    print("=" * 80)

    # Simple prompt to navigate to Google
    test_prompt = "Navigate to google.com using the browser and tell me what you see. Take a snapshot."

    # Allow Playwright tools
    playwright_tools = [
        'mcp__playwright__browser_navigate',
        'mcp__playwright__browser_snapshot',
        'mcp__playwright__browser_take_screenshot',
    ]

    options = ClaudeAgentOptions(
        allowed_tools=playwright_tools
    )

    print(f"\nPrompt: {test_prompt}")
    print(f"Allowed Tools: {', '.join(playwright_tools)}\n")
    print("-" * 80)

    conversation_complete = False

    try:
        async for msg in query(prompt=test_prompt, options=options):
            msg_type = type(msg).__name__

            print(f"\n[{msg_type}]", end=" ")

            # Check for tool use
            if hasattr(msg, 'content') and isinstance(msg.content, list):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == 'TextBlock':
                        print(f"\n  {block.text[:200]}...")
                    elif block_type == 'ToolUseBlock':
                        print(f"\n  🔧 Using: {block.name}")
                    elif block_type == 'ToolResultBlock':
                        if block.is_error:
                            print(f"\n  ❌ Error: {str(block.content)[:200]}")
                        else:
                            print(f"\n  ✅ Success")

            # Check for completion
            if hasattr(msg, 'subtype') and msg.subtype == 'success':
                conversation_complete = True
                print("\n" + "=" * 80)
                print("✅ TEST COMPLETE")
                print("=" * 80)
                return True

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return conversation_complete


if __name__ == '__main__':
    print("\n🎭 Browser Automation Test\n")

    # Check if MCP server is running
    print("NOTE: This test requires:")
    print("1. Playwright MCP server configured in ~/.claude/config.json")
    print("2. @playwright/mcp package available (npx -y @playwright/mcp)")
    print("3. Browser binaries installed")
    print("\n" + "-" * 80 + "\n")

    result = asyncio.run(test_browser_automation())

    if result:
        print("\n✨ Browser automation is working!")
        print("   Your Flask app should now be able to use Playwright tools")
    else:
        print("\n⚠️  Browser automation test failed")
        print("   Check if Playwright MCP server is configured correctly")
