#!/usr/bin/env python3
"""
Test script to verify WCAG level is properly retrieved from project config
"""

# This is a diagnostic script to trace the data flow
print("""
WCAG Level Data Flow:
====================

1. Page has website_id
   └─> page.website_id

2. Get Website from database using website_id
   └─> website = db.get_website(page.website_id)

3. Website has project_id  
   └─> website.project_id

4. Get Project from database using project_id
   └─> project = db.get_project(website.project_id)

5. Project has config with wcag_level
   └─> project.config['wcag_level'] = 'AA' or 'AAA'

6. Pass WCAG level to JavaScript context
   └─> window.WCAG_LEVEL = wcag_level

7. JavaScript tests use WCAG level to:
   - Determine pass/fail threshold
   - Select appropriate error code (AA vs AAA)

Current Implementation in test_runner.py:
=========================================
""")

code = '''
# Get WCAG compliance level from project
wcag_level = 'AA'  # Default to AA
try:
    # Get website to find project
    website = self.db.get_website(page.website_id)
    if website:
        project = self.db.get_project(website.project_id)
        if project and project.config:
            wcag_level = project.config.get('wcag_level', 'AA')
            logger.info(f"Project config: {project.config}")
            logger.info(f"Using WCAG {wcag_level} compliance level for testing")
        else:
            logger.info(f"No config found in project, using default AA")
    else:
        logger.warning(f"Could not find website for page {page.website_id}")
except Exception as e:
    logger.warning(f"Could not get WCAG level from project: {e}, defaulting to AA")

# Set WCAG level in page context
await browser_page.evaluate(f\'\'\'
    window.WCAG_LEVEL = "{wcag_level}";
    console.log("Testing with WCAG Level:", window.WCAG_LEVEL);
\'\'\')
'''

print(code)

print("""
Error Code Selection in JavaScript:
====================================
""")

js_code = '''
// In colorContrast.js:
const wcagLevel = window.WCAG_LEVEL || 'AA';
const passesLevel = (wcagLevel === 'AAA') ? isAAA : isAA;

// In color.js:
if (!col.passesLevel) {
    let errorCode;
    if (col.wcagLevel === 'AAA') {
        errorCode = col.isLargeText ? 'ErrLargeTextContrastAAA' : 'ErrTextContrastAAA';
    } else {
        errorCode = col.isLargeText ? 'ErrLargeTextContrastAA' : 'ErrTextContrastAA';
    }
}
'''

print(js_code)

print("""
Fix Applied:
============
Changed: website = self.db.get_website_by_id(page.website_id)
To:      website = self.db.get_website(page.website_id)

This should now properly retrieve the project's WCAG level setting.
""")