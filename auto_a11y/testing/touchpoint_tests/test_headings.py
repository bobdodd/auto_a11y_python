"""
Headings touchpoint test module
Evaluates the document's heading structure to ensure proper hierarchy, positioning, and semantic markup.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Heading Structure Analysis",
    "touchpoint": "headings",
    "description": "Evaluates the document's heading structure to ensure proper hierarchy, positioning, and semantic markup. Properly structured headings are essential for screen reader users to navigate content and understand document organization.",
    "version": "1.2.0",
    "wcagCriteria": ["1.3.1", "2.4.1", "2.4.6", "2.4.10"],
    "tests": [
        {
            "id": "h1-presence",
            "name": "H1 Presence and Uniqueness",
            "description": "Checks if the page has exactly one H1 heading that serves as the main title of the page.",
            "impact": "high",
            "wcagCriteria": ["1.3.1", "2.4.1", "2.4.6"],
        },
        {
            "id": "heading-hierarchy",
            "name": "Heading Hierarchy",
            "description": "Verifies that headings follow a logical hierarchy without skipping levels.",
            "impact": "high",
            "wcagCriteria": ["1.3.1", "2.4.10"],
        },
        {
            "id": "empty-headings",
            "name": "Empty Headings",
            "description": "Identifies headings that have no text content or contain only whitespace.",
            "impact": "high",
            "wcagCriteria": ["1.3.1", "2.4.6"],
        },
    ]
}

async def test_headings(page) -> Dict[str, Any]:
    """
    Test headings for proper hierarchy and structure
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze headings
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
                    test_name: 'headings',
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
                
                // Get heading length limit from config, default to 60
                const headingLengthLimit = (window.a11yConfig && window.a11yConfig.headingLengthLimit) || 60;
                const headingNearLimit = Math.floor(headingLengthLimit * 0.67); // ~40 for default 60

                // Get all headings
                const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));

                // Check for elements with role="heading" and invalid aria-level
                const roleHeadings = Array.from(document.querySelectorAll('[role="heading"]'));
                roleHeadings.forEach(element => {
                    const ariaLevel = element.getAttribute('aria-level');

                    if (ariaLevel) {
                        const levelNum = parseInt(ariaLevel, 10);

                        // Check if aria-level is invalid (not 1-6 or not a valid number)
                        if (isNaN(levelNum) || levelNum < 1 || levelNum > 6) {
                            results.errors.push({
                                err: 'ErrInvalidAriaLevel',
                                type: 'err',
                                cat: 'headings',
                                element: element.tagName,
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                description: `Element with role="heading" has invalid aria-level="${ariaLevel}" (must be 1-6)`,
                                ariaLevel: ariaLevel,
                                role: element.getAttribute('role')
                            });
                            results.elements_failed++;
                        }
                    }
                });

                if (headings.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No headings found on the page';
                    return results;
                }

                results.elements_tested = headings.length + roleHeadings.length;
                
                // Track heading counts
                const headingCounts = { h1: 0, h2: 0, h3: 0, h4: 0, h5: 0, h6: 0 };
                const headingHierarchy = [];
                
                // Check for H1 presence
                const h1Elements = headings.filter(h => h.tagName.toLowerCase() === 'h1');
                headingCounts.h1 = h1Elements.length;
                
                if (h1Elements.length === 0) {
                    results.errors.push({
                        err: 'ErrNoH1',
                        type: 'err',
                        cat: 'headings',
                        element: 'page',
                        xpath: '/html',
                        html: '<page>',
                        description: 'Page is missing an H1 heading'
                    });
                    results.elements_failed++;
                } else if (h1Elements.length > 1) {
                    // Create ONE error with all H1s listed
                    const allH1s = [];
                    h1Elements.forEach((h1, index) => {
                        allH1s.push({
                            index: index + 1,
                            xpath: getFullXPath(h1),
                            html: h1.outerHTML.substring(0, 200),
                            text: h1.textContent.trim()
                        });
                    });

                    results.errors.push({
                        err: 'ErrMultipleH1',
                        type: 'err',
                        cat: 'headings',
                        element: 'page',
                        xpath: allH1s[0].xpath,  // Use first H1's xpath as primary location
                        html: allH1s[0].html,     // Use first H1's HTML as primary snippet
                        description: `Page contains ${h1Elements.length} h1 elements instead of just one`,
                        count: h1Elements.length,
                        allH1s: allH1s
                    });
                    results.elements_failed++;
                } else {
                    results.elements_passed++;
                }
                
                // Check each heading
                let previousLevel = 0;
                let previousHeading = null;
                headings.forEach(heading => {
                    const tagName = heading.tagName.toLowerCase();
                    const level = parseInt(tagName.charAt(1));
                    headingCounts[tagName]++;
                    headingHierarchy.push(level);

                    // Check for empty headings
                    const textContent = heading.textContent.trim();
                    const originalText = heading.textContent;  // Capture original (untrimmed) text

                    // Check if heading has images with alt text (not empty if so)
                    const images = heading.querySelectorAll('img[alt]');
                    const hasImageWithAlt = Array.from(images).some(img => img.alt.trim() !== '');

                    if (!textContent && !hasImageWithAlt) {
                        // Create visual representation of the empty/whitespace content
                        let textDisplay = originalText;
                        if (textDisplay === '') {
                            textDisplay = '(empty)';
                        } else {
                            // Show whitespace characters visibly using split/join to avoid regex
                            textDisplay = textDisplay.split(' ').join('\u00B7')    // Space to middle dot
                                                     .split('\\t').join('\u2192')   // Tab to arrow
                                                     .split('\\n').join('\u21B5')   // Newline to return symbol
                                                     .split('\\r').join('');        // Remove carriage return
                            if (textDisplay === '') textDisplay = '(whitespace)';
                        }

                        results.errors.push({
                            err: 'ErrEmptyHeading',
                            type: 'err',
                            cat: 'headings',
                            element: heading.tagName,
                            xpath: getFullXPath(heading),
                            html: heading.outerHTML.substring(0, 200),
                            description: `${heading.tagName} element is empty`,
                            text: textDisplay,           // Visual representation
                            originalText: originalText    // Raw original text
                        });
                        results.elements_failed++;
                    } else {
                        // Check for heading hierarchy gaps
                        if (previousLevel > 0 && level > previousLevel + 1) {
                            const expectedLevel = previousLevel + 1;
                            results.errors.push({
                                err: 'ErrSkippedHeadingLevel',
                                type: 'err',
                                cat: 'headings',
                                element: heading.tagName,
                                xpath: getFullXPath(heading),
                                html: heading.outerHTML.substring(0, 200),
                                description: `Heading level skipped from H${previousLevel} to H${level}`,
                                skippedFrom: previousLevel,
                                skippedTo: level,
                                expectedLevel: expectedLevel,
                                previousHeadingHtml: previousHeading ? previousHeading.outerHTML.substring(0, 200) : '',
                                previousHeadingXpath: previousHeading ? getFullXPath(previousHeading) : '',
                                previousHeadingText: previousHeading ? previousHeading.textContent.trim().substring(0, 100) : ''
                            });
                            results.elements_failed++;
                        } else {
                            results.elements_passed++;
                        }

                        previousHeading = heading;
                        
                        // Check for excessively long headings
                        if (textContent.length > headingLengthLimit) {
                            results.warnings.push({
                                err: 'WarnHeadingOver60CharsLong',
                                type: 'warn',
                                cat: 'headings',
                                element: heading.tagName,
                                xpath: getFullXPath(heading),
                                html: heading.outerHTML.substring(0, 200),
                                description: `${heading.tagName} text is ${textContent.length} characters long (should be under ${headingLengthLimit})`,
                                length: textContent.length,
                                limit: headingLengthLimit,
                                text: textContent.substring(0, 100)
                            });
                        }

                        // Info: Check for optimal heading length (best practice)
                        if (textContent.length > headingNearLimit && textContent.length <= headingLengthLimit) {
                            results.warnings.push({
                                err: 'InfoHeadingNearLengthLimit',
                                type: 'info',
                                cat: 'headings',
                                element: heading.tagName,
                                xpath: getFullXPath(heading),
                                html: heading.outerHTML.substring(0, 200),
                                description: `${heading.tagName} is ${textContent.length} characters - consider shortening for better readability`,
                                length: textContent.length,
                                limit: headingLengthLimit,
                                nearLimit: headingNearLimit,
                                text: textContent.substring(0, 100)
                            });
                        }
                        
                        // Discovery: Track heading usage patterns
                        if (heading.id || heading.className) {
                            results.warnings.push({
                                err: 'DiscoHeadingWithID',
                                type: 'disco',
                                cat: 'headings',
                                element: heading.tagName,
                                xpath: getFullXPath(heading),
                                html: heading.outerHTML.substring(0, 200),
                                description: `${heading.tagName} has ID or class attributes (potential navigation anchor)`,
                                metadata: {
                                    id: heading.id,
                                    classes: heading.className
                                }
                            });
                        }
                    }
                    
                    previousLevel = level;
                });
                
                // Check for headings inside display:none elements
                headings.forEach(heading => {
                    const style = window.getComputedStyle(heading);
                    if (style.display === 'none' || style.visibility === 'hidden') {
                        results.warnings.push({
                            err: 'WarnHeadingInsideDisplayNone',
                            type: 'warn',
                            cat: 'headings',
                            element: heading.tagName,
                            xpath: getFullXPath(heading),
                            html: heading.outerHTML.substring(0, 200),
                            description: `${heading.tagName} is hidden from view`
                        });
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'H1 presence and uniqueness',
                    wcag: ['1.3.1', '2.4.1', '2.4.6'],
                    total: 1,
                    passed: headingCounts.h1 === 1 ? 1 : 0,
                    failed: headingCounts.h1 === 1 ? 0 : 1
                });
                
                results.checks.push({
                    description: 'Heading hierarchy',
                    wcag: ['1.3.1', '2.4.10'],
                    total: headings.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });
                
                return results;
            }
        ''')

        # Log skipped heading errors for debugging
        if 'errors' in results:
            # Validation of heading errors
            skipped_errors = [e for e in results['errors'] if e.get('err') == 'ErrSkippedHeadingLevel']

        return results
        
    except Exception as e:
        logger.error(f"Error in test_headings: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }