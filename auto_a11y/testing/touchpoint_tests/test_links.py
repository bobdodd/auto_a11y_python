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

import asyncio
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Link Focus Indicators",
    "touchpoint": "links",
    "description": "Tests for proper link focus indicators ensuring keyboard users can see which link has focus. Checks for missing focus indicators, color-only changes, insufficient contrast, and proper handling of text vs image links including underline as valid text link indicator.",
    "version": "2.0.0",
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


def parse_color(color_str: str) -> Dict[str, float]:
    """Parse CSS color string to RGBA dict"""
    if not color_str or color_str == 'transparent':
        return {'r': 0, 'g': 0, 'b': 0, 'a': 0}

    rgba_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', color_str)
    if rgba_match:
        return {
            'r': int(rgba_match.group(1)),
            'g': int(rgba_match.group(2)),
            'b': int(rgba_match.group(3)),
            'a': float(rgba_match.group(4)) if rgba_match.group(4) else 1.0
        }

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


def get_luminance(color: Dict[str, float]) -> float:
    """Calculate relative luminance"""
    r_srgb = color['r'] / 255.0
    g_srgb = color['g'] / 255.0
    b_srgb = color['b'] / 255.0

    r = r_srgb / 12.92 if r_srgb <= 0.03928 else ((r_srgb + 0.055) / 1.055) ** 2.4
    g = g_srgb / 12.92 if g_srgb <= 0.03928 else ((g_srgb + 0.055) / 1.055) ** 2.4
    b = b_srgb / 12.92 if b_srgb <= 0.03928 else ((b_srgb + 0.055) / 1.055) ** 2.4

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_contrast_ratio(color1: Dict[str, float], color2: Dict[str, float]) -> float:
    """Calculate contrast ratio between two colors"""
    lum1 = get_luminance(color1)
    lum2 = get_luminance(color2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)


def parse_px(value_str: str, font_size: float = 16, root_font_size: float = 16) -> float:
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


def has_gradient_background(bg_str: str) -> bool:
    """Check if background contains a gradient"""
    if not bg_str:
        return False
    return 'gradient' in bg_str.lower()


def merge_focus_styles(link_data: Dict, css_focus_rules: Optional[Dict]) -> Dict:
    """
    Merge pre-captured CSS focus rules into link data.
    
    Args:
        link_data: Link data from page.evaluate()
        css_focus_rules: Pre-captured focus rules from CSSFocusCapture
        
    Returns:
        Updated link_data with focus styles populated
    """
    if not css_focus_rules or 'rules' not in css_focus_rules:
        return link_data
    
    rules = css_focus_rules.get('rules', {})
    
    element_id = link_data.get('elementId', '')
    class_name = link_data.get('className', '')
    
    selectors_to_check = ['a', '*']
    
    if element_id:
        selectors_to_check.extend([f'#{element_id}', f'a#{element_id}'])
    
    if class_name:
        for cls in class_name.split():
            if cls:
                selectors_to_check.extend([f'.{cls}', f'a.{cls}'])
    
    for selector in selectors_to_check:
        if selector in rules:
            props = rules[selector]
            
            if 'outline-style' in props and link_data.get('focusOutlineStyle') is None:
                link_data['focusOutlineStyle'] = props['outline-style']
            if 'outline-width' in props and link_data.get('focusOutlineWidth') is None:
                link_data['focusOutlineWidth'] = props['outline-width']
            if 'outline-color' in props and link_data.get('focusOutlineColor') is None:
                link_data['focusOutlineColor'] = props['outline-color']
            if 'outline-offset' in props and link_data.get('focusOutlineOffset') is None:
                link_data['focusOutlineOffset'] = props['outline-offset']
            if 'outline' in props:
                outline_val = props['outline']
                if outline_val == 'none' or outline_val == '0':
                    if link_data.get('focusOutlineStyle') is None:
                        link_data['focusOutlineStyle'] = 'none'
                        link_data['focusOutlineWidth'] = '0px'
            if 'text-decoration' in props and link_data.get('focusTextDecoration') is None:
                link_data['focusTextDecoration'] = props['text-decoration']
            if 'text-decoration-line' in props and link_data.get('focusTextDecorationLine') is None:
                link_data['focusTextDecorationLine'] = props['text-decoration-line']
            if 'color' in props and link_data.get('focusColor') is None:
                link_data['focusColor'] = props['color']
            if 'background-color' in props and link_data.get('focusBackgroundColor') is None:
                link_data['focusBackgroundColor'] = props['background-color']
            if 'border-color' in props and link_data.get('focusBorderColor') is None:
                link_data['focusBorderColor'] = props['border-color']
            if 'border-width' in props and link_data.get('focusBorderWidth') is None:
                link_data['focusBorderWidth'] = props['border-width']
            if 'box-shadow' in props and link_data.get('focusBoxShadow') is None:
                link_data['focusBoxShadow'] = props['box-shadow']
    
    return link_data


