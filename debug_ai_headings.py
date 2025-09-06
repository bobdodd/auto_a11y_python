#!/usr/bin/env python3
"""
Debug why AI heading issues aren't being detected/stored
"""

import asyncio
from auto_a11y.core.database import Database
from auto_a11y.core.browser_manager import BrowserManager
from auto_a11y.ai import ClaudeAnalyzer
from config import config

async def debug_heading_detection():
    # Get the test website URL
    mongo_host = getattr(config, 'MONGO_HOST', 'localhost')
    mongo_port = getattr(config, 'MONGO_PORT', 27017)
    mongo_db = getattr(config, 'MONGO_DB_NAME', 'auto_a11y')
    mongo_user = getattr(config, 'MONGO_USERNAME', None)
    mongo_pass = getattr(config, 'MONGO_PASSWORD', None)
    
    if mongo_user and mongo_pass:
        connection_uri = f'mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}'
    else:
        connection_uri = f'mongodb://{mongo_host}:{mongo_port}'
    
    db = Database(connection_uri, mongo_db)
    
    # Get the test project and website
    projects = db.get_projects()
    website = None
    for project in projects:
        if project.config and project.config.get('enable_ai_testing'):
            websites = db.get_websites(project.id)
            if websites:
                website = websites[0]
                break
    
    if not website:
        print("No websites found with AI testing enabled")
        return
    print(f"Testing website: {website.name} ({website.url})")
    
    # Get API key
    api_key = getattr(config, 'CLAUDE_API_KEY', None)
    if not api_key:
        print("No API key configured")
        return
    
    # Initialize browser
    browser_config = {
        'headless': True,
        'viewport_width': 1920,
        'viewport_height': 1080
    }
    
    browser_manager = BrowserManager(browser_config)
    await browser_manager.start()
    
    try:
        async with browser_manager.get_page() as page:
            # Navigate to the test website
            print(f"\nNavigating to {website.url}...")
            await page.goto(website.url, {'waitUntil': 'networkidle2', 'timeout': 30000})
            await page.waitForSelector('body', {'timeout': 5000})
            
            # Take screenshot
            screenshot = await page.screenshot({'fullPage': True})
            print(f"Screenshot captured: {len(screenshot)} bytes")
            
            # Get HTML
            html = await page.content()
            print(f"HTML captured: {len(html)} chars")
            
            # Initialize analyzer
            analyzer = ClaudeAnalyzer(api_key)
            
            # Run heading analysis
            print("\nRunning AI heading analysis...")
            results = await analyzer.analyze_page(
                screenshot=screenshot,
                html=html,
                analyses=['headings']
            )
            
            # Check raw results
            raw = results.get('raw_results', {}).get('headings', {})
            visual = raw.get('visual_headings', [])
            html_headings = raw.get('html_headings', [])
            issues = raw.get('issues', [])
            
            print(f"\nRaw AI Results:")
            print(f"  Visual headings detected: {len(visual)}")
            for i, vh in enumerate(visual, 1):
                print(f"    {i}. '{vh.get('text', '')[:50]}...' (level {vh.get('appears_to_be_level')})")
                print(f"       Element: {vh.get('likely_element')} class='{vh.get('element_class')}' id='{vh.get('element_id')}'")
            
            print(f"\n  HTML headings detected: {len(html_headings)}")
            for i, hh in enumerate(html_headings, 1):
                print(f"    {i}. <{hh.get('tag')}> '{hh.get('text', '')[:50]}...'")
            
            print(f"\n  Issues from AI: {len(issues)}")
            for issue in issues:
                print(f"    - {issue.get('type')}: {issue.get('description')}")
            
            # Check processed findings
            findings = results.get('findings', [])
            print(f"\nProcessed Findings: {len(findings)}")
            heading_findings = [f for f in findings if 'heading' in f.id.lower()]
            print(f"  Heading-related findings: {len(heading_findings)}")
            for f in heading_findings:
                print(f"    - {f.id}: {f.description[:60]}...")
            
            # Check which visual headings are NOT in HTML
            print("\n" + "=" * 60)
            print("Visual vs HTML comparison:")
            visual_texts = [v.get('text', '').lower().strip() for v in visual]
            html_texts = [h.get('text', '').lower().strip() for h in html_headings]
            
            for vh in visual:
                text = vh.get('text', '')
                if text.lower().strip() not in html_texts:
                    print(f"  ❌ NOT MARKED UP: '{text[:50]}...'")
                    print(f"     Should create AI_ErrVisualHeadingNotMarked")
                else:
                    print(f"  ✓ Properly marked: '{text[:50]}...'")
            
            # Clean up
            await analyzer.client.aclose()
            
    finally:
        await browser_manager.stop()

# Run the debug
print("AI Heading Detection Debug")
print("=" * 60)
asyncio.run(debug_heading_detection())