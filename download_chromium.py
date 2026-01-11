#!/usr/bin/env python
"""
Download/install Chromium browser for Playwright
"""

import subprocess
import sys
from pathlib import Path


def download():
    """Install Playwright Chromium browser"""
    try:
        print("Installing Playwright Chromium browser...")
        print("This may take a few minutes on first run...\n")

        # Use playwright install command
        result = subprocess.run(
            [sys.executable, '-m', 'playwright', 'install', 'chromium'],
            capture_output=False,  # Show output in real-time
            text=True
        )

        if result.returncode == 0:
            print("\n✓ Playwright Chromium installed successfully!")

            # Show installation location
            playwright_cache = Path.home() / '.cache' / 'ms-playwright'
            if not playwright_cache.exists():
                # Try macOS location
                playwright_cache = Path.home() / 'Library' / 'Caches' / 'ms-playwright'

            if playwright_cache.exists():
                print(f"Location: {playwright_cache}")
        else:
            print(f"\n✗ Installation failed with return code: {result.returncode}")
            sys.exit(1)

    except FileNotFoundError:
        print("\n✗ Playwright not found. Please install it first:")
        print("   pip install playwright")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Installation failed: {e}")
        print("\nAlternative: You can manually install Playwright browsers:")
        print("   python -m playwright install chromium")
        sys.exit(1)


if __name__ == "__main__":
    download()
