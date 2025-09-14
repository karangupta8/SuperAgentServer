"""
A utility script to manage the Telegram bot webhook and test communication.

Usage:
  - Set Webhook: python scripts/telegram_setup.py set-webhook https://your-ngrok-url/webhook/telegram
  - Get Info:    python scripts/telegram_setup.py get-info
  - Send Test:   python scripts/telegram_setup.py send-message "Hello from server!"
  - Delete Webhook: python scripts/telegram_setup.py delete-webhook
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def check_token():
    """Check if the Telegram bot token is set."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN is not set in your .env file.")
        print("   Please get a token from @BotFather on Telegram and add it to your .env file.")
        sys.exit(1)
    print("✅ TELEGRAM_BOT_TOKEN found.")


def set_webhook(url: str):
    """Set the bot's webhook URL."""
    check_token()

    # Add a check to guide the user
    if "/webhook/telegram" not in url:
        print("⚠️  Warning: The provided URL does not seem to point to the Telegram webhook endpoint.")
        print(f"   Your URL: {url}")
        print("   It should typically look like: https://<your-ngrok-url>/webhook/telegram")
        print("   Continuing, but this may not work as expected.")
        print()

    webhook_url = f"{TELEGRAM_API_URL}/setWebhook"
    params = {"url": url}
    print(f"🚀 Setting webhook to: {url}")
    try:
        response = requests.get(webhook_url, params=params)
        response.raise_for_status()
        result = response.json()
        if result.get("ok"):
            print(f"✅ Webhook set successfully! Description: {result.get('description')}")
        else:
            print(f"❌ Failed to set webhook. Reason: {result.get('description')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred: {e}")


def get_webhook_info():
    """Get information about the current webhook."""
    check_token()
    info_url = f"{TELEGRAM_API_URL}/getWebhookInfo"
    print("ℹ️  Fetching webhook info...")
    try:
        response = requests.get(info_url)
        response.raise_for_status()
        print("✅ Success! Current webhook info:")
        import json
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred: {e}")


def delete_webhook():
    """Delete the bot's webhook."""
    check_token()
    delete_url = f"{TELEGRAM_API_URL}/deleteWebhook"
    print("🗑️  Deleting webhook...")
    try:
        response = requests.get(delete_url)
        response.raise_for_status()
        result = response.json()
        if result.get("ok"):
            print("✅ Webhook deleted successfully.")
        else:
            print(f"❌ Failed to delete webhook. Reason: {result.get('description')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred: {e}")


def send_message(message: str):
    """Send a test message to the configured chat ID."""
    check_token()
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("❌ Error: TELEGRAM_CHAT_ID is not set in your .env file.")
        sys.exit(1)

    send_url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    print(f"🚀 Sending message to chat_id {chat_id}...")
    try:
        response = requests.post(send_url, json=payload)
        response.raise_for_status()
        print("✅ Message sent successfully!")
    except requests.exceptions.HTTPError as e:
        print(f"❌ An HTTP error occurred while sending the message: {e}")
        if e.response is not None:
            print(f"   Status Code: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
            if e.response.status_code in [400, 403]:
                print("\n💡 Tip: This error often happens if the bot hasn't been started by the user in the chat.")
                print(f"   Ensure the user corresponding to TELEGRAM_CHAT_ID ({chat_id}) has sent at least one message to the bot.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram Bot Setup Utility for SuperAgentServer.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # set-webhook command
    parser_set = subparsers.add_parser("set-webhook", help="Set the Telegram webhook URL.")
    parser_set.add_argument("url", help="The public URL for the webhook (e.g., from ngrok).")

    # get-info command
    parser_info = subparsers.add_parser("get-info", help="Get current webhook information.")

    # delete-webhook command
    parser_delete = subparsers.add_parser("delete-webhook", help="Delete the current webhook.")

    # send-message command
    parser_send = subparsers.add_parser("send-message", help="Send a test message.")
    parser_send.add_argument("message", help="The message to send.")

    args = parser.parse_args()

    if args.command == "set-webhook":
        set_webhook(args.url)
    elif args.command == "get-info":
        get_webhook_info()
    elif args.command == "delete-webhook":
        delete_webhook()
    elif args.command == "send-message":
        send_message(args.message)