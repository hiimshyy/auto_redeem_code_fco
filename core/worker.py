from utils.logger import setup_logger
from core.retry import retry

logger = setup_logger()

class Worker:
    def __init__(self, queue, browser_service):
        self.queue = queue
        self.browser = browser_service

    def process(self, code):
        logger.info(f"Processing: {code}")

        def task():
            self.browser.open_page()
            self.browser.fill_coupon(code)
            return True

        retry(task)
        logger.info(f"Done: {code}")

    def run(self):
        while True:
            code = self.queue.pop()
            try:
                self.process(code)
            except Exception as e:
                logger.error(f"Failed {code}: {e}")