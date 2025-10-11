"""
Button touchpoint test module
Tests for proper button focus indicators and keyboard accessibility.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Button Focus Indicators",
    "touchpoint": "buttons",
    "description": "Tests for proper button focus indicators ensuring keyboard users can see which button has focus. Checks for outline:none without alternatives, invisible focus indicators, and insufficient contrast ratios.",
    "version": "1.0.0",
    "wcagCriteria": ["2.4.7"],
    "tests": [
        {
            "id": "button-focus-visible",
            "name": "Button Focus Visible",
            "description": "Checks if buttons have visible focus indicators with sufficient contrast",
            "impact": "high",
            "wcagCriteria": ["2.4.7"],
        }
    ]
}

async def test_buttons(page) -> Dict[str, Any]:
    """
    Test button focus indicators for keyboard accessibility

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Extract button focus data from the page
        button_data = await page.evaluate('''
            () => {
                // Simple XPath generator
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

                // Helper to parse color values to RGBA
                function parseColor(colorStr) {
                    if (!colorStr || colorStr === 'transparent') {
                        return { r: 0, g: 0, b: 0, a: 0 };
                    }

                    // Handle rgba format
                    const rgbaMatch = colorStr.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
                    if (rgbaMatch) {
                        return {
                            r: parseInt(rgbaMatch[1]),
                            g: parseInt(rgbaMatch[2]),
                            b: parseInt(rgbaMatch[3]),
                            a: rgbaMatch[4] !== undefined ? parseFloat(rgbaMatch[4]) : 1
                        };
                    }

                    // Handle hex format
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

                // Get all buttons (button element and elements with role="button")
                const allButtons = Array.from(document.querySelectorAll('button, [role="button"]')).filter(btn => {
                    const style = window.getComputedStyle(btn);
                    return style.display !== 'none' && style.visibility !== 'hidden';
                });

                return allButtons.map(button => {
                    const normalStyle = window.getComputedStyle(button);

                    // Get background color of button's container for contrast calculation
                    let bgElement = button.parentElement;
                    let backgroundColor = normalStyle.backgroundColor;

                    // Walk up the DOM to find a non-transparent background
                    while (bgElement && backgroundColor === 'rgba(0, 0, 0, 0)') {
                        backgroundColor = window.getComputedStyle(bgElement).backgroundColor;
                        bgElement = bgElement.parentElement;
                    }

                    // Default to white if we couldn't find a background
                    if (backgroundColor === 'rgba(0, 0, 0, 0)') {
                        backgroundColor = 'rgb(255, 255, 255)';
                    }

                    // Try to get focus styles by checking stylesheets
                    let focusOutlineStyle = null;
                    let focusOutlineWidth = null;
                    let focusOutlineColor = null;
                    let focusBackgroundColor = null;
                    let focusBorderColor = null;
                    let focusBoxShadow = null;

                    // Check all stylesheets for :focus rules
                    const sheets = Array.from(document.styleSheets);
                    for (const sheet of sheets) {
                        try {
                            const rules = Array.from(sheet.cssRules || sheet.rules || []);
                            for (const rule of rules) {
                                if (rule.selectorText && rule.selectorText.includes(':focus')) {
                                    // Check if this rule applies to our button
                                    const selector = rule.selectorText.replace(':focus', '');
                                    try {
                                        if (button.matches(selector)) {
                                            if (rule.style.outlineStyle !== undefined && rule.style.outlineStyle !== '') {
                                                focusOutlineStyle = rule.style.outlineStyle;
                                            }
                                            if (rule.style.outlineWidth !== undefined && rule.style.outlineWidth !== '') {
                                                focusOutlineWidth = rule.style.outlineWidth;
                                            }
                                            if (rule.style.outlineColor !== undefined && rule.style.outlineColor !== '') {
                                                focusOutlineColor = rule.style.outlineColor;
                                            }
                                            if (rule.style.outline !== undefined && rule.style.outline !== '') {
                                                const outlineValue = rule.style.outline;
                                                if (outlineValue === 'none' || outlineValue === '0') {
                                                    focusOutlineStyle = 'none';
                                                    focusOutlineWidth = '0px';
                                                }
                                            }
                                            if (rule.style.backgroundColor !== undefined && rule.style.backgroundColor !== '') {
                                                focusBackgroundColor = rule.style.backgroundColor;
                                            }
                                            if (rule.style.borderColor !== undefined && rule.style.borderColor !== '') {
                                                focusBorderColor = rule.style.borderColor;
                                            }
                                            if (rule.style.boxShadow !== undefined && rule.style.boxShadow !== '') {
                                                focusBoxShadow = rule.style.boxShadow;
                                            }
                                        }
                                    } catch (e) {
                                        // Selector might not be valid or might not match
                                    }
                                }
                            }
                        } catch (e) {
                            // Cross-origin stylesheet or other access issue
                        }
                    }

                    return {
                        tagName: button.tagName,
                        text: button.textContent.trim().substring(0, 50),
                        xpath: getXPath(button),
                        html: button.outerHTML.substring(0, 200),
                        className: button.className,
                        normalOutlineStyle: normalStyle.outlineStyle,
                        normalOutlineWidth: normalStyle.outlineWidth,
                        normalOutlineColor: normalStyle.outlineColor,
                        focusOutlineStyle: focusOutlineStyle,
                        focusOutlineWidth: focusOutlineWidth,
                        focusOutlineColor: focusOutlineColor,
                        focusBackgroundColor: focusBackgroundColor,
                        focusBorderColor: focusBorderColor,
                        focusBoxShadow: focusBoxShadow,
                        backgroundColor: backgroundColor,
                        normalBackgroundColor: normalStyle.backgroundColor
                    };
                });
            }
        ''')

        results = {
            'applicable': True,
            'errors': [],
            'warnings': [],
            'passes': [],
            'elements_tested': 0,
            'elements_passed': 0,
            'elements_failed': 0,
            'test_name': 'buttons',
            'checks': []
        }

        # Check if test is applicable
        if len(button_data) == 0:
            results['applicable'] = False
            results['not_applicable_reason'] = 'No buttons found on the page'
            return results

        results['elements_tested'] = len(button_data)

        # Helper function to parse color values
        def parse_color(color_str):
            if not color_str or color_str == 'transparent':
                return {'r': 0, 'g': 0, 'b': 0, 'a': 0}

            # Handle rgba format
            import re
            rgba_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', color_str)
            if rgba_match:
                return {
                    'r': int(rgba_match.group(1)),
                    'g': int(rgba_match.group(2)),
                    'b': int(rgba_match.group(3)),
                    'a': float(rgba_match.group(4)) if rgba_match.group(4) else 1.0
                }

            # Handle hex format
            hex_match = re.match(r'^#([0-9a-f]{6})$', color_str, re.IGNORECASE)
            if hex_match:
                hex_val = hex_match.group(1)
                return {
                    'r': int(hex_val[0:2], 16),
                    'g': int(hex_val[2:4], 16),
                    'b': int(hex_val[4:6], 16),
                    'a': 1.0
                }

            return {'r': 0, 'g': 0, 'b': 0, 'a': 1.0}

        def get_luminance(color):
            r_srgb = color['r'] / 255.0
            g_srgb = color['g'] / 255.0
            b_srgb = color['b'] / 255.0

            r = r_srgb / 12.92 if r_srgb <= 0.03928 else ((r_srgb + 0.055) / 1.055) ** 2.4
            g = g_srgb / 12.92 if g_srgb <= 0.03928 else ((g_srgb + 0.055) / 1.055) ** 2.4
            b = b_srgb / 12.92 if b_srgb <= 0.03928 else ((b_srgb + 0.055) / 1.055) ** 2.4

            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        def get_contrast_ratio(color1, color2):
            lum1 = get_luminance(color1)
            lum2 = get_luminance(color2)
            lighter = max(lum1, lum2)
            darker = min(lum1, lum2)
            return (lighter + 0.05) / (darker + 0.05)

        # Test each button for focus indicators
        for button in button_data:
            tag = button['tagName'].lower()
            violation_reason = None

            # Check if outline is explicitly set to none on focus
            if button['focusOutlineStyle'] == 'none':
                # Check if there are alternative focus indicators
                has_alternative = False

                # Check for background color change
                if button['focusBackgroundColor'] and button['focusBackgroundColor'] != button['normalBackgroundColor']:
                    bg_color = parse_color(button['backgroundColor'])
                    focus_bg = parse_color(button['focusBackgroundColor'])
                    contrast = get_contrast_ratio(bg_color, focus_bg)
                    if contrast >= 3.0:
                        has_alternative = True

                # Check for border color change
                if button['focusBorderColor']:
                    has_alternative = True

                # Check for box-shadow
                if button['focusBoxShadow'] and button['focusBoxShadow'] != 'none':
                    has_alternative = True

                if not has_alternative:
                    violation_reason = 'Button has outline:none on focus with no alternative focus indicator'

            # If outline is not none but is specified, check its contrast
            elif button['focusOutlineColor']:
                outline_color = parse_color(button['focusOutlineColor'])
                bg_color = parse_color(button['backgroundColor'])

                # Check if outline color is transparent/invisible
                if outline_color['a'] == 0:
                    violation_reason = 'Button focus outline is transparent/invisible'
                else:
                    contrast = get_contrast_ratio(outline_color, bg_color)
                    if contrast < 3.0:
                        violation_reason = f'Button focus outline has insufficient contrast ({contrast:.2f}:1, needs 3:1)'

            # If no focus styles were explicitly set, browser default is used (which is good)
            # So we only report violations if we found problems above

            # If we found a violation
            if violation_reason:
                results['errors'].append({
                    'err': 'ErrButtonNoVisibleFocus',
                    'type': 'err',
                    'cat': 'buttons',
                    'element': tag,
                    'xpath': button['xpath'],
                    'html': button['html'],
                    'description': violation_reason,
                    'text': button['text']
                })
                results['elements_failed'] += 1
            else:
                results['elements_passed'] += 1

        # Add check information for reporting
        results['checks'].append({
            'description': 'Button focus indicators',
            'wcag': ['2.4.7'],
            'total': results['elements_tested'],
            'passed': results['elements_passed'],
            'failed': results['elements_failed']
        })

        return results

    except Exception as e:
        logger.error(f"Error in test_buttons: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }
