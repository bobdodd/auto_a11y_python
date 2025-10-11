"""
Test for form input field focus indicators (WCAG 2.4.7, 1.4.1, 1.4.11, 2.4.11)

Tests text input fields (<input>, <textarea>) for visible focus indicators with
nuanced handling of border changes and box-shadows as focus indicators.

Key differences from buttons/links:
- Input fields often have borders by default to show the input area
- Border thickening (≥1px increase) is acceptable as a focus indicator
- Border color change alone violates WCAG 1.4.1 Use of Color
- Box-shadow can serve as focus indicator if contrast ≥3:1
- Single-sided box-shadows are failures (don't follow field shape)
- Separate outline is STRONGLY RECOMMENDED for screen magnifier users
  (they may not see other fields to compare visual differences)

WCAG Success Criteria:
- 2.4.7 Focus Visible (Level AA) - Focus indicator must be visible
- 1.4.1 Use of Color (Level A) - Color cannot be the only indicator
- 1.4.11 Non-text Contrast (Level AA) - Focus indicator must have ≥3:1 contrast
- 2.4.11 Focus Appearance (Level AAA) - Outline should be ≥2px
- Conformance Requirement 5.2.4 - Indicator must follow element shape (all sides)
"""

import asyncio
from typing import Dict, List, Any
import re


TEST_DOCUMENTATION = {
    "id": "test_form_focus",
    "name": "Form Input Focus Indicators",
    "description": "Tests text input fields for visible focus indicators with proper contrast and structural changes",
    "category": "forms",
    "wcag": ["2.4.7", "1.4.1", "1.4.11", "2.4.11"],
    "impact": "High",
    "why": "Users who navigate by keyboard must be able to see which input field has focus. Screen magnifier users especially need clear indicators as they may only see one field at a time."
}