async def test_links(page) -> Dict[str, Any]:
    """
    Test links for visible focus indicators
    
    Uses pre-captured CSS focus rules when available (from CSSFocusCapture)
    to avoid expensive runtime stylesheet iteration.

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

    from auto_a11y.testing.css_focus_capture import get_css_capture_for_page
    css_capture = get_css_capture_for_page(page)
    css_focus_rules = css_capture.to_dict() if css_capture else None
    
    if css_focus_rules:
        logger.debug(f"Using pre-captured CSS focus rules: {css_focus_rules.get('stylesheet_count', 0)} stylesheets, "
                    f"{len(css_focus_rules.get('selectors', []))} selectors")

    try:
        link_data = await asyncio.wait_for(
            page.evaluate('''
        (cssRules) => {
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

            const allLinks = Array.from(document.querySelectorAll('a[href]'));

            const visibleLinks = allLinks.filter(link => {
                const style = window.getComputedStyle(link);
                return style.display !== 'none' && style.visibility !== 'hidden';
            });

            return visibleLinks.map(link => {
                const normalStyle = window.getComputedStyle(link);

                const fontSize = parseFloat(normalStyle.fontSize) || 16;
                const rootFontSize = parseFloat(window.getComputedStyle(document.documentElement).fontSize) || 16;

                const hasImage = link.querySelector('img') !== null;
                const hasOnlyImage = hasImage && link.textContent.trim() === '';

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

                // Focus styles will be populated from pre-captured CSS (in Python)
                // Only do minimal stylesheet check if no pre-captured rules available
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

                // If no pre-captured CSS rules, do a quick check (limited)
                if (!cssRules || !cssRules.rules) {
                    const sheets = Array.from(document.styleSheets).slice(0, 5);
                    let rulesChecked = 0;
                    sheetLoop:
                    for (const sheet of sheets) {
                        if (rulesChecked >= 100) break;
                        try {
                            const rules = Array.from(sheet.cssRules || sheet.rules || []).slice(0, 50);
                            for (const rule of rules) {
                                rulesChecked++;
                                if (rulesChecked >= 100) break sheetLoop;
                                if (rule.selectorText && rule.selectorText.includes(':focus')) {
                                    const selector = rule.selectorText.replace(/:focus(-visible|-within)?/g, '');
                                    try {
                                        if (link.matches(selector)) {
                                            if (rule.style.outlineStyle) focusOutlineStyle = rule.style.outlineStyle;
                                            if (rule.style.outlineWidth) focusOutlineWidth = rule.style.outlineWidth;
                                            if (rule.style.outlineColor) focusOutlineColor = rule.style.outlineColor;
                                            if (rule.style.outlineOffset) focusOutlineOffset = rule.style.outlineOffset;
                                            if (rule.style.outline === 'none' || rule.style.outline === '0') {
                                                focusOutlineStyle = 'none';
                                                focusOutlineWidth = '0px';
                                            }
                                            if (rule.style.textDecoration) focusTextDecoration = rule.style.textDecoration;
                                            if (rule.style.textDecorationLine) focusTextDecorationLine = rule.style.textDecorationLine;
                                            if (rule.style.color) focusColor = rule.style.color;
                                            if (rule.style.backgroundColor) focusBackgroundColor = rule.style.backgroundColor;
                                            if (rule.style.borderColor) focusBorderColor = rule.style.borderColor;
                                            if (rule.style.borderWidth) focusBorderWidth = rule.style.borderWidth;
                                            if (rule.style.boxShadow) focusBoxShadow = rule.style.boxShadow;
                                        }
                                    } catch (e) {}
                                }
                            }
                        } catch (e) {}
                    }
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
                    fullBackground: fullBackground,
                    target: link.getAttribute('target') || '',
                    ariaLabel: link.getAttribute('aria-label') || '',
                    title: link.getAttribute('title') || '',
                    padding: normalStyle.padding,
                    border: normalStyle.border,
                    borderRadius: normalStyle.borderRadius,
                    borderStyle: normalStyle.borderStyle,
                    display: normalStyle.display,
                    cursor: normalStyle.cursor,
                    hasOnKeyDown: !!link.onkeydown || link.hasAttribute('onkeydown'),
                    hasOnKeyPress: !!link.onkeypress || link.hasAttribute('onkeypress'),
                    hasOnKeyUp: !!link.onkeyup || link.hasAttribute('onkeyup'),
                    onKeyDownAttr: link.getAttribute('onkeydown') || '',
                    onKeyPressAttr: link.getAttribute('onkeypress') || '',
                    onKeyUpAttr: link.getAttribute('onkeyup') || '',
                    elementId: link.id || '',
                    className: link.className || ''
                };
            });
        }
    ''', css_focus_rules),
            timeout=15.0
        )
    except asyncio.TimeoutError:
        logger.warning("Link data extraction timed out")
        return results
    except Exception as e:
        logger.error(f"Error extracting link data: {e}")
        return results

    if not link_data:
        return results

    if css_focus_rules:
        link_data = [merge_focus_styles(link, css_focus_rules) for link in link_data]

    results['elements_tested'] = len(link_data)

    try:
        page_scripts = await asyncio.wait_for(
            page.evaluate('''
                () => {
                    const scripts = [];
                    const scriptElements = document.querySelectorAll('script');
                    const maxScripts = 30;
                    let count = 0;
                    scriptElements.forEach(script => {
                        if (count < maxScripts && script.textContent && script.textContent.length < 30000) {
                            scripts.push(script.textContent);
                            count++;
                        }
                    });
                    return scripts.join('\\n');
                }
            '''),
            timeout=5.0
        )
    except (asyncio.TimeoutError, Exception) as e:
        logger.debug(f"Could not extract page scripts: {e}")
        page_scripts = ""

    def has_space_key_handler(link: Dict) -> bool:
        """Check if link has a Space key handler"""
        on_keydown = link.get('onKeyDownAttr', '')
        on_keypress = link.get('onKeyPressAttr', '')
        on_keyup = link.get('onKeyUpAttr', '')

        space_patterns = [
            r'keyCode\s*===?\s*32',
            r'which\s*===?\s*32',
            r'key\s*===?\s*["\'] ["\']',
            r'charCode\s*===?\s*32'
        ]

        for attr in [on_keydown, on_keypress, on_keyup]:
            if attr:
                for pattern in space_patterns:
                    if re.search(pattern, attr, re.IGNORECASE):
                        return True

        if page_scripts and link.get('elementId'):
            element_id = link.get('elementId')
            patterns = [
                rf'getElementById\(["\']?{re.escape(element_id)}["\']?\)\.addEventListener\s*\(\s*["\']key',
                rf'#{re.escape(element_id)}.*\.on\s*\(\s*["\']key'
            ]
            for pattern in patterns:
                match = re.search(pattern, page_scripts, re.IGNORECASE)
                if match:
                    handler_snippet = page_scripts[match.end():match.end() + 150]
                    for space_pattern in space_patterns:
                        if re.search(space_pattern, handler_snippet, re.IGNORECASE):
                            return True

        return False

    def has_underline_on_focus(link: Dict) -> bool:
        """Check if link has underline on focus"""
        text_dec = link.get('focusTextDecoration', '')
        text_dec_line = link.get('focusTextDecorationLine', '')

        if text_dec:
            if 'underline' in text_dec.lower():
                return True
            if 'none' in text_dec.lower():
                return False

        if text_dec_line:
            if 'underline' in text_dec_line.lower():
                return True
            if 'none' in text_dec_line.lower():
                return False

        normal_dec = link.get('normalTextDecoration', '')
        normal_dec_line = link.get('normalTextDecorationLine', '')

        if normal_dec and 'underline' in normal_dec.lower():
            return True
        if normal_dec_line and 'underline' in normal_dec_line.lower():
            return True

        return False

    for link in link_data:
        tag = link['tagName'].lower()
        error_code = None
        violation_reason = None

        font_size = link.get('fontSize', 16)
        root_font_size = link.get('rootFontSize', 16)

        target = link.get('target', '').lower()
        if target == '_blank':
            link_text = link.get('text', '').lower()
            aria_label = link.get('ariaLabel', '').lower()
            title = link.get('title', '').lower()
            combined_text = f"{link_text} {aria_label} {title}"

            new_window_indicators = [
                'new window', 'new tab',
                'opens in a new window', 'opens in a new tab',
                'opens in new window', 'opens in new tab',
                'external link',
                '(opens in', '(new window', '(new tab'
            ]

            has_warning = any(indicator in combined_text for indicator in new_window_indicators)

            if not has_warning:
                results['errors'].append({
                    'err': 'ErrLinkOpensNewWindowNoWarning',
                    'type': 'err',
                    'cat': 'links',
                    'element': tag,
                    'xpath': link['xpath'],
                    'html': link['html'],
                    'description': 'Link opens in new window (target="_blank") without warning users in link text, aria-label, or title',
                    'text': link.get('text', '')
                })

        link_background = link.get('fullBackground', '') or link.get('normalBackgroundColor', '')
        link_bg_image = link.get('backgroundImage', '')
        has_gradient = has_gradient_background(link_background) or has_gradient_background(link_bg_image)

        is_image_link = link.get('hasOnlyImage', False)

        has_custom_focus = (
            link.get('focusOutlineStyle') is not None or
            link.get('focusOutlineWidth') is not None or
            link.get('focusOutlineColor') is not None or
            link.get('focusTextDecoration') is not None or
            link.get('focusColor') is not None or
            link.get('focusBackgroundColor') is not None or
            link.get('focusBorderColor') is not None or
            link.get('focusBoxShadow') is not None
        )

        has_underline = has_underline_on_focus(link)

        if not has_custom_focus:
            error_code = 'WarnLinkDefaultFocus'
            violation_reason = 'Link uses browser default focus styles which may not meet 3:1 contrast on all backgrounds'

        elif is_image_link:
            has_outline = link.get('focusOutlineStyle') and link.get('focusOutlineStyle') != 'none'
            has_border = link.get('focusBorderColor') or link.get('focusBorderWidth')
            has_box_shadow = link.get('focusBoxShadow') and link.get('focusBoxShadow') != 'none'

            if not (has_outline or has_border or has_box_shadow):
                error_code = 'ErrLinkImageNoFocusIndicator'
                violation_reason = 'Image link has no visible focus indicator (must have outline, border, or box-shadow)'

        elif link.get('focusOutlineStyle') == 'none':
            has_box_shadow = link.get('focusBoxShadow') and link.get('focusBoxShadow') != 'none'

            if has_underline or has_box_shadow:
                pass
            else:
                has_color_change = (
                    link.get('focusColor') and
                    link.get('focusColor') != link.get('normalColor')
                ) or link.get('focusBackgroundColor')

                if has_color_change:
                    error_code = 'ErrLinkColorChangeOnly'
                    violation_reason = 'Link has outline:none with only color change (violates WCAG 1.4.1 Use of Color - must have underline or outline)'

        elif link.get('focusOutlineColor') and link.get('focusOutlineWidth'):
            outline_width = parse_px(link.get('focusOutlineWidth'), font_size, root_font_size)
            outline_offset = parse_px(link.get('focusOutlineOffset', '0px'), font_size, root_font_size)

            if outline_width > 0 and outline_width < 2.0 and not has_underline:
                error_code = 'ErrLinkOutlineWidthInsufficient'
                violation_reason = f'Link focus outline is too thin ({outline_width:.2f}px, needs ≥2px) and has no underline'

            elif not has_gradient:
                outline_color = parse_color(link.get('focusOutlineColor'))
                bg_color = parse_color(link.get('backgroundColor'))

                if outline_color['a'] < 0.5:
                    error_code = 'WarnLinkTransparentOutline'
                    violation_reason = f'Link focus outline is semi-transparent (alpha={outline_color["a"]:.2f}) which may not provide sufficient visibility'
                else:
                    contrast = get_contrast_ratio(outline_color, bg_color)
                    if contrast < 3.0:
                        error_code = 'ErrLinkFocusContrastFail'
                        violation_reason = f'Link focus outline has insufficient contrast ({contrast:.2f}:1, needs ≥3:1 per WCAG 1.4.11)'
                    elif has_underline and outline_offset > 1.0:
                        error_code = 'WarnLinkOutlineOffsetTooLarge'
                        violation_reason = f'Link has underline and outline-offset > 1px ({outline_offset:.2f}px) - creates confusing gap between underline and outline'

            elif has_gradient:
                error_code = 'WarnLinkFocusGradientBackground'
                violation_reason = 'Link has gradient background - focus outline contrast cannot be automatically verified'

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
                'text': link.get('text', '')
            })
            results['elements_failed'] += 1
        else:
            results['elements_passed'] += 1

        looks_like_button = False
        button_indicators = []

        padding = link.get('padding', '')
        border_radius = link.get('borderRadius', '0px')
        background_color = link.get('normalBackgroundColor', '')
        display = link.get('display', 'inline')
        cursor = link.get('cursor', 'auto')

        has_substantial_padding = False
        if padding and padding != '0px':
            px_values = re.findall(r'(\d+(?:\.\d+)?)px', padding)
            if any(float(val) >= 8 for val in px_values):
                has_substantial_padding = True
                button_indicators.append('substantial padding')

        if border_radius and border_radius != '0px':
            try:
                radius_val = float(border_radius.replace('px', '').strip())
                if radius_val >= 3:
                    button_indicators.append('border-radius')
            except:
                pass

        has_solid_background = False
        if background_color and background_color not in ['transparent', 'rgba(0, 0, 0, 0)', 'inherit', 'initial']:
            bg_parsed = parse_color(background_color)
            if bg_parsed['a'] > 0.5:
                has_solid_background = True
                button_indicators.append('solid background color')

        if display in ['block', 'inline-block', 'flex', 'inline-flex']:
            button_indicators.append('block-level display')

        if cursor == 'pointer':
            button_indicators.append('pointer cursor')

        if (has_solid_background and has_substantial_padding) or len(button_indicators) >= 3:
            looks_like_button = True

        if looks_like_button:
            has_space_handler = has_space_key_handler(link)

            results['warnings'].append({
                'err': 'WarnLinkLooksLikeButton',
                'type': 'warn',
                'cat': 'links',
                'element': tag,
                'xpath': link['xpath'],
                'html': link['html'],
                'description': f'Link is styled to look like a button ({", ".join(button_indicators)}) but uses anchor element - consider using <button> for actions or keeping link styling for navigation',
                'text': link.get('text', '')
            })

            if not has_space_handler:
                results['errors'].append({
                    'err': 'ErrLinkButtonMissingSpaceHandler',
                    'type': 'err',
                    'cat': 'links',
                    'element': tag,
                    'xpath': link['xpath'],
                    'html': link['html'],
                    'description': f'Link is styled as a button ({", ".join(button_indicators)}) but lacks Space key handler - keyboard users expect Space to activate button-like elements',
                    'text': link.get('text', '')
                })

    return results
