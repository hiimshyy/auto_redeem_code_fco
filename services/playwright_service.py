from typing import List, Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from utils.logger import get_logger

logger = get_logger()

# Standard selector for the coupon input
_INPUT_SELECTOR = 'input[name="coupon"], input[id*="coupon"], input[placeholder*="Code"]'

class PlaywrightService:
    """
    Manages a single Playwright browser instance and its contexts/pages.
    Headless is explicitly False so the user can log in manually.
    """

    def __init__(self) -> None:
        self._playwright_context_mgr = None
        self._playwright = None
        self._browser: Optional[Browser] = None

    def start_browser(self) -> None:
        """Launch the Playwright browser instance (headful)."""
        logger.info("Starting Playwright browser instance...")
        self._playwright_context_mgr = sync_playwright()
        self._playwright = self._playwright_context_mgr.__enter__()
        
        # We use Chromium by default
        self._browser = self._playwright.chromium.launch(
            headless=False,
            # Arguments to reduce crashing / anti-bot flags occasionally
            args=["--disable-blink-features=AutomationControlled"]
        )
        logger.debug("Browser started successfully.")

    def create_pages(self, n: int) -> List[Page]:
        """Create N isolated incognito pages/contexts."""
        if not self._browser:
            raise RuntimeError("Browser not started. Call start_browser() first.")
            
        logger.info("Creating %d browser contexts/pages...", n)
        pages = []
        for i in range(n):
            # Create a new isolated context for each window so they don't share cookies
            # (allowing the user to log into multiple different Garena accounts)
            context: BrowserContext = self._browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            pages.append(page)
            logger.debug("Target %d created.", i + 1)
        return pages

    def navigate_all(self, pages: List[Page], url: str) -> None:
        """Navigate all given pages to the URL."""
        logger.info("Navigating %d pages to %s...", len(pages), url)
        for i, page in enumerate(pages):
            try:
                page.goto(url, wait_until="domcontentloaded")
                logger.debug("Page %d navigated.", i + 1)
            except Exception as e:
                logger.error("Failed to navigate page %d: %s", i + 1, e)

    def fill_coupon(self, page: Page, code: str) -> bool:
        """Fill the coupon code into the page without auto-submitting."""
        try:
            # Wait briefly to ensure the input field is ready
            # We don't fail hard if it's missing, just handle the exception
            page.wait_for_selector(_INPUT_SELECTOR, state="visible", timeout=3000)
            page.fill(_INPUT_SELECTOR, code)
            return True
        except Exception as e:
            logger.error("Failed to fill coupon code on page: %s", e)
            return False

    def get_page_url(self, page: Page) -> str:
        """Safe URL getter handling disconnected pages."""
        try:
            return page.url
        except Exception:
            return "<closed>"

    def shutdown(self) -> None:
        """Close browser and Release resources."""
        logger.info("Shutting down PlaywrightService...")
        if self._browser:
            try:
                self._browser.close()
            except Exception as e:
                logger.error("Error closing browser: %s", e)
        
        if self._playwright_context_mgr:
            try:
                self._playwright_context_mgr.__exit__(None, None, None)
            except Exception as e:
                logger.error("Error exiting playwright context: %s", e)
                
        self._browser = None
        self._playwright = None
        self._playwright_context_mgr = None
        logger.debug("PlaywrightService shutdown complete.")