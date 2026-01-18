import asyncio
import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from claude_agent_sdk import query, ClaudeAgentOptions
import threading
from queue import Queue

# Browser automation setup
BROWSER_AVAILABLE = False
try:
    from playwright.async_api import async_playwright
    BROWSER_AVAILABLE = True
    print("✅ Playwright available for browser automation")
except ImportError:
    print("⚠️  Playwright not installed. Install with: pip install playwright && playwright install chromium")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global browser state
browser_instance = None
browser_page = None
playwright_instance = None

# Global state for managing permission requests
permission_queue = Queue()
permission_response = {}
conversation_active = False

# Pre-approved common tools
allowed_tools_set = {
    'WebSearch',
    'WebFetch',
    'Read',
    'Glob',
    'Grep',
    'Bash',
    'Write',
    'Edit'
}

# Configuration
USE_API = 0  # 0 = Pro Subscription, 1 = API Key


async def init_browser():
    """Initialize browser for automation"""
    global browser_instance, browser_page, playwright_instance

    if not BROWSER_AVAILABLE:
        return None, "Playwright not installed"

    try:
        if playwright_instance is None:
            playwright_instance = await async_playwright().start()

        if browser_instance is None:
            browser_instance = await playwright_instance.chromium.launch(
                headless=False  # Set to True for headless mode
            )

        if browser_page is None:
            browser_page = await browser_instance.new_page()

        return browser_page, None
    except Exception as e:
        return None, str(e)


async def close_browser():
    """Close browser instance"""
    global browser_instance, browser_page, playwright_instance

    try:
        if browser_page:
            await browser_page.close()
        if browser_instance:
            await browser_instance.close()
        if playwright_instance:
            await playwright_instance.stop()
    except Exception as e:
        print(f"Error closing browser: {e}")
    finally:
        browser_instance = None
        browser_page = None
        playwright_instance = None


