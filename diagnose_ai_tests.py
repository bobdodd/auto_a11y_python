#!/usr/bin/env python3
"""
Diagnostic script to check AI testing configuration and functionality
"""

import asyncio
import os
from pathlib import Path
from auto_a11y.core.database import Database
from auto_a11y.core.browser_manager import BrowserManager
from config import config

print("AI Testing Diagnostic")
print("=" * 50)

# Check environment
print("\n1. Environment Check:")
print(f"   - CLAUDE_API_KEY configured: {bool(getattr(config, 'CLAUDE_API_KEY', None))}")
print(f"   - API Key length: {len(getattr(config, 'CLAUDE_API_KEY', '')) if hasattr(config, 'CLAUDE_API_KEY') else 0}")

# Check database
print("\n2. Database Check:")
# Build connection URI
mongo_host = getattr(config, 'MONGO_HOST', 'localhost')
mongo_port = getattr(config, 'MONGO_PORT', 27017)
mongo_db = getattr(config, 'MONGO_DB_NAME', 'auto_a11y')
mongo_user = getattr(config, 'MONGO_USERNAME', None)
mongo_pass = getattr(config, 'MONGO_PASSWORD', None)

if mongo_user and mongo_pass:
    connection_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"
else:
    connection_uri = f"mongodb://{mongo_host}:{mongo_port}"

db = Database(connection_uri, mongo_db)

# Get first project
projects = db.get_projects()
if projects:
    project = projects[0]
    print(f"   - Project: {project.name}")
    print(f"   - Config: {project.config}")
    print(f"   - AI Enabled: {project.config.get('enable_ai_testing', False)}")
    print(f"   - AI Tests: {project.config.get('ai_tests', [])}")
else:
    print("   - No projects found")

# Test screenshot capability
async def test_screenshot():
    print("\n3. Screenshot Test:")
    browser_config = {
        'headless': True,
        'viewport_width': 1920,
        'viewport_height': 1080
    }
    
    browser_manager = BrowserManager(browser_config)
    try:
        await browser_manager.start()
        async with browser_manager.get_page() as page:
            await page.goto('https://example.com')
            screenshot = await page.screenshot({'fullPage': True})
            print(f"   - Screenshot captured: {len(screenshot)} bytes")
            
            # Test if screenshot contains valid image data
            if screenshot[:2] == b'\xff\xd8':  # JPEG magic number
                print(f"   - Valid JPEG image")
            elif screenshot[:8] == b'\x89PNG\r\n\x1a\n':  # PNG magic number
                print(f"   - Valid PNG image")
            else:
                print(f"   - Warning: Unknown image format")
                
    except Exception as e:
        print(f"   - Error: {e}")
    finally:
        await browser_manager.stop()

# Test AI analysis (if API key exists)
async def test_ai_analysis():
    api_key = getattr(config, 'CLAUDE_API_KEY', None)
    if not api_key:
        print("\n4. AI Analysis Test:")
        print("   - Skipped: No API key configured")
        return
        
    print("\n4. AI Analysis Test:")
    
    # Create simple test HTML with obvious heading issue
    test_html = """
    <html>
    <body>
        <div style="font-size: 24px; font-weight: bold;">This Should Be A Heading</div>
        <p>This is regular paragraph text.</p>
        <h2>This is a proper h2 heading</h2>
    </body>
    </html>
    """
    
    try:
        from auto_a11y.ai import ClaudeAnalyzer
        
        # Take screenshot of test page
        browser_config = {
            'headless': True,
            'viewport_width': 1920,
            'viewport_height': 1080
        }
        
        browser_manager = BrowserManager(browser_config)
        await browser_manager.start()
        
        async with browser_manager.get_page() as page:
            await page.setContent(test_html)
            screenshot = await page.screenshot({'fullPage': True})
            
            # Initialize analyzer
            analyzer = ClaudeAnalyzer(api_key)
            
            # Run analysis
            print("   - Running heading analysis...")
            results = await analyzer.analyze_page(
                screenshot=screenshot,
                html=test_html,
                analyses=['headings']
            )
            
            print(f"   - Findings: {len(results.get('findings', []))}")
            for finding in results.get('findings', []):
                print(f"      • {finding.id}: {finding.description}")
            
            # Check raw results
            raw = results.get('raw_results', {}).get('headings', {})
            if raw:
                print(f"   - Visual headings detected: {len(raw.get('visual_headings', []))}")
                print(f"   - HTML headings detected: {len(raw.get('html_headings', []))}")
                print(f"   - Issues found: {len(raw.get('issues', []))}")
                
                # Debug: Show raw response
                print(f"\n   - Raw AI Response:")
                import json
                print(json.dumps(raw, indent=4)[:1000])  # First 1000 chars
                
                for issue in raw.get('issues', []):
                    print(f"      • Type: {issue.get('type')}")
                    print(f"        Description: {issue.get('description')}")
            
            # Clean up
            await analyzer.client.aclose()
            
    except ImportError as e:
        print(f"   - Import error: {e}")
    except Exception as e:
        print(f"   - Error: {e}")
    finally:
        await browser_manager.stop()

# Run tests
print("\nRunning diagnostics...")
asyncio.run(test_screenshot())
asyncio.run(test_ai_analysis())

print("\n" + "=" * 50)
print("Diagnostic complete")
print("\nTo enable AI testing:")
print("1. Set CLAUDE_API_KEY in your .env file")
print("2. Enable AI testing in project settings")
print("3. Select which AI tests to run")