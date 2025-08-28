#!/usr/bin/env python
"""
Auto A11y Python - Main entry point
"""

import sys
import os
import asyncio
import logging
import argparse
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from auto_a11y.web.app import create_app
from auto_a11y.core.database import Database


def setup_logging(debug=False):
    """Configure logging"""
    level = logging.DEBUG if debug else logging.INFO
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logs_dir / 'auto_a11y.log')
        ]
    )
    
    # Reduce noise from some libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('pymongo').setLevel(logging.WARNING)
    logging.getLogger('pyppeteer').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def init_directories():
    """Initialize required directories"""
    directories = [
        Path(config.SCREENSHOTS_DIR),
        Path(config.REPORTS_DIR),
        Path('logs'),
        Path('temp'),
        Path('static/screenshots')
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True, parents=True)
        logging.info(f"Ensured directory exists: {directory}")


def setup_database():
    """Initialize database and create indexes"""
    logger = logging.getLogger(__name__)
    logger.info("Setting up database...")
    
    db = Database(config.MONGODB_URI, config.DATABASE_NAME)
    
    # Test connection
    if not db.test_connection():
        logger.error("Failed to connect to database")
        return False
    
    # Create indexes
    db.create_indexes()
    logger.info("Database indexes created")
    
    # Create sample project if no projects exist
    projects = db.get_all_projects()
    if not projects:
        from auto_a11y.models import Project
        sample_project = Project(
            name='Sample Project',
            description='A sample project to get started'
        )
        project_id = db.create_project(sample_project)
        logger.info(f"Created sample project: {project_id}")
    
    return True


def download_browser():
    """Download Chromium browser for Pyppeteer"""
    logger = logging.getLogger(__name__)
    try:
        from pyppeteer import chromium_downloader
        logger.info("Downloading Chromium browser...")
        chromium_downloader.download_chromium()
        logger.info("Chromium browser downloaded successfully")
        return True
    except Exception as e:
        logger.warning(f"Could not download Chromium: {e}")
        return False


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Auto A11y Python - Accessibility Testing Tool')
    parser.add_argument('--host', default=None, help='Host to bind to')
    parser.add_argument('--port', type=int, default=None, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--setup', action='store_true', help='Run initial setup')
    parser.add_argument('--test-db', action='store_true', help='Test database connection')
    parser.add_argument('--download-browser', action='store_true', help='Download Chromium browser')
    
    args = parser.parse_args()
    
    # Override config with command line arguments
    if args.debug:
        config.DEBUG = True
    if args.host:
        config.HOST = args.host
    if args.port:
        config.PORT = args.port
    
    # Setup logging
    setup_logging(config.DEBUG)
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("Auto A11y Python - Accessibility Testing Tool")
    logger.info("="*60)
    
    # Initialize directories
    init_directories()
    
    # Test database if requested
    if args.test_db:
        logger.info("Testing database connection...")
        db = Database(config.MONGODB_URI, config.DATABASE_NAME)
        if db.test_connection():
            logger.info("✓ Database connection successful!")
        else:
            logger.error("✗ Database connection failed!")
            sys.exit(1)
        return
    
    # Download browser if requested
    if args.download_browser:
        if download_browser():
            logger.info("Browser download complete")
        else:
            logger.error("Browser download failed")
            sys.exit(1)
        return
    
    # Run setup if requested
    if args.setup:
        logger.info("Running initial setup...")
        
        # Setup database
        if not setup_database():
            logger.error("Database setup failed")
            sys.exit(1)
        
        # Download browser
        download_browser()
        
        logger.info("\n" + "="*60)
        logger.info("Setup complete! You can now run the application with:")
        logger.info("  python run.py")
        logger.info("="*60)
        return
    
    # Print configuration
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"MongoDB: {config.MONGODB_URI}/{config.DATABASE_NAME}")
    logger.info(f"AI Analysis: {'Enabled' if config.RUN_AI_ANALYSIS else 'Disabled'}")
    logger.info(f"Screenshots: {config.SCREENSHOTS_DIR}")
    logger.info(f"Reports: {config.REPORTS_DIR}")
    
    try:
        # Create and run Flask app
        app = create_app(config)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Server starting on http://{config.HOST}:{config.PORT}")
        logger.info(f"Press Ctrl+C to stop the server")
        logger.info(f"{'='*60}\n")
        
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            use_reloader=config.DEBUG
        )
    except KeyboardInterrupt:
        logger.info("\nApplication stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()