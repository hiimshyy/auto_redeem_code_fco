from telegram.ext import ApplicationBuilder, MessageHandler, filters
from utils.logger import setup_logger

logger = setup_logger()

class TelegramBot:
    def __init__(self, token, queue):
        self.queue = queue
        self.app = ApplicationBuilder().token(token).build()

        self.app.add_handler(
            MessageHandler(filters.TEXT, self.handle)
        )

    async def handle(self, update, context):
        code = update.message.text.strip()
        self.queue.push(code)

        logger.info(f"Received code: {code}")
        await update.message.reply_text(f"Queued: {code}")

    def run(self):
        self.app.run_polling()