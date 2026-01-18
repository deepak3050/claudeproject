import asyncio
import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from claude_agent_sdk import query, ClaudeAgentOptions
import threading
from queue import Queue

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state for managing permission requests
permission_queue = Queue()
permission_response = {}
conversation_active = False

# Pre-approved common tools - user can add more via UI
# These are commonly used tools that are generally safe
allowed_tools_set = {
    'WebSearch',
    'WebFetch',
    'Read',
    'Glob',
    'Grep',
    'Bash',
    'Write',
    'Edit',
    # Playwright MCP tools for browser automation
    'mcp__playwright__browser_navigate',
    'mcp__playwright__browser_snapshot',
    'mcp__playwright__browser_click',
    'mcp__playwright__browser_type',
    'mcp__playwright__browser_evaluate',
    'mcp__playwright__browser_take_screenshot',
    'mcp__playwright__browser_fill_form',
    'mcp__playwright__browser_select_option',
    'mcp__playwright__browser_hover',
    'mcp__playwright__browser_wait_for',
    'mcp__playwright__browser_console_messages',
    'mcp__playwright__browser_network_requests',
    'mcp__playwright__browser_navigate_back',
    'mcp__playwright__browser_tabs',
    'mcp__playwright__browser_close',
    'mcp__playwright__browser_resize',
    'mcp__playwright__browser_handle_dialog',
    'mcp__playwright__browser_file_upload',
    'mcp__playwright__browser_press_key',
    'mcp__playwright__browser_drag',
    'mcp__playwright__browser_run_code',
    'mcp__playwright__browser_install'
}

# Configuration
USE_API = 0  # 0 = Pro Subscription, 1 = API Key


def format_message(msg):
    """Format message for display in UI"""
    msg_type = type(msg).__name__

    # Skip SystemMessage - too verbose
    if msg_type == 'SystemMessage':
        return None

    # Extract clean content from messages
    if hasattr(msg, 'content') and isinstance(msg.content, list):
        formatted_parts = []

        for block in msg.content:
            block_type = type(block).__name__

            if block_type == 'TextBlock':
                # Extract just the text
                formatted_parts.append(f"📝 {block.text}")

            elif block_type == 'ToolUseBlock':
                # Show tool being used
                tool_name = block.name
                formatted_parts.append(f"🔧 Using tool: {tool_name}")

            elif block_type == 'ToolResultBlock':
                # Show tool results (truncated)
                content_str = str(block.content)
                if len(content_str) > 300:
                    content_str = content_str[:300] + "..."
                if not block.is_error:
                    formatted_parts.append(f"✅ Tool completed")
                else:
                    formatted_parts.append(f"❌ Tool error: {content_str}")

        if formatted_parts:
            return {
                'type': msg_type,
                'content': '\n'.join(formatted_parts)
            }

    # For ResultMessage, show summary
    if msg_type == 'ResultMessage' and hasattr(msg, 'result'):
        result_text = str(msg.result)
        if len(result_text) > 2000:
            result_text = result_text[:2000] + "..."
        return {
            'type': 'Final Result',
            'content': f"📊 {result_text}"
        }

    return None  # Skip other message types


