# FC Online Multi-Window Coupon Bot

A personal Telegram bot that opens multiple isolated browser windows for you to manually log into, and then broadcasts coupon codes to all of them simultaneously.

## Features

- **Multi-Window Support**: Open up to 5 isolated browser windows at once (`/start [n]`). Each window maintains its own separate cookie session, allowing you to manually log into 5 different Garena accounts.
- **Broadcast System**: Paste a coupon code into Telegram, and the bot will instantly type it into all active windows.
- **Strictly Manual Login**: To adhere to strict security constraints, this bot does *not* bypass CAPTCHAs and does *not* auto-login. You press "Submit" yourself. 

## Requirements

- Python 3.9+
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))

## Setup Instructions

1. **Clone the repository and enter the directory**:
   ```powershell
   cd Auto_redeem
   ```

2. **Create and activate a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure environment variables**:
   Create a `.env` file in the root directory (or copy `.env.example`):
   ```env
   TELEGRAM_BOT_TOKEN="your-bot-token-here"
   COUPON_URL="https://coupon.fconline.garena.vn/"
   ```

5. **Run the bot**:
   ```powershell
   python app.py
   ```

## Usage

1. Message your bot on Telegram with `/start 3` (to open 3 windows, for example).
2. The bot will open 3 Chromium browser windows.
3. **Manually log in** to your different FC Online/Garena accounts in each window.
4. When you get a coupon code, just send it as a message to the bot.
5. The bot will broadcast the code by typing it into the coupon field on all 3 windows.
6. **Manually click Submit** in each window.
7. Send `/end` to safely close the session and browsers.

## Architecture & Design

Built with a clean, thread-safe architecture:
- `bot.telegram_bot`: Async command handlers and thread-executor dispatches.
- `core.session_manager`: Singleton-like controller for the active broadcast session.
- `core.window_pool`: Playwright `Page` state management and loop dispatcher.
- `services.playwright_service`: Synchronous interactions with the DOM.