async def execute_browser_action(action, params):
    """Execute browser action and return result"""
    page, error = await init_browser()

    if error:
        return {"error": error, "success": False}

    try:
        result = {"success": True}

        if action == "navigate":
            url = params.get("url", "")
            await page.goto(url, wait_until="domcontentloaded")
            result["message"] = f"Navigated to {url}"
            result["title"] = await page.title()
            result["url"] = page.url

        elif action == "get_content":
            content = await page.content()
            result["content"] = content[:5000]  # Limit content size
            result["title"] = await page.title()

        elif action == "screenshot":
            filename = params.get("filename", "screenshot.png")
            filepath = os.path.join("/tmp", filename)
            await page.screenshot(path=filepath)
            result["message"] = f"Screenshot saved to {filepath}"
            result["filepath"] = filepath

        elif action == "click":
            selector = params.get("selector", "")
            await page.click(selector)
            result["message"] = f"Clicked on {selector}"

        elif action == "type":
            selector = params.get("selector", "")
            text = params.get("text", "")
            await page.fill(selector, text)
            result["message"] = f"Typed '{text}' into {selector}"

        elif action == "get_text":
            selector = params.get("selector", "body")
            text = await page.inner_text(selector)
            result["text"] = text[:2000]  # Limit text size

        elif action == "extract_links":
            # Extract all links from page
            links = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('a'))
                        .map(a => ({ text: a.innerText.trim(), href: a.href }))
                        .filter(link => link.text && link.href);
                }
            """)
            result["links"] = links[:100]  # Limit to 100 links
            result["message"] = f"Extracted {len(links)} links"

        elif action == "search_google":
            query_text = params.get("query", "")
            await page.goto("https://www.google.com")
            await page.fill("textarea[name='q']", query_text)
            await page.press("textarea[name='q']", "Enter")
            await page.wait_for_load_state("domcontentloaded")

            # Get search results
            await asyncio.sleep(2)  # Wait for results to load
            results_text = await page.inner_text("body")
            result["results"] = results_text[:3000]
            result["message"] = f"Searched Google for: {query_text}"

        elif action == "close":
            await close_browser()
            result["message"] = "Browser closed"

        else:
            result["success"] = False
            result["error"] = f"Unknown action: {action}"

        return result

    except Exception as e:
        return {"error": str(e), "success": False}


def format_message(msg):
    """Format message for display in UI"""
    msg_type = type(msg).__name__

    if msg_type == 'SystemMessage':
        return None

    if hasattr(msg, 'content') and isinstance(msg.content, list):
        formatted_parts = []

        for block in msg.content:
            block_type = type(block).__name__

            if block_type == 'TextBlock':
                formatted_parts.append(f"📝 {block.text}")
            elif block_type == 'ToolUseBlock':
                tool_name = block.name
                formatted_parts.append(f"🔧 Using tool: {tool_name}")
            elif block_type == 'ToolResultBlock':
                if not block.is_error:
                    formatted_parts.append(f"✅ Tool completed")
                else:
                    content_str = str(block.content)
                    if len(content_str) > 300:
                        content_str = content_str[:300] + "..."
                    formatted_parts.append(f"❌ Tool error: {content_str}")

        if formatted_parts:
            return {
                'type': msg_type,
                'content': '\n'.join(formatted_parts)
            }

    if msg_type == 'ResultMessage' and hasattr(msg, 'result'):
        result_text = str(msg.result)
        if len(result_text) > 2000:
            result_text = result_text[:2000] + "..."
        return {
            'type': 'Final Result',
            'content': f"📊 {result_text}"
        }

    return None


async def process_browser_request(user_prompt):
    """Process browser request and return results"""

    # Check if prompt is requesting browser action
    prompt_lower = user_prompt.lower()
    results = []

    # Detect navigation request
    should_navigate = any(keyword in prompt_lower for keyword in ["navigate", "go to", "open", "visit", "imdb", "bbc", "cnn", "weather.com"])
    should_screenshot = "screenshot" in prompt_lower or "capture" in prompt_lower
    should_search = "google" in prompt_lower and "search" in prompt_lower

    # Extract URL from prompt
    url = None
    words = user_prompt.split()
    for word in words:
        if "http" in word or "www" in word or any(domain in word for domain in [".com", ".org", ".net", ".io", "imdb", "bbc", "cnn"]):
            if "http" not in word and not word.startswith("www"):
                url = f"https://{word}"
            else:
                url = word if word.startswith("http") else f"https://{word}"
            break

    # Google search handling
    if should_search and "google" in prompt_lower:
        query = user_prompt.replace("google", "").replace("search for", "").replace("search", "").strip()

        socketio.emit('status', {'message': f'🔍 Searching Google for: {query}...', 'type': 'info'})

        result = await execute_browser_action("search_google", {"query": query})

        if result.get("success"):
            socketio.emit('status', {'message': '✅ Search completed', 'type': 'success'})
            results.append(f"Google search results for '{query}':\n\n{result.get('results', '')}")
        else:
            socketio.emit('status', {'message': f'❌ Error: {result.get("error")}', 'type': 'error'})
            return f"Error: {result.get('error')}"

    # Navigation handling
    elif should_navigate and url:
        socketio.emit('status', {'message': f'🌐 Navigating to {url}...', 'type': 'info'})

        result = await execute_browser_action("navigate", {"url": url})

        if not result.get("success"):
            socketio.emit('status', {'message': f'❌ Navigation error: {result.get("error")}', 'type': 'error'})
            return f"Error navigating to {url}: {result.get('error')}"

        socketio.emit('status', {'message': f'✅ Loaded: {result.get("title")}', 'type': 'success'})

        # Get page content
        content_result = await execute_browser_action("get_text", {})
        page_content = content_result.get('text', '')

        # If it's IMDb and looking for movies, extract links
        if "imdb" in url.lower() and any(keyword in prompt_lower for keyword in ["movie", "film", "top"]):
            socketio.emit('status', {'message': '🎬 Extracting movie information...', 'type': 'info'})
            links_result = await execute_browser_action("extract_links", {})
            links = links_result.get('links', [])

            # Filter for movie links
            movie_links = [link for link in links if '/title/' in link.get('href', '')][:50]

            if movie_links:
                movie_info = f"\n\nFound {len(movie_links)} movies:\n"
                for i, link in enumerate(movie_links[:20], 1):  # Show first 20
                    movie_info += f"{i}. {link['text']}\n"
                page_content += movie_info

        results.append(f"Website: {url}\nTitle: {result.get('title')}\n\nPage content:\n{page_content}")

        # Take screenshot if requested
        if should_screenshot:
            socketio.emit('status', {'message': '📸 Taking screenshot...', 'type': 'info'})

            import re
            url_clean = re.sub(r'https?://', '', url).replace('/', '_').replace('.', '_')
            screenshot_name = f"{url_clean}_screenshot.png"

            screenshot_result = await execute_browser_action("screenshot", {"filename": screenshot_name})

            if screenshot_result.get("success"):
                filepath = screenshot_result.get("filepath")
                socketio.emit('status', {
                    'message': f'✅ Screenshot saved: {filepath}',
                    'type': 'success'
                })
                results.append(f"\n📸 Screenshot saved to: {filepath}")
            else:
                socketio.emit('status', {
                    'message': f'⚠️ Screenshot failed: {screenshot_result.get("error")}',
                    'type': 'warning'
                })

    return "\n\n".join(results) if results else None


async def run_agent(user_prompt):
    """Run the Claude agent with browser automation support"""
    global conversation_active, allowed_tools_set
    conversation_active = True

    if allowed_tools_set:
        socketio.emit('status', {
            'message': f'Starting agent with allowed tools: {", ".join(allowed_tools_set)}',
            'type': 'info'
        })
    else:
        socketio.emit('status', {'message': 'Starting agent...', 'type': 'info'})

    # Check if this is a browser automation request
    browser_result = await process_browser_request(user_prompt)

    if browser_result:
        # Feed browser results into agent prompt
        enhanced_prompt = f"{user_prompt}\n\nBrowser automation results:\n{browser_result}\n\nPlease analyze and summarize these results."
    else:
        enhanced_prompt = user_prompt

    # Determine authentication method
    if USE_API == 1:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            socketio.emit('error', {'message': 'ANTHROPIC_API_KEY not set!'})
            conversation_active = False
            return
        options = ClaudeAgentOptions(
            api_key=api_key,
            allowed_tools=list(allowed_tools_set) if allowed_tools_set else None
        )
    else:
        options = ClaudeAgentOptions(
            allowed_tools=list(allowed_tools_set) if allowed_tools_set else None
        )

    query_iterator = None
    try:
        query_iterator = query(prompt=enhanced_prompt, options=options)
        async for msg in query_iterator:
            formatted_msg = format_message(msg)
            if formatted_msg:
                socketio.emit('message', formatted_msg)

            if hasattr(msg, 'content') and isinstance(msg.content, list):
                for block in msg.content:
                    if hasattr(block, 'is_error') and block.is_error:
                        content_str = str(block.content) if hasattr(block, 'content') else str(block)
                        if 'permission' in content_str.lower() and 'requested permissions to use' in content_str:
                            tool_name = extract_tool_name(content_str)
                            socketio.emit('permission_request', {
                                'tool': tool_name,
                                'message': content_str
                            })
                            response = await wait_for_permission_response()
                            if response['granted']:
                                allowed_tools_set.add(tool_name)
                                socketio.emit('status', {
                                    'message': f'✓ Permission granted for {tool_name}',
                                    'type': 'success'
                                })
                                socketio.emit('permission_granted', {
                                    'tool': tool_name,
                                    'message': f'Permission granted. Click "Start Agent" to retry.'
                                })
                                conversation_active = False
                                # Don't return - let iterator finish naturally
                                break
                            else:
                                socketio.emit('status', {
                                    'message': f'✗ Permission denied for {tool_name}',
                                    'type': 'warning'
                                })
                                conversation_active = False
                                break

            if hasattr(msg, 'subtype') and msg.subtype == 'success':
                socketio.emit('status', {
                    'message': '✓ Conversation complete!',
                    'type': 'success'
                })

                if hasattr(msg, 'usage') and msg.usage:
                    usage = msg.usage
                    total_cost = getattr(msg, 'total_cost_usd', 0)
                    socketio.emit('usage', {
                        'input_tokens': usage.get('input_tokens', 0),
                        'output_tokens': usage.get('output_tokens', 0),
                        'cache_read': usage.get('cache_read_input_tokens', 0),
                        'total_cost': total_cost
                    })

                conversation_active = False
                # Don't return - let iterator finish naturally
                break

    except GeneratorExit:
        # Normal generator exit - suppress
        pass
    except RuntimeError as e:
        # Suppress cancel scope errors from SDK
        if 'cancel scope' not in str(e).lower():
            import traceback
            error_details = traceback.format_exc()
            socketio.emit('error', {'message': f'Runtime Error: {str(e)}\n\nDetails:\n{error_details}'})
    except Exception as e:
        # Only show non-cancel-scope errors
        if 'cancel scope' not in str(e).lower():
            import traceback
            error_details = traceback.format_exc()
            socketio.emit('error', {'message': f'Error: {str(e)}\n\nDetails:\n{error_details}'})
    finally:
        conversation_active = False
        # Don't try to manually close the iterator - let it close naturally


def extract_tool_name(error_message):
    """Extract tool name from permission error message"""
    if 'use ' in error_message:
        parts = error_message.split('use ')
        if len(parts) > 1:
            tool = parts[1].split(',')[0].split(' ')[0]
            return tool
    return "Unknown Tool"


async def wait_for_permission_response():
    """Wait for user to grant or deny permission"""
    global permission_response
    permission_response = {}

    timeout = 300
    start_time = asyncio.get_event_loop().time()

    while not permission_response:
        if asyncio.get_event_loop().time() - start_time > timeout:
            return {'granted': False, 'reason': 'timeout'}
        await asyncio.sleep(0.1)

    response = permission_response
    permission_response = {}
    return response


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    status_msg = 'Connected to server'
    if BROWSER_AVAILABLE:
        status_msg += ' - Browser automation enabled 🎭'
    emit('status', {'message': status_msg, 'type': 'success'})


@socketio.on('start_agent')
def handle_start_agent(data):
    """Start the agent with user prompt"""
    user_prompt = data.get('prompt', '')

    if not user_prompt:
        emit('error', {'message': 'Please enter a prompt'})
        return

    if conversation_active:
        emit('error', {'message': 'Conversation already in progress'})
        return

    def run_in_thread():
        import sys
        import io
        import warnings

        # Suppress the SDK's cancel scope warnings
        warnings.filterwarnings('ignore', category=RuntimeWarning)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Temporarily redirect stderr to suppress SDK traceback
        old_stderr = sys.stderr

        try:
            # Suppress SDK error output
            sys.stderr = io.StringIO()

            loop.run_until_complete(run_agent(user_prompt))
        except Exception as e:
            # Only log non-cancellation errors
            error_msg = str(e)
            if 'cancel scope' not in error_msg.lower() and 'cancel' not in error_msg.lower():
                # Restore stderr for actual errors
                sys.stderr = old_stderr
                socketio.emit('error', {'message': f'Thread error: {error_msg}'})
        finally:
            # Restore stderr
            sys.stderr = old_stderr

            # Graceful cleanup
            try:
                if not loop.is_closed():
                    try:
                        loop.run_until_complete(asyncio.sleep(0.05))
                    except:
                        pass
                    loop.close()
            except Exception:
                pass

    thread = threading.Thread(target=run_in_thread)
    thread.daemon = True
    thread.start()


@socketio.on('permission_response')
def handle_permission_response(data):
    """Handle user's permission grant/deny"""
    global permission_response
    permission_response = {
        'granted': data.get('granted', False),
        'tool': data.get('tool', '')
    }


@socketio.on('close_browser')
def handle_close_browser():
    """Close browser on request"""
    def close_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(close_browser())
            socketio.emit('status', {'message': 'Browser closed', 'type': 'success'})
        finally:
            loop.close()

    thread = threading.Thread(target=close_in_thread)
    thread.daemon = True
    thread.start()


if __name__ == '__main__':
    print("=" * 80)
    print("FLASK SERVER WITH BROWSER AUTOMATION")
    print("=" * 80)
    if BROWSER_AVAILABLE:
        print("✅ Playwright installed - Browser automation enabled")
    else:
        print("⚠️  Install Playwright: pip install playwright && playwright install chromium")
    print("=" * 80)
    print("Open your browser and navigate to: http://localhost:5001")
    print("=" * 80)
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