async def run_agent(user_prompt):
    """Run the Claude agent and handle permission requests"""
    global conversation_active, allowed_tools_set
    conversation_active = True

    # Show currently allowed tools
    if allowed_tools_set:
        socketio.emit('status', {
            'message': f'Starting agent with allowed tools: {", ".join(allowed_tools_set)}',
            'type': 'info'
        })
    else:
        socketio.emit('status', {'message': 'Starting agent (no tools allowed yet)...', 'type': 'info'})

    # Determine authentication method and setup options
    if USE_API == 1:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            socketio.emit('error', {'message': 'ANTHROPIC_API_KEY not set!'})
            conversation_active = False
            return
        # Start with allowed tools that have been granted
        options = ClaudeAgentOptions(
            api_key=api_key,
            allowed_tools=list(allowed_tools_set) if allowed_tools_set else None
        )
    else:
        # Start with allowed tools that have been granted
        options = ClaudeAgentOptions(
            allowed_tools=list(allowed_tools_set) if allowed_tools_set else None
        )

    try:
        async for msg in query(prompt=user_prompt, options=options):
            # Format and send message to UI
            formatted_msg = format_message(msg)
            if formatted_msg:  # Only emit if we have formatted content
                socketio.emit('message', formatted_msg)

            # Check for permission requests
            if hasattr(msg, 'content') and isinstance(msg.content, list):
                for block in msg.content:
                    # Check if this is a permission error
                    if hasattr(block, 'is_error') and block.is_error:
                        content_str = str(block.content) if hasattr(block, 'content') else str(block)
                        if 'permission' in content_str.lower() and 'requested permissions to use' in content_str:
                            # Extract tool name from error message
                            tool_name = extract_tool_name(content_str)

                            # Send permission request to UI
                            socketio.emit('permission_request', {
                                'tool': tool_name,
                                'message': content_str
                            })

                            # Wait for user response
                            response = await wait_for_permission_response()

                            if response['granted']:
                                # Add tool to allowed set
                                allowed_tools_set.add(tool_name)

                                socketio.emit('status', {
                                    'message': f'✓ Permission granted for {tool_name}',
                                    'type': 'success'
                                })

                                socketio.emit('permission_granted', {
                                    'tool': tool_name,
                                    'message': f'Permission has been granted for {tool_name}. Click "Start Agent" again to retry with this permission.'
                                })

                                # Let the query finish normally
                                conversation_active = False
                                return
                            else:
                                socketio.emit('status', {
                                    'message': f'✗ Permission denied for {tool_name}',
                                    'type': 'warning'
                                })
                                conversation_active = False
                                return

            # Check if conversation is complete
            if hasattr(msg, 'subtype') and msg.subtype == 'success':
                socketio.emit('status', {
                    'message': '✓ Conversation complete!',
                    'type': 'success'
                })

                # Display token usage if available
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
                return

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        socketio.emit('error', {'message': f'Error: {str(e)}\n\nDetails:\n{error_details}'})
        conversation_active = False


def extract_tool_name(error_message):
    """Extract tool name from permission error message"""
    # Example: "Claude requested permissions to use WebSearch"
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

    # Wait for response (with timeout)
    timeout = 300  # 5 minutes
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
    emit('status', {'message': 'Connected to server', 'type': 'success'})


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

    # Run agent in background thread
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_agent(user_prompt))
        except Exception as e:
            socketio.emit('error', {'message': f'Thread error: {str(e)}'})
        finally:
            # Improved cleanup to avoid cancel scope errors
            try:
                # Get all pending tasks
                pending = asyncio.all_tasks(loop)
                if pending:
                    # Cancel them without waiting in the same context
                    for task in pending:
                        task.cancel()
                    # Give them a moment to cancel
                    loop.run_until_complete(asyncio.sleep(0.1))
            except Exception as e:
                pass  # Ignore errors during cleanup
            finally:
                try:
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


@socketio.on('get_allowed_tools')
def handle_get_allowed_tools():
    """Send current list of allowed tools to client"""
    emit('allowed_tools_list', {'tools': list(allowed_tools_set)})


@socketio.on('remove_tool')
def handle_remove_tool(data):
    """Remove a tool from allowed tools (for testing permission system)"""
    global allowed_tools_set
    tool = data.get('tool', '')
    if tool in allowed_tools_set:
        allowed_tools_set.remove(tool)
        emit('allowed_tools_list', {'tools': list(allowed_tools_set)})
        emit('status', {'message': f'Removed {tool} from allowed tools', 'type': 'warning'})


@socketio.on('add_tool')
def handle_add_tool(data):
    """Add a tool to allowed tools"""
    global allowed_tools_set
    tool = data.get('tool', '')
    if tool:
        allowed_tools_set.add(tool)
        emit('allowed_tools_list', {'tools': list(allowed_tools_set)})
        emit('status', {'message': f'Added {tool} to allowed tools', 'type': 'success'})


if __name__ == '__main__':
    print("=" * 80)
    print("FLASK SERVER STARTING")
    print("=" * 80)
    print("Open your browser and navigate to: http://localhost:5000")
    print("=" * 80)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
