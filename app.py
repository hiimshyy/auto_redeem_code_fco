import threading
from bot.telegram_bot import TelegramBot
from core.queue_manager import CouponQueue
from core.worker import Worker
from services.playwright_service import PlaywrightService

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

queue = CouponQueue()
browser = PlaywrightService()
worker = Worker(queue, browser)

bot = TelegramBot(TOKEN, queue)

t1 = threading.Thread(target=worker.run)
t1.start()

bot.run()