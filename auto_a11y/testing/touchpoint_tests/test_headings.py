"""
Headings touchpoint test module
Evaluates the document's heading structure to ensure proper hierarchy, positioning, and semantic markup.
"""

from typing import Dict, Any
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

                // Check for elements with aria-level but NO role attribute
                const ariaLevelWithoutRole = Array.from(document.querySelectorAll('[aria-level]')).filter(el => !el.hasAttribute('role'));
                ariaLevelWithoutRole.forEach(element => {
                    results.errors.push({
                        err: 'ErrFoundAriaLevelButNoRoleAppliedAtAll',
                        type: 'err',
                        cat: 'headings',
                        element: element.tagName.toLowerCase(),
                        xpath: getFullXPath(element),
                        html: element.outerHTML.substring(0, 200),
                        description: `Element has aria-level="${element.getAttribute('aria-level')}" but no role attribute - aria-level requires role="heading"`,
                        ariaLevel: element.getAttribute('aria-level')
                    });
                    results.elements_failed++;
                });

                // Check for elements with aria-level but role is NOT "heading"
                const ariaLevelWithWrongRole = Array.from(document.querySelectorAll('[aria-level][role]')).filter(el => el.getAttribute('role') !== 'heading');
                ariaLevelWithWrongRole.forEach(element => {
                    results.errors.push({
                        err: 'ErrFoundAriaLevelButRoleIsNotHeading',
                        type: 'err',
                        cat: 'headings',
                        element: element.tagName.toLowerCase(),
                        xpath: getFullXPath(element),
                        html: element.outerHTML.substring(0, 200),
                        description: `Element has aria-level="${element.getAttribute('aria-level')}" with role="${element.getAttribute('role')}" - aria-level requires role="heading"`,
                        ariaLevel: element.getAttribute('aria-level'),
                        role: element.getAttribute('role')
                    });
                    results.elements_failed++;
                });

                // Check for elements with role="heading" and validate aria-level
                const roleHeadings = Array.from(document.querySelectorAll('[role="heading"]'));
                roleHeadings.forEach(element => {
                    const ariaLevel = element.getAttribute('aria-level');

                    if (!ariaLevel) {
                        // role="heading" without aria-level
                        results.errors.push({
                            err: 'ErrRoleOfHeadingButNoLevelGiven',
                            type: 'err',
                            cat: 'headings',
                            element: element.tagName.toLowerCase(),
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `Element has role="heading" but no aria-level attribute - heading level is undefined`,
                            role: element.getAttribute('role')
                        });
                        results.elements_failed++;
                    } else {
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

                // Check if page has NO headings at all (major accessibility error)
                if (headings.length === 0 && roleHeadings.length === 0) {
                    results.errors.push({
                        err: 'ErrNoHeadingsOnPage',
                        type: 'err',
                        cat: 'headings',
                        element: 'page',
                        xpath: '/html',
                        html: '<page>',
                        description: 'No heading elements (h1-h6) found anywhere on the page'
                    });
                    results.elements_failed++;
                    return results;
                }

                // If we only have ARIA headings, use those
                if (headings.length === 0 && roleHeadings.length > 0) {
                    // Continue with analysis using only ARIA headings
                    // Note: roleHeadings will be checked separately below
                }

                results.elements_tested = headings.length + roleHeadings.length;
                
                // Track heading counts
                const headingCounts = { h1: 0, h2: 0, h3: 0, h4: 0, h5: 0, h6: 0 };
                const headingHierarchy = [];
                
                // Check for H1 presence (native <h1> or ARIA heading with aria-level="1")
                const h1Elements = headings.filter(h => h.tagName.toLowerCase() === 'h1');
                const ariaH1Elements = roleHeadings.filter(h => h.getAttribute('aria-level') === '1');
                const totalH1Count = h1Elements.length + ariaH1Elements.length;
                headingCounts.h1 = totalH1Count;

                if (totalH1Count === 0) {
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
                } else if (totalH1Count > 1) {
                    // Create ONE error with all H1s listed (both native and ARIA)
                    const allH1s = [];
                    h1Elements.forEach((h1, index) => {
                        allH1s.push({
                            index: index + 1,
                            type: 'native',
                            xpath: getFullXPath(h1),
                            html: h1.outerHTML.substring(0, 200),
                            text: h1.textContent.trim()
                        });
                    });
                    ariaH1Elements.forEach((h1, index) => {
                        allH1s.push({
                            index: h1Elements.length + index + 1,
                            type: 'aria',
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
                        description: `Page contains ${totalH1Count} h1 elements (${h1Elements.length} native, ${ariaH1Elements.length} ARIA) instead of just one`,
                        count: totalH1Count,
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

                    // Check for illogical heading order BEFORE incrementing counters
                    // This detects when a high-level heading appears after lower-level ones FOR THE FIRST TIME
                    // Examples: page starts with H3, then has H1 later (wrong)
                    // But: H1, H2, H3, then H2 again is CORRECT (returning from subsection)
                    if (level <= 2) {
                        // Check if this is the FIRST occurrence of this heading level
                        const isFirstOccurrence = (headingCounts[tagName] || 0) === 0;

                        // Check if we've already seen lower-level (higher number) headings
                        const maxLevelSeenSoFar = headingHierarchy.length > 0 ? Math.max(...headingHierarchy) : 0;

                        // If this is the first H1 or H2, and we've already seen H3+ headings, that's wrong order
                        if (isFirstOccurrence && maxLevelSeenSoFar > level) {
                            results.errors.push({
                                err: 'ErrHeadingOrder',
                                type: 'err',
                                cat: 'headings',
                                element: heading.tagName,
                                xpath: getFullXPath(heading),
                                html: heading.outerHTML.substring(0, 200),
                                description: `Illogical heading order: ${heading.tagName} appears after H${maxLevelSeenSoFar}, but high-level headings should come first`,
                                currentLevel: level,
                                maxLevelSeen: maxLevelSeenSoFar,
                                previousHeadingHtml: previousHeading ? previousHeading.outerHTML.substring(0, 200) : '',
                                previousHeadingXpath: previousHeading ? getFullXPath(previousHeading) : '',
                                previousHeadingText: previousHeading ? previousHeading.textContent.trim().substring(0, 100) : ''
                            });
                            results.elements_failed++;
                        }
                    }

                    // Now update counters
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
                            description: 'Heading element contains only whitespace or special characters',
                            text: textDisplay,           // Visual representation
                            originalText: originalText    // Raw original text
                        });
                        results.elements_failed++;
                    } else {

                        // Check for heading hierarchy gaps
                        if (previousLevel > 0 && level > previousLevel + 1) {
                            const expectedLevel = previousLevel + 1;
                            const levelsSkipped = level - previousLevel - 1;

                            // If skipping 2+ levels, it's likely choosing heading for visual appearance
                            // Example: H1 -> H4 (skipping H2 and H3) suggests using H4 for its visual size
                            if (levelsSkipped >= 2) {
                                results.errors.push({
                                    err: 'ErrIncorrectHeadingLevel',
                                    type: 'err',
                                    cat: 'headings',
                                    element: heading.tagName,
                                    xpath: getFullXPath(heading),
                                    html: heading.outerHTML.substring(0, 200),
                                    description: `Heading level ${heading.tagName} appears after H${previousLevel}, skipping ${levelsSkipped} levels - likely chosen for visual appearance rather than document structure`,
                                    skippedFrom: previousLevel,
                                    skippedTo: level,
                                    levelsSkipped: levelsSkipped,
                                    previousHeadingHtml: previousHeading ? previousHeading.outerHTML.substring(0, 200) : '',
                                    previousHeadingXpath: previousHeading ? getFullXPath(previousHeading) : '',
                                    previousHeadingText: previousHeading ? previousHeading.textContent.trim().substring(0, 100) : ''
                                });
                                results.elements_failed++;
                            } else {
                                // Only skipped 1 level - this is ErrSkippedHeadingLevel
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
                            }
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

                        // Check for WCAG 2.5.3: Visible text must match accessible name
                        const ariaLabel = heading.getAttribute('aria-label');
                        const ariaLabelledby = heading.getAttribute('aria-labelledby');

                        if (ariaLabel || ariaLabelledby) {
                            let accessibleName = ariaLabel;

                            // If using aria-labelledby, get the text from referenced element(s)
                            if (ariaLabelledby && !ariaLabel) {
                                const ids = ariaLabelledby.split(/\s+/);
                                accessibleName = ids.map(id => {
                                    const el = document.getElementById(id);
                                    return el ? el.textContent.trim() : '';
                                }).filter(text => text).join(' ');
                            }

                            if (accessibleName && textContent) {
                                // Get only visible text (excluding aria-hidden elements)
                                const visibleText = Array.from(heading.childNodes).map(node => {
                                    if (node.nodeType === Node.TEXT_NODE) {
                                        return node.textContent;
                                    } else if (node.nodeType === Node.ELEMENT_NODE) {
                                        const el = node;
                                        if (el.getAttribute('aria-hidden') === 'true') {
                                            return '';
                                        }
                                        // Exclude sr-only elements from visible text
                                        const classes = el.className || '';
                                        if (classes.includes('sr-only') || classes.includes('visually-hidden')) {
                                            return '';
                                        }
                                        return el.textContent;
                                    }
                                    return '';
                                }).join(' ').trim();

                                const visibleTextLower = visibleText.toLowerCase();
                                const accessibleNameLower = accessibleName.toLowerCase();

                                // WCAG 2.5.3: Visible text should START the accessible name (or match exactly)
                                // This is stricter than just "contained" but more aligned with voice control needs
                                if (visibleText && !accessibleNameLower.startsWith(visibleTextLower)) {
                                    results.errors.push({
                                        err: 'ErrHeadingAccessibleNameMismatch',
                                        type: 'err',
                                        cat: 'headings',
                                        element: heading.tagName,
                                        xpath: getFullXPath(heading),
                                        html: heading.outerHTML.substring(0, 200),
                                        description: `${heading.tagName} visible text "${visibleText}" does not start accessible name "${accessibleName}" - voice control users cannot reference it`,
                                        visibleText: visibleText,
                                        accessibleName: accessibleName
                                    });
                                    results.elements_failed++;
                                }
                            }
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

                // Check for visual hierarchy mismatches
                // Visual size should match semantic hierarchy (H1 largest, H6 smallest)
                const headingsWithSizes = headings.map(heading => {
                    const style = window.getComputedStyle(heading);
                    const fontSize = parseFloat(style.fontSize);
                    const fontWeight = style.fontWeight === 'bold' || parseInt(style.fontWeight) >= 600 ? 1.2 : 1.0;
                    // Calculate visual "weight" combining size and boldness
                    const visualWeight = fontSize * fontWeight;

                    return {
                        element: heading,
                        tagName: heading.tagName.toLowerCase(),
                        level: parseInt(heading.tagName.charAt(1)),
                        fontSize: fontSize,
                        fontWeight: style.fontWeight,
                        visualWeight: visualWeight,
                        xpath: getFullXPath(heading)
                    };
                });

                // Compare each heading with others to find visual hierarchy issues
                for (let i = 0; i < headingsWithSizes.length; i++) {
                    const current = headingsWithSizes[i];

                    // Check if a lower-level heading (higher number) is visually larger
                    for (let j = 0; j < headingsWithSizes.length; j++) {
                        if (i === j) continue;

                        const other = headingsWithSizes[j];

                        // If current is higher level (lower number) but visually smaller, that's wrong
                        // Example: H2 should be visually larger than H3
                        if (current.level < other.level && current.visualWeight < other.visualWeight * 0.9) {
                            // Use 0.9 threshold to avoid false positives from minor differences
                            results.warnings.push({
                                err: 'WarnVisualHierarchy',
                                type: 'warn',
                                cat: 'headings',
                                element: current.tagName,
                                xpath: current.xpath,
                                html: current.element.outerHTML.substring(0, 200),
                                description: `${current.tagName.toUpperCase()} (${current.fontSize.toFixed(1)}px) is visually smaller than ${other.tagName.toUpperCase()} (${other.fontSize.toFixed(1)}px) - visual hierarchy doesn't match semantic hierarchy`,
                                currentLevel: current.level,
                                currentSize: current.fontSize,
                                otherLevel: other.level,
                                otherSize: other.fontSize,
                                otherXpath: other.xpath
                            });
                            // Only report once per heading
                            break;
                        }
                    }
                }

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