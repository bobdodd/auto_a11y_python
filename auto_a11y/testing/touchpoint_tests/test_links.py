"""
Link Focus Indicator Testing

Tests focus indicators on links (both text and image links) for WCAG compliance.
Handles the nuances of link focus, including:
- Text decoration (underline) as a valid focus indicator
- Outline-offset constraints when combined with underline
- Image links requiring visible borders/outlines
- Color change requirements (must be combined with underline, not alone)

WCAG Success Criteria:
- 2.4.7 Focus Visible (Level AA)
- 1.4.1 Use of Color (Level A)
- 1.4.11 Non-text Contrast (Level AA)
- 2.4.11 Focus Appearance (Level AAA)
"""

TEST_DOCUMENTATION = {
    "testName": "Link Focus Indicators",
    "touchpoint": "links",
    "description": "Tests for proper link focus indicators ensuring keyboard users can see which link has focus. Checks for missing focus indicators, color-only changes, insufficient contrast, and proper handling of text vs image links including underline as valid text link indicator.",
    "version": "1.0.0",
    "wcagCriteria": ["2.4.7", "1.4.1", "1.4.11", "2.4.11"],
    "tests": [
        {
            "id": "link-focus-visible",
            "name": "Link Focus Visible",
            "description": "Checks if links have visible focus indicators appropriate for their type (text vs image links)",
            "impact": "high",
            "wcagCriteria": ["2.4.7", "1.4.1"],
        }
    ]
}

