"""
config/settings.py
Centralized configuration for the broadcast bot.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")

class Settings:
    # ------------------------------------------------------------------ #
    # Telegram
    # ------------------------------------------------------------------ #
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

    # ------------------------------------------------------------------ #
    # Application / Broadcast
    # ------------------------------------------------------------------ #
    COUPON_URL: str = os.getenv("COUPON_URL", "https://coupon.fconline.garena.vn/")
    MAX_WINDOWS: int = int(os.getenv("MAX_WINDOWS", "5"))
    BROADCAST_DELAY: float = float(os.getenv("BROADCAST_DELAY", "0.5"))

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #
    LOG_DIR: str = os.getenv("LOG_DIR", str(_BASE_DIR / "logs"))
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "5000000"))
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "3"))

    def validate(self) -> None:
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is missing in environment variables.")

settings = Settings()