async def test_form_focus(page):
    """
    Test form input fields for visible focus indicators

    This test focuses on <input> and <textarea> elements that accept text,
    checking for visible focus indicators with nuanced handling of:
    - Border changes (thickness and color)
    - Box-shadows (including single-sided detection)
    - Separate outlines (recommended best practice)
    - Contrast ratios
    """
    results = {
        'errors': [],
        'warnings': [],
        'info': [],
        'discoveries': []
    }

    # JavaScript to extract input field focus styles from stylesheets
    input_styles = await page.evaluate('''
        () => {
            const inputs = [];

            // Get all text input fields and textareas
            const fields = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="search"], input[type="tel"], input[type="url"], input[type="number"], textarea, input:not([type])');

            // Helper: Parse computed style to get actual values
            function getComputedStyleValue(element, property) {
                return window.getComputedStyle(element).getPropertyValue(property);
            }

            // Helper: Get style from stylesheets (not just computed)
            function getStyleFromSheets(element, pseudo, property) {
                // Try to get from stylesheet rules
                for (const sheet of document.styleSheets) {
                    try {
                        for (const rule of sheet.cssRules || sheet.rules) {
                            if (rule.style) {
                                const selector = rule.selectorText;
                                if (selector && selector.includes(':focus') && element.matches(selector.replace(':focus', ''))) {
                                    const value = rule.style.getPropertyValue(property);
                                    if (value) return value;
                                }
                            }
                        }
                    } catch (e) {
                        // Cross-origin stylesheet, skip
                    }
                }
                return null;
            }

            fields.forEach((field, index) => {
                // Get normal state styles
                const normalOutlineStyle = getComputedStyleValue(field, 'outline-style');
                const normalOutlineWidth = getComputedStyleValue(field, 'outline-width');
                const normalOutlineColor = getComputedStyleValue(field, 'outline-color');
                const normalOutlineOffset = getComputedStyleValue(field, 'outline-offset');
                const normalBorderWidth = getComputedStyleValue(field, 'border-width');
                const normalBorderTopWidth = getComputedStyleValue(field, 'border-top-width');
                const normalBorderRightWidth = getComputedStyleValue(field, 'border-right-width');
                const normalBorderBottomWidth = getComputedStyleValue(field, 'border-bottom-width');
                const normalBorderLeftWidth = getComputedStyleValue(field, 'border-left-width');
                const normalBorderColor = getComputedStyleValue(field, 'border-color');
                const normalBorderTopColor = getComputedStyleValue(field, 'border-top-color');
                const normalBoxShadow = getComputedStyleValue(field, 'box-shadow');
                const backgroundColor = getComputedStyleValue(field, 'background-color');
                const backgroundImage = getComputedStyleValue(field, 'background-image');

                // Simulate focus to get focus styles
                field.focus();

                const focusOutlineStyle = getComputedStyleValue(field, 'outline-style');
                const focusOutlineWidth = getComputedStyleValue(field, 'outline-width');
                const focusOutlineColor = getComputedStyleValue(field, 'outline-color');
                const focusOutlineOffset = getComputedStyleValue(field, 'outline-offset');
                const focusBorderWidth = getComputedStyleValue(field, 'border-width');
                const focusBorderTopWidth = getComputedStyleValue(field, 'border-top-width');
                const focusBorderRightWidth = getComputedStyleValue(field, 'border-right-width');
                const focusBorderBottomWidth = getComputedStyleValue(field, 'border-bottom-width');
                const focusBorderLeftWidth = getComputedStyleValue(field, 'border-left-width');
                const focusBorderColor = getComputedStyleValue(field, 'border-color');
                const focusBorderTopColor = getComputedStyleValue(field, 'border-top-color');
                const focusBoxShadow = getComputedStyleValue(field, 'box-shadow');

                // Remove focus
                field.blur();

                // Get tag and selector info
                const tag = field.tagName.toLowerCase();
                const type = field.type || 'text';
                const id = field.id || '';
                const className = field.className || '';
                const name = field.name || '';

                inputs.push({
                    index,
                    tag,
                    type,
                    id,
                    className,
                    name,
                    // Normal state
                    normalOutlineStyle,
                    normalOutlineWidth,
                    normalOutlineColor,
                    normalOutlineOffset,
                    normalBorderWidth,
                    normalBorderTopWidth,
                    normalBorderRightWidth,
                    normalBorderBottomWidth,
                    normalBorderLeftWidth,
                    normalBorderColor,
                    normalBorderTopColor,
                    normalBoxShadow,
                    // Focus state
                    focusOutlineStyle,
                    focusOutlineWidth,
                    focusOutlineColor,
                    focusOutlineOffset,
                    focusBorderWidth,
                    focusBorderTopWidth,
                    focusBorderRightWidth,
                    focusBorderBottomWidth,
                    focusBorderLeftWidth,
                    focusBorderColor,
                    focusBorderTopColor,
                    focusBoxShadow,
                    // Background
                    backgroundColor,
                    backgroundImage
                });
            });

            return inputs;
        }
    ''')

    if not input_styles:
        return results

    # Process each input field
    for field in input_styles:
        error_code = None
        violation_reason = None

        # Build element identifier
        if field['id']:
            element_id = f"#{field['id']}"
        elif field['className']:
            element_id = f".{field['className'].split()[0]}"
        elif field['name']:
            element_id = f"[name='{field['name']}']"
        else:
            element_id = f"{field['tag']}[{field['index']}]"

        # Determine if there's a gradient background (prevents auto-contrast check)
        has_gradient = 'gradient' in field.get('backgroundImage', '').lower()

        # Check if outline is set to none
        outline_is_none = (
            field['focusOutlineStyle'] == 'none' or
            field['focusOutlineWidth'] == '0px' or
            field['normalOutlineStyle'] == 'none'
        )

        # Parse border widths and colors
        def parse_px(value):
            """Extract pixel value from CSS string"""
            if not value or value == 'auto':
                return 0
            try:
                # Handle em/rem by assuming 16px base
                if 'em' in value:
                    return float(value.replace('em', '').replace('rem', '')) * 16
                return float(value.replace('px', ''))
            except:
                return 0

        def parse_color(color_str):
            """Parse CSS color to RGBA dict"""
            if not color_str:
                return {'r': 0, 'g': 0, 'b': 0, 'a': 1}

            # rgba(r, g, b, a)
            rgba_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', color_str)
            if rgba_match:
                return {
                    'r': int(rgba_match.group(1)),
                    'g': int(rgba_match.group(2)),
                    'b': int(rgba_match.group(3)),
                    'a': float(rgba_match.group(4)) if rgba_match.group(4) else 1.0
                }

            return {'r': 0, 'g': 0, 'b': 0, 'a': 1}

        def get_relative_luminance(color):
            """Calculate relative luminance for contrast ratio"""
            def adjust(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

            r = adjust(color['r'])
            g = adjust(color['g'])
            b = adjust(color['b'])
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        def get_contrast_ratio(color1, color2):
            """Calculate WCAG contrast ratio between two colors"""
            l1 = get_relative_luminance(color1)
            l2 = get_relative_luminance(color2)
            lighter = max(l1, l2)
            darker = min(l1, l2)
            return (lighter + 0.05) / (darker + 0.05)

        # Get border width changes
        normal_border_top = parse_px(field['normalBorderTopWidth'])
        normal_border_right = parse_px(field['normalBorderRightWidth'])
        normal_border_bottom = parse_px(field['normalBorderBottomWidth'])
        normal_border_left = parse_px(field['normalBorderLeftWidth'])

        focus_border_top = parse_px(field['focusBorderTopWidth'])
        focus_border_right = parse_px(field['focusBorderRightWidth'])
        focus_border_bottom = parse_px(field['focusBorderBottomWidth'])
        focus_border_left = parse_px(field['focusBorderLeftWidth'])

        border_top_change = focus_border_top - normal_border_top
        border_right_change = focus_border_right - normal_border_right
        border_bottom_change = focus_border_bottom - normal_border_bottom
        border_left_change = focus_border_left - normal_border_left

        max_border_change = max(border_top_change, border_right_change, border_bottom_change, border_left_change)

        # Check for border color change
        normal_border_color = field['normalBorderColor'] or field['normalBorderTopColor']
        focus_border_color = field['focusBorderColor'] or field['focusBorderTopColor']
        border_color_changed = normal_border_color != focus_border_color

        # Check for box-shadow changes
        normal_box_shadow = field['normalBoxShadow']
        focus_box_shadow = field['focusBoxShadow']
        box_shadow_changed = normal_box_shadow != focus_box_shadow and focus_box_shadow != 'none'

        # Check if box-shadow is single-sided
        is_single_side_shadow = False
        if box_shadow_changed and focus_box_shadow != 'none':
            # Parse box-shadow to check if it's only on one side
            # box-shadow: 0 2px 0 0 blue (bottom only)
            # box-shadow: 2px 0 0 0 blue (right only)
            shadow_parts = focus_box_shadow.split('rgb')
            if shadow_parts:
                shadow_values = shadow_parts[0].strip()
                values = shadow_values.split()
                if len(values) >= 2:
                    h_offset = parse_px(values[0])
                    v_offset = parse_px(values[1])
                    # Single-sided if only one offset is non-zero
                    is_single_side_shadow = (h_offset != 0 and v_offset == 0) or (h_offset == 0 and v_offset != 0)

        # Check for outline
        has_outline = (
            field['focusOutlineStyle'] not in ['none', 'hidden'] and
            field['focusOutlineWidth'] != '0px' and
            parse_px(field['focusOutlineWidth']) > 0
        )

        outline_width = parse_px(field['focusOutlineWidth']) if has_outline else 0

        # DETECTION LOGIC - Priority order: errors before warnings

        # ERROR 1: Single-sided box-shadow (violates Conformance Requirement 5.2.4)
        if is_single_side_shadow:
            error_code = 'ErrInputSingleSideBoxShadow'
            violation_reason = 'Input field uses single-sided box-shadow for focus which does not follow the field shape (violates WCAG Conformance Requirement 5.2.4)'

        # ERROR 2: No visible focus indicator at all
        elif outline_is_none and not border_color_changed and max_border_change <= 0 and not box_shadow_changed:
            error_code = 'ErrInputNoVisibleFocus'
            violation_reason = f'Input field has no visible focus indicator (outline:none, no border change, no box-shadow) - violates WCAG 2.4.7'

        # ERROR 3: Only border color changes (violates 1.4.1 Use of Color)
        elif outline_is_none and border_color_changed and max_border_change <= 0 and not box_shadow_changed:
            error_code = 'ErrInputColorChangeOnly'
            violation_reason = f'Input field focus relies solely on border color change without structural indicator (violates WCAG 1.4.1 Use of Color)'

        # ERROR 4: Border thickens but change is insufficient (< 1px)
        elif max_border_change > 0 and max_border_change < 1.0 and not has_outline and not box_shadow_changed:
            error_code = 'ErrInputBorderChangeInsufficient'
            violation_reason = f'Input field border thickens by only {max_border_change:.2f}px on focus (needs ≥1px to be manifest)'

        # ERROR 5: Outline width insufficient (< 2px for AAA)
        elif has_outline and outline_width < 2.0:
            error_code = 'ErrInputOutlineWidthInsufficient'
            violation_reason = f'Input field focus outline is {outline_width:.2f}px (WCAG 2.4.11 AAA recommends ≥2px)'

        # ERROR 6: Focus contrast insufficient (< 3:1)
        elif not has_gradient:
            bg_color = parse_color(field['backgroundColor'])

            # Check outline contrast if present
            if has_outline:
                outline_color = parse_color(field['focusOutlineColor'])
                if outline_color['a'] < 0.5:
                    error_code = 'WarnInputTransparentFocus'
                    violation_reason = f'Input field focus outline is semi-transparent (alpha={outline_color["a"]:.2f})'
                else:
                    contrast = get_contrast_ratio(outline_color, bg_color)
                    if contrast < 3.0:
                        error_code = 'ErrInputFocusContrastFail'
                        violation_reason = f'Input field focus outline has insufficient contrast ({contrast:.2f}:1, needs ≥3:1 per WCAG 1.4.11)'

            # Check box-shadow contrast if no outline
            elif box_shadow_changed and not error_code:
                # Extract box-shadow color (rough approximation)
                shadow_color_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', focus_box_shadow)
                if shadow_color_match:
                    shadow_color = {
                        'r': int(shadow_color_match.group(1)),
                        'g': int(shadow_color_match.group(2)),
                        'b': int(shadow_color_match.group(3)),
                        'a': 1.0
                    }
                    contrast = get_contrast_ratio(shadow_color, bg_color)
                    if contrast < 3.0:
                        error_code = 'ErrInputFocusContrastFail'
                        violation_reason = f'Input field focus box-shadow has insufficient contrast ({contrast:.2f}:1, needs ≥3:1)'

        # GRADIENT background - cannot verify contrast
        elif has_gradient and not error_code:
            error_code = 'WarnInputFocusGradientBackground'
            violation_reason = 'Input field has gradient background - focus indicator contrast cannot be automatically verified'

        # WARNINGS (best practices)

        # WARNING 1: No separate outline (screen magnifier users may not see comparison)
        if not error_code and not has_outline and (border_color_changed or max_border_change > 0 or box_shadow_changed):
            error_code = 'WarnInputNoBorderOutline'
            violation_reason = 'Input field uses border/box-shadow changes but no separate outline - screen magnifier users may not see other fields to compare visual differences. Best practice: add outline.'

        # WARNING 2: Default browser focus styles
        elif not error_code and has_outline and outline_width == parse_px('1px') and not border_color_changed and not box_shadow_changed:
            # Check if it looks like default browser styling
            if field['focusOutlineColor'] in ['rgb(0, 103, 244)', 'rgb(94, 158, 214)', 'rgb(77, 144, 254)']:  # Common browser defaults
                error_code = 'WarnInputDefaultFocus'
                violation_reason = 'Input field relies on default browser focus styles which vary across browsers/platforms - consider custom focus indicator'

        # Report violation
        if error_code:
            result_type = 'warn' if error_code.startswith('Warn') else 'err'
            result_list = results['warnings'] if result_type == 'warn' else results['errors']

            result_list.append({
                'err': error_code,
                'type': result_type,
                'cat': 'forms',
                'element': field['tag'],
                'selector': element_id,
                'metadata': {
                    'what': violation_reason,
                    'element_type': f"{field['tag']}[type='{field['type']}']",
                    'identifier': element_id
                }
            })

    return results
