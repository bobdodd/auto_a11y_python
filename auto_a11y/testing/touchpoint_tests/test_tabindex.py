"""
Tabindex touchpoint test module
Evaluates the proper usage of tabindex attributes across different element types.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Tabindex Attribute Analysis",
    "touchpoint": "tabindex",
    "description": "Evaluates the proper usage of tabindex attributes across different element types. This test identifies improper use of positive tabindex values, non-interactive elements with tabindex='0', and missing negative tabindex on in-page targets.",
    "version": "1.0.0",
    "wcagCriteria": ["2.4.3", "2.1.1", "4.1.2"],
    "tests": [
        {
            "id": "positive-tabindex",
            "name": "Positive Tabindex Values",
            "description": "Identifies elements with positive tabindex values that can disrupt natural tab order.",
            "impact": "high",
            "wcagCriteria": ["2.4.3"],
        },
        {
            "id": "non-interactive-zero-tabindex",
            "name": "Non-interactive Elements with Zero Tabindex",
            "description": "Checks for non-interactive elements that have been made focusable with tabindex='0'.",
            "impact": "medium",
            "wcagCriteria": ["2.1.1", "4.1.2"],
        },
        {
            "id": "missing-negative-tabindex",
            "name": "Missing Negative Tabindex on In-Page Targets",
            "description": "Verifies that non-interactive elements that are targets of in-page links have tabindex='-1'.",
            "impact": "medium",
            "wcagCriteria": ["2.4.3"],
        },
        {
            "id": "svg-tabindex",
            "name": "SVG Element Tabindex",
            "description": "Checks tabindex usage on SVG elements, which may have special considerations.",
            "impact": "low",
            "wcagCriteria": ["2.1.1"],
        }
    ]
}

async def test_tabindex(page) -> Dict[str, Any]:
    """
    Test tabindex attributes for proper usage across different element types
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze tabindex usage
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
                    test_name: 'tabindex',
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
                
                // Check if element is interactive
                function isInteractiveElement(element) {
                    const interactiveTags = [
                        'a', 'button', 'input', 'select', 'textarea', 'video',
                        'audio', 'details', 'summary'
                    ];
                    const interactiveRoles = [
                        'button', 'checkbox', 'combobox', 'link', 'menuitem',
                        'radio', 'slider', 'spinbutton', 'switch', 'tab',
                        'textbox'
                    ];

                    return interactiveTags.includes(element.tagName.toLowerCase()) ||
                           (element.getAttribute('role') && 
                            interactiveRoles.includes(element.getAttribute('role')));
                }
                
                // Check if element is target of in-page link
                function isInPageTarget(element) {
                    if (!element.id) return false;
                    const selector = `a[href="#${element.id}"]`;
                    const link = document.querySelector(selector);
                    return !!link;
                }
                
                // Check if element is within SVG
                function isWithinSVG(element) {
                    let current = element;
                    while (current && current !== document.body) {
                        if (current.tagName.toLowerCase() === 'svg') {
                            return true;
                        }
                        current = current.parentElement;
                    }
                    return false;
                }
                
                // Find all elements with tabindex
                const elementsWithTabindex = Array.from(document.querySelectorAll('[tabindex]'));
                
                if (elementsWithTabindex.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No elements with tabindex found on the page';
                    return results;
                }
                
                results.elements_tested = elementsWithTabindex.length;
                
                let positiveTabindexCount = 0;
                let nonInteractiveZeroCount = 0;
                let svgTabindexWarnings = 0;
                
                // Process each element with tabindex
                elementsWithTabindex.forEach(element => {
                    const tabindexValue = element.getAttribute('tabindex');
                    const tabindex = parseInt(tabindexValue);
                    const isInteractive = isInteractiveElement(element);
                    const inSVG = isWithinSVG(element);

                    let hasViolation = false;

                    // Check for invalid tabindex (non-numeric values)
                    if (isNaN(tabindex)) {
                        results.errors.push({
                            err: 'ErrInvalidTabindex',
                            type: 'err',
                            cat: 'tabindex',
                            element: element.tagName.toLowerCase(),
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `Element has invalid tabindex value "${tabindexValue}" which is not a valid integer`,
                            tabindex: tabindexValue
                        });
                        hasViolation = true;
                        results.elements_failed++;
                        return; // Skip other checks for this element
                    }

                    // Check for positive tabindex
                    if (tabindex > 0 && !inSVG) {
                        positiveTabindexCount++;
                        results.errors.push({
                            err: 'ErrPositiveTabindex',
                            type: 'err',
                            cat: 'tabindex',
                            element: element.tagName.toLowerCase(),
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `Element has positive tabindex (${tabindex}) which disrupts natural tab order`,
                            tabindex: tabindex
                        });
                        hasViolation = true;
                    }
                    
                    // Check for non-interactive elements with tabindex="0"
                    // Skip this check for in-page link targets - they're handled separately with more specific error
                    if (tabindex === 0 && !isInteractive && !isInPageTarget(element)) {
                        nonInteractiveZeroCount++;
                        results.errors.push({
                            err: 'ErrNonInteractiveZeroTabindex',
                            type: 'err',
                            cat: 'tabindex',
                            element: element.tagName.toLowerCase(),
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Non-interactive element has tabindex="0" making it focusable without interaction capability',
                            role: element.getAttribute('role') || 'none'
                        });
                        hasViolation = true;
                    }
                    
                    // Check for SVG elements with positive tabindex
                    if (inSVG && tabindex > 0) {
                        svgTabindexWarnings++;
                        results.warnings.push({
                            err: 'WarnSvgPositiveTabindex',
                            type: 'warn',
                            cat: 'tabindex',
                            element: element.tagName.toLowerCase(),
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `SVG element has positive tabindex (${tabindex}) which may cause accessibility issues`,
                            tabindex: tabindex
                        });
                    }
                    
                    if (!hasViolation) {
                        results.elements_passed++;
                    } else {
                        results.elements_failed++;
                    }
                });
                
                // Check for incorrect tabindex on in-page targets
                const inPageTargets = Array.from(document.querySelectorAll('*[id]'));
                let missingRequiredTabindex = 0;

                inPageTargets.forEach(element => {
                    if (isInPageTarget(element) && !isInteractiveElement(element)) {
                        const tabindexValue = element.getAttribute('tabindex');

                        // Check if it's a skip link target specifically
                        const skipLinks = Array.from(document.querySelectorAll('a[href^="#"]'))
                            .filter(a => {
                                const href = a.getAttribute('href');
                                return href === `#${element.id}` &&
                                       (a.textContent.toLowerCase().includes('skip') ||
                                        a.classList.contains('skip-link') ||
                                        a.classList.contains('skip'));
                            });
                        const isSkipTarget = skipLinks.length > 0;

                        if (tabindexValue !== '-1') {
                            missingRequiredTabindex++;

                            // Use ErrAnchorTargetTabindex for both missing and wrong tabindex values
                            const currentTabindexDesc = tabindexValue !== null ? `tabindex="${tabindexValue}"` : 'no tabindex';
                            const description = tabindexValue !== null
                                ? `In-page link target has tabindex="${tabindexValue}" but should be tabindex="-1" for programmatic focus only`
                                : 'In-page link target missing tabindex="-1" for proper focus management';

                            results.errors.push({
                                err: 'ErrAnchorTargetTabindex',
                                type: 'err',
                                cat: 'tabindex',
                                element: element.tagName.toLowerCase(),
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                description: description,
                                id: element.id,
                                currentTabindex: tabindexValue !== null ? tabindexValue : 'not set',
                                isSkipTarget: isSkipTarget,
                                linkingElements: skipLinks.map(a => ({
                                    text: a.textContent.trim(),
                                    href: a.getAttribute('href')
                                }))
                            });
                            results.elements_failed++;
                        }
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Tabindex usage violations',
                    wcag: ['2.4.3', '2.1.1', '4.1.2'],
                    total: elementsWithTabindex.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });
                
                if (positiveTabindexCount > 0) {
                    results.checks.push({
                        description: 'Positive tabindex values',
                        wcag: ['2.4.3'],
                        total: elementsWithTabindex.length,
                        passed: elementsWithTabindex.length - positiveTabindexCount,
                        failed: positiveTabindexCount
                    });
                }
                
                if (nonInteractiveZeroCount > 0) {
                    results.checks.push({
                        description: 'Non-interactive elements with zero tabindex',
                        wcag: ['2.1.1', '4.1.2'],
                        total: elementsWithTabindex.length,
                        passed: elementsWithTabindex.length - nonInteractiveZeroCount,
                        failed: nonInteractiveZeroCount
                    });
                }
                
                if (missingRequiredTabindex > 0) {
                    results.checks.push({
                        description: 'In-page link targets missing tabindex',
                        wcag: ['2.4.3'],
                        total: inPageTargets.filter(el => isInPageTarget(el) && !isInteractiveElement(el)).length,
                        passed: inPageTargets.filter(el => isInPageTarget(el) && !isInteractiveElement(el)).length - missingRequiredTabindex,
                        failed: missingRequiredTabindex
                    });
                }
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_tabindex: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }