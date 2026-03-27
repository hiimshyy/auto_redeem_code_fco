"""
Telegram bot – handles `/start`, `/end`, and code broadcasting.
"""
import asyncio
from typing import Optional
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, Application,
    CommandHandler, MessageHandler,
    ContextTypes, filters,
)

from config.settings import settings
from core.session_manager import SessionManager
from utils.logger import get_logger

logger = get_logger()

class TelegramBot:
    """Telegram interface for the Multi-Window Broadcast System."""

    def __init__(self, token: str, session_manager: SessionManager) -> None:
        self._sm = session_manager
        self._app: Application = ApplicationBuilder().token(token).build()
        self._register_handlers()

    def run(self) -> None:
        """Run the bot in polling mode. Blocks until interrupted."""
        logger.info("Starting Telegram bot polling...")
        self._app.run_polling(drop_pending_updates=True)

    def _register_handlers(self) -> None:
        add = self._app.add_handler
        add(CommandHandler("start", self._cmd_start))
        add(CommandHandler("end", self._cmd_end))
        # Any text message that isn't a command is treated as a coupon code
        add(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_coupon))

    # ──────────────────────────────────────────────────────────────────────
    # Commands
    # ──────────────────────────────────────────────────────────────────────

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start [n] to initialise the session."""
        if self._sm.is_active:
            await update.message.reply_text("⚠️ A session is already active. Send /end to close it first.")
            return

        # Parse number of windows
        n_windows = 1
        if context.args:
            try:
                n_windows = int(context.args[0])
            except ValueError:
                await update.message.reply_text("❌ Invalid number. Usage: `/start [n]`")
                return

        # Enforce limits
        if n_windows < 1 or n_windows > settings.MAX_WINDOWS:
            await update.message.reply_text(f"❌ Allowable window count is between 1 and {settings.MAX_WINDOWS}.")
            return

        try:
            await update.message.reply_text(f"⏳ Opening {n_windows} windows. Please wait...")
            
            # Start session blocks while Playwright launches since it's synchronous
            # To avoid freezing the entire bot event loop, we run it in a thread executor
            loop = asyncio.get_event_loop()
            actual_count = await loop.run_in_executor(None, self._sm.start_session, n_windows)
            
            await update.message.reply_text(f"✅ Opened {actual_count} windows. Please login manually on each one.")
        except Exception as e:
            logger.error("Error during /start: %s", e)
            await update.message.reply_text(f"❌ Failed to start session: {e}")

    async def _cmd_end(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /end to close the session."""
        if not self._sm.is_active:
            await update.message.reply_text("Session already closed.")
            return

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._sm.stop_session)
            await update.message.reply_text("✅ Session closed.")
        except Exception as e:
            logger.error("Error during /end: %s", e)
            await update.message.reply_text(f"❌ Failed to close session: {e}")

    # ──────────────────────────────────────────────────────────────────────
    # Broadcast Handling
    # ──────────────────────────────────────────────────────────────────────

    async def _handle_coupon(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Treat text messages as coupons and broadcast them."""
        text = update.message.text.strip()
        
        if not text:
            return
            
        if not self._sm.is_active:
            await update.message.reply_text("⚠️ No active session. Send `/start [n]` first.")
            return

        pool = self._sm.get_window_pool()
        if not pool:
            await update.message.reply_text("⚠️ Internal error: Window pool unavailable.")
            return

        window_count = pool.get_active_count()
        if window_count == 0:
            await update.message.reply_text("⚠️ All windows appear to be closed. Send `/end` then `/start` again.")
            return

        # Acknowledge receipt immediately
        ack_msg = await update.message.reply_text(f"⚙️ Filling code `{text}` into {window_count} window(s)...", parse_mode="Markdown")
        
        try:
            # Broadcast the code synchronously via thread executor
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self._sm.broadcast_code, text)
            
            successes = sum(1 for status in results.values() if status)
            failures = len(results) - successes
            
            result_text = f"✅ Code `{text}` filled into {successes} window(s)."
            if failures > 0:
                result_text += f"\n⚠️ Failed to fill {failures} window(s). Ensure they are logged in and navgated to the coupon page."
                
            await ack_msg.edit_text(result_text, parse_mode="Markdown")
            
        except Exception as e:
            logger.error("Broadcast failed for code %r: %s", text, e)
            await update.message.reply_text(f"❌ Broadcast failed: {e}")