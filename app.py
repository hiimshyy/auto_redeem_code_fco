import signal
import sys
from config.settings import settings
from utils.logger import setup_logger
from core.session_manager import SessionManager
from bot.telegram_bot import TelegramBot

# ── Bootstrap ──────────────────────────────────────────────────────────────
settings.validate()
logger = setup_logger()

# ── Shared objects ──────────────────────────────────────────────────────────
# The architecture no longer uses SQLite or background worker queues.
# Everything is driven directly by the user interacting with the Telegram Bot
# making calls synchronous to the Playwright pages.
session_manager = SessionManager()

# ── Signal handling ─────────────────────────────────────────────────────────
def _shutdown(signum, frame) -> None:
    logger.info("Shutdown signal received (%s). Stopping…", signum)
    session_manager.stop_session()
    sys.exit(0)

signal.signal(signal.SIGINT,  _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


def main() -> None:
    logger.info("=" * 60)
    logger.info("  FC Online Multi-Window Broadcast Bot  – starting up")
    logger.info("=" * 60)

    # Build bot injecting the SessionManager
    bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN, session_manager)

    try:
        bot.run()          # blocks until interrupt
    except KeyboardInterrupt:
        logger.info("Bot polling stopping natively (KeyboardInterrupt).")
    finally:
        logger.info("Cleaning up remaining sessions before exit...")
        session_manager.stop_session()
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    main()