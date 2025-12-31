"""
Fonts touchpoint test module
Evaluates webpage font usage and typography for accessibility concerns.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
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


def load_inaccessible_fonts_config():
    """
    Load inaccessible fonts configuration from JSON file

    Returns:
        Dict with 'fonts' (list of font names) and 'categories' (dict with category info)
    """
    try:
        config_path = Path(__file__).parent.parent.parent / 'config' / 'inaccessible_fonts_defaults.json'

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Flatten all fonts from all categories into a single list
        all_fonts = []
        categories_data = {}

        for category_name, category_info in config.get('categories', {}).items():
            fonts_in_category = category_info.get('fonts', [])
            all_fonts.extend(fonts_in_category)

            categories_data[category_name] = {
                'description': category_info.get('description', ''),
                'fonts': fonts_in_category
            }

        logger.info(f"Loaded {len(all_fonts)} inaccessible fonts from {len(categories_data)} categories")

        return {
            'fonts': all_fonts,
            'categories': categories_data
        }

    except Exception as e:
        logger.error(f"Error loading inaccessible fonts config: {e}")
        # Return empty config as fallback
        return {
            'fonts': [],
            'categories': {}
        }

async def test_fonts(page, project_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Test fonts and typography for accessibility requirements

    Args:
        page: Pyppeteer page object
        project_config: Optional project configuration dict for project-specific font settings

    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Load inaccessible fonts configuration
        # If project_config is provided, use project-specific settings
        # Otherwise, use system defaults only
        from auto_a11y.utils.font_config import font_config_manager

        font_config_data = load_inaccessible_fonts_config()
        font_categories = font_config_data['categories']

        # Get the appropriate font list based on project config
        if project_config:
            inaccessible_fonts_list = list(font_config_manager.get_project_inaccessible_fonts(project_config))
            logger.info(f"Using project-specific font configuration: {len(inaccessible_fonts_list)} fonts")
        else:
            inaccessible_fonts_list = font_config_data['fonts']
            logger.info(f"Using system default font configuration: {len(inaccessible_fonts_list)} fonts")

        # Execute JavaScript to analyze fonts and typography
        # Pass the font configuration to JavaScript
        results = await page.evaluate('''
            (inaccessibleFontsList, fontCategoriesData) => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    discovery: [],
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
                
                // Test each text element - collect small text instances for grouping
                let smallTextViolations = 0;
                let lineHeightViolations = 0;
                let italicTextCount = 0;
                let alignmentViolations = 0;
                let hierarchyViolations = 0;

                // Collect small text instances by element type for grouping
                const smallTextInstances = [];

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

                    // Check for small text - collect instances
                    if (fontSize < 16) {
                        smallTextViolations++;
                        smallTextInstances.push({
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
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
                            lineHeight: lineHeight.toFixed(2),
                            fontSize: fontSize.toFixed(2),
                            text: text
                        });
                        hasViolation = true;
                    }
                    
                    // Check for italic text (only flag if substantial length, not brief emphasis)
                    // Short italic text (<50 chars) is acceptable for emphasis (em, i tags)
                    // Extensive italic text is harder to read for users with dyslexia
                    const fullText = element.textContent.trim();
                    if (fontStyle === 'italic' && fullText.length >= 50) {
                        italicTextCount++;
                        results.warnings.push({
                            err: 'WarnItalicText',
                            type: 'warn',
                            cat: 'fonts',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `Text uses italic styling for ${fullText.length} characters which may be difficult to read`,
                            text: text,
                            textLength: fullText.length
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
                    
                    // Only flag actual right-aligned text, not center or left
                    // Body text that is right-aligned is difficult to read (WCAG 1.4.8 AAA)
                    if (textAlign === 'right' && text.length > 20) {
                        // Additional check: ensure this is body text, not headings or short labels
                        // Exclude inline emphasis elements (strong, em, b, i) - they inherit alignment
                        const isBodyText = ['p', 'div', 'span', 'li', 'td', 'th', 'blockquote', 'article', 'section'].includes(tag);
                        const isInlineEmphasis = ['strong', 'em', 'b', 'i', 'mark', 'code', 'kbd', 'samp', 'var', 'cite', 'abbr'].includes(tag);

                        if (isBodyText && !isInlineEmphasis) {
                            alignmentViolations++;
                            results.warnings.push({
                                err: 'WarnRightAlignedText',
                                type: 'warn',
                                cat: 'fonts',
                                element: tag,
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                description: 'Body text uses right alignment which can be difficult to read',
                                text: text,
                                textAlign: textAlign
                            });
                            hasViolation = true;
                        }
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

                // Create single grouped error for all small text instances
                if (smallTextInstances.length > 0) {
                    // Find smallest font size for the summary
                    const smallestSize = Math.min(...smallTextInstances.map(i => parseFloat(i.fontSize)));
                    results.errors.push({
                        err: 'ErrSmallText',
                        type: 'err',
                        cat: 'fonts',
                        element: 'text',
                        description: `${smallTextInstances.length} element(s) have text smaller than the recommended minimum of 16px (smallest: ${smallestSize}px)`,
                        metadata: {
                            fontSize: smallestSize,
                            instanceCount: smallTextInstances.length,
                            allInstances: smallTextInstances.map((inst, idx) => ({
                                index: idx + 1,
                                element: inst.element,
                                xpath: inst.xpath,
                                html: inst.html,
                                fontSize: inst.fontSize,
                                text: inst.text
                            }))
                        }
                    });
                }

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
                        description: 'Line height adequacy (best practice)',
                        wcag: [],
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

                // Load inaccessible fonts from config (passed from Python)
                // This list is maintained in auto_a11y/config/inaccessible_fonts_defaults.json
                const inaccessibleFonts = new Set(inaccessibleFontsList);

                // Font category descriptions loaded from config
                const fontCategories = fontCategoriesData;

                // Helper function to get category for a font
                function getFontCategory(fontName) {
                    const normalized = fontName.toLowerCase();
                    for (const [category, data] of Object.entries(fontCategories)) {
                        if (data.fonts.includes(normalized)) {
                            return { category, description: data.description };
                        }
                    }
                    return { category: 'unknown', description: 'difficult to read' };
                }

                // DISCOVERY: Report each unique font with the sizes it's used at
                const allElements = Array.from(document.querySelectorAll('*'));
                const fontData = new Map(); // Map of font name -> Set of sizes

                allElements.forEach(el => {
                    const computedStyle = window.getComputedStyle(el);
                    const fontFamily = computedStyle.fontFamily;
                    const fontSize = computedStyle.fontSize;

                    if (fontFamily && fontFamily !== 'inherit' && fontSize) {
                        // Clean up font family string - take the first font in the stack
                        const fonts = fontFamily.split(',').map(f => f.trim().replace(/['"]/g, ''));
                        const primaryFont = fonts[0]; // Use the first (primary) font

                        if (!fontData.has(primaryFont)) {
                            fontData.set(primaryFont, new Set());
                        }
                        fontData.get(primaryFont).add(fontSize);
                    }
                });

                // Check each font and report issues
                fontData.forEach((sizes, fontName) => {
                    const sortedSizes = Array.from(sizes).sort((a, b) => {
                        // Sort by numeric value (converting px to numbers)
                        const aNum = parseFloat(a);
                        const bNum = parseFloat(b);
                        return aNum - bNum;
                    });

                    // Discovery: Report that this font was found
                    results.warnings.push({
                        err: 'DiscoFontFound',
                        type: 'disco',
                        cat: 'fonts',
                        element: 'document',
                        xpath: '/html[1]',
                        html: `<meta>Font: ${fontName}</meta>`,
                        description: sortedSizes.length === 1
                            ? `Font is used at 1 size on this page`
                            : `Font is used at ${sortedSizes.length} different sizes on this page`,
                        fontName: fontName,
                        fontSizes: sortedSizes,
                        sizeCount: sortedSizes.length
                    });

                    // ERROR: Check if this is an inaccessible font
                    const normalizedFont = fontName.toLowerCase();
                    if (inaccessibleFonts.has(normalizedFont)) {
                        const categoryInfo = getFontCategory(fontName);
                        results.errors.push({
                            err: 'ErrInaccessibleFont',
                            type: 'error',
                            cat: 'fonts',
                            element: 'document',
                            xpath: '/html[1]',
                            html: `<meta>Font: ${fontName}</meta>`,
                            description: `Font '${fontName}' is difficult to read. ${categoryInfo.description}. Research shows these fonts are harder to read, especially for users with dyslexia or low vision.`,
                            fontName: fontName,
                            category: categoryInfo.category,
                            reason: categoryInfo.description,
                            fontSizes: sortedSizes,
                            sizeCount: sortedSizes.length
                        });
                        results.elements_failed++;
                        hasViolation = true;
                    }
                });

                return results;
            }
        ''', inaccessible_fonts_list, font_categories)

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