import asyncio
import websockets
import json
import sys

def run_diagnostics():
    """Prints diagnostic information to identify environment issues."""
    print("=" * 60)
    print("🐍 Running Environment Diagnostics...")
    print(f"   Python Executable: {sys.executable}")
    print(f"   Python Version:    {sys.version.split()[0]}")

    try:
        import websockets
        print(f"   Websockets Version:  {websockets.__version__}")
        print(f"   Websockets Path:     {websockets.__file__}")

        # Version check
        if tuple(map(int, websockets.__version__.split('.'))) < (12, 0):
            print("\n❌ CRITICAL ERROR: Your websockets version is too old.")
            print("   Please upgrade: pip install --upgrade websockets")
            return False

    except ImportError:
        print("\n❌ CRITICAL ERROR: The 'websockets' library is not installed.")
        print("   Please run: pip install websockets")
        return False
    except Exception as e:
        print(f"   An unexpected error occurred: {e}")
        return False

    print("   ✅ Environment check passed.")
    print("=" * 60)
    return True


async def run_websocket_test():
    """Connects to the streaming endpoint and prints the agent's response."""
    uri = "ws://localhost:8000/chat/stream"
    print(f"🚀 Connecting to WebSocket at {uri}")

    try:
        # Try with additional_headers first (correct parameter for websockets 15.0.1)
        try:
            async with websockets.connect(
                uri, additional_headers={"Origin": "http://localhost:3000"}
            ) as websocket:
                print("✅ Connected! Sending a message to the agent...")
                await test_websocket_communication(websocket)
        except TypeError as e:
            if "unexpected keyword argument" in str(e):
                print("   additional_headers not supported, trying without headers...")
                async with websockets.connect(uri) as websocket:
                    print("✅ Connected! Sending a message to the agent...")
                    await test_websocket_communication(websocket)
            else:
                raise

    except Exception as e:
        print(f"❌ An error occurred: {e}")


async def test_websocket_communication(websocket):
    """Test the WebSocket communication once connected."""
    # Send a message in LangServe format
    input_data = {
        "input": {
            "input": "What time is it in Amsterdam and SF, Cali?",
            "chat_history": []
        }
    }

    await websocket.send(json.dumps([input_data]))
    print("\n⏳ Waiting for response stream from agent...\n---")

    # Listen for responses
    while True:
        try:
            message = await websocket.recv()
            data = json.loads(message)
            
            # Handle different event types
            if data.get('event') == 'on_chat_model_stream':
                chunk = data.get('data', {}).get('chunk', {})
                if 'content' in chunk:
                    print(chunk['content'], end="", flush=True)
            elif data.get('event') == 'on_chat_model_end':
                print("\n---\n✅ Stream finished.")
                break
            elif data.get('event') == 'error':
                error = data.get('data', {}).get('error', 'Unknown error')
                print(f"\n❌ Error: {error}")
                break

        except websockets.ConnectionClosed:
            print("\n---\n✅ Connection closed by server.")
            break


if __name__ == "__main__":
    # Windows compatibility
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if run_diagnostics():
        asyncio.run(run_websocket_test())
    else:
        print("\nAborting due to critical environment error.")
        sys.exit(1)
