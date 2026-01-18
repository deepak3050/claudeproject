import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    # Prompt for Claude to control browser via MCP Playwright
    prompt = "Navigate to imdb.com and get the top movies. Take a screenshot."

    # MCP Playwright tools that Claude can use
    playwright_tools = [
        'mcp__playwright__browser_navigate',
        'mcp__playwright__browser_snapshot',
        'mcp__playwright__browser_take_screenshot',
        'mcp__playwright__browser_click',
        'mcp__playwright__browser_type',
        'mcp__playwright__browser_evaluate',
    ]

    # Configure Claude Agent SDK - Claude will manage the browser
    options = ClaudeAgentOptions(
        allowed_tools=playwright_tools
    )

    print(f"Asking Claude: {prompt}\n")
    print("=" * 60)

    # Query Claude Agent - it will launch browser and control it
    try:
        async for message in query(prompt=prompt, options=options):
            msg_type = type(message).__name__

            # Skip system messages
            if msg_type == 'SystemMessage':
                continue

            # Handle messages with content blocks
            if hasattr(message, 'content') and isinstance(message.content, list):
                for block in message.content:
                    block_type = type(block).__name__

                    if block_type == 'TextBlock':
                        print(f"\n💬 Claude: {block.text}")
                    elif block_type == 'ToolUseBlock':
                        print(f"\n🔧 Using tool: {block.name}")
                    elif block_type == 'ToolResultBlock':
                        if not block.is_error:
                            print(f"✅ Tool completed successfully")
                        else:
                            print(f"❌ Tool error: {block.content}")

            # Handle result message
            elif msg_type == 'ResultMessage' and hasattr(message, 'result'):
                result_text = str(message.result)
                if len(result_text) > 500:
                    result_text = result_text[:500] + "..."
                print(f"\n📊 Final Result: {result_text}")

    except GeneratorExit:
        # Normal cleanup - ignore
        pass
    except RuntimeError as e:
        # Ignore cancel scope errors from SDK
        if 'cancel scope' not in str(e).lower():
            raise

    print("\n" + "=" * 60)
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())