"""
Colors touchpoint test module
Evaluates color usage and contrast ratios on the page to ensure content is perceivable by users with low vision.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Color Usage Analysis",
    "touchpoint": "colors",
    "description": "Evaluates color usage on the page to ensure content is perceivable by users with low vision, color vision deficiencies, or those who use high contrast modes. This test examines color-only distinctions and color scheme support. Note: Text contrast is tested separately by test_text_contrast.py.",
    "version": "1.0.0",
    "wcagCriteria": ["1.4.1"],
    "tests": [
        {
            "id": "color-only-distinction",
            "name": "Color-Only Distinctions",
            "description": "Identifies cases where color alone is used to convey information, particularly for links that are distinguished only by color without additional visual cues.",
            "impact": "high",
            "wcagCriteria": ["1.4.1"],
        }
    ]
}

async def test_colors(page) -> Dict[str, Any]:
    """
    Test color usage and contrast requirements across the page
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze colors and contrast
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
                    test_name: 'colors',
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
                
                // Helper functions for link distinction testing

                function hasNonColorDistinction(element) {
                    const style = window.getComputedStyle(element);

                    // Strong indicators (pass without warning)
                    const hasUnderline = style.textDecoration !== 'none' && style.textDecoration.includes('underline');
                    const hasTextDecorationLine = style.textDecorationLine !== 'none' && style.textDecorationLine !== '';
                    const hasBorder = style.borderWidth && style.borderWidth !== '0px' &&
                                    (style.borderStyle !== 'none' && style.borderStyle !== '');
                    const hasOutline = style.outlineWidth && style.outlineWidth !== '0px' &&
                                     (style.outlineStyle !== 'none' && style.outlineStyle !== '');

                    if (hasUnderline || hasTextDecorationLine || hasBorder || hasOutline) {
                        return { hasIndicator: true, isWeak: false };
                    }

                    // Weak indicators (pass but generate warning)
                    const parentStyle = element.parentElement ? window.getComputedStyle(element.parentElement) : null;
                    const linkWeight = parseInt(style.fontWeight) || 400;
                    const parentWeight = parentStyle ? (parseInt(parentStyle.fontWeight) || 400) : 400;
                    const hasWeightDifference = linkWeight > parentWeight;

                    const hasBoldTag = element.querySelector('b, strong') !== null ||
                                      element.tagName === 'B' || element.tagName === 'STRONG';

                    const hasTextShadow = style.textShadow && style.textShadow !== 'none';

                    if (hasWeightDifference || hasBoldTag || hasTextShadow) {
                        return { hasIndicator: true, isWeak: true };
                    }

                    return { hasIndicator: false, isWeak: false };
                }

                function isInNavigationContext(element) {
                    // Check if link is within navigation regions where context makes purpose clear
                    let current = element;
                    while (current && current !== document.body) {
                        const role = current.getAttribute('role');
                        const tagName = current.tagName.toLowerCase();

                        // Check for navigation landmarks
                        if (role === 'navigation' || tagName === 'nav') {
                            return true;
                        }

                        // Check for common navigation class names
                        const className = current.className || '';
                        if (typeof className === 'string' &&
                            (className.includes('nav') || className.includes('menu') ||
                             className.includes('header') || className.includes('footer'))) {
                            return true;
                        }

                        current = current.parentElement;
                    }
                    return false;
                }

                function isInFlowingText(element) {
                    // Check if link is within flowing text (paragraphs, list items, etc.)
                    // AND has actual text content before or after it (not a standalone link)
                    let current = element.parentElement;
                    while (current && current !== document.body) {
                        const tagName = current.tagName.toLowerCase();

                        // Flowing text containers
                        if (['p', 'li', 'td', 'th', 'dd', 'dt', 'blockquote', 'figcaption'].includes(tagName)) {
                            // Check if there's actual text content in this container besides the link
                            const hasTextContent = Array.from(current.childNodes).some(node => {
                                // Text node with content (not just whitespace)
                                if (node.nodeType === 3 && node.textContent.trim().length > 0) {
                                    return true;
                                }
                                // Other elements that might contain text (but not the link itself)
                                if (node.nodeType === 1 && node !== element &&
                                    !node.contains(element) && node.textContent.trim().length > 0) {
                                    return true;
                                }
                                return false;
                            });

                            return hasTextContent;
                        }

                        // Article content
                        if (tagName === 'article' || current.getAttribute('role') === 'article') {
                            // Check if there's text content in the article besides the link
                            const hasTextContent = Array.from(current.childNodes).some(node => {
                                if (node.nodeType === 3 && node.textContent.trim().length > 0) {
                                    return true;
                                }
                                if (node.nodeType === 1 && node !== element &&
                                    !node.contains(element) && node.textContent.trim().length > 0) {
                                    return true;
                                }
                                return false;
                            });

                            return hasTextContent;
                        }

                        current = current.parentElement;
                    }
                    return false;
                }
                
                // Note: Text contrast checking is now handled by test_text_contrast.py
                // This test focuses on link distinction and color scheme support

                // Test links for color-only distinction (only in flowing text, not navigation)
                const links = Array.from(document.querySelectorAll('a[href]'));
                let colorOnlyLinks = 0;
                let weakIndicatorLinks = 0;

                links.forEach(link => {
                    // Skip links in navigation contexts - they have clear context
                    if (isInNavigationContext(link)) {
                        return;
                    }

                    // Only check links within flowing text (paragraphs, articles, etc.)
                    if (!isInFlowingText(link)) {
                        return;
                    }

                    const distinction = hasNonColorDistinction(link);

                    if (!distinction.hasIndicator) {
                        // No non-color indicator at all - this is a violation
                        colorOnlyLinks++;
                        results.warnings.push({
                            err: 'WarnColorOnlyLink',
                            type: 'warn',
                            cat: 'links',
                            element: 'a',
                            xpath: getFullXPath(link),
                            html: link.outerHTML.substring(0, 200),
                            description: 'Link in flowing text is distinguished only by color without underline, border, or other non-color visual indicator',
                            linkText: link.textContent.trim()
                        });
                    } else if (distinction.isWeak) {
                        // Has weak indicator (font-weight, bold, text-shadow) - passes but warn
                        weakIndicatorLinks++;
                        results.warnings.push({
                            err: 'WarnColorOnlyLinkWeakIndicator',
                            type: 'warn',
                            cat: 'links',
                            element: 'a',
                            xpath: getFullXPath(link),
                            html: link.outerHTML.substring(0, 200),
                            description: 'Link in flowing text uses only subtle visual indicators (font-weight, bold, or text-shadow) - these can be difficult for users to recognize as links. Consider using underline or border for clearer indication.',
                            linkText: link.textContent.trim()
                        });
                    }
                });
                
                // Check for media query support
                let hasContrastSupport = false;
                let hasColorSchemeSupport = false;
                
                try {
                    for (let sheet of document.styleSheets) {
                        try {
                            for (let rule of sheet.cssRules) {
                                if (rule instanceof CSSMediaRule) {
                                    const condition = rule.conditionText.toLowerCase();
                                    if (condition.includes('prefers-contrast')) {
                                        hasContrastSupport = true;
                                    }
                                    if (condition.includes('prefers-color-scheme')) {
                                        hasColorSchemeSupport = true;
                                    }
                                }
                            }
                        } catch (e) {
                            // Skip inaccessible stylesheets
                        }
                    }
                } catch (e) {
                    // Error accessing stylesheets
                }
                
                // Add check information for reporting
                if (links.length > 0) {
                    results.checks.push({
                        description: 'Link distinction',
                        wcag: ['1.4.1'],
                        total: links.length,
                        passed: links.length - colorOnlyLinks,
                        failed: colorOnlyLinks
                    });
                }
                
                // Add warning for missing high contrast support
                if (!hasContrastSupport) {
                    results.warnings.push({
                        err: 'WarnNoContrastSupport',
                        type: 'warn',
                        cat: 'colors',
                        element: 'page',
                        xpath: '/html',
                        html: '<page>',
                        description: 'Page lacks prefers-contrast media query support for high contrast preferences, failing to support users who require high contrast mode'
                    });
                }

                if (!hasColorSchemeSupport) {
                    results.warnings.push({
                        err: 'WarnNoColorSchemeSupport',
                        type: 'warn',
                        cat: 'colors',
                        element: 'page',
                        xpath: '/html',
                        html: '<page>',
                        description: 'Page lacks prefers-color-scheme media query support for dark/light mode preferences, failing to support users who require dark mode or other color scheme preferences'
                    });
                }

                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_colors: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }