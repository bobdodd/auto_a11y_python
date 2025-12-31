"""
Text contrast touchpoint test module
Tests for WCAG text contrast requirements at AA and AAA levels for normal and large text.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Text Contrast",
    "touchpoint": "colors_contrast",
    "description": "Tests text color contrast against background colors to ensure readability. Checks WCAG AA (4.5:1 normal, 3:1 large) and AAA (7:1 normal, 4.5:1 large) requirements. Handles transparent backgrounds, gradients, images, z-index floating elements, and text overflow.",
    "version": "1.0.0",
    "wcagCriteria": ["1.4.3", "1.4.6"],
    "tests": [
        {
            "id": "text-contrast-aa-normal",
            "name": "Text Contrast AA Normal",
            "description": "Checks if normal text meets WCAG AA 4.5:1 contrast requirement",
            "impact": "high",
            "wcagCriteria": ["1.4.3"],
        },
        {
            "id": "text-contrast-aa-large",
            "name": "Text Contrast AA Large",
            "description": "Checks if large text (18pt+ or 14pt+ bold) meets WCAG AA 3:1 contrast requirement",
            "impact": "high",
            "wcagCriteria": ["1.4.3"],
        },
        {
            "id": "text-contrast-aaa-normal",
            "name": "Text Contrast AAA Normal",
            "description": "Checks if normal text meets WCAG AAA 7:1 contrast requirement",
            "impact": "medium",
            "wcagCriteria": ["1.4.6"],
        },
        {
            "id": "text-contrast-aaa-large",
            "name": "Text Contrast AAA Large",
            "description": "Checks if large text meets WCAG AAA 4.5:1 contrast requirement",
            "impact": "medium",
            "wcagCriteria": ["1.4.6"],
        }
    ]
}

async def test_text_contrast(page) -> Dict[str, Any]:
    """
    Test text color contrast against background colors

    Tests both AA and AAA levels for normal and large text.
    Tests at all responsive breakpoints defined in CSS.
    Handles edge cases like transparent backgrounds, gradients, images,
    z-index floating elements, text overflow, pseudoclasses, and media queries.

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # First, discover all breakpoints from CSS media queries
        breakpoint_data = await page.evaluate('''
            () => {
                const breakpoints = new Set();

                // Always test at a base mobile size
                breakpoints.add(320);

                // Parse all stylesheets for media queries
                for (const sheet of document.styleSheets) {
                    try {
                        if (sheet.cssRules) {
                            for (const rule of sheet.cssRules) {
                                if (rule instanceof CSSMediaRule) {
                                    // Extract width values from media query
                                    const media = rule.media.mediaText;
                                    const widthMatches = media.match(/(?:min-width|max-width):\\s*(\\d+)(?:px|em|rem)?/g);

                                    if (widthMatches) {
                                        widthMatches.forEach(match => {
                                            const valueMatch = match.match(/(\\d+)/);
                                            if (valueMatch) {
                                                let value = parseInt(valueMatch[1]);
                                                // Convert em/rem to px (assume 16px base)
                                                if (match.includes('em') || match.includes('rem')) {
                                                    value = value * 16;
                                                }
                                                breakpoints.add(value);
                                            }
                                        });
                                    }
                                }
                            }
                        }
                    } catch (e) {
                        // Skip inaccessible stylesheets
                    }
                }

                // Always include common standard breakpoints to catch content changes
                breakpoints.add(768);  // Tablet
                breakpoints.add(1024); // Desktop

                return Array.from(breakpoints).sort((a, b) => a - b);
            }
        ''')

        # Aggregate results across all breakpoints
        results = {
            'applicable': True,
            'errors': [],
            'warnings': [],
            'passes': [],
            'elements_tested': 0,
            'elements_passed': 0,
            'elements_failed': 0,
            'test_name': 'text_contrast',
            'checks': [],
            'breakpoints_tested': breakpoint_data
        }

        # Test at each breakpoint
        import asyncio
        for breakpoint in breakpoint_data:
            # Set viewport to this breakpoint
            try:
                await page.setViewport({'width': breakpoint, 'height': 800})
            except Exception as viewport_err:
                logger.error(f"setViewport failed for {breakpoint}px: {viewport_err}")
                break

            # Wait a moment for any dynamic content to adjust
            await asyncio.sleep(0.1)

            # Extract text elements and their contrast data at this breakpoint
            text_data = await page.evaluate('''
                (breakpointWidth) => {
                // Get WCAG level from project config (set by test runner)
                const wcagLevel = window.WCAG_LEVEL || 'AA';

                // XPath generator
                function getXPath(element) {
                    if (element.id) {
                        return `//*[@id="${element.id}"]`;
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    let ix = 0;
                    const siblings = element.parentNode ? element.parentNode.childNodes : [];
                    for (let i = 0; i < siblings.length; i++) {
                        const sibling = siblings[i];
                        if (sibling === element) {
                            return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }

                // Parse color to RGBA
                function parseColor(colorStr) {
                    if (!colorStr || colorStr === 'transparent') {
                        return { r: 0, g: 0, b: 0, a: 0 };
                    }

                    // Try to parse rgba/rgb format first (most common)
                    const rgbaMatch = colorStr.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
                    if (rgbaMatch) {
                        return {
                            r: parseInt(rgbaMatch[1]),
                            g: parseInt(rgbaMatch[2]),
                            b: parseInt(rgbaMatch[3]),
                            a: rgbaMatch[4] !== undefined ? parseFloat(rgbaMatch[4]) : 1
                        };
                    }

                    // Try 6-digit hex
                    const hexMatch6 = colorStr.match(/^#([0-9a-f]{6})$/i);
                    if (hexMatch6) {
                        const hex = hexMatch6[1];
                        return {
                            r: parseInt(hex.substr(0, 2), 16),
                            g: parseInt(hex.substr(2, 2), 16),
                            b: parseInt(hex.substr(4, 2), 16),
                            a: 1
                        };
                    }

                    // Try 3-digit hex
                    const hexMatch3 = colorStr.match(/^#([0-9a-f]{3})$/i);
                    if (hexMatch3) {
                        const hex = hexMatch3[1];
                        return {
                            r: parseInt(hex[0] + hex[0], 16),
                            g: parseInt(hex[1] + hex[1], 16),
                            b: parseInt(hex[2] + hex[2], 16),
                            a: 1
                        };
                    }

                    // For any other format (named colors, hsl, etc.), use a temporary canvas
                    // to let the browser convert it to rgba
                    try {
                        const canvas = document.createElement('canvas');
                        canvas.width = canvas.height = 1;
                        const ctx = canvas.getContext('2d');
                        ctx.fillStyle = colorStr;
                        ctx.fillRect(0, 0, 1, 1);
                        const imageData = ctx.getImageData(0, 0, 1, 1).data;
                        return {
                            r: imageData[0],
                            g: imageData[1],
                            b: imageData[2],
                            a: imageData[3] / 255
                        };
                    } catch (e) {
                        // If all else fails, return transparent black
                        console.warn('Could not parse color:', colorStr, e);
                        return { r: 0, g: 0, b: 0, a: 0 };
                    }
                }

                // Calculate relative luminance
                function getLuminance(color) {
                    const rsRGB = color.r / 255;
                    const gsRGB = color.g / 255;
                    const bsRGB = color.b / 255;

                    const r = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
                    const g = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
                    const b = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4);

                    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
                }

                // Calculate contrast ratio
                function getContrastRatio(color1, color2) {
                    const lum1 = getLuminance(color1);
                    const lum2 = getLuminance(color2);
                    const lighter = Math.max(lum1, lum2);
                    const darker = Math.min(lum1, lum2);
                    return (lighter + 0.05) / (darker + 0.05);
                }

                // Check if element is visually hidden (screen reader only)
                function isVisuallyHidden(element) {
                    const style = window.getComputedStyle(element);

                    // Common screen-reader-only patterns
                    if (style.position === 'absolute' &&
                        (style.clip === 'rect(1px, 1px, 1px, 1px)' || style.clip === 'rect(0, 0, 0, 0)')) {
                        return true;
                    }

                    if (style.position === 'absolute' &&
                        style.width === '1px' && style.height === '1px' &&
                        style.overflow === 'hidden') {
                        return true;
                    }

                    if (style.clip === 'rect(0px, 0px, 0px, 0px)') {
                        return true;
                    }

                    return false;
                }

                // Check for gradient or image background
                function hasComplexBackground(bgStr) {
                    if (!bgStr || bgStr === 'none') return { hasGradient: false, hasImage: false };

                    const lower = bgStr.toLowerCase();
                    return {
                        hasGradient: lower.includes('gradient'),
                        hasImage: lower.includes('url(')
                    };
                }

                // Check if element has CSS animations
                function hasAnimation(element) {
                    const style = window.getComputedStyle(element);
                    const animationName = style.animationName || style.webkitAnimationName || '';
                    const transition = style.transition || style.webkitTransition || '';
                    const transitionDuration = style.transitionDuration || '0s';

                    // Check if animation-name is not 'none'
                    const hasAnim = animationName && animationName !== 'none';
                    
                    // Check if transition affects color/opacity and has non-zero duration
                    // Browser default 'all 0s ease 0s' should not be flagged as animation
                    const hasNonZeroDuration = transitionDuration && !transitionDuration.match(/^0s(,\\s*0s)*$/);
                    const hasColorTransition = hasNonZeroDuration && transition && (
                        transition.includes('color') ||
                        transition.includes('background') ||
                        transition.includes('opacity') ||
                        transition.includes('all')
                    );

                    return hasAnim || hasColorTransition;
                }

                // Get effective background color by walking up the DOM
                // Returns: { backgroundColor, stoppedAtZIndex, hasGradient, hasImage }
                function getEffectiveBackground(element) {
                    let currentElement = element;
                    let backgroundColor = 'rgba(0, 0, 0, 0)';
                    let stoppedAtZIndex = false;
                    let hasGradient = false;
                    let hasImage = false;

                    while (currentElement && backgroundColor === 'rgba(0, 0, 0, 0)') {
                        const style = window.getComputedStyle(currentElement);

                        // Check for gradient or image first
                        const bgImage = style.backgroundImage;
                        const fullBg = style.background;
                        const complex = hasComplexBackground(bgImage) || hasComplexBackground(fullBg);

                        if (complex.hasGradient) hasGradient = true;
                        if (complex.hasImage) hasImage = true;

                        // If we find gradient or image, we still note the solid background color if present
                        backgroundColor = style.backgroundColor;

                        // Check for z-index (creates stacking context)
                        const zIndex = style.zIndex;
                        const position = style.position;
                        if (zIndex !== 'auto' && position !== 'static') {
                            stoppedAtZIndex = true;
                            break;
                        }

                        // If we found a solid background, stop
                        if (backgroundColor !== 'rgba(0, 0, 0, 0)' && !hasGradient && !hasImage) {
                            break;
                        }

                        currentElement = currentElement.parentElement;
                    }

                    // Default to white if we reached the root without finding a background
                    if (backgroundColor === 'rgba(0, 0, 0, 0)' && !hasGradient && !hasImage) {
                        backgroundColor = 'rgb(255, 255, 255)';
                    }

                    return {
                        backgroundColor,
                        stoppedAtZIndex,
                        hasGradient,
                        hasImage
                    };
                }

                // Check if text overflows its container
                function checkTextOverflow(element) {
                    const elementRect = element.getBoundingClientRect();
                    let parent = element.parentElement;

                    if (!parent) return false;

                    const parentRect = parent.getBoundingClientRect();

                    // Check if text extends beyond parent boundaries
                    const overflows =
                        elementRect.top < parentRect.top ||
                        elementRect.bottom > parentRect.bottom ||
                        elementRect.left < parentRect.left ||
                        elementRect.right > parentRect.right;

                    return overflows;
                }

                // Check if element or any ancestor is hidden
                function isElementOrAncestorHidden(element) {
                    let current = element;
                    while (current && current !== document.body) {
                        const style = window.getComputedStyle(current);
                        if (style.display === 'none' || 
                            style.visibility === 'hidden' || 
                            parseFloat(style.opacity) === 0) {
                            return true;
                        }
                        current = current.parentElement;
                    }
                    return false;
                }

                // Get all text nodes
                const textElements = [];
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode: function(node) {
                            // Skip empty or whitespace-only text
                            if (!node.textContent || !node.textContent.trim()) {
                                return NodeFilter.FILTER_REJECT;
                            }

                            const parent = node.parentElement;
                            if (!parent) return NodeFilter.FILTER_REJECT;

                            // Skip if element or any ancestor is hidden
                            if (isElementOrAncestorHidden(parent)) {
                                return NodeFilter.FILTER_REJECT;
                            }

                            // Skip if visually hidden (screen reader only)
                            if (isVisuallyHidden(parent)) {
                                return NodeFilter.FILTER_REJECT;
                            }

                            return NodeFilter.FILTER_ACCEPT;
                        }
                    }
                );

                // Function to check if a rule selector matches an element
                function ruleSelectorMatchesElement(rule, element, classes, idSelector) {
                    if (!rule.selectorText) return false;

                    const selectorText = rule.selectorText;

                    // If element has an ID and rule targets that ID
                    if (idSelector && selectorText.includes(idSelector)) {
                        return true;
                    }
                    // If element has classes and rule targets those classes
                    if (classes.length > 0 && classes.every(cls => selectorText.includes(`.${cls}`))) {
                        return true;
                    }
                    // Generic tag selector (e.g., just "a:hover" or "a")
                    const tagName = element.tagName.toLowerCase();
                    if (selectorText.startsWith(tagName + ':') ||
                        selectorText.startsWith(tagName + '.') ||
                        selectorText === tagName) {
                        return true;
                    }

                    return false;
                }

                // Function to extract styles from a rule for pseudoclasses
                function extractPseudoclassStylesFromRule(rule, element, classes, idSelector, pseudoclasses) {
                    const states = {};

                    if (!rule.selectorText) return states;

                    for (let pseudo of pseudoclasses) {
                        if (rule.selectorText.includes(pseudo)) {
                            if (ruleSelectorMatchesElement(rule, element, classes, idSelector)) {
                                if (!states[pseudo]) {
                                    states[pseudo] = {};
                                }

                                // Extract color and background-color
                                if (rule.style.color) {
                                    states[pseudo].color = rule.style.color;
                                }
                                if (rule.style.backgroundColor) {
                                    states[pseudo].backgroundColor = rule.style.backgroundColor;
                                }
                            }
                        }
                    }

                    return states;
                }

                // Function to get pseudoclass styles from CSS rules, including media queries
                function getPseudoclassStyles(element) {
                    const pseudoclassStates = {};

                    // Determine which pseudoclasses to check based on element type
                    // Links (<a> and role="link") should check :link and :visited in addition to common ones
                    // Other interactive elements (buttons, etc.) should NOT check :link or :visited
                    const isLink = element.tagName === 'A' ||
                                   element.getAttribute('role') === 'link';

                    const pseudoclasses = isLink
                        ? [':hover', ':focus', ':visited', ':active', ':link']
                        : [':hover', ':focus', ':active'];

                    // Build element's class selector
                    const classes = element.className ? element.className.split(' ').filter(c => c.trim()) : [];
                    const idSelector = element.id ? `#${element.id}` : '';

                    // Also track styles from prefers-contrast media queries
                    const prefersContrastStates = {
                        'more': {},    // prefers-contrast: more
                        'less': {},    // prefers-contrast: less
                        'custom': {}   // prefers-contrast: custom
                    };

                    // Parse all stylesheets
                    try {
                        for (let sheet of document.styleSheets) {
                            try {
                                for (let rule of sheet.cssRules || sheet.rules || []) {
                                    // Check for media rules (including prefers-contrast)
                                    if (rule instanceof CSSMediaRule) {
                                        const mediaText = rule.conditionText || rule.media.mediaText || '';

                                        // Check if this is a prefers-contrast media query
                                        let contrastLevel = null;
                                        if (mediaText.includes('prefers-contrast')) {
                                            if (mediaText.includes('more')) contrastLevel = 'more';
                                            else if (mediaText.includes('less')) contrastLevel = 'less';
                                            else if (mediaText.includes('custom')) contrastLevel = 'custom';
                                        }

                                        // Process rules within the media query
                                        for (let innerRule of rule.cssRules || []) {
                                            if (contrastLevel) {
                                                // This is inside a prefers-contrast media query
                                                // Extract both default and pseudoclass styles

                                                // Check for pseudoclass rules
                                                const pseudoStyles = extractPseudoclassStylesFromRule(
                                                    innerRule, element, classes, idSelector, pseudoclasses
                                                );

                                                for (let pseudo in pseudoStyles) {
                                                    const key = `${pseudo}@prefers-contrast:${contrastLevel}`;
                                                    if (!pseudoclassStates[key]) {
                                                        pseudoclassStates[key] = {};
                                                    }
                                                    Object.assign(pseudoclassStates[key], pseudoStyles[pseudo]);
                                                }

                                                // Also check for default state (no pseudoclass)
                                                if (innerRule.selectorText && !pseudoclasses.some(p => innerRule.selectorText.includes(p))) {
                                                    if (ruleSelectorMatchesElement(innerRule, element, classes, idSelector)) {
                                                        const key = `default@prefers-contrast:${contrastLevel}`;
                                                        if (!pseudoclassStates[key]) {
                                                            pseudoclassStates[key] = {};
                                                        }
                                                        if (innerRule.style.color) {
                                                            pseudoclassStates[key].color = innerRule.style.color;
                                                        }
                                                        if (innerRule.style.backgroundColor) {
                                                            pseudoclassStates[key].backgroundColor = innerRule.style.backgroundColor;
                                                        }
                                                    }
                                                }
                                            } else {
                                                // Regular media query (not prefers-contrast), process pseudoclasses
                                                const pseudoStyles = extractPseudoclassStylesFromRule(
                                                    innerRule, element, classes, idSelector, pseudoclasses
                                                );
                                                for (let pseudo in pseudoStyles) {
                                                    if (!pseudoclassStates[pseudo]) {
                                                        pseudoclassStates[pseudo] = {};
                                                    }
                                                    Object.assign(pseudoclassStates[pseudo], pseudoStyles[pseudo]);
                                                }
                                            }
                                        }
                                    } else if (rule.selectorText) {
                                        // Regular rule (not in media query)
                                        const pseudoStyles = extractPseudoclassStylesFromRule(
                                            rule, element, classes, idSelector, pseudoclasses
                                        );
                                        for (let pseudo in pseudoStyles) {
                                            if (!pseudoclassStates[pseudo]) {
                                                pseudoclassStates[pseudo] = {};
                                            }
                                            Object.assign(pseudoclassStates[pseudo], pseudoStyles[pseudo]);
                                        }
                                    }
                                }
                            } catch (e) {
                                // Skip inaccessible stylesheets (CORS)
                            }
                        }
                    } catch (e) {
                        // Error accessing stylesheets
                    }

                    return pseudoclassStates;
                }

                let node;
                while (node = walker.nextNode()) {
                    const element = node.parentElement;
                    const style = window.getComputedStyle(element);

                    // Get text color
                    const textColor = parseColor(style.color);

                    // Get font size and weight to determine if it's "large text"
                    const fontSize = parseFloat(style.fontSize);
                    const fontWeight = parseInt(style.fontWeight) || 400;
                    const isBold = fontWeight >= 700;

                    // Large text = 18pt+ (24px+) OR 14pt+ bold (18.66px+)
                    const isLargeText = fontSize >= 24 || (fontSize >= 18.66 && isBold);

                    // Get background
                    const bgInfo = getEffectiveBackground(element);
                    const bgColor = parseColor(bgInfo.backgroundColor);

                    // Check for text overflow
                    const hasOverflow = checkTextOverflow(element);

                    // Check for animations
                    const hasAnim = hasAnimation(element);

                    // Calculate contrast ratio for default state
                    // We CAN calculate if text is inside container, even if it also overflows
                    // We CANNOT calculate if background is gradient/image/transparent
                    let contrastRatio = null;
                    let canCalculateInsideContrast = bgColor.a > 0 && !bgInfo.hasGradient && !bgInfo.hasImage;

                    if (canCalculateInsideContrast) {
                        contrastRatio = getContrastRatio(textColor, bgColor);
                    }

                    // Get pseudoclass styles and prefers-contrast media query styles
                    // Check for ALL elements (not just interactive) because media queries affect all text
                    const pseudoclassStates = {};
                    const pseudoStyles = getPseudoclassStyles(element);

                    // Calculate contrast for each pseudoclass/media query state
                    for (let pseudo in pseudoStyles) {
                        const pseudoColor = pseudoStyles[pseudo].color ?
                            parseColor(pseudoStyles[pseudo].color) : textColor;
                        const pseudoBg = pseudoStyles[pseudo].backgroundColor ?
                            parseColor(pseudoStyles[pseudo].backgroundColor) : bgColor;

                        if (pseudoBg.a > 0 && !bgInfo.hasGradient && !bgInfo.hasImage) {
                            const pseudoContrast = getContrastRatio(pseudoColor, pseudoBg);
                            pseudoclassStates[pseudo] = {
                                color: `rgba(${pseudoColor.r}, ${pseudoColor.g}, ${pseudoColor.b}, ${pseudoColor.a})`,
                                backgroundColor: `rgba(${pseudoBg.r}, ${pseudoBg.g}, ${pseudoBg.b}, ${pseudoBg.a})`,
                                contrastRatio: pseudoContrast
                            };
                        }
                    }

                    textElements.push({
                        text: node.textContent.trim().substring(0, 100),
                        xpath: getXPath(element),
                        html: element.outerHTML.substring(0, 200),
                        textColor: `rgba(${textColor.r}, ${textColor.g}, ${textColor.b}, ${textColor.a})`,
                        backgroundColor: bgInfo.backgroundColor,
                        contrastRatio: contrastRatio,
                        fontSize: fontSize,
                        fontWeight: fontWeight,
                        isLargeText: isLargeText,
                        stoppedAtZIndex: bgInfo.stoppedAtZIndex,
                        hasGradient: bgInfo.hasGradient,
                        hasImage: bgInfo.hasImage,
                        hasOverflow: hasOverflow,
                        hasAnimation: hasAnim,
                        canCalculateInsideContrast: canCalculateInsideContrast,
                        tag: element.tagName.toLowerCase(),
                        pseudoclassStates: pseudoclassStates,
                        wcagLevel: wcagLevel  // Add WCAG level to each element
                    });
                }

                return textElements;
            }
            ''', breakpoint)

            # Process results from this breakpoint
            for text_elem in text_data:
                results['elements_tested'] += 1

                contrast = text_elem['contrastRatio']
                is_large = text_elem['isLargeText']
                wcag_level = text_elem.get('wcagLevel', 'AA')
                can_calculate_inside = text_elem.get('canCalculateInsideContrast', False)

                # Determine required ratio based on project's WCAG level
                if wcag_level == 'AAA':
                    required_ratio = 4.5 if is_large else 7.0
                    wcag_criterion = '1.4.6'
                    error_code = 'ErrLargeTextContrastAAA' if is_large else 'ErrTextContrastAAA'
                else:  # AA (default)
                    required_ratio = 3.0 if is_large else 4.5
                    wcag_criterion = '1.4.3'
                    error_code = 'ErrLargeTextContrastAA' if is_large else 'ErrTextContrastAA'

                # Case 1: Text inside FAILS contrast AND has overflow/complex conditions
                # Result: ErrPartialTextContrastAA or ErrPartialTextContrastAAA (partial failure)
                if can_calculate_inside and contrast is not None and contrast < required_ratio and text_elem['hasOverflow']:
                    partial_error_code = 'ErrPartialTextContrastAAA' if wcag_level == 'AAA' else 'ErrPartialTextContrastAA'
                    results['errors'].append({
                        'err': partial_error_code,
                        'type': 'err',
                        'cat': 'color_contrast',
                        'element': text_elem['tag'],
                        'xpath': text_elem['xpath'],
                        'html': text_elem['html'],
                        'description': f'{"Large" if is_large else "Normal"} text contrast {contrast:.2f}:1 fails WCAG {wcag_level} requirement ({required_ratio}:1) inside container. Additionally, text overflows container where contrast cannot be determined. Text color {text_elem["textColor"]} on background {text_elem["backgroundColor"]}. (Breakpoint: {breakpoint}px)',
                        'text': text_elem['text'],
                        'textColor': text_elem['textColor'],
                        'backgroundColor': text_elem['backgroundColor'],
                        'contrastRatio': f'{contrast:.2f}:1',
                        'required': f'{required_ratio}:1',
                        'fontSize': text_elem['fontSize'],
                        'isLargeText': is_large,
                        'breakpoint': breakpoint,
                        'wcag': wcag_criterion,
                        'partialReason': 'Text overflows container'
                    })
                    results['elements_failed'] += 1
                    continue

                # Case 2: Cannot calculate contrast inside OR has complex conditions with passing/unknown contrast
                # Result: WarnTextContrastCannotCalculate (manual testing required)
                # Only warn for truly problematic cases: gradients, images, animations, overflow
                should_warn = False
                warning_reasons = []

                # Cannot calculate inside at all (gradient, image, or transparent background)
                if not can_calculate_inside:
                    should_warn = True
                    if text_elem['hasGradient']:
                        warning_reasons.append('gradient background')
                    if text_elem['hasImage']:
                        warning_reasons.append('image background')
                    if not warning_reasons:
                        warning_reasons.append('transparent or undefined background')

                # Can calculate inside and contrast passes, but has truly complex conditions
                # that make automated testing unreliable (NOT just z-index)
                elif can_calculate_inside and contrast is not None and contrast >= required_ratio:
                    if text_elem['hasGradient']:
                        should_warn = True
                        warning_reasons.append('gradient background')
                    if text_elem['hasImage']:
                        should_warn = True
                        warning_reasons.append('image background')
                    if text_elem['hasAnimation']:
                        should_warn = True
                        warning_reasons.append('CSS animation present')
                    if text_elem['hasOverflow']:
                        should_warn = True
                        warning_reasons.append('text overflows container')
                    # Note: We do NOT warn for stoppedAtZIndex alone - only if combined with other issues

                if should_warn and warning_reasons:
                    results['warnings'].append({
                        'err': 'WarnTextContrastCannotCalculate',
                        'type': 'warn',
                        'cat': 'color_contrast',
                        'element': text_elem['tag'],
                        'xpath': text_elem['xpath'],
                        'html': text_elem['html'],
                        'description': f'Cannot automatically calculate text contrast due to: {", ".join(warning_reasons)}. Manual inspection required. (Breakpoint: {breakpoint}px)',
                        'text': text_elem['text'],
                        'textColor': text_elem['textColor'],
                        'backgroundColor': text_elem['backgroundColor'],
                        'fontSize': text_elem['fontSize'],
                        'isLargeText': text_elem['isLargeText'],
                        'breakpoint': breakpoint,
                        'wcag': wcag_criterion
                    })
                    continue

                # Case 3: Can calculate and no overflow - proceed with normal contrast check
                # Skip if foreground and background are identical (data error)
                if text_elem.get('textColor') == text_elem.get('backgroundColor'):
                    continue

                # Check contrast against the project's required level ONLY
                if contrast < required_ratio:
                    results['errors'].append({
                        'err': error_code,
                        'type': 'err',
                        'cat': 'color_contrast',
                        'element': text_elem['tag'],
                        'xpath': text_elem['xpath'],
                        'html': text_elem['html'],
                        'description': f'{"Large" if is_large else "Normal"} text contrast {contrast:.2f}:1 fails WCAG {wcag_level} requirement ({required_ratio}:1). Text color {text_elem["textColor"]} on background {text_elem["backgroundColor"]}.',
                        'text': text_elem['text'],
                        'textColor': text_elem['textColor'],
                        'backgroundColor': text_elem['backgroundColor'],
                        'contrastRatio': f'{contrast:.2f}:1',
                        'required': f'{required_ratio}:1',
                        'fontSize': text_elem['fontSize'],
                        'isLargeText': is_large,
                        'breakpoint': breakpoint,
                        'wcag': wcag_criterion
                    })
                    results['elements_failed'] += 1
                else:
                    # Passes the project's required level
                    results['elements_passed'] += 1

                # Check pseudoclass states (hover, focus, visited, active)
                pseudoclass_states = text_elem.get('pseudoclassStates', {})
                for pseudo, state_data in pseudoclass_states.items():
                    pseudo_contrast = state_data.get('contrastRatio')
                    if pseudo_contrast is None:
                        continue

                    # Skip if foreground and background are identical (data error)
                    if state_data.get('color') == state_data.get('backgroundColor'):
                        continue

                    # Check if pseudoclass state fails the project's required level
                    if pseudo_contrast < required_ratio:
                        results['errors'].append({
                            'err': error_code,
                            'type': 'err',
                            'cat': 'color_contrast',
                            'element': text_elem['tag'],
                            'xpath': text_elem['xpath'],
                            'html': text_elem['html'],
                            'description': f'{"Large" if is_large else "Normal"} text contrast {pseudo_contrast:.2f}:1 fails WCAG {wcag_level} requirement ({required_ratio}:1) in {pseudo} state. Text color {state_data["color"]} on background {state_data["backgroundColor"]}.',
                            'text': text_elem['text'],
                            'textColor': state_data['color'],
                            'backgroundColor': state_data['backgroundColor'],
                            'contrastRatio': f'{pseudo_contrast:.2f}:1',
                            'required': f'{required_ratio}:1',
                            'fontSize': text_elem['fontSize'],
                            'isLargeText': is_large,
                            'pseudoclass': pseudo,
                            'breakpoint': breakpoint,
                            'wcag': wcag_criterion
                        })
                        # Note: We don't increment elements_failed again, as this is the same element

        # Add check information
        results['checks'].append({
            'description': 'Text color contrast (including pseudoclass states)',
            'wcag': ['1.4.3', '1.4.6'],
            'total': results['elements_tested'],
            'passed': results['elements_passed'],
            'failed': results['elements_failed']
        })

        return results

    except Exception as e:
        logger.error(f"Error in test_text_contrast: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }
