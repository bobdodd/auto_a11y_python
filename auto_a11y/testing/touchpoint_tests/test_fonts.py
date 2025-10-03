"""
Fonts touchpoint test module
Evaluates webpage font usage and typography for accessibility concerns.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Font Accessibility Analysis",
    "touchpoint": "fonts",
    "description": "Evaluates webpage font usage and typography for accessibility concerns, including font size, line height, and text alignment. This test identifies small text, insufficient line spacing, and other typographic issues that may impact readability for users with visual impairments.",
    "version": "1.0.0",
    "wcagCriteria": ["1.4.4", "1.4.8", "1.3.1"],
    "tests": [
        {
            "id": "small-text",
            "name": "Small Text Size",
            "description": "Identifies text with font size smaller than 16px that may be difficult to read.",
            "impact": "high",
            "wcagCriteria": ["1.4.4"],
        },
        {
            "id": "line-height",
            "name": "Insufficient Line Height",
            "description": "Checks if line height is adequate for readability (at least 1.5 times the font size).",
            "impact": "medium",
            "wcagCriteria": ["1.4.8"],
        },
        {
            "id": "italic-text",
            "name": "Excessive Italic Text",
            "description": "Identifies usage of italic text that may be difficult to read for some users.",
            "impact": "medium",
            "wcagCriteria": ["1.4.8"],
        },
        {
            "id": "text-alignment",
            "name": "Text Alignment Issues",
            "description": "Checks for justified or right-aligned text that may create readability problems.",
            "impact": "medium",
            "wcagCriteria": ["1.4.8"],
        },
        {
            "id": "visual-hierarchy",
            "name": "Visual Hierarchy Issues",
            "description": "Identifies cases where non-heading text appears more prominent than actual headings.",
            "impact": "medium",
            "wcagCriteria": ["1.3.1"],
        }
    ]
}

async def test_fonts(page) -> Dict[str, Any]:
    """
    Test fonts and typography for accessibility requirements
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze fonts and typography
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
                    test_name: 'fonts',
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
                
                // Get all text elements
                const textElements = [];
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode: function(node) {
                            if (!node.textContent.trim() || 
                                ['SCRIPT', 'STYLE'].includes(node.parentElement.tagName)) {
                                return NodeFilter.FILTER_REJECT;
                            }
                            return NodeFilter.FILTER_ACCEPT;
                        }
                    }
                );
                
                while (walker.nextNode()) {
                    const textNode = walker.currentNode;
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
                
                // Get smallest heading size for comparison
                const headingSizes = [];
                document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
                    const size = parseFloat(window.getComputedStyle(heading).fontSize);
                    headingSizes.push(size);
                });
                const smallestHeading = headingSizes.length > 0 ? Math.min(...headingSizes) : null;
                
                // Test each text element
                let smallTextViolations = 0;
                let lineHeightViolations = 0;
                let italicTextCount = 0;
                let alignmentViolations = 0;
                let hierarchyViolations = 0;
                
                textElements.forEach(element => {
                    const style = window.getComputedStyle(element);
                    const fontSize = parseFloat(style.fontSize);
                    const lineHeight = parseFloat(style.lineHeight);
                    const fontStyle = style.fontStyle;
                    const fontWeight = parseInt(style.fontWeight) || 400;
                    const textAlign = style.textAlign;
                    const text = element.textContent.trim().substring(0, 50);
                    const tag = element.tagName.toLowerCase();
                    
                    let hasViolation = false;
                    
                    // Check for small text
                    if (fontSize < 16) {
                        smallTextViolations++;
                        results.errors.push({
                            err: 'ErrSmallText',
                            type: 'err',
                            cat: 'fonts',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `Text size is ${fontSize}px (should be at least 16px)`,
                            fontSize: fontSize,
                            text: text
                        });
                        hasViolation = true;
                    }
                    
                    // Check line height
                    if (lineHeight && lineHeight > 0 && (lineHeight / fontSize) < 1.5) {
                        lineHeightViolations++;
                        results.warnings.push({
                            err: 'WarnSmallLineHeight',
                            type: 'warn',
                            cat: 'fonts',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `Line height ratio is ${(lineHeight / fontSize).toFixed(2)} (should be at least 1.5)`,
                            ratio: (lineHeight / fontSize).toFixed(2),
                            text: text
                        });
                        hasViolation = true;
                    }
                    
                    // Check for italic text
                    if (fontStyle === 'italic') {
                        italicTextCount++;
                        results.warnings.push({
                            err: 'WarnItalicText',
                            type: 'warn',
                            cat: 'fonts',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Text uses italic styling which may be difficult to read',
                            text: text
                        });
                        hasViolation = true;
                    }
                    
                    // Check text alignment
                    if (textAlign === 'justify') {
                        alignmentViolations++;
                        results.warnings.push({
                            err: 'WarnJustifiedText',
                            type: 'warn',
                            cat: 'fonts',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Text uses justify alignment which can create uneven spacing',
                            text: text
                        });
                        hasViolation = true;
                    }
                    
                    if (textAlign === 'right' && text.length > 20) {
                        alignmentViolations++;
                        results.warnings.push({
                            err: 'WarnRightAlignedText',
                            type: 'warn',
                            cat: 'fonts',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Long text uses right alignment which can be difficult to read',
                            text: text
                        });
                        hasViolation = true;
                    }
                    
                    // Check visual hierarchy
                    if (fontWeight >= 700 && !['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tag)) {
                        if (smallestHeading && fontSize > smallestHeading) {
                            hierarchyViolations++;
                            results.warnings.push({
                                err: 'WarnVisualHierarchy',
                                type: 'warn',
                                cat: 'fonts',
                                element: tag,
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                description: `Bold non-heading text (${fontSize}px) is larger than smallest heading (${smallestHeading}px)`,
                                fontSize: fontSize,
                                smallestHeading: smallestHeading,
                                text: text
                            });
                            hasViolation = true;
                        }
                    }
                    
                    if (!hasViolation) {
                        results.elements_passed++;
                    } else {
                        results.elements_failed++;
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Text size accessibility',
                    wcag: ['1.4.4'],
                    total: textElements.length,
                    passed: textElements.length - smallTextViolations,
                    failed: smallTextViolations
                });
                
                if (lineHeightViolations > 0) {
                    results.checks.push({
                        description: 'Line height adequacy',
                        wcag: ['1.4.8'],
                        total: textElements.length,
                        passed: textElements.length - lineHeightViolations,
                        failed: lineHeightViolations
                    });
                }
                
                if (italicTextCount > 0) {
                    results.checks.push({
                        description: 'Italic text usage',
                        wcag: ['1.4.8'],
                        total: italicTextCount,
                        passed: 0,
                        failed: italicTextCount
                    });
                }
                
                return results;
            }
        ''')

        # Log small text errors for debugging
        if 'errors' in results:
            small_text_errors = [e for e in results['errors'] if e.get('err') == 'ErrSmallText']
            if small_text_errors:
                logger.warning(f"FONTS DEBUG: Found {len(small_text_errors)} ErrSmallText errors")
                for i, error in enumerate(small_text_errors[:3]):  # Log first 3
                    logger.warning(f"  [{i}] fontSize={error.get('fontSize')} description='{error.get('description', 'N/A')[:80]}'")

        return results
        
    except Exception as e:
        logger.error(f"Error in test_fonts: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }