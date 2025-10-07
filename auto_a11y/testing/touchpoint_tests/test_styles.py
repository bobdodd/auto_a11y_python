"""
Styles touchpoint test module
Evaluates inline style attributes to ensure proper separation of presentation from content.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Inline Styles Analysis",
    "touchpoint": "styles",
    "description": "Evaluates inline style attributes on HTML elements. Inline styles for colors and fonts are flagged as errors because they prevent users from customizing content to their accessibility needs. Other inline styles are flagged as warnings for maintainability.",
    "version": "1.0.0",
    "wcagCriteria": ["1.4.3", "1.4.8", "1.4.12"],
    "tests": [
        {
            "id": "inline-color-font-styles",
            "name": "Inline Color and Font Styles",
            "description": "Identifies elements with inline color or font-related styles that prevent user customization.",
            "impact": "high",
            "wcagCriteria": ["1.4.3", "1.4.8", "1.4.12"],
        },
        {
            "id": "inline-other-styles",
            "name": "Other Inline Styles",
            "description": "Identifies elements with inline layout styles that should be moved to CSS for maintainability.",
            "impact": "low",
            "wcagCriteria": ["1.4.8"],
        }
    ]
}

async def test_styles(page) -> Dict[str, Any]:
    """
    Test inline style attributes for proper separation of concerns

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze inline styles
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
                    test_name: 'styles',
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

                // ERROR/WARNING: Analyze inline style attributes
                const elementsWithStyleAttr = Array.from(document.querySelectorAll('[style]'));
                const styleElements = Array.from(document.querySelectorAll('style'));

                // Check if there are any styles to analyze
                if (elementsWithStyleAttr.length === 0 && styleElements.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No inline style attributes or <style> tags found';
                    return results;
                }

                // Comprehensive list of color-related CSS properties
                const colorProperties = [
                    'color',
                    'background-color',
                    'background',
                    'border-color',
                    'border-top-color',
                    'border-right-color',
                    'border-bottom-color',
                    'border-left-color',
                    'outline-color',
                    'text-decoration-color',
                    'column-rule-color',
                    'caret-color',
                    'fill',
                    'stroke'
                ];

                // Comprehensive list of font-related CSS properties
                const fontProperties = [
                    'font',
                    'font-family',
                    'font-size',
                    'font-weight',
                    'font-style',
                    'font-variant',
                    'font-stretch',
                    'line-height',
                    'letter-spacing',
                    'word-spacing',
                    'text-transform',
                    'text-decoration',
                    'text-decoration-line',
                    'text-decoration-style',
                    'text-decoration-thickness',
                    'font-kerning',
                    'font-size-adjust',
                    'font-synthesis'
                ];

                results.elements_tested = elementsWithStyleAttr.length;
                let colorFontViolations = 0;
                let otherStyleWarnings = 0;

                elementsWithStyleAttr.forEach((element, index) => {
                    const styleAttr = element.getAttribute('style');
                    const xpath = getFullXPath(element);

                    // Get element tag and truncated HTML for context
                    const tagName = element.tagName.toLowerCase();
                    const outerHTML = element.outerHTML;
                    const truncatedHTML = outerHTML.length > 200
                        ? outerHTML.substring(0, 200) + '...'
                        : outerHTML;

                    // Parse style attribute to check for color properties
                    const styleLower = styleAttr.toLowerCase();
                    const hasColor = colorProperties.some(prop => {
                        // Match property name followed by colon
                        // Use (^|;|\\s) to match start, semicolon, or whitespace before property
                        const regex = new RegExp(`(^|;|\\s)${prop}\\s*:`, 'i');
                        return regex.test(styleLower);
                    });

                    // Parse style attribute to check for font properties
                    const hasFont = fontProperties.some(prop => {
                        // Match property name followed by colon
                        // Use (^|;|\\s) to match start, semicolon, or whitespace before property
                        const regex = new RegExp(`(^|;|\\s)${prop}\\s*:`, 'i');
                        return regex.test(styleLower);
                    });

                    if (hasColor || hasFont) {
                        // ERROR: Color or font-related inline styles
                        const issueType = hasColor && hasFont ? 'color and font' :
                                         hasColor ? 'color' : 'font';

                        results.errors.push({
                            err: 'ErrStyleAttrColorFont',
                            type: 'error',
                            cat: 'styles',
                            element: tagName,
                            xpath: xpath,
                            html: truncatedHTML,
                            description: `Inline style with ${issueType} properties on <${tagName}> element`,
                            style: styleAttr,
                            metadata: {
                                styleContent: styleAttr,
                                elementTag: tagName,
                                hasColor: hasColor,
                                hasFont: hasFont,
                                instanceNumber: index + 1,
                                totalInstances: elementsWithStyleAttr.length
                            }
                        });
                        results.elements_failed++;
                        colorFontViolations++;
                    } else {
                        // WARNING: Other inline styles (layout-related)
                        results.warnings.push({
                            err: 'WarnStyleAttrOther',
                            type: 'warning',
                            cat: 'styles',
                            element: tagName,
                            xpath: xpath,
                            html: truncatedHTML,
                            description: `Inline style with layout properties on <${tagName}> element`,
                            style: styleAttr,
                            metadata: {
                                styleContent: styleAttr,
                                elementTag: tagName,
                                instanceNumber: index + 1,
                                totalInstances: elementsWithStyleAttr.length
                            }
                        });
                        otherStyleWarnings++;
                    }
                });

                // Add check information for inline style attributes if any were found
                if (elementsWithStyleAttr.length > 0) {
                    results.elements_passed = elementsWithStyleAttr.length - colorFontViolations;

                    results.checks.push({
                        description: 'Inline color/font styles',
                        wcag: ['1.4.3', '1.4.8', '1.4.12'],
                        total: elementsWithStyleAttr.length,
                        passed: results.elements_passed,
                        failed: colorFontViolations
                    });

                    if (otherStyleWarnings > 0) {
                        results.checks.push({
                            description: 'Other inline styles',
                            wcag: ['1.4.8'],
                            total: otherStyleWarnings,
                            passed: 0,
                            failed: otherStyleWarnings
                        });
                    }
                }

                // ERROR/WARNING: Analyze <style> tag content
                styleElements.forEach((styleElement, styleIndex) => {
                    const cssContent = styleElement.textContent || '';
                    if (!cssContent.trim()) return; // Skip empty style tags

                    const xpath = getFullXPath(styleElement);

                    // Truncate CSS content for display
                    const truncatedCSS = cssContent.length > 300
                        ? cssContent.substring(0, 300) + '...'
                        : cssContent;

                    // Check if CSS contains color or font property definitions
                    const cssLower = cssContent.toLowerCase();

                    // Match CSS property declarations (property: value;)
                    const hasColorProps = colorProperties.some(prop => {
                        const regex = new RegExp(`${prop}\\s*:`, 'i');
                        return regex.test(cssLower);
                    });

                    const hasFontProps = fontProperties.some(prop => {
                        const regex = new RegExp(`${prop}\\s*:`, 'i');
                        return regex.test(cssLower);
                    });

                    if (hasColorProps || hasFontProps) {
                        // ERROR: <style> tag contains color or font definitions
                        const issueType = hasColorProps && hasFontProps ? 'color and font' :
                                         hasColorProps ? 'color' : 'font';

                        results.errors.push({
                            err: 'ErrStyleTagColorFont',
                            type: 'error',
                            cat: 'styles',
                            element: 'style',
                            xpath: xpath,
                            html: `<style>${truncatedCSS}</style>`,
                            description: `<style> tag contains ${issueType} definitions`,
                            metadata: {
                                cssContent: truncatedCSS,
                                hasColor: hasColorProps,
                                hasFont: hasFontProps,
                                styleElementNumber: styleIndex + 1,
                                totalStyleElements: styleElements.length
                            }
                        });
                        results.elements_failed++;
                    } else {
                        // WARNING: <style> tag contains other CSS (layout)
                        results.warnings.push({
                            err: 'WarnStyleTagOther',
                            type: 'warning',
                            cat: 'styles',
                            element: 'style',
                            xpath: xpath,
                            html: `<style>${truncatedCSS}</style>`,
                            description: `<style> tag contains layout CSS definitions`,
                            metadata: {
                                cssContent: truncatedCSS,
                                styleElementNumber: styleIndex + 1,
                                totalStyleElements: styleElements.length
                            }
                        });
                    }
                });

                return results;
            }
        ''')

        return results

    except Exception as e:
        logger.error(f"Error in test_styles: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }
