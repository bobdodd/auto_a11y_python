"""
Configuration management for Auto A11y Python
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / 'auto_a11y' / 'scripts'
DATA_DIR = BASE_DIR / 'data'
REPORTS_DIR = BASE_DIR / 'reports'
SCREENSHOTS_DIR = BASE_DIR / 'screenshots'

# Create directories if they don't exist
for directory in [DATA_DIR, REPORTS_DIR, SCREENSHOTS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)


@dataclass
class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST: str = os.getenv('HOST', '127.0.0.1')
    PORT: int = int(os.getenv('PORT', 5001))  # Changed from 5000 to avoid macOS AirPlay Receiver conflict
    
    # Database
    MONGODB_URI: str = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME: str = os.getenv('DATABASE_NAME', 'auto_a11y')
    
    # Claude AI
    CLAUDE_API_KEY: str = os.getenv('CLAUDE_API_KEY', '')
    CLAUDE_MODEL: str = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')
    CLAUDE_MAX_TOKENS: int = int(os.getenv('CLAUDE_MAX_TOKENS', 8192))
    CLAUDE_TEMPERATURE: float = float(os.getenv('CLAUDE_TEMPERATURE', 0.5))
    
    # Pyppeteer
    BROWSER_HEADLESS: bool = os.getenv('BROWSER_HEADLESS', 'True').lower() == 'true'
    BROWSER_TIMEOUT: int = int(os.getenv('BROWSER_TIMEOUT', 30000))
    BROWSER_VIEWPORT_WIDTH: int = int(os.getenv('BROWSER_VIEWPORT_WIDTH', 1920))
    BROWSER_VIEWPORT_HEIGHT: int = int(os.getenv('BROWSER_VIEWPORT_HEIGHT', 1080))
    
    # Scraping
    MAX_PAGES_PER_SITE: int = int(os.getenv('MAX_PAGES_PER_SITE', 50000))
    MAX_CRAWL_DEPTH: int = int(os.getenv('MAX_CRAWL_DEPTH', 10))
    REQUEST_DELAY: float = float(os.getenv('REQUEST_DELAY', 1.0))
    USER_AGENT: str = os.getenv('USER_AGENT', 'Auto-A11y/1.0 Accessibility Scanner')
    RESPECT_ROBOTS_TXT: bool = os.getenv('RESPECT_ROBOTS_TXT', 'True').lower() == 'true'
    
    # Testing
    PARALLEL_TESTS: int = int(os.getenv('PARALLEL_TESTS', 5))
    TEST_TIMEOUT: int = int(os.getenv('TEST_TIMEOUT', 60000))
    RUN_AI_ANALYSIS: bool = os.getenv('RUN_AI_ANALYSIS', 'True').lower() == 'true'
    
    # Developer mode - show error codes in reports (useful for debugging)
    SHOW_ERROR_CODES: bool = os.getenv('SHOW_ERROR_CODES', 'False').lower() == 'true'

    # UI Pagination
    PAGES_PER_PAGE: int = int(os.getenv('PAGES_PER_PAGE', 100))
    MAX_PAGES_PER_PAGE: int = int(os.getenv('MAX_PAGES_PER_PAGE', 500))

    # Paths
    SCRIPTS_DIR: Path = SCRIPTS_DIR
    DATA_DIR: Path = DATA_DIR
    REPORTS_DIR: Path = REPORTS_DIR
    SCREENSHOTS_DIR: Path = SCREENSHOTS_DIR
    
    def validate(self) -> bool:
        """Validate configuration"""
        if self.RUN_AI_ANALYSIS and not self.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY is required when RUN_AI_ANALYSIS is True")
        return True


# Global config instance
config = Config()
config.validate()
