"""
Responsive Breakpoints touchpoint test module
Discovers and reports CSS media query breakpoints defined on the page.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Responsive Breakpoints Discovery",
    "touchpoint": "responsive_breakpoints",
    "description": "Discovers CSS media query breakpoints defined on the page for accessibility testing at different viewport widths.",
    "version": "1.0.0",
    "wcagCriteria": ["1.4.10", "2.4.3"],
    "tests": [
        {
            "id": "responsive-breakpoints",
            "name": "CSS Media Query Breakpoints",
            "description": "Identifies responsive breakpoints defined in CSS @media rules to guide testing at different viewport widths.",
            "impact": "info",
            "wcagCriteria": ["1.4.10", "2.4.3"],
        }
    ]
}

async def test_responsive_breakpoints(page) -> Dict[str, Any]:
    """
    Discover responsive breakpoints defined in CSS media queries

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing discovery items for responsive breakpoints
    """
    try:
        # Execute JavaScript to extract breakpoints from CSS
        results = await page.evaluate('''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    discovery: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'responsive_breakpoints',
                    checks: []
                };

                // Extract breakpoints from CSS @media rules
                const breakpoints = new Set();

                // Parse all stylesheets for media queries
                for (const sheet of document.styleSheets) {
                    try {
                        if (sheet.cssRules) {
                            for (const rule of sheet.cssRules) {
                                if (rule instanceof CSSMediaRule) {
                                    // Extract width values from media query
                                    const media = rule.media.mediaText;
                                    const widthMatches = media.match(/(?:min-width|max-width):\\s*(\\d+)px/g);

                                    if (widthMatches) {
                                        widthMatches.forEach(match => {
                                            const value = parseInt(match.match(/(\\d+)px/)[1]);
                                            breakpoints.add(value);
                                        });
                                    }
                                }
                            }
                        }
                    } catch (e) {
                        // Skip stylesheets we can't access (CORS)
                    }
                }

                // Convert to sorted array
                const breakpointArray = Array.from(breakpoints).sort((a, b) => a - b);

                // If we found breakpoints, create a discovery issue
                if (breakpointArray.length > 0) {
                    results.warnings.push({
                        err: 'DiscoResponsiveBreakpoints',
                        type: 'disco',
                        cat: 'responsive',
                        description: `Page defines ${breakpointArray.length} responsive breakpoint${breakpointArray.length === 1 ? '' : 's'}: ${breakpointArray.join(', ')}px`,
                        metadata: {
                            breakpointCount: breakpointArray.length,
                            breakpoints: breakpointArray.join(', '),
                            minBreakpoint: breakpointArray[0],
                            maxBreakpoint: breakpointArray[breakpointArray.length - 1]
                        },
                        xpath: '/html',
                        fpTempId: '0'
                    });

                    results.checks.push({
                        description: 'Responsive breakpoints detected',
                        wcag: ['1.4.10', '2.4.3'],
                        total: 1,
                        passed: 0,
                        failed: 0
                    });
                } else {
                    results.applicable = false;
                    results.not_applicable_reason = 'No responsive breakpoints found in CSS media queries';
                }

                return results;
            }
        ''')

        return results

    except Exception as e:
        logger.error(f"Error in test_responsive_breakpoints: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'discovery': [],
            'passes': []
        }
