#!/usr/bin/env python
"""
Manually download Chromium for Pyppeteer
"""

import asyncio
from pyppeteer import chromium_downloader
import sys

async def download():
    """Download Chromium with better error handling"""
    try:
        print("Starting Chromium download...")
        print(f"Download URL: {chromium_downloader.get_url()}")
        print(f"Download path: {chromium_downloader.DOWNLOADS_FOLDER}")
        
        # This should handle the download better
        chromium_downloader.download_chromium()
        
        print("\n✓ Chromium downloaded successfully!")
        print(f"Location: {chromium_downloader.DOWNLOADS_FOLDER}")
        
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        print("\nAlternative: You can manually download Chromium:")
        print(f"1. Download from: {chromium_downloader.get_url()}")
        print(f"2. Extract to: {chromium_downloader.DOWNLOADS_FOLDER}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(download())