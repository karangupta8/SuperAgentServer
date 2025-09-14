# Telegram Integration

This guide explains how to connect your SuperAgentServer to Telegram, enabling bi-directional communication with your agent via a Telegram bot.

## Overview

The Telegram adapter works by using a webhook. When a user sends a message to your bot, Telegram forwards it to your server. Your agent processes the message and sends a reply back to the user through the Telegram Bot API.

## Prerequisites

Before you begin, you will need:
1.  **A Telegram Bot Token**: Create a bot by talking to the `@BotFather` on Telegram.
2.  **Your Chat ID**: Get your personal user ID by sending a message to a bot like `@userinfobot`.
3.  **A Public URL**: Your server must be accessible from the internet. We recommend using ngrok for local development.

## Step 1: Configure Your Environment

Your server needs the bot token and your chat ID to communicate with Telegram.

1.  Open your `.env` file.
2.  Add the following lines, replacing the placeholder values with your own:

    ```env
    # .env
    TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
    TELEGRAM_CHAT_ID=123456789
    ```

## Step 2: Expose Your Server with ngrok

Telegram cannot send webhooks to `localhost`. You need a public URL.

1.  **Install ngrok** if you haven't already.
2.  In a new terminal, start ngrok to expose your local server on port 8000:
    ```bash
    ngrok http 8000
    ```
3.  **Copy the `https` URL** provided by ngrok. It will look something like `https://<random-string>.ngrok-free.app`.

## Step 3: Register the Webhook

Now, tell Telegram where to send messages using the `telegram_setup.py` script.

1.  In another terminal, run the following command. **Replace `<your-ngrok-url>`** with the URL you copied from ngrok.
    ```bash
    python scripts/telegram_setup.py set-webhook <your-ngrok-url>/webhook/telegram
    ```
    For example:
    ```bash
    python scripts/telegram_setup.py set-webhook https://8a2b-192-0-2-1.ngrok-free.app/webhook/telegram
    ```
2.  You should see a success message confirming the webhook was set.

## Step 4: Run SuperAgentServer

With the webhook registered, start your server.

1.  In a separate terminal, run the development server:
    ```bash
    python scripts/dev_runner.py
    ```

## Step 5: Test the Integration

You are now ready to chat with your agent!

1.  **Incoming Message**: Open Telegram and send a message to your bot. You should see activity in the `dev_runner.py` terminal, and your agent will reply in the Telegram chat.
2.  **Outgoing Message**: To test if the server can initiate a message, use the `telegram_setup.py` script:
    ```bash
    python scripts/telegram_setup.py send-message "This is a test from the server."
    ```
    You should receive this message from your bot in Telegram.

## Managing Your Integration with `telegram_setup.py`

The `telegram_setup.py` script is your primary tool for managing the Telegram integration. Beyond the initial setup, it provides several commands for testing and maintenance.

-   **Set or Update the Webhook**: Registers your server's public URL with Telegram. You must run this whenever your public URL changes (e.g., when you restart ngrok).
    ```bash
    python scripts/telegram_setup.py set-webhook <your-ngrok-url>/webhook/telegram
    ```

-   **Get Webhook Info**: Fetches and displays the current webhook configuration from Telegram. This is useful for debugging and confirming that your webhook is set correctly.
    ```bash
    python scripts/telegram_setup.py get-info
    ```

-   **Delete Webhook**: Removes the webhook from your bot. It's good practice to run this when you shut down your server or ngrok tunnel to prevent Telegram from sending requests to a dead endpoint.
    ```bash
    python scripts/telegram_setup.py delete-webhook
    ```

-   **Send a Test Message**: Sends a message *from* your server *to* your Telegram chat. This directly tests the outbound part of the connection and confirms your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correct.
    ```bash
    python scripts/telegram_setup.py send-message "Testing outbound message."
    ```
