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
                    // Filter out hidden buttons
                    if (style.display === 'none' || style.visibility === 'hidden') {
                        return false;
                    }
                    // Filter out disabled buttons - they cannot receive focus
                    if (btn.disabled || btn.hasAttribute('disabled') || btn.getAttribute('aria-disabled') === 'true') {
                        return false;
                    }
                    return true;
                });

                return allButtons.map(button => {
                    const normalStyle = window.getComputedStyle(button);

                    // Get font size for em/rem calculations
                    const fontSize = parseFloat(normalStyle.fontSize) || 16;
                    const rootFontSize = parseFloat(window.getComputedStyle(document.documentElement).fontSize) || 16;

                    // Get clip-path for non-rectangular button detection
                    const clipPath = normalStyle.clipPath;

                    // Get background color of button's container for contrast calculation
                    let bgElement = button.parentElement;
                    let backgroundColor = normalStyle.backgroundColor;
                    let backgroundImage = normalStyle.backgroundImage; // For gradient/image detection

                    // Walk up the DOM to find a non-transparent background
                    while (bgElement && backgroundColor === 'rgba(0, 0, 0, 0)') {
                        backgroundColor = window.getComputedStyle(bgElement).backgroundColor;
                        bgElement = bgElement.parentElement;
                    }

                    // Default to white if we couldn't find a background
                    if (backgroundColor === 'rgba(0, 0, 0, 0)') {
                        backgroundColor = 'rgb(255, 255, 255)';
                    }

                    // Also get the full background property for gradient/image detection
                    const fullBackground = normalStyle.background;

                    // Try to get focus styles by checking stylesheets
                    let focusOutlineStyle = null;
                    let focusOutlineWidth = null;
                    let focusOutlineColor = null;
                    let focusOutlineOffset = null;
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
                                            if (rule.style.outlineOffset !== undefined && rule.style.outlineOffset !== '') {
                                                focusOutlineOffset = rule.style.outlineOffset;
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
                        fontSize: fontSize,
                        rootFontSize: rootFontSize,
                        clipPath: clipPath,
                        normalOutlineStyle: normalStyle.outlineStyle,
                        normalOutlineWidth: normalStyle.outlineWidth,
                        normalOutlineColor: normalStyle.outlineColor,
                        focusOutlineStyle: focusOutlineStyle,
                        focusOutlineWidth: focusOutlineWidth,
                        focusOutlineColor: focusOutlineColor,
                        focusOutlineOffset: focusOutlineOffset,
                        focusBackgroundColor: focusBackgroundColor,
                        focusBorderColor: focusBorderColor,
                        focusBoxShadow: focusBoxShadow,
                        backgroundColor: backgroundColor,
                        normalBackgroundColor: normalStyle.backgroundColor,
                        backgroundImage: backgroundImage,
                        fullBackground: fullBackground
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

        # Helper function to parse px values (including em/rem)
        def parse_px(value_str, font_size=16, root_font_size=16):
            """Parse CSS pixel values, return float or 0

            Args:
                value_str: CSS value string (e.g., '2px', '1.5em', '2rem', 'thin')
                font_size: Element font size in pixels (for em)
                root_font_size: Root font size in pixels (for rem)
            """
            if not value_str:
                return 0.0
            if value_str == '0' or value_str == 'none':
                return 0.0

            value_str = str(value_str).strip()

            # Handle px values
            if 'px' in value_str:
                try:
                    return float(value_str.replace('px', '').strip())
                except:
                    return 0.0

            # Handle em values (relative to element font size)
            if 'em' in value_str and 'rem' not in value_str:
                try:
                    em_value = float(value_str.replace('em', '').strip())
                    return em_value * font_size
                except:
                    return 0.0

            # Handle rem values (relative to root font size)
            if 'rem' in value_str:
                try:
                    rem_value = float(value_str.replace('rem', '').strip())
                    return rem_value * root_font_size
                except:
                    return 0.0

            # Handle keywords: thin=1px, medium=3px, thick=5px
            if value_str == 'thin':
                return 1.0
            if value_str == 'medium':
                return 3.0
            if value_str == 'thick':
                return 5.0

            # Try parsing as plain number (assume px)
            try:
                return float(value_str)
            except:
                return 0.0

        # Helper to detect gradient backgrounds
        def has_gradient_background(bg_str):
            if not bg_str:
                return False
            return 'gradient' in bg_str.lower()

        # Helper to detect image backgrounds
        def has_image_background(bg_str):
            if not bg_str:
                return False
            return 'url(' in bg_str.lower()

        # Helper to analyze box-shadow (check if it's on all sides)
        def is_single_side_box_shadow(box_shadow_str):
            """Check if box-shadow only appears on one side (not all around)"""
            if not box_shadow_str or box_shadow_str == 'none':
                return False

            # Parse box-shadow: x-offset y-offset blur spread color
            # If x-offset or y-offset is non-zero, it's directional (one-sided)
            # Examples:
            #   "0 0 0 3px blue" - all sides (spread with no offset)
            #   "0 4px 0 0 blue" - bottom only (y-offset=4px)
            #   "2px 0 0 0 blue" - right only (x-offset=2px)
            import re

            # Simple heuristic: if x or y offset is non-zero, it's single-sided
            # Note: browsers return box-shadow as "color x y blur spread" so we need to search not match
            # Match: number(unit)? number(unit)? (these are x and y offsets)
            match = re.search(r'(-?\d+(?:\.\d+)?(?:px|em|rem)?)\s+(-?\d+(?:\.\d+)?(?:px|em|rem)?)', box_shadow_str)
            if match:
                x_offset_str = match.group(1)
                y_offset_str = match.group(2)

                # Simple px parser for box-shadow (usually in px)
                def simple_parse_px(val_str):
                    if not val_str:
                        return 0.0
                    val_str = val_str.strip()
                    if val_str == '0':
                        return 0.0
                    # Remove px suffix if present
                    if 'px' in val_str:
                        val_str = val_str.replace('px', '').strip()
                    try:
                        return float(val_str)
                    except:
                        return 0.0

                x_val = simple_parse_px(x_offset_str)
                y_val = simple_parse_px(y_offset_str)

                # If either offset is non-zero, it's directional
                if abs(x_val) > 0 or abs(y_val) > 0:
                    return True

            return False

        # Helper to detect clip-path (non-rectangular buttons)
        def has_clip_path(clip_path_str):
            """Check if button has non-rectangular clip-path"""
            if not clip_path_str or clip_path_str == 'none':
                return False
            # Any clip-path that's not 'none' is potentially problematic
            # Common: circle(), ellipse(), polygon(), path(), inset()
            return True

        # Test each button for focus indicators
        for button in button_data:
            tag = button['tagName'].lower()
            error_code = None
            violation_reason = None

            # Get font sizes for em/rem calculations
            font_size = button.get('fontSize', 16)
            root_font_size = button.get('rootFontSize', 16)

            # Check for gradient or image backgrounds first (for warnings)
            button_background = button.get('fullBackground', '') or button.get('normalBackgroundColor', '')
            button_bg_image = button.get('backgroundImage', '')
            has_gradient = has_gradient_background(button_background) or has_gradient_background(button_bg_image)
            has_image = has_image_background(button_background) or has_image_background(button_bg_image)

            # Check for clip-path (non-rectangular buttons)
            button_clip_path = button.get('clipPath', 'none')
            has_nonrect_clip = has_clip_path(button_clip_path)

            # Check if this button is using browser default focus (no custom styles)
            has_custom_focus = (
                button['focusOutlineStyle'] is not None or
                button['focusOutlineWidth'] is not None or
                button['focusOutlineColor'] is not None or
                button['focusBackgroundColor'] is not None or
                button['focusBoxShadow'] is not None
            )

            # Error: clip-path with outline (fails Conformance Requirement 5.2.4)
            # Only flag if button has clip-path AND is using outline (not box-shadow or other methods)
            uses_outline_for_focus = (
                button['focusOutlineStyle'] is not None and
                button['focusOutlineStyle'] != 'none' and
                button['focusOutlineStyle'] != ''
            )
            if has_nonrect_clip and uses_outline_for_focus:
                error_code = 'ErrButtonClipPathWithOutline'
                violation_reason = f'Button has clip-path ({button_clip_path}) but uses outline for focus - outline does not follow clipped shape and may appear disconnected (fails WCAG Conformance Requirement 5.2.4 for magnification users)'

            # Warning: Browser default focus (no custom styles)
            elif not has_custom_focus:
                error_code = 'WarnButtonDefaultFocus'
                violation_reason = 'Button uses browser default focus styles which may not meet 3:1 contrast on all backgrounds (best practice: define explicit focus styles)'

            # Check if outline is explicitly set to none on focus
            elif button['focusOutlineStyle'] == 'none':
                # Check if there's a box-shadow (acceptable alternative)
                has_box_shadow = button['focusBoxShadow'] and button['focusBoxShadow'] != 'none'

                if has_box_shadow:
                    # Check if box-shadow is single-sided (insufficient)
                    if is_single_side_box_shadow(button['focusBoxShadow']):
                        error_code = 'ErrButtonSingleSideBoxShadow'
                        violation_reason = 'Button uses outline:none with single-side box-shadow (only visible on one edge, insufficient for all users)'
                    else:
                        # Has all-around box-shadow - issue warning but not error
                        error_code = 'WarnButtonOutlineNoneWithBoxShadow'
                        violation_reason = 'Button uses outline:none with box-shadow instead of outline (suboptimal but acceptable)'
                else:
                    # No box-shadow - check if only using color changes (WCAG 1.4.1 violation)
                    has_color_change = (
                        button['focusBackgroundColor'] and
                        button['focusBackgroundColor'] != button['normalBackgroundColor']
                    ) or button['focusBorderColor']

                    if has_color_change:
                        # Color change only - WCAG 1.4.1 Use of Color violation
                        error_code = 'ErrButtonOutlineNoneNoBoxShadow'
                        violation_reason = 'Button has outline:none with only color change (violates WCAG 1.4.1 Use of Color - users with color blindness cannot perceive focus)'
                    else:
                        # No visible focus indicator at all
                        error_code = 'ErrButtonNoVisibleFocus'
                        violation_reason = 'Button has outline:none with no alternative focus indicator'

            # If outline is present, check its properties
            elif button['focusOutlineColor'] and button['focusOutlineWidth']:
                # Parse with em/rem support
                outline_width = parse_px(button['focusOutlineWidth'], font_size, root_font_size)
                outline_offset = parse_px(button.get('focusOutlineOffset', '0px'), font_size, root_font_size)

                # Check outline width (must be >= 2px per WCAG 2.4.11)
                if outline_width > 0 and outline_width < 2.0:
                    error_code = 'ErrButtonOutlineWidthInsufficient'
                    violation_reason = f'Button focus outline is too thin ({outline_width:.2f}px, needs ≥2px per WCAG 2.4.11)'

                # Check outline offset (should be >= 2px when outline is present)
                elif outline_width >= 2.0 and outline_offset < 2.0:
                    error_code = 'ErrButtonOutlineOffsetInsufficient'
                    violation_reason = f'Button focus outline offset is too small ({outline_offset:.2f}px, needs ≥2px for clear separation from button)'

                # Check outline contrast (only if width and offset are sufficient)
                else:
                    # Warning: Gradient background (cannot auto-verify contrast)
                    if has_gradient:
                        error_code = 'WarnButtonFocusGradientBackground'
                        violation_reason = 'Button has gradient background - focus outline contrast cannot be automatically verified (manual testing required against lightest and darkest gradient colors)'

                    # Warning: Image background (cannot auto-verify contrast)
                    elif has_image:
                        error_code = 'WarnButtonFocusImageBackground'
                        violation_reason = 'Button has background image - focus outline contrast cannot be automatically verified (manual testing required against all parts of image)'

                    # Check contrast against solid background
                    else:
                        outline_color = parse_color(button['focusOutlineColor'])
                        bg_color = parse_color(button['backgroundColor'])

                        # Check if outline color is fully transparent
                        if outline_color['a'] == 0:
                            error_code = 'ErrButtonNoVisibleFocus'
                            violation_reason = 'Button focus outline is transparent/invisible'
                        # Check if outline is semi-transparent (< 50% opacity) - Error, not warning
                        elif outline_color['a'] < 0.5:
                            error_code = 'ErrButtonTransparentOutline'
                            violation_reason = f'Button focus outline is semi-transparent (alpha={outline_color["a"]:.2f}) which cannot guarantee 3:1 contrast in all contexts (fails WCAG 1.4.11)'
                        else:
                            # For semi-transparent colors, we should ideally blend with background
                            # For now, just calculate contrast with the opaque version
                            contrast = get_contrast_ratio(outline_color, bg_color)
                            if contrast < 3.0:
                                error_code = 'ErrButtonFocusContrastFail'
                                violation_reason = f'Button focus outline has insufficient contrast ({contrast:.2f}:1, needs ≥3:1 per WCAG 1.4.11)'

            # Check for generic button text (independent check - can co-exist with other issues)
            button_text = button.get('text', '').lower().strip()

            # List of generic/vague terms that should be avoided
            # Excludes standard form actions (submit, reset, cancel, ok, yes, no, etc.)
            generic_terms = [
                'click here', 'click', 'tap here', 'tap',
                'read more', 'learn more', 'see more', 'view more', 'show more',
                'more', 'less',
                'go', 'here', 'there',
                'link', 'button',
                'info', 'details',
                'get', 'download'  # only if standalone
            ]

            # Check if button text matches generic terms
            is_generic = False
            for term in generic_terms:
                if button_text == term or button_text == term + '.':
                    is_generic = True
                    break

            if is_generic:
                results['warnings'].append({
                    'err': 'WarnButtonGenericText',
                    'type': 'warn',
                    'cat': 'buttons',
                    'element': tag,
                    'xpath': button['xpath'],
                    'html': button['html'],
                    'description': f'Button uses generic text "{button.get("text", "")}" which provides no context about its purpose when read in isolation',
                    'text': button['text']
                })
                # Note: Don't increment elements_failed here as it will be counted below

            # If we found a violation or warning
            if error_code:
                result_type = 'warn' if error_code.startswith('Warn') else 'err'
                result_list = results['warnings'] if result_type == 'warn' else results['errors']

                result_list.append({
                    'err': error_code,
                    'type': result_type,
                    'cat': 'buttons',
                    'element': tag,
                    'xpath': button['xpath'],
                    'html': button['html'],
                    'description': violation_reason,
                    'text': button['text']
                })
                results['elements_failed'] += 1
            else:
                # Only increment passed if no issues found (including generic text)
                if not is_generic:
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
