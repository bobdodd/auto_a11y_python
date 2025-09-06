#!/usr/bin/env python3
"""
Quick test for AI heading detection
"""

import asyncio
from auto_a11y.core.browser_manager import BrowserManager
from auto_a11y.ai import ClaudeAnalyzer
from config import config

# Simple test HTML with obvious heading issues
test_html = """
<html>
<body>
    <div style="font-size: 32px; font-weight: bold;">This Should Be H1</div>
    <div style="font-size: 24px; font-weight: bold;">This Should Be H2</div>
    <p>Regular paragraph text</p>
    <h1>Real H1 Heading</h1>
    <h3>Skipped to H3</h3>
</body>
</html>
"""

async def test():
    api_key = getattr(config, 'CLAUDE_API_KEY', None)
    if not api_key:
        print("No API key")
        return
    
    browser_config = {'headless': True, 'viewport_width': 1920, 'viewport_height': 1080}
    browser_manager = BrowserManager(browser_config)
    await browser_manager.start()
    
    try:
        async with browser_manager.get_page() as page:
            await page.setContent(test_html)
            screenshot = await page.screenshot({'fullPage': True})
            
            analyzer = ClaudeAnalyzer(api_key)
            
            # Just test headings
            print("Testing heading detection...")
            results = await analyzer.analyze_page(
                screenshot=screenshot,
                html=test_html,
                analyses=['headings']
            )
            
            findings = results.get('findings', [])
            print(f"Found {len(findings)} issues")
            
            for finding in findings:
                print(f"- {finding.id}: {finding.description[:60]}...")
                
            raw = results.get('raw_results', {}).get('headings', {})
            print(f"\nRaw results:")
            print(f"- Visual headings: {len(raw.get('visual_headings', []))}")
            print(f"- HTML headings: {len(raw.get('html_headings', []))}")
            print(f"- Issues: {len(raw.get('issues', []))}")
            
            await analyzer.client.aclose()
    finally:
        await browser_manager.stop()

asyncio.run(test())