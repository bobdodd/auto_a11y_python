"""
Colors touchpoint test module
Evaluates color usage and contrast ratios on the page to ensure content is perceivable by users with low vision.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Color and Contrast Analysis",
    "touchpoint": "colors",
    "description": "Evaluates color usage and contrast ratios on the page to ensure content is perceivable by users with low vision, color vision deficiencies, or those who use high contrast modes. This test examines text contrast, color-only distinctions, non-text contrast, color references, and adjacent element contrast.",
    "version": "1.0.0",
    "wcagCriteria": ["1.4.1", "1.4.3", "1.4.6", "1.4.11", "1.4.12"],
    "tests": [
        {
            "id": "color-text-contrast",
            "name": "Text Contrast Ratio",
            "description": "Evaluates the contrast ratio between text color and its background to ensure readability. Normal text should have a contrast ratio of at least 4.5:1, while large text should have a ratio of at least 3:1.",
            "impact": "high",
            "wcagCriteria": ["1.4.3", "1.4.6"],
        },
        {
            "id": "color-only-distinction",
            "name": "Color-Only Distinctions",
            "description": "Identifies cases where color alone is used to convey information, particularly for links that are distinguished only by color without additional visual cues.",
            "impact": "high",
            "wcagCriteria": ["1.4.1"],
        },
        {
            "id": "color-non-text-contrast",
            "name": "Non-Text Contrast",
            "description": "Evaluates contrast for UI components and graphical objects to ensure they're perceivable by users with low vision.",
            "impact": "medium",
            "wcagCriteria": ["1.4.11"],
        }
    ]
}

async def test_colors(page) -> Dict[str, Any]:
    """
    Test color usage and contrast requirements across the page
    
    Args:
        page: Pyppeteer page object
        
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
                
                // Color utility functions
                function getLuminance(r, g, b) {
                    const [rs, gs, bs] = [r, g, b].map(c => {
                        c = c / 255;
                        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
                    });
                    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
                }
                
                function getContrastRatio(l1, l2) {
                    const lighter = Math.max(l1, l2);
                    const darker = Math.min(l1, l2);
                    return (lighter + 0.05) / (darker + 0.05);
                }
                
                function parseColor(color) {
                    const temp = document.createElement('div');
                    temp.style.color = color;
                    document.body.appendChild(temp);
                    const style = window.getComputedStyle(temp);
                    const rgb = style.color.match(/\\d+/g);
                    document.body.removeChild(temp);
                    return rgb ? rgb.map(Number) : [0, 0, 0];
                }
                
                function getEffectiveBackground(element) {
                    let current = element;
                    while (current && current !== document.body) {
                        const style = window.getComputedStyle(current);
                        if (style.backgroundColor !== 'rgba(0, 0, 0, 0)' && 
                            style.backgroundColor !== 'transparent') {
                            return parseColor(style.backgroundColor);
                        }
                        if (style.backgroundImage !== 'none') {
                            return null; // Can't calculate contrast with image
                        }
                        current = current.parentElement;
                    }
                    return parseColor(window.getComputedStyle(document.body).backgroundColor);
                }
                
                function isLargeText(element) {
                    const style = window.getComputedStyle(element);
                    const fontSize = parseFloat(style.fontSize);
                    const fontWeight = parseInt(style.fontWeight) || (style.fontWeight === 'bold' ? 700 : 400);
                    return (fontSize >= 18) || (fontSize >= 14 && fontWeight >= 700);
                }
                
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
                    let current = element.parentElement;
                    while (current && current !== document.body) {
                        const tagName = current.tagName.toLowerCase();

                        // Flowing text containers
                        if (['p', 'li', 'td', 'th', 'dd', 'dt', 'blockquote', 'figcaption'].includes(tagName)) {
                            return true;
                        }

                        // Article content
                        if (tagName === 'article' || current.getAttribute('role') === 'article') {
                            return true;
                        }

                        current = current.parentElement;
                    }
                    return false;
                }
                
                // Get all text elements
                const textElements = [];
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode: function(node) {
                            return node.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
                        }
                    }
                );
                
                let textNode;
                while (textNode = walker.nextNode()) {
                    const element = textNode.parentElement;
                    if (element && element.offsetHeight > 0 && element.offsetWidth > 0) {
                        textElements.push(element);
                    }
                }
                
                if (textElements.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No text elements found on the page';
                    return results;
                }
                
                results.elements_tested = textElements.length;
                
                // Test text contrast
                let contrastViolations = 0;
                textElements.forEach(element => {
                    const style = window.getComputedStyle(element);
                    const foreground = parseColor(style.color);
                    const background = getEffectiveBackground(element);
                    
                    if (background) {
                        const foreLum = getLuminance(...foreground);
                        const backLum = getLuminance(...background);
                        const ratio = getContrastRatio(foreLum, backLum);
                        const isLarge = isLargeText(element);
                        const requiredRatio = isLarge ? 3 : 4.5;

                        if (ratio < requiredRatio) {
                            contrastViolations++;

                            // Helper to convert RGB array to hex color
                            function rgbToHex(rgb) {
                                return '#' + rgb.map(c => {
                                    const hex = Math.round(c).toString(16);
                                    return hex.length === 1 ? '0' + hex : hex;
                                }).join('');
                            }

                            // Get font size for metadata
                            const fontSize = parseInt(style.fontSize) || 16;

                            // Use different error codes for normal vs large text
                            const errorCode = isLarge ? 'ErrLargeTextContrastAA' : 'ErrTextContrastAA';

                            results.errors.push({
                                err: errorCode,
                                type: 'err',
                                cat: 'colors',
                                element: element.tagName,
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                description: `${isLarge ? 'Large text' : 'Text'} has insufficient contrast ratio: ${ratio.toFixed(2)}:1 (required: ${requiredRatio}:1)`,
                                ratio: ratio.toFixed(2),
                                required: requiredRatio.toFixed(1),
                                isLarge: isLarge,
                                fg: rgbToHex(foreground),
                                bg: rgbToHex(background),
                                fontSize: fontSize
                            });
                            results.elements_failed++;
                        } else {
                            results.elements_passed++;
                        }
                    } else {
                        results.elements_passed++;
                    }
                });
                
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
                results.checks.push({
                    description: 'Text contrast ratio',
                    wcag: ['1.4.3', '1.4.6'],
                    total: textElements.length,
                    passed: results.elements_passed,
                    failed: contrastViolations
                });
                
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