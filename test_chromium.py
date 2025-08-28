#!/usr/bin/env python
"""
Test if Chromium is properly detected
"""

import os
import sys
from pathlib import Path

# Test pyppeteer's chromium detection
try:
    from pyppeteer import chromium_downloader
    
    print("Testing Chromium detection...")
    print("-" * 50)
    
    # Check download folder
    download_folder = chromium_downloader.DOWNLOADS_FOLDER
    print(f"Download folder: {download_folder}")
    print(f"Folder exists: {os.path.exists(download_folder)}")
    
    # Check for chromium executable
    try:
        chromium_path = chromium_downloader.chromium_executable()
        print(f"\nChromium executable: {chromium_path}")
        print(f"Executable exists: {os.path.exists(chromium_path) if chromium_path else False}")
        
        if chromium_path and os.path.exists(chromium_path):
            print(f"✅ Chromium is properly installed at: {chromium_path}")
        else:
            print("❌ Chromium executable not found")
            
    except Exception as e:
        print(f"❌ Error finding chromium: {e}")
    
    # List contents of download folder
    print(f"\nContents of {download_folder}:")
    if os.path.exists(download_folder):
        for item in os.listdir(download_folder):
            item_path = os.path.join(download_folder, item)
            print(f"  - {item} ({'dir' if os.path.isdir(item_path) else 'file'})")
    
    # Try to find Chromium.app on Mac
    print("\nLooking for Chromium.app...")
    home = Path.home()
    possible_paths = [
        home / "Library/Application Support/pyppeteer/local-chromium",
        home / ".pyppeteer/local-chromium",
        Path("/Users/bob3/Library/Application Support/pyppeteer/local-chromium"),
    ]
    
    for path in possible_paths:
        print(f"Checking: {path}")
        if path.exists():
            for root, dirs, files in os.walk(path):
                if "Chromium.app" in dirs:
                    chromium_app = os.path.join(root, "Chromium.app")
                    print(f"  ✅ Found: {chromium_app}")
                    
                    # Check the actual executable
                    exe_path = os.path.join(chromium_app, "Contents", "MacOS", "Chromium")
                    if os.path.exists(exe_path):
                        print(f"  ✅ Executable exists: {exe_path}")
                    else:
                        print(f"  ❌ Executable not found at: {exe_path}")
    
    # Test if we can get the revision
    print(f"\nChromium revision: {chromium_downloader.REVISION}")
    
except ImportError as e:
    print(f"Error importing pyppeteer: {e}")
    sys.exit(1)
    
print("\n" + "-" * 50)
print("Test complete!")