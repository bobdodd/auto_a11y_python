"""
ARIA touchpoint test module
Tests for proper ARIA attribute usage and accessibility.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "ARIA Accessibility Test",
    "touchpoint": "aria",
    "description": "Tests for proper ARIA attribute usage, focusing on voice control compatibility and ensuring aria-label includes visible text per WCAG 2.5.3 Label in Name.",
    "version": "1.0.0",
    "wcagCriteria": ["2.5.3"],
    "tests": [
        {
            "id": "aria-label-voice-control",
            "name": "ARIA Label Voice Control Compatibility",
            "description": "Checks if aria-label includes the visible text so voice control users can activate elements by saying the visible text.",
            "impact": "medium",
            "wcagCriteria": ["2.5.3"],
        }
    ]
}

async def test_aria(page) -> Dict[str, Any]:
    """
    Test ARIA attributes for accessibility issues

    Specifically checks for WCAG 2.5.3 Label in Name violation where
    aria-label doesn't include the visible text, preventing voice control
    users from activating the element.

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze ARIA label usage
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
                    test_name: 'aria',
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

                // Get all elements with aria-label attribute
                const elementsWithAriaLabel = Array.from(document.querySelectorAll('[aria-label]'));

                if (elementsWithAriaLabel.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No elements with aria-label found on the page';
                    return results;
                }

                results.elements_tested = elementsWithAriaLabel.length;

                elementsWithAriaLabel.forEach(element => {
                    const ariaLabel = element.getAttribute('aria-label').trim();
                    const tag = element.tagName.toLowerCase();

                    // Get the visible text of the element
                    let visibleText = '';

                    // For buttons and links, get the direct text content (not including children)
                    if (tag === 'button' || tag === 'a') {
                        // Get only the direct text nodes, not nested elements
                        const textNodes = Array.from(element.childNodes)
                            .filter(node => node.nodeType === Node.TEXT_NODE)
                            .map(node => node.textContent.trim())
                            .join(' ');

                        visibleText = textNodes || element.textContent.trim();
                    } else {
                        visibleText = element.textContent.trim();
                    }

                    // Skip if no visible text (like icon-only buttons)
                    if (!visibleText || visibleText.length === 0) {
                        results.elements_passed++;
                        return;
                    }

                    // Check if aria-label includes the visible text (case-insensitive)
                    const ariaLabelLower = ariaLabel.toLowerCase();
                    const visibleTextLower = visibleText.toLowerCase();

                    // WCAG 2.5.3: The accessible name should include the visible text
                    // Voice control users say the visible text to activate the element
                    if (!ariaLabelLower.includes(visibleTextLower)) {
                        results.errors.push({
                            err: 'ErrAriaLabelMayNotBeFoundByVoiceControl',
                            type: 'err',
                            cat: 'aria',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `aria-label does not include visible text - voice control users cannot activate by saying "${visibleText}"`,
                            ariaLabel: ariaLabel,
                            visibleText: visibleText,
                            wcag: '2.5.3'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });

                // Add check information for reporting
                results.checks.push({
                    description: 'ARIA label includes visible text for voice control',
                    wcag: ['2.5.3'],
                    total: elementsWithAriaLabel.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });

                return results;
            }
        ''')

        return results

    except Exception as e:
        logger.error(f"Error in test_aria: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }
