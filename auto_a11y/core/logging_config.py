"""
Logging configuration for Auto A11y
"""

import logging
import logging.config
import os
from pathlib import Path

# Get log level from environment or default to WARNING for production
LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING').upper()
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'

# If in debug mode, show more logs
if DEBUG_MODE:
    LOG_LEVEL = 'INFO'

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True, parents=True)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': LOG_LEVEL,
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',  # Always log INFO and above to file
            'formatter': 'standard',
            'filename': str(LOGS_DIR / 'auto_a11y.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'loggers': {
        '': {  # Root logger
            'level': LOG_LEVEL,
            'handlers': ['console', 'file']
        },
        'auto_a11y': {
            'level': LOG_LEVEL,
            'handlers': ['console', 'file'],
            'propagate': False
        },
        # Silence verbose third-party libraries
        'playwright': {
            'level': 'WARNING',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'websockets': {
            'level': 'WARNING',
            'handlers': ['file'],
            'propagate': False
        },
        'urllib3': {
            'level': 'WARNING',
            'handlers': ['file'],
            'propagate': False
        },
        'werkzeug': {
            'level': 'WARNING',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'httpx': {
            'level': 'WARNING',
            'handlers': ['file'],
            'propagate': False
        }
    }
}

def setup_logging():
    """Configure logging for the application"""
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Set specific loggers to reduce noise
    logging.getLogger('playwright').setLevel(logging.WARNING)
    logging.getLogger('playwright._impl').setLevel(logging.WARNING)
    logging.getLogger('websockets.client').setLevel(logging.WARNING)
    logging.getLogger('websockets.protocol').setLevel(logging.WARNING)
    
    # Log configuration info
    logger = logging.getLogger(__name__)
    if DEBUG_MODE:
        logger.info(f"Logging configured - Level: {LOG_LEVEL}, Debug: {DEBUG_MODE}")
    
    return logger