async def test_links(page):
    """
    Test links for visible focus indicators

    Args:
        page: Pyppeteer page object

    Returns:
        dict: Test results with errors, warnings, and passes
    """

    results = {
        'errors': [],
        'warnings': [],
        'passes': [],
        'elements_tested': 0,
        'elements_passed': 0,
        'elements_failed': 0
    }

    # Extract link data from page
    link_data = await page.evaluate('''
        () => {
            // Helper to get XPath
            function getXPath(element) {
                if (element.id !== '') {
                    return '//' + element.tagName.toLowerCase() + '[@id="' + element.id + '"]';
                }
                if (element === document.body) {
                    return '//' + element.tagName.toLowerCase();
                }

                let ix = 0;
                const siblings = element.parentNode ? element.parentNode.childNodes : [];
                for (let i = 0; i < siblings.length; i++) {
                    const sibling = siblings[i];
                    if (sibling === element) {
                        const parentPath = element.parentNode ? getXPath(element.parentNode) : '';
                        return parentPath + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    }
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                        ix++;
                    }
                }
                return '';
            }

            // Get all links
            const allLinks = Array.from(document.querySelectorAll('a[href]'));

            // Filter out invisible links
            const visibleLinks = allLinks.filter(link => {
                const style = window.getComputedStyle(link);
                return style.display !== 'none' && style.visibility !== 'hidden';
            });

            return visibleLinks.map(link => {
                const normalStyle = window.getComputedStyle(link);

                // Get font size for em/rem calculations
                const fontSize = parseFloat(normalStyle.fontSize) || 16;
                const rootFontSize = parseFloat(window.getComputedStyle(document.documentElement).fontSize) || 16;

                // Determine if this is an image link
                const hasImage = link.querySelector('img') !== null;
                const hasOnlyImage = hasImage && link.textContent.trim() === '';

                // Get background for contrast calculations
                let bgElement = link.parentElement;
                let backgroundColor = normalStyle.backgroundColor;
                let backgroundImage = normalStyle.backgroundImage;

                while (bgElement && backgroundColor === 'rgba(0, 0, 0, 0)') {
                    backgroundColor = window.getComputedStyle(bgElement).backgroundColor;
                    bgElement = bgElement.parentElement;
                }

                if (backgroundColor === 'rgba(0, 0, 0, 0)') {
                    backgroundColor = 'rgb(255, 255, 255)';
                }

                const fullBackground = normalStyle.background;

                // Try to get focus styles by checking stylesheets
                let focusOutlineStyle = null;
                let focusOutlineWidth = null;
                let focusOutlineColor = null;
                let focusOutlineOffset = null;
                let focusTextDecoration = null;
                let focusTextDecorationLine = null;
                let focusColor = null;
                let focusBackgroundColor = null;
                let focusBorderColor = null;
                let focusBorderWidth = null;
                let focusBoxShadow = null;

                // Check all stylesheets for :focus rules
                const sheets = Array.from(document.styleSheets);
                for (const sheet of sheets) {
                    try {
                        const rules = Array.from(sheet.cssRules || sheet.rules || []);
                        for (const rule of rules) {
                            if (rule.selectorText && rule.selectorText.includes(':focus')) {
                                const selector = rule.selectorText.replace(':focus', '');
                                try {
                                    if (link.matches(selector)) {
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
                                        if (rule.style.textDecoration !== undefined && rule.style.textDecoration !== '') {
                                            focusTextDecoration = rule.style.textDecoration;
                                        }
                                        if (rule.style.textDecorationLine !== undefined && rule.style.textDecorationLine !== '') {
                                            focusTextDecorationLine = rule.style.textDecorationLine;
                                        }
                                        if (rule.style.color !== undefined && rule.style.color !== '') {
                                            focusColor = rule.style.color;
                                        }
                                        if (rule.style.backgroundColor !== undefined && rule.style.backgroundColor !== '') {
                                            focusBackgroundColor = rule.style.backgroundColor;
                                        }
                                        if (rule.style.borderColor !== undefined && rule.style.borderColor !== '') {
                                            focusBorderColor = rule.style.borderColor;
                                        }
                                        if (rule.style.borderWidth !== undefined && rule.style.borderWidth !== '') {
                                            focusBorderWidth = rule.style.borderWidth;
                                        }
                                        if (rule.style.boxShadow !== undefined && rule.style.boxShadow !== '') {
                                            focusBoxShadow = rule.style.boxShadow;
                                        }
                                    }
                                } catch (e) {}
                            }
                        }
                    } catch (e) {}
                }

                return {
                    tagName: link.tagName,
                    text: link.textContent.trim().substring(0, 50),
                    xpath: getXPath(link),
                    html: link.outerHTML.substring(0, 200),
                    hasImage: hasImage,
                    hasOnlyImage: hasOnlyImage,
                    fontSize: fontSize,
                    rootFontSize: rootFontSize,
                    normalTextDecoration: normalStyle.textDecoration,
                    normalTextDecorationLine: normalStyle.textDecorationLine,
                    normalColor: normalStyle.color,
                    normalOutlineStyle: normalStyle.outlineStyle,
                    normalOutlineWidth: normalStyle.outlineWidth,
                    normalOutlineColor: normalStyle.outlineColor,
                    focusOutlineStyle: focusOutlineStyle,
                    focusOutlineWidth: focusOutlineWidth,
                    focusOutlineColor: focusOutlineColor,
                    focusOutlineOffset: focusOutlineOffset,
                    focusTextDecoration: focusTextDecoration,
                    focusTextDecorationLine: focusTextDecorationLine,
                    focusColor: focusColor,
                    focusBackgroundColor: focusBackgroundColor,
                    focusBorderColor: focusBorderColor,
                    focusBorderWidth: focusBorderWidth,
                    focusBoxShadow: focusBoxShadow,
                    backgroundColor: backgroundColor,
                    normalBackgroundColor: normalStyle.backgroundColor,
                    backgroundImage: backgroundImage,
                    fullBackground: fullBackground
                };
            });
        }
    ''')

    if not link_data:
        return results

    results['elements_tested'] = len(link_data)

    # Helper function to parse colors
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
        """Parse CSS pixel values, return float or 0"""
        if not value_str:
            return 0.0
        if value_str == '0' or value_str == 'none':
            return 0.0

        value_str = str(value_str).strip()

        if 'px' in value_str:
            try:
                return float(value_str.replace('px', '').strip())
            except:
                return 0.0

        if 'em' in value_str and 'rem' not in value_str:
            try:
                em_value = float(value_str.replace('em', '').strip())
                return em_value * font_size
            except:
                return 0.0

        if 'rem' in value_str:
            try:
                rem_value = float(value_str.replace('rem', '').strip())
                return rem_value * root_font_size
            except:
                return 0.0

        if value_str == 'thin':
            return 1.0
        if value_str == 'medium':
            return 3.0
        if value_str == 'thick':
            return 5.0

        try:
            return float(value_str)
        except:
            return 0.0

    # Helper to detect gradient backgrounds
    def has_gradient_background(bg_str):
        if not bg_str:
            return False
        return 'gradient' in bg_str.lower()

    # Helper to detect underline on focus
    def has_underline_on_focus(link):
        """Check if link has underline on focus"""
        # Check text-decoration or text-decoration-line
        text_dec = link.get('focusTextDecoration', '')
        text_dec_line = link.get('focusTextDecorationLine', '')

        # Check if focus explicitly sets text-decoration
        if text_dec:
            # If focus state explicitly sets decoration, check if it includes underline
            if 'underline' in text_dec.lower():
                return True
            # If focus explicitly sets 'none', there's no underline even if normal has it
            if 'none' in text_dec.lower():
                return False

        if text_dec_line:
            if 'underline' in text_dec_line.lower():
                return True
            if 'none' in text_dec_line.lower():
                return False

        # If focus state doesn't explicitly set decoration, check normal state
        # (links often have underline by default which persists on focus)
        normal_dec = link.get('normalTextDecoration', '')
        normal_dec_line = link.get('normalTextDecorationLine', '')

        if normal_dec and 'underline' in normal_dec.lower():
            return True
        if normal_dec_line and 'underline' in normal_dec_line.lower():
            return True

        return False

    # Test each link for focus indicators
    for link in link_data:
        tag = link['tagName'].lower()
        error_code = None
        violation_reason = None

        # Get font sizes for em/rem calculations
        font_size = link.get('fontSize', 16)
        root_font_size = link.get('rootFontSize', 16)

        # Check for gradient backgrounds
        link_background = link.get('fullBackground', '') or link.get('normalBackgroundColor', '')
        link_bg_image = link.get('backgroundImage', '')
        has_gradient = has_gradient_background(link_background) or has_gradient_background(link_bg_image)

        # Determine if link is image-only
        is_image_link = link.get('hasOnlyImage', False)

        # Check if this link has custom focus styles
        has_custom_focus = (
            link['focusOutlineStyle'] is not None or
            link['focusOutlineWidth'] is not None or
            link['focusOutlineColor'] is not None or
            link['focusTextDecoration'] is not None or
            link['focusColor'] is not None or
            link['focusBackgroundColor'] is not None or
            link['focusBorderColor'] is not None or
            link['focusBoxShadow'] is not None
        )

        # Check for underline
        has_underline = has_underline_on_focus(link)

        # Warning: Browser default focus (no custom styles)
        if not has_custom_focus:
            error_code = 'WarnLinkDefaultFocus'
            violation_reason = 'Link uses browser default focus styles which may not meet 3:1 contrast on all backgrounds'

        # IMAGE LINKS - Different requirements
        elif is_image_link:
            # Image links must have outline, border, or box-shadow
            has_outline = link['focusOutlineStyle'] and link['focusOutlineStyle'] != 'none'
            has_border = link['focusBorderColor'] or link['focusBorderWidth']
            has_box_shadow = link['focusBoxShadow'] and link['focusBoxShadow'] != 'none'

            if not (has_outline or has_border or has_box_shadow):
                error_code = 'ErrLinkImageNoFocusIndicator'
                violation_reason = 'Image link has no visible focus indicator (must have outline, border, or box-shadow)'

        # TEXT LINKS - Check outline:none
        elif link['focusOutlineStyle'] == 'none':
            # If outline is none, must have underline or box-shadow
            has_box_shadow = link['focusBoxShadow'] and link['focusBoxShadow'] != 'none'

            if has_underline or has_box_shadow:
                # OK - has alternative focus indicator
                pass
            else:
                # Check if only color change
                has_color_change = (
                    link['focusColor'] and
                    link['focusColor'] != link['normalColor']
                ) or link['focusBackgroundColor']

                if has_color_change:
                    error_code = 'ErrLinkColorChangeOnly'
                    violation_reason = 'Link has outline:none with only color change (violates WCAG 1.4.1 Use of Color - must have underline or outline)'
                # else: no error - link has outline:none but this is caught by WarnLinkDefaultFocus if no custom styles

        # TEXT LINKS - If outline is present, check its properties
        elif link['focusOutlineColor'] and link['focusOutlineWidth']:
            outline_width = parse_px(link['focusOutlineWidth'], font_size, root_font_size)
            outline_offset = parse_px(link.get('focusOutlineOffset', '0px'), font_size, root_font_size)

            # PRIORITY 1: Check outline width (ERROR - must be >= 2px if no underline)
            if outline_width > 0 and outline_width < 2.0 and not has_underline:
                error_code = 'ErrLinkOutlineWidthInsufficient'
                violation_reason = f'Link focus outline is too thin ({outline_width:.2f}px, needs ≥2px) and has no underline'

            # PRIORITY 2: Check contrast (ERROR - more critical than offset warning)
            elif not has_gradient:
                outline_color = parse_color(link['focusOutlineColor'])
                bg_color = parse_color(link['backgroundColor'])

                # Check if outline is semi-transparent (< 50% opacity)
                if outline_color['a'] < 0.5:
                    error_code = 'WarnLinkTransparentOutline'
                    violation_reason = f'Link focus outline is semi-transparent (alpha={outline_color["a"]:.2f}) which may not provide sufficient visibility'
                else:
                    contrast = get_contrast_ratio(outline_color, bg_color)
                    if contrast < 3.0:
                        error_code = 'ErrLinkFocusContrastFail'
                        violation_reason = f'Link focus outline has insufficient contrast ({contrast:.2f}:1, needs ≥3:1 per WCAG 1.4.11)'
                    # PRIORITY 3: If contrast is OK, check offset (WARNING)
                    elif has_underline and outline_offset > 1.0:
                        error_code = 'WarnLinkOutlineOffsetTooLarge'
                        violation_reason = f'Link has underline and outline-offset > 1px ({outline_offset:.2f}px) - creates confusing gap between underline and outline'

            # PRIORITY 4: Gradient background (cannot verify contrast automatically)
            elif has_gradient:
                error_code = 'WarnLinkFocusGradientBackground'
                violation_reason = 'Link has gradient background - focus outline contrast cannot be automatically verified'

        # If we found a violation or warning
        if error_code:
            result_type = 'warn' if error_code.startswith('Warn') else 'err'
            result_list = results['warnings'] if result_type == 'warn' else results['errors']

            result_list.append({
                'err': error_code,
                'type': result_type,
                'cat': 'links',
                'element': tag,
                'xpath': link['xpath'],
                'html': link['html'],
                'description': violation_reason,
                'text': link['text']
            })
            results['elements_failed'] += 1
        else:
            results['elements_passed'] += 1

    return results
