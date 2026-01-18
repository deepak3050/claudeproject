import asyncio
import os
import json
import re
from pprint import pprint
from claude_agent_sdk import query, ClaudeAgentOptions


def clean_text(text):
    """Remove excessive whitespace and format text in a readable way."""
    if not isinstance(text, str):
        return text

    # Remove multiple newlines (keep max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove trailing/leading whitespace from each line
    text = '\n'.join(line.strip() for line in text.split('\n'))
    # Remove extra spaces
    text = re.sub(r' +', ' ', text)

    return text


# Configuration flag:
# use_api = 1: Use API key from environment variable ANTHROPIC_API_KEY
# use_api = 0: Use Pro subscription (default Claude Code authentication)
USE_API = 0


async def my_agent():
    """Query the Claude agent with a prompt and track token usage."""
    print("=" * 80)
    print("STARTING AGENT QUERY")
    print("=" * 80)

    # Determine authentication method
    if USE_API == 1:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("ERROR: USE_API=1 but ANTHROPIC_API_KEY environment variable not set!")
            print("Please set ANTHROPIC_API_KEY or change USE_API to 0")
            return
        print(f"Authentication: API Key (from environment)")
        print(f"API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else ''}")
        options = ClaudeAgentOptions(
            allowed_tools=["Bash","WebSearch","WebFetch","Read","Glob","Grep","Write","Edit"],
            api_key=api_key
        )
    else:
        print(f"Authentication: Pro Subscription (Claude Code)")
        options = ClaudeAgentOptions(allowed_tools=["Bash","WebSearch","WebFetch","Read","Glob","Grep","Write","Edit"])

    print("=" * 80)

    total_tokens_before = 0
    usage_data = None
    api_key_source = None
    sequence = 0  # Track message sequence

    try:
        async for msg in query(
            prompt="tell me top 10 news in finance as of jan29, 2025",
            options=options
        ):
            sequence += 1
            msg_type = type(msg).__name__

            # Display sequence header
            print(f"\n{'='*80}")
            print(f"SEQUENCE #{sequence} | TYPE: {msg_type}")
            print(f"{'='*80}")

            # Extract and clean content for readable display
            if hasattr(msg, 'content') and msg.content:
                if isinstance(msg.content, list):
                    for block in msg.content:
                        # Clean and display text content
                        if hasattr(block, 'text'):
                            cleaned = clean_text(block.text)
                            print(f"\n[Assistant]: {cleaned}\n")
                        # Display tool content
                        elif hasattr(block, 'content'):
                            cleaned = clean_text(block.content)
                            print(f"\n[Response]:\n{cleaned}\n")
                        # Display tool use
                        elif hasattr(block, 'name'):
                            print(f"\n[Tool]: {block.name}")
                            if hasattr(block, 'input'):
                                print(json.dumps(block.input, indent=2))
            # Display result
            elif hasattr(msg, 'result') and msg.result:
                cleaned = clean_text(msg.result)
                print(f"\n[Result]: {cleaned}\n")

            print(f"{'-'*80}")
            print(f"END SEQUENCE #{sequence}")
            print(f"{'-'*80}")

            # Capture API key source from SystemMessage
            if hasattr(msg, 'subtype') and msg.subtype == 'init':
                if hasattr(msg, 'data') and 'apiKeySource' in msg.data:
                    api_key_source = msg.data['apiKeySource']

            # Check if this is a ResultMessage with usage data
            #if hasattr(msg, 'usage') and msg.usage:
            #    usage_data = msg.usage

    except Exception as e:
        print(f"Error: {e}")

    # Display token usage summary
    '''
    if usage_data:
        print("\n" + "=" * 80)
        print("TOKEN USAGE SUMMARY")
        print("=" * 80)

        # Display authentication method used
        if api_key_source:
            auth_method = "API Key" if api_key_source != "none" else "Pro Subscription"
            print(f"Authentication Used:       {auth_method} (source: {api_key_source})")
            print("-" * 80)

        input_tokens = usage_data.get('input_tokens', 0)
        cache_creation = usage_data.get('cache_creation_input_tokens', 0)
        cache_read = usage_data.get('cache_read_input_tokens', 0)
        output_tokens = usage_data.get('output_tokens', 0)

        total_input = input_tokens + cache_creation + cache_read
        total_tokens = total_input + output_tokens

        # Prettify usage data as JSON
        usage_summary = {
            "token_breakdown": {
                "input_tokens": input_tokens,
                "cache_creation_tokens": cache_creation,
                "cache_read_tokens": cache_read,
                "output_tokens": output_tokens
            },
            "totals": {
                "total_input_tokens": total_input,
                "total_tokens": total_tokens
            }
        }

        if hasattr(msg, 'total_cost_usd') and msg.total_cost_usd:
            usage_summary["cost_usd"] = round(msg.total_cost_usd, 6)

        print(json.dumps(usage_summary, indent=2))
        print("=" * 80)
    else:
        print("\n[No usage data available]")
    '''


if __name__ == "__main__":
    asyncio.run(my_agent())