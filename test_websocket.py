import asyncio
import websockets
import json

async def run_websocket_test():
    """Connects to the streaming endpoint and prints the agent's response."""

    # The LangServe WebSocket endpoint is at /chat/stream
    uri = "ws://localhost:8000/chat/stream"

    print(f"🚀 Connecting to WebSocket at {uri}")

    try:
        # Add an Origin header to satisfy the server's CORS policy.
        # This is the standard way to add headers with a modern `websockets` library.
        async with websockets.connect(
            uri, extra_headers={"Origin": "http://localhost"}
        ) as websocket:
            print("✅ Connected! Sending a message to the agent...")

            # The input format for the agent_executor is a dictionary
            # with an "input" key.
            input_data = {
                "input": {
                    "input": "What time is it in Amsterdam and SF, Cali?",
                    "chat_history": [] # You can manage chat history here
                }
            }

            # LangServe expects a specific structure: a list of inputs.
            # We are sending one request.
            await websocket.send(json.dumps([input_data]))

            print("\n⏳ Waiting for response stream from agent...\n---")

            # The agent will stream back chunks of the response.
            # We'll print them as they arrive.
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    # LangServe streams events; we are interested in the content chunks.
                    if data['event'] == 'on_chat_model_stream':
                        chunk = data['data']['chunk']
                        if 'content' in chunk:
                            print(chunk['content'], end="", flush=True)

                except websockets.ConnectionClosed:
                    print("\n---\n✅ Connection closed by server. Stream finished.")
                    break

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(run_websocket_test())
