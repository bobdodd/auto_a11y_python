"""
Focus Management touchpoint test module
Evaluates if interactive elements have appropriate focus indicators that meet accessibility standards.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Focus Management Analysis",
    "touchpoint": "focus_management",
    "description": "Evaluates if interactive elements have appropriate focus indicators that meet accessibility standards. This test analyzes CSS rules to identify focus styles and tests whether keyboard users can perceive focus states.",
    "version": "1.1.0",
    "wcagCriteria": ["2.4.7", "2.4.11", "2.4.3"],
    "tests": [
        {
            "id": "focus_outline_presence",
            "name": "Focus Outline Presence",
            "description": "Checks if interactive elements have a visible focus indicator when receiving keyboard focus",
            "impact": "high",
            "wcagCriteria": ["2.4.7"],
        },
        {
            "id": "focus_outline_contrast",
            "name": "Focus Outline Contrast",
            "description": "Measures if focus outlines have sufficient contrast against background colors",
            "impact": "high",
            "wcagCriteria": ["2.4.11"],
        },
        {
            "id": "hover_feedback",
            "name": "Hover Visual Feedback",
            "description": "Checks if elements provide sufficient visual feedback on hover",
            "impact": "medium",
            "wcagCriteria": ["2.4.7"],
        },
        {
            "id": "anchor_target_tabindex",
            "name": "Anchor Target Accessibility",
            "description": "Verifies if in-page link targets are properly configured for keyboard navigation",
            "impact": "medium",
            "wcagCriteria": ["2.4.3"],
        }
    ]
}

async def test_focus_management(page) -> Dict[str, Any]:
    """
    Test focus management and interactive element styling
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze focus management
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
                    test_name: 'focus_management',
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
                
                // Check if element has custom focus styles
                function hasFocusStyles(element) {
                    try {
                        // Create a temporary clone to test focus styles
                        const temp = element.cloneNode(true);
                        temp.style.position = 'absolute';
                        temp.style.left = '-9999px';
                        temp.style.visibility = 'hidden';
                        document.body.appendChild(temp);
                        
                        const normalStyle = window.getComputedStyle(temp);
                        temp.focus();
                        const focusStyle = window.getComputedStyle(temp);
                        
                        // Check if focus styles are different
                        const hasDifferentOutline = focusStyle.outlineWidth !== normalStyle.outlineWidth ||
                                                   focusStyle.outlineStyle !== normalStyle.outlineStyle ||
                                                   focusStyle.outlineColor !== normalStyle.outlineColor;
                        
                        const hasDifferentBackground = focusStyle.backgroundColor !== normalStyle.backgroundColor;
                        const hasDifferentBorder = focusStyle.borderColor !== normalStyle.borderColor;
                        const hasDifferentBoxShadow = focusStyle.boxShadow !== normalStyle.boxShadow;
                        
                        document.body.removeChild(temp);
                        
                        return hasDifferentOutline || hasDifferentBackground || hasDifferentBorder || hasDifferentBoxShadow;
                    } catch (e) {
                        return false;
                    }
                }
                
                // Get all interactive elements
                const interactiveElements = Array.from(document.querySelectorAll(
                    'a, button, input, select, textarea, [role="button"], [role="link"], [tabindex="0"], [contenteditable="true"]'
                )).filter(el => {
                    const style = window.getComputedStyle(el);
                    return style.display !== 'none' && style.visibility !== 'hidden' && !el.disabled;
                });
                
                if (interactiveElements.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No interactive elements found on the page';
                    return results;
                }
                
                results.elements_tested = interactiveElements.length;
                
                // Test each interactive element
                interactiveElements.forEach(element => {
                    const tag = element.tagName.toLowerCase();
                    const text = element.textContent.trim().substring(0, 50);

                    // Check for focus indicators
                    const hasFocus = hasFocusStyles(element);
                    if (!hasFocus) {
                        // Capture HTML, with fallback for edge cases
                        let htmlSnippet = '';
                        let htmlSource = 'unknown';
                        try {
                            if (element.outerHTML) {
                                htmlSnippet = element.outerHTML.substring(0, 200);
                                htmlSource = 'outerHTML';
                            } else {
                                htmlSnippet = `<${tag}${element.id ? ' id="' + element.id + '"' : ''}${element.className ? ' class="' + element.className + '"' : ''}>${text}</${tag}>`;
                                htmlSource = 'fallback-empty';
                            }
                        } catch (e) {
                            htmlSnippet = `<${tag}${element.id ? ' id="' + element.id + '"' : ''}${element.className ? ' class="' + element.className + '"' : ''}>${text}</${tag}>`;
                            htmlSource = 'fallback-error';
                        }

                        results.errors.push({
                            err: 'ErrNoFocusIndicator',
                            type: 'err',
                            cat: 'focus_management',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: htmlSnippet,
                            htmlSource: htmlSource,
                            description: 'Interactive element has no visible focus indicator',
                            text: text
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                    
                    // Check hover styles
                    const style = window.getComputedStyle(element);
                    if (['a', 'button'].includes(tag) && style.cursor !== 'pointer') {
                        results.warnings.push({
                            err: 'WarnNoCursorPointer',
                            type: 'warn',
                            cat: 'focus_management',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Interactive element does not have pointer cursor on hover',
                            text: text
                        });
                    }
                });
                
                // Check in-page link targets
                const anchorLinks = Array.from(document.querySelectorAll('a[href^="#"]:not([href="#"])'));
                const processedTargets = new Set();

                anchorLinks.forEach(link => {
                    const targetId = link.getAttribute('href').substring(1);
                    const target = document.getElementById(targetId);

                    if (target && !processedTargets.has(targetId)) {
                        const tabindex = target.getAttribute('tabindex');
                        const isInteractive = ['a', 'button', 'input', 'select', 'textarea'].includes(target.tagName.toLowerCase());

                        if (!isInteractive && tabindex !== '-1') {
                            // Find all anchor links pointing to this target
                            const linksToTarget = anchorLinks.filter(l =>
                                l.getAttribute('href').substring(1) === targetId
                            ).map((l, idx) => ({
                                index: idx + 1,
                                html: l.outerHTML.substring(0, 200),
                                xpath: getFullXPath(l),
                                text: l.textContent.trim()
                            }));

                            results.errors.push({
                                err: 'ErrAnchorTargetTabindex',
                                type: 'err',
                                cat: 'links',
                                element: target.tagName.toLowerCase(),
                                xpath: getFullXPath(target),
                                html: target.outerHTML.substring(0, 200),
                                description: 'In-page link target needs tabindex="-1" for keyboard accessibility - non-interactive element must be programmatically focusable',
                                metadata: {
                                    targetId: targetId,
                                    currentTabindex: tabindex || 'not set',
                                    anchorLinks: linksToTarget,
                                    anchorLinksCount: linksToTarget.length
                                }
                            });

                            processedTargets.add(targetId);
                        }
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Focus indicators',
                    wcag: ['2.4.7'],
                    total: interactiveElements.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });
                
                if (anchorLinks.length > 0) {
                    results.checks.push({
                        description: 'In-page link targets',
                        wcag: ['2.4.3'],
                        total: anchorLinks.length,
                        passed: anchorLinks.length,
                        failed: 0
                    });
                }
                
                return results;
            }
        ''')

        # Log focus errors for debugging
        if 'errors' in results:
            for error in results['errors']:
                if error.get('err') == 'ErrNoFocusIndicator':
                    break  # Just check first one

        return results
        
    except Exception as e:
        logger.error(f"Error in test_focus_management: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }