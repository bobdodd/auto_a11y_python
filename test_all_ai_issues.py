#!/usr/bin/env python3
"""
Test script to verify all AI tests are running and reporting correctly
"""

import asyncio
import os
from pathlib import Path
from auto_a11y.core.database import Database
from auto_a11y.core.browser_manager import BrowserManager
from auto_a11y.ai import ClaudeAnalyzer
from config import config

print("AI Testing Comprehensive Check")
print("=" * 50)

# Test HTML with various accessibility issues
test_html = """
<html>
<head>
    <title>AI Test Page</title>
</head>
<body>
    <!-- Visual heading not marked up -->
    <div style="font-size: 32px; font-weight: bold; margin-bottom: 20px;">
        Main Page Title (Should Be H1)
    </div>
    
    <!-- Another visual heading -->
    <div class="section-title" style="font-size: 24px; font-weight: 600;">
        Section Title (Should Be H2)
    </div>
    
    <!-- Skipped heading level -->
    <h1>Actual H1</h1>
    <h3>Skipped to H3 (missing H2)</h3>
    
    <!-- Non-semantic button -->
    <div onclick="submitForm()" style="padding: 10px; background: blue; color: white; cursor: pointer;">
        Submit Form (Should Be Button)
    </div>
    
    <!-- Toggle without state -->
    <div onclick="toggleMenu()" class="menu-toggle">
        Menu Toggle (Missing aria-expanded)
    </div>
    
    <!-- Tabs without ARIA -->
    <div class="tabs">
        <div class="tab" onclick="selectTab(1)">Tab 1</div>
        <div class="tab" onclick="selectTab(2)">Tab 2</div>
    </div>
    
    <!-- Dropdown without ARIA -->
    <div class="dropdown">
        <div onclick="toggleDropdown()">Select Option</div>
        <div class="dropdown-menu">
            <div>Option 1</div>
            <div>Option 2</div>
        </div>
    </div>
    
    <!-- Modal without proper ARIA -->
    <div class="modal" style="display: block;">
        <div class="modal-content">
            <h2>Login</h2>
            <input type="text" placeholder="Username">
            <button>Submit</button>
        </div>
    </div>
    
    <!-- Mixed language without lang attribute -->
    <p>This is English text. Bonjour, comment allez-vous? Back to English.</p>
    
    <!-- Reading order issue (CSS positioned) -->
    <div style="position: relative;">
        <div style="position: absolute; right: 0;">Step 1: Start Here</div>
        <div>Step 2: Then Here</div>
    </div>
</body>
</html>
"""

async def test_ai_analysis():
    api_key = getattr(config, 'CLAUDE_API_KEY', None)
    if not api_key:
        print("ERROR: No CLAUDE_API_KEY configured")
        return
    
    print(f"\n1. API Key configured: {len(api_key)} chars")
    
    # Initialize browser for screenshot
    browser_config = {
        'headless': True,
        'viewport_width': 1920,
        'viewport_height': 1080
    }
    
    browser_manager = BrowserManager(browser_config)
    await browser_manager.start()
    
    try:
        async with browser_manager.get_page() as page:
            # Load test HTML
            await page.setContent(test_html)
            await page.waitForSelector('body')
            
            # Take screenshot
            screenshot = await page.screenshot({'fullPage': True})
            print(f"2. Screenshot captured: {len(screenshot)} bytes")
            
            # Initialize analyzer
            analyzer = ClaudeAnalyzer(api_key)
            
            # Run ALL available AI tests
            all_tests = ['headings', 'reading_order', 'modals', 'language', 'animations', 'interactive']
            print(f"\n3. Running AI tests: {all_tests}")
            
            results = await analyzer.analyze_page(
                screenshot=screenshot,
                html=test_html,
                analyses=all_tests
            )
            
            # Process findings
            findings = results.get('findings', [])
            print(f"\n4. Total findings: {len(findings)}")
            
            # Group findings by ID
            findings_by_id = {}
            for finding in findings:
                issue_id = finding.id
                if issue_id not in findings_by_id:
                    findings_by_id[issue_id] = []
                findings_by_id[issue_id].append(finding)
            
            print("\n5. Findings by Issue Type:")
            for issue_id in sorted(findings_by_id.keys()):
                count = len(findings_by_id[issue_id])
                print(f"   - {issue_id}: {count} occurrence(s)")
                # Show first example
                first = findings_by_id[issue_id][0]
                if first.element:
                    print(f"     Example: {first.element} - {first.description[:80]}...")
            
            # Check for expected heading issues
            print("\n6. Heading Issue Check:")
            heading_issues = [f for f in findings if 'heading' in f.id.lower()]
            print(f"   - Found {len(heading_issues)} heading-related issues")
            for issue in heading_issues[:3]:
                print(f"     • {issue.id}: {issue.description[:80]}...")
            
            # Check raw results for each analyzer
            print("\n7. Raw Analyzer Results:")
            raw_results = results.get('raw_results', {})
            for analyzer_name, result in raw_results.items():
                if 'error' in result:
                    print(f"   - {analyzer_name}: ERROR - {result['error']}")
                else:
                    if analyzer_name == 'headings':
                        visual = result.get('visual_headings', [])
                        html = result.get('html_headings', [])
                        issues = result.get('issues', [])
                        print(f"   - {analyzer_name}: {len(visual)} visual, {len(html)} HTML, {len(issues)} issues")
                        if visual:
                            print(f"       Visual headings found: {[v.get('text', '')[:30] for v in visual]}")
                    elif analyzer_name == 'interactive':
                        custom = result.get('custom_controls', [])
                        issues = result.get('issues', [])
                        print(f"   - {analyzer_name}: {len(custom)} custom controls, {len(issues)} issues")
                    else:
                        issues = result.get('issues', [])
                        print(f"   - {analyzer_name}: {len(issues)} issues")
            
            # Clean up
            await analyzer.client.aclose()
            
    finally:
        await browser_manager.stop()

# Run the test
print("\nRunning comprehensive AI test...")
asyncio.run(test_ai_analysis())
print("\n" + "=" * 50)
print("Test complete")