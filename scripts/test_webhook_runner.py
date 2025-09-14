"""
A simple script to test the generic webhook endpoint of the SuperAgentServer.
"""

import sys
import json
import requests


def run_webhook_test(message: str, user_id: str = "cli-user", platform: str = "cli-test"):
    """Sends a message to the generic webhook endpoint."""
    url = "http://localhost:8000/webhook"
    payload = {"message": message, "user_id": user_id, "platform": platform}
    headers = {"Content-Type": "application/json"}

    print(f"🚀 Sending POST request to {url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        print("\n✅ Success! Server responded with:")
        print(json.dumps(response.json(), indent=2))

    except requests.exceptions.RequestException as e:
        print(f"\n❌ An error occurred: {e}")
        print("   Please ensure the SuperAgentServer is running on http://localhost:8000")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        message_to_send = " ".join(sys.argv[1:])
    else:
        message_to_send = "Hello from the webhook test script!"

    run_webhook_test(message_to_send)