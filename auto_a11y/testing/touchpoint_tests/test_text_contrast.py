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
        for breakpoint in breakpoint_data:
            # Set viewport to this breakpoint
            await page.setViewport({'width': breakpoint, 'height': 800})

            # Wait a moment for any dynamic content to adjust
            await page.waitFor(100)

            # Extract text elements and their contrast data at this breakpoint
            text_data = await page.evaluate('''
                (breakpointWidth) => {
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

                    const rgbaMatch = colorStr.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
                    if (rgbaMatch) {
                        return {
                            r: parseInt(rgbaMatch[1]),
                            g: parseInt(rgbaMatch[2]),
                            b: parseInt(rgbaMatch[3]),
                            a: rgbaMatch[4] !== undefined ? parseFloat(rgbaMatch[4]) : 1
                        };
                    }

                    const hexMatch = colorStr.match(/^#([0-9a-f]{6})$/i);
                    if (hexMatch) {
                        const hex = hexMatch[1];
                        return {
                            r: parseInt(hex.substr(0, 2), 16),
                            g: parseInt(hex.substr(2, 2), 16),
                            b: parseInt(hex.substr(4, 2), 16),
                            a: 1
                        };
                    }

                    return { r: 0, g: 0, b: 0, a: 1 };
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
                        hasImage: lower.includes('url(') && !lower.includes('data:')
                    };
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

                            const style = window.getComputedStyle(parent);

                            // Skip if hidden
                            if (style.display === 'none' || style.visibility === 'hidden') {
                                return NodeFilter.FILTER_REJECT;
                            }

                            // Skip if visually hidden (screen reader only)
                            if (isVisuallyHidden(parent)) {
                                return NodeFilter.FILTER_REJECT;
                            }

                            // Skip if zero opacity
                            if (parseFloat(style.opacity) === 0) {
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

                    // Calculate contrast ratio for default state
                    let contrastRatio = null;
                    if (bgColor.a > 0 && !bgInfo.hasGradient && !bgInfo.hasImage && !hasOverflow) {
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
                        tag: element.tagName.toLowerCase(),
                        pseudoclassStates: pseudoclassStates
                    });
                }

                return textElements;
            }
            ''', breakpoint)

            # Process results from this breakpoint
            for text_elem in text_data:
                results['elements_tested'] += 1

                # If we can't calculate contrast, issue a warning
                if text_elem['contrastRatio'] is None:
                    warning_reasons = []
                    if text_elem['hasGradient']:
                        warning_reasons.append('gradient background')
                    if text_elem['hasImage']:
                        warning_reasons.append('image background')
                    if text_elem['hasOverflow']:
                        warning_reasons.append('text overflows container')
                    if text_elem['stoppedAtZIndex']:
                        warning_reasons.append('floating element with z-index')

                    if warning_reasons:
                        results['warnings'].append({
                            'err': 'WarnTextContrastCannotCalculate',
                            'type': 'warn',
                            'cat': 'colors_contrast',
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
                            'wcag': '1.4.3'
                        })
                    continue

                contrast = text_elem['contrastRatio']
                is_large = text_elem['isLargeText']

                # Determine required ratios
                # AA: 4.5:1 normal, 3:1 large
                # AAA: 7:1 normal, 4.5:1 large
                aa_required = 3.0 if is_large else 4.5
                aaa_required = 4.5 if is_large else 7.0

                # Check AA levels
                if contrast < aa_required:
                    error_code = 'ErrLargeTextContrastAA' if is_large else 'ErrTextContrastAA'
                    results['errors'].append({
                        'err': error_code,
                        'type': 'err',
                        'cat': 'colors_contrast',
                        'element': text_elem['tag'],
                        'xpath': text_elem['xpath'],
                        'html': text_elem['html'],
                        'description': f'{"Large" if is_large else "Normal"} text contrast {contrast:.2f}:1 fails WCAG AA requirement ({aa_required}:1). Text color {text_elem["textColor"]} on background {text_elem["backgroundColor"]}.',
                        'text': text_elem['text'],
                        'textColor': text_elem['textColor'],
                        'backgroundColor': text_elem['backgroundColor'],
                        'contrastRatio': f'{contrast:.2f}:1',
                        'required': f'{aa_required}:1',
                        'fontSize': text_elem['fontSize'],
                        'isLargeText': is_large,
                        'breakpoint': breakpoint,
                        'wcag': '1.4.3'
                    })
                    results['elements_failed'] += 1

                # Check AAA levels only if AA passes (AAA is enhanced/informational)
                elif contrast < aaa_required:
                    error_code = 'ErrLargeTextContrastAAA' if is_large else 'ErrTextContrastAAA'
                    results['errors'].append({
                        'err': error_code,
                        'type': 'err',
                        'cat': 'colors_contrast',
                        'element': text_elem['tag'],
                        'xpath': text_elem['xpath'],
                        'html': text_elem['html'],
                        'description': f'{"Large" if is_large else "Normal"} text contrast {contrast:.2f}:1 fails WCAG AAA requirement ({aaa_required}:1) but passes AA. Text color {text_elem["textColor"]} on background {text_elem["backgroundColor"]}.',
                        'text': text_elem['text'],
                        'textColor': text_elem['textColor'],
                        'backgroundColor': text_elem['backgroundColor'],
                        'contrastRatio': f'{contrast:.2f}:1',
                        'required': f'{aaa_required}:1',
                        'fontSize': text_elem['fontSize'],
                        'isLargeText': is_large,
                        'breakpoint': breakpoint,
                        'wcag': '1.4.6'
                    })
                    # AAA failures don't count as "failed" since AA is the baseline requirement
                    results['elements_passed'] += 1
                else:
                    # Passes both AA and AAA
                    results['elements_passed'] += 1

                # Check pseudoclass states (hover, focus, visited, active)
                pseudoclass_states = text_elem.get('pseudoclassStates', {})
                for pseudo, state_data in pseudoclass_states.items():
                    pseudo_contrast = state_data.get('contrastRatio')
                    if pseudo_contrast is None:
                        continue

                    # Check if pseudoclass state fails contrast
                    if pseudo_contrast < aa_required:
                        error_code = 'ErrLargeTextContrastAA' if is_large else 'ErrTextContrastAA'
                        results['errors'].append({
                            'err': error_code,
                            'type': 'err',
                            'cat': 'colors_contrast',
                            'element': text_elem['tag'],
                            'xpath': text_elem['xpath'],
                            'html': text_elem['html'],
                            'description': f'{"Large" if is_large else "Normal"} text contrast {pseudo_contrast:.2f}:1 fails WCAG AA requirement ({aa_required}:1) in {pseudo} state. Text color {state_data["color"]} on background {state_data["backgroundColor"]}.',
                            'text': text_elem['text'],
                            'textColor': state_data['color'],
                            'backgroundColor': state_data['backgroundColor'],
                            'contrastRatio': f'{pseudo_contrast:.2f}:1',
                            'required': f'{aa_required}:1',
                            'fontSize': text_elem['fontSize'],
                            'isLargeText': is_large,
                            'pseudoclass': pseudo,
                            'breakpoint': breakpoint,
                            'wcag': '1.4.3'
                        })
                        # Note: We don't increment elements_failed again, as this is the same element

                    # Check AAA for pseudoclass states
                    elif pseudo_contrast < aaa_required:
                        error_code = 'ErrLargeTextContrastAAA' if is_large else 'ErrTextContrastAAA'
                        results['errors'].append({
                            'err': error_code,
                            'type': 'err',
                            'cat': 'colors_contrast',
                            'element': text_elem['tag'],
                            'xpath': text_elem['xpath'],
                            'html': text_elem['html'],
                            'description': f'{"Large" if is_large else "Normal"} text contrast {pseudo_contrast:.2f}:1 fails WCAG AAA requirement ({aaa_required}:1) but passes AA in {pseudo} state. Text color {state_data["color"]} on background {state_data["backgroundColor"]}.',
                            'text': text_elem['text'],
                            'textColor': state_data['color'],
                            'backgroundColor': state_data['backgroundColor'],
                            'contrastRatio': f'{pseudo_contrast:.2f}:1',
                            'required': f'{aaa_required}:1',
                            'fontSize': text_elem['fontSize'],
                            'isLargeText': is_large,
                            'pseudoclass': pseudo,
                            'breakpoint': breakpoint,
                            'wcag': '1.4.6'
                        })

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
