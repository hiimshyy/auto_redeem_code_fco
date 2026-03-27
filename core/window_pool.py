from typing import List
import time
from playwright.sync_api import Page
from services.playwright_service import PlaywrightService
from config.settings import settings
from utils.logger import get_logger

logger = get_logger()

class WindowPool:
    """
    Manages a pool of Playwright pages and implements the Broadcast Service.
    """

    def __init__(self, pw_service: PlaywrightService) -> None:
        self._pw_service = pw_service
        self._pages: List[Page] = []
        
    def setup_pages(self, n: int) -> None:
        """Create N pages and navigate them to the target URL."""
        if n < 1 or n > settings.MAX_WINDOWS:
            raise ValueError(f"Number of windows must be between 1 and {settings.MAX_WINDOWS}")
            
        self._pw_service.start_browser()
        self._pages = self._pw_service.create_pages(n)
        self._pw_service.navigate_all(self._pages, settings.COUPON_URL)
        logger.info("Window pool set up with %d pages.", n)

    def fill_all(self, code: str) -> dict:
        """
        Broadcasts the coupon code to all pages sequentially.
        Returns a dictionary mapping window index to success (bool).
        """
        results = {}
        successful = 0
        
        for i, page in enumerate(self._pages):
            try:
                # Page could have been closed manually by the user
                if page.is_closed():
                    logger.warning("Window %d is closed. Skipping.", i + 1)
                    results[i] = False
                    continue
                    
                logger.debug("Filling code into window %d...", i + 1)
                success = self._pw_service.fill_coupon(page, code)
                results[i] = success
                if success:
                    successful += 1
                
                # Small delay between pages as requested
                time.sleep(settings.BROADCAST_DELAY)
                
            except Exception as e:
                logger.error("Unexpected error filling window %d: %s", i + 1, e)
                results[i] = False
                
        logger.info("Broadcast complete. Filled %d/%d windows.", successful, len(self._pages))
        return results

    def get_count(self) -> int:
        """Return the total number of managed pages."""
        return len(self._pages)

    def get_active_count(self) -> int:
        """Return the count of pages that are still open."""
        return sum(1 for p in self._pages if not p.is_closed())

    def cleanup(self) -> None:
        """Clean up all pages and the browser via the PlaywrightService."""
        logger.info("Cleaning up window pool...")
        self._pages.clear()
        self._pw_service.shutdown()
