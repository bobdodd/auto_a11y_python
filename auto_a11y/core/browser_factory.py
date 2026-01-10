"""
Browser factory for selecting between Playwright and Pyppeteer engines.

This module provides a factory function to create the appropriate BrowserManager
based on the configured browser engine. This allows gradual migration from
Pyppeteer to Playwright without breaking existing code.

Usage:
    from auto_a11y.core.browser_factory import create_browser_manager

    # Uses engine from config (default: playwright)
    manager = create_browser_manager(config)

    # Or explicitly specify engine
    manager = create_browser_manager(config, engine='playwright')
    manager = create_browser_manager(config, engine='pyppeteer')
"""

import logging
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from auto_a11y.core.browser_manager import BrowserManager as PyppeteerBrowserManager
    from auto_a11y.core.browser_manager_playwright import BrowserManager as PlaywrightBrowserManager

logger = logging.getLogger(__name__)


def create_browser_manager(
    config: Dict[str, Any],
    engine: Optional[str] = None
) -> 'PyppeteerBrowserManager | PlaywrightBrowserManager':
    """
    Create a BrowserManager instance using the specified or configured engine.

    Args:
        config: Browser configuration dictionary
        engine: Browser engine to use ('playwright' or 'pyppeteer').
                If not specified, uses BROWSER_ENGINE from config.

    Returns:
        BrowserManager instance (either Playwright or Pyppeteer based)

    Raises:
        ValueError: If unknown engine is specified
        ImportError: If required browser library is not installed
    """
    # Determine which engine to use
    if engine is None:
        engine = config.get('BROWSER_ENGINE', config.get('browser_engine', 'playwright'))

    engine = engine.lower()

    if engine == 'playwright':
        try:
            from auto_a11y.core.browser_manager_playwright import BrowserManager
            logger.info("Using Playwright browser engine")
            return BrowserManager(config)
        except ImportError as e:
            logger.error(f"Failed to import Playwright: {e}")
            logger.error("Install with: pip install playwright && playwright install chromium")
            raise

    elif engine == 'pyppeteer':
        try:
            from auto_a11y.core.browser_manager import BrowserManager
            logger.info("Using Pyppeteer browser engine (legacy)")
            return BrowserManager(config)
        except ImportError as e:
            logger.error(f"Failed to import Pyppeteer: {e}")
            logger.error("Install with: pip install pyppeteer")
            raise

    else:
        raise ValueError(f"Unknown browser engine: {engine}. Use 'playwright' or 'pyppeteer'.")


def get_browser_engine_name(config: Dict[str, Any]) -> str:
    """
    Get the name of the configured browser engine.

    Args:
        config: Browser configuration dictionary

    Returns:
        Engine name ('playwright' or 'pyppeteer')
    """
    return config.get('BROWSER_ENGINE', config.get('browser_engine', 'playwright')).lower()


def is_playwright_available() -> bool:
    """
    Check if Playwright is installed and available.

    Returns:
        True if Playwright can be imported
    """
    try:
        import playwright
        return True
    except ImportError:
        return False


def is_pyppeteer_available() -> bool:
    """
    Check if Pyppeteer is installed and available.

    Returns:
        True if Pyppeteer can be imported
    """
    try:
        import pyppeteer
        return True
    except ImportError:
        return False
