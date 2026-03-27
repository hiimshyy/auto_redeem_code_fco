import threading
from typing import Optional
from core.window_pool import WindowPool
from services.playwright_service import PlaywrightService
from utils.logger import get_logger

logger = get_logger()

class SessionManager:
    """
    Singleton-like session controller managing the active broadcast session.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._is_active: bool = False
        self._window_pool: Optional[WindowPool] = None
        
    @property
    def is_active(self) -> bool:
        """Check if a session is currently running."""
        with self._lock:
            return self._is_active

    def start_session(self, n_windows: int) -> int:
        """
        Starts a new session, creating N windows.
        Returns the number of windows successfully created.
        Raises ValueError if a session is already active or N is invalid.
        """
        with self._lock:
            if self._is_active:
                raise ValueError("A session is already active. Send /end to close it first.")
                
            logger.info("Starting new broadcast session with %d windows...", n_windows)
            
            try:
                pw_service = PlaywrightService()
                self._window_pool = WindowPool(pw_service)
                self._window_pool.setup_pages(n_windows)
                
                self._is_active = True
                return self._window_pool.get_count()
            except Exception as e:
                logger.error("Failed to start session: %s", e)
                if self._window_pool:
                    self._window_pool.cleanup()
                self._window_pool = None
                self._is_active = False
                raise

    def get_window_pool(self) -> Optional[WindowPool]:
        """Accessor for the active window pool, intended for broadcasting codes."""
        with self._lock:
            if not self._is_active:
                return None
            return self._window_pool

    def broadcast_code(self, code: str) -> dict:
        """
        Broadcasts the code to all windows in the pool.
        Returns a dictionary mapping window index to success bool.
        Raises ValueError if no session is active.
        """
        with self._lock:
            if not self._is_active or not self._window_pool:
                raise ValueError("No active session to broadcast to.")
                
            logger.info("Broadcasting code %r", code)
            return self._window_pool.fill_all(code)

    def stop_session(self) -> None:
        """Stops the session and closes all browsers."""
        with self._lock:
            if not self._is_active:
                logger.info("Stop requested, but no session is active.")
                return
                
            logger.info("Stopping active broadcast session...")
            if self._window_pool:
                try:
                    self._window_pool.cleanup()
                except Exception as e:
                    logger.error("Error cleaning up window pool: %s", e)
                self._window_pool = None
                
            self._is_active = False
            logger.info("Session stopped completely.")
