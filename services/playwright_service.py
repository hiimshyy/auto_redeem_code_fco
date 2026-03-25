from playwright.sync_api import sync_playwright

class PlaywrightService:
    def __init__(self):
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch_persistent_context(
            user_data_dir="./user_data",
            headless=False
        )
        self.page = self.browser.new_page()

    def open_page(self):
        self.page.goto("https://coupon.fconline.garena.vn/")

    def fill_coupon(self, code):
        self.page.fill("input[name='coupon']", code)

    def submit(self):
        self.page.click("button[type='submit']")

    def close(self):
        self.browser.close()
        self.p.stop()