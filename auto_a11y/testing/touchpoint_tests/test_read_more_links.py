"""
Read More Links touchpoint test module
Evaluates links and buttons with generic text for proper accessibility.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Generic Link Text Analysis",
    "touchpoint": "read_more_links", 
    "description": "Evaluates links and buttons with generic text like 'Read more' or 'Click here' for proper accessibility. This test identifies elements with non-descriptive text that lack proper accessible names to provide context for screen reader users.",
    "version": "1.0.0",
    "wcagCriteria": ["2.4.4", "2.4.9", "2.5.3"],
    "tests": [
        {
            "id": "generic-link-detection",
            "name": "Generic Link Text Detection",
            "description": "Identifies links and buttons with non-descriptive text like 'Read more', 'Learn more', 'Click here', etc.",
            "impact": "informational",
            "wcagCriteria": ["2.4.4", "2.4.9"],
        },
        {
            "id": "accessible-name-quality",
            "name": "Generic Link Accessible Name",
            "description": "Checks if links with generic visible text have proper accessible names that provide additional context.",
            "impact": "high",
            "wcagCriteria": ["2.4.4", "2.4.9"],
        },
        {
            "id": "accessible-name-pattern",
            "name": "Accessible Name Pattern",
            "description": "Verifies that accessible names for generic links follow the pattern of starting with the visible text.",
            "impact": "medium",
            "wcagCriteria": ["2.5.3"],
        }
    ]
}

async def test_read_more_links(page) -> Dict[str, Any]:
    """
    Test 'read more' type links and buttons for proper accessible names
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze generic links
        results = await page.evaluate('''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'read_more_links',
                    checks: []
                };
                
                // Function to generate XPath for elements
                function getFullXPath(element) {
                    if (!element) return '';
                    
                    function getElementIdx(el) {
                        let count = 1;
                        for (let sib = el.previousSibling; sib; sib = sib.previousSibling) {
                            if (sib.nodeType === 1 && sib.tagName === el.tagName) {
                                count++;
                            }
                        }
                        return count;
                    }
                    
                    let path = '';
                    while (element && element.nodeType === 1) {
                        const idx = getElementIdx(element);
                        const tagName = element.tagName.toLowerCase();
                        path = `/${tagName}[${idx}]${path}`;
                        element = element.parentNode;
                    }
                    return path;
                }
                
                // Get accessible name
                function getAccessibleName(element) {
                    const ariaLabel = element.getAttribute('aria-label');
                    if (ariaLabel) return ariaLabel.trim();

                    const ariaLabelledBy = element.getAttribute('aria-labelledby');
                    if (ariaLabelledBy) {
                        const labelElements = ariaLabelledBy.split(' ')
                            .map(id => document.getElementById(id))
                            .filter(el => el);
                        if (labelElements.length > 0) {
                            return labelElements.map(el => el.textContent.trim()).join(' ');
                        }
                    }

                    return element.textContent.trim();
                }
                
                // Regular expressions for matching generic text
                const genericTextPatterns = [
                    /^read more$/i,
                    /^learn more$/i,
                    /^more$/i,
                    /^more\.\.\.$/i,
                    /^read more\.\.\.$/i,
                    /^learn more\.\.\.$/i,
                    /^click here$/i,
                    /^details$/i,
                    /^more details$/i,
                    /^here$/i,
                    /^link$/i,
                    /^view more$/i,
                    /^see more$/i,
                    /^continue reading$/i,
                    /^download$/i,
                    /^get$/i,
                    /^go$/i,
                    /^this$/i,
                    /^that$/i
                ];
                
                // Find all links and buttons
                const elements = Array.from(document.querySelectorAll('a, button, [role="button"], [role="link"]'))
                    .filter(el => {
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    });
                
                const genericElements = [];
                
                elements.forEach(element => {
                    const visibleText = element.textContent.trim();
                    const accessibleName = getAccessibleName(element);
                    
                    // Check if this is a generic "read more" type element
                    const isGenericText = genericTextPatterns.some(pattern => 
                        pattern.test(visibleText)
                    );

                    if (isGenericText) {
                        genericElements.push({
                            element: element,
                            visibleText: visibleText,
                            accessibleName: accessibleName,
                            isValid: accessibleName.length > visibleText.length && 
                                    accessibleName.toLowerCase().startsWith(visibleText.toLowerCase())
                        });
                    }
                });
                
                if (genericElements.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No generic link text found on the page';
                    return results;
                }
                
                results.elements_tested = genericElements.length;
                
                let invalidAccessibleNames = 0;
                
                genericElements.forEach(item => {
                    const { element, visibleText, accessibleName, isValid } = item;

                    // Check for violations
                    // isValid means the link has been improved with aria-label or screen-reader-only text
                    // that extends beyond the visible text (e.g., "Read more" becomes "Read more about our 2024 report")
                    if (!isValid) {
                        invalidAccessibleNames++;
                        results.errors.push({
                            err: 'ErrLinkTextNotDescriptive',
                            type: 'err',
                            cat: 'links',
                            element: element.tagName.toLowerCase(),
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: "Link text does not adequately describe the link's destination or purpose - consider adding aria-label or visually hidden text with more context",
                            visibleText: visibleText,
                            accessibleName: accessibleName,
                            href: element.href || null
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Generic link accessible names',
                    wcag: ['2.4.4', '2.4.9'],
                    total: genericElements.length,
                    passed: results.elements_passed,
                    failed: invalidAccessibleNames
                });
                
                if (genericElements.length > 0) {
                    results.checks.push({
                        description: 'Generic link text detection (informational)',
                        wcag: ['2.4.4'],
                        total: genericElements.length,
                        passed: 0,
                        failed: 0
                    });
                }
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_read_more_links: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }