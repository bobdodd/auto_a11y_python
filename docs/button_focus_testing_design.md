# Button Focus Indicator Testing - Design Documentation

**Created:** 2025-01-11
**Author:** Bob + Claude
**Status:** Implementation In Progress

## Overview

This document describes the comprehensive design for testing button focus indicators in our automated accessibility testing system. The design replaces the single `ErrButtonNoVisibleFocus` error with 9 specific error and warning codes that provide granular feedback to developers about focus indicator accessibility issues.

## Design Rationale

### Why More Specific Error Codes?

The original single error code (`ErrButtonNoVisibleFocus`) was insufficient because:

1. **Lack of Specificity**: Developers couldn't tell what exactly was wrong with their focus indicator
2. **No Guidance**: Generic error messages didn't provide actionable remediation steps
3. **Missing Edge Cases**: Many subtle but important failures weren't detected (thin outlines, low contrast, offset issues)
4. **Educational Value**: More specific codes help educate developers about different aspects of focus accessibility

### Core Testing Principles

Our button focus testing follows these rigorous principles:

1. **Color Alone Fails**: `outline: none` with only color change violates WCAG 1.4.1 Use of Color
2. **Contrast Matters**: All focus indicators must have ≥3:1 contrast per WCAG 1.4.11
3. **Thickness Requirements**: Outlines must be ≥2px wide per WCAG 2.4.11 (Level AAA)
4. **Spacing Requirements**: outline-offset must be ≥2px to prevent outline from being lost in button
5. **Structural Indicators**: box-shadow is acceptable but outline is preferred for clarity
6. **Browser Defaults Are Risky**: Default outlines vary by browser and often fail contrast
7. **Complex Backgrounds Need Manual Review**: Gradients and images cannot be programmatically verified
8. **Z-Index Issues**: Focus indicators can be obscured by other elements

## Error Codes (5 Total)

### 1. ErrButtonOutlineNoneNoBoxShadow
**WCAG:** 2.4.7 Focus Visible, 1.4.1 Use of Color
**Impact:** High
**Detection:** Button has `outline: none` on `:focus` with no `box-shadow`, relying only on color change

**Why It's An Error:**
- Violates WCAG 1.4.1 Use of Color - users with color blindness cannot perceive focus
- 8% of males and 0.5% of females have some form of color vision deficiency
- Monochrome displays show no focus indication at all

**Detection Logic:**
```javascript
// In CSS rules for :focus
if (outlineStyle === 'none' && !hasBoxShadow && hasBackgroundColorChange) {
    error: 'ErrButtonOutlineNoneNoBoxShadow'
}
```

**Example Violation:**
```css
button:focus {
    outline: none;
    background-color: #0066cc; /* Color change only */
}
```

**Correct Implementation:**
```css
button:focus {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
}
```

---

### 2. ErrButtonFocusContrastFail
**WCAG:** 2.4.7 Focus Visible, 1.4.11 Non-text Contrast
**Impact:** High
**Detection:** Focus outline has contrast ratio < 3:1 against button background

**Why It's An Error:**
- WCAG 1.4.11 requires 3:1 minimum contrast for non-text UI components
- Low contrast makes focus invisible to users with low vision
- Fails in bright lighting conditions or on certain displays

**Detection Logic:**
```python
outline_color = parse_color(focusOutlineColor)
bg_color = parse_color(buttonBackgroundColor)
contrast_ratio = calculate_contrast(outline_color, bg_color)

if contrast_ratio < 3.0:
    error: 'ErrButtonFocusContrastFail'
    include_actual_ratio: f'{contrast_ratio:.2f}:1'
```

**Example Violation:**
```css
button {
    background: white;
}
button:focus {
    outline: 2px solid #f0f0f0; /* 1.2:1 contrast - too low */
    outline-offset: 2px;
}
```

**Correct Implementation:**
```css
button {
    background: white;
}
button:focus {
    outline: 2px solid #0066cc; /* High contrast */
    outline-offset: 2px;
}
```

---

### 3. ErrButtonOutlineWidthInsufficient
**WCAG:** 2.4.7 Focus Visible, 2.4.11 Focus Appearance
**Impact:** High
**Detection:** outline-width < 2px

**Why It's An Error:**
- WCAG 2.4.11 Level AAA requires ≥2 CSS pixels thickness
- Thin outlines are difficult to see, especially on high-DPI displays
- Users with low vision may miss thin focus indicators entirely

**Detection Logic:**
```python
outline_width_px = parse_px(focusOutlineWidth)

if outline_width_px < 2.0:
    error: 'ErrButtonOutlineWidthInsufficient'
    include_actual_width: f'{outline_width_px}px'
```

**Example Violation:**
```css
button:focus {
    outline: 1px solid #0066cc; /* Too thin */
    outline-offset: 2px;
}
```

**Correct Implementation:**
```css
button:focus {
    outline: 2px solid #0066cc; /* Or 3px for better visibility */
    outline-offset: 2px;
}
```

---

### 4. ErrButtonOutlineOffsetInsufficient
**WCAG:** 2.4.7 Focus Visible
**Impact:** High
**Detection:** outline-offset < 2px (when outline-width >= 2px)

**Why It's An Error:**
- Outline too close to button edge gets lost, especially on colored/image buttons
- Blends with button border making it invisible
- Particularly problematic with rounded corners or gradients

**Detection Logic:**
```python
outline_offset_px = parse_px(focusOutlineOffset) or 0

if outline_width_px >= 2.0 and outline_offset_px < 2.0:
    error: 'ErrButtonOutlineOffsetInsufficient'
    include_actual_offset: f'{outline_offset_px}px'
```

**Example Violation:**
```css
button:focus {
    outline: 2px solid #0066cc;
    outline-offset: 0px; /* Too close - gets lost in button */
}
```

**Correct Implementation:**
```css
button:focus {
    outline: 2px solid #0066cc;
    outline-offset: 2px; /* Clear separation */
}
```

---

### 5. ErrButtonFocusObscured
**WCAG:** 2.4.7 Focus Visible
**Impact:** High
**Detection:** Focus indicator partially/fully hidden by other elements (z-index)

**Why It's An Error:**
- Completely breaks keyboard navigation if focus is invisible
- Common with sticky headers, overlays, modals
- Results from improperly managed z-index stacking contexts

**Detection Logic:**
```javascript
// This is complex and may require DOM inspection
// Check if button has lower z-index than overlapping elements
// Or note for manual testing if complex stacking detected
```

**Example Violation:**
```css
button:focus {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
    z-index: 1;
}
.header {
    z-index: 100; /* Covers button outline */
    position: sticky;
}
```

**Correct Implementation:**
```css
button:focus {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
    position: relative;
    z-index: 101; /* Above header */
}
```

## Warning Codes (4 Total)

Warnings indicate suboptimal implementations that may cause accessibility issues but don't completely fail WCAG requirements.

### 6. WarnButtonOutlineNoneWithBoxShadow
**WCAG:** 2.4.7 Focus Visible
**Impact:** Medium
**Detection:** `outline: none` with `box-shadow` present

**Why It's A Warning:**
- box-shadow is acceptable but not optimal
- May not be visible on all sides depending on shadow direction
- Harder to see in certain contexts
- Outline on all 4 sides is clearer

**Preferred Solution:** Use outline instead

---

### 7. WarnButtonDefaultFocus
**WCAG:** 2.4.7 Focus Visible
**Impact:** Medium
**Detection:** No custom `:focus` styles (browser default)

**Why It's A Warning:**
- Browser defaults vary significantly (Chrome: thin blue, Firefox: dotted, Safari: glow)
- May not meet 3:1 contrast on all backgrounds
- Inconsistent user experience across browsers
- Often too thin or too light

**Preferred Solution:** Define explicit focus styles

---

### 8. WarnButtonFocusGradientBackground
**WCAG:** 2.4.7 Focus Visible, 1.4.11 Non-text Contrast
**Impact:** Medium
**Detection:** Button has `linear-gradient` or `radial-gradient` in background

**Why It's A Warning:**
- Cannot programmatically verify contrast against varying gradient colors
- Outline may meet 3:1 at some points but fail at others
- Requires manual verification

**Required Action:** Manual contrast checking against lightest AND darkest gradient colors

---

### 9. WarnButtonFocusImageBackground
**WCAG:** 2.4.7 Focus Visible, 1.4.11 Non-text Contrast
**Impact:** Medium
**Detection:** Button has `background-image` or `url()` in background

**Why It's A Warning:**
- Cannot programmatically verify contrast against image
- Outline may be invisible against parts of image
- Particularly problematic with photos or complex patterns

**Required Action:** Manual testing against all parts of image, preferably avoid images on focusable buttons

## Implementation Details

### Detection Order

Tests must be performed in this order to avoid false positives:

1. **Detect browser default** (no custom :focus styles) → WarnButtonDefaultFocus
2. **Detect gradient background** → WarnButtonFocusGradientBackground (skip contrast calc)
3. **Detect image background** → WarnButtonFocusImageBackground (skip contrast calc)
4. **Check outline: none**
   - Has box-shadow? → WarnButtonOutlineNoneWithBoxShadow
   - No box-shadow? → ErrButtonOutlineNoneNoBoxShadow
5. **Check outline-width** → ErrButtonOutlineWidthInsufficient if < 2px
6. **Check outline-offset** → ErrButtonOutlineOffsetInsufficient if < 2px (when width >= 2px)
7. **Calculate contrast** → ErrButtonFocusContrastFail if < 3:1 (solid colors only)
8. **Check z-index** → ErrButtonFocusObscured (if detectable)

### CSS Parsing Requirements

The test must parse and extract:
- `outline`, `outline-style`, `outline-width`, `outline-color`, `outline-offset`
- `box-shadow`
- `background`, `background-color`, `background-image`
- `z-index` and stacking context

### Contrast Calculation

Use WCAG formula for relative luminance:
```python
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
```

## Fixture Design

### Fixture Naming Convention
```
[ErrorCode]_[001]_[violations|correct]_[description].html
```

Examples:
- `ErrButtonOutlineNoneNoBoxShadow_001_violations_color_only.html`
- `ErrButtonOutlineNoneNoBoxShadow_002_correct_with_outline.html`
- `ErrButtonFocusContrastFail_001_violations_low_contrast.html`

### Fixture Structure

Each fixture must include:
1. **Test metadata** (JSON in script tag)
   - `id`: Unique fixture ID
   - `issueId`: Error/warning code
   - `expectedViolationCount`: Number of expected violations
   - `expectedPassCount`: Number of expected passes
   - `description`: What the fixture tests
   - `wcag`: WCAG criteria
   - `impact`: Impact level

2. **Multiple test cases** in single fixture where logical
3. **Data attributes** for validation:
   - `data-expected-violation="true"`
   - `data-violation-id="[code]"`
   - `data-violation-reason="[reason]"`
   - OR `data-expected-pass="true"`

### Example Fixture Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ErrButtonOutlineNoneNoBoxShadow - Violations</title>
    <script type="application/json" id="test-metadata">
{
    "id": "ErrButtonOutlineNoneNoBoxShadow_001_violations_color_only",
    "issueId": "ErrButtonOutlineNoneNoBoxShadow",
    "expectedViolationCount": 2,
    "expectedPassCount": 0,
    "description": "Buttons with outline:none and only color change",
    "wcag": "2.4.7, 1.4.1",
    "impact": "High"
}
    </script>
    <style>
        .color-only-focus:focus {
            outline: none;
            background-color: #0066cc;
        }
    </style>
</head>
<body>
    <h1>Test: outline:none with Color Change Only</h1>

    <button class="color-only-focus"
            data-expected-violation="true"
            data-violation-id="ErrButtonOutlineNoneNoBoxShadow"
            data-violation-reason="Outline removed with only color change">
        Submit
    </button>
</body>
</html>
```

## Test Implementation Architecture

### File: test_buttons.py

**Structure:**
1. Extract button data via page.evaluate() (JavaScript)
2. Parse CSS :focus rules for each button
3. Detect background type (solid/gradient/image)
4. Parse outline properties (width, offset, color, style)
5. Detect box-shadow presence
6. Calculate contrast (if solid background)
7. Apply detection logic in order
8. Return detailed error/warning objects

**Key Functions:**
- `parse_css_unit(value)` - Parse px/em/rem to pixels
- `parse_color(color_string)` - RGB/hex to dict
- `has_gradient_background(bg_string)` - Detect gradients
- `has_image_background(bg_string)` - Detect images
- `get_focus_styles(element)` - Extract :focus rules
- `is_browser_default_focus(styles)` - Detect no custom styles
- `calculate_contrast_ratio(color1, color2)` - WCAG formula

## Testing Strategy

### Unit Testing
- Test contrast calculation with known color pairs
- Test CSS unit parsing (px, em, rem)
- Test color parsing (rgb, rgba, hex, named)
- Test gradient/image detection

### Integration Testing
- Run all fixtures through test_buttons.py
- Verify expected violation/pass counts match
- Ensure no false positives
- Ensure no false negatives

### Manual Verification
For warnings that cannot be fully automated:
- WarnButtonFocusGradientBackground: Manual contrast check
- WarnButtonFocusImageBackground: Manual visibility check
- ErrButtonFocusObscured: May need manual z-index verification

## Future Enhancements

### Potential Additions
1. **:focus-visible detection** - Modern best practice
2. **Animation testing** - Animated focus transitions
3. **High contrast mode** - Test in Windows high contrast
4. **Reduced motion** - Test with prefers-reduced-motion
5. **Touch target size** - Ensure buttons are large enough (44x44px minimum)

### Research Areas
1. Better z-index obscuring detection algorithms
2. Automated testing against image backgrounds using computer vision
3. Gradient contrast verification using sampling techniques

## References

### WCAG Success Criteria
- **2.4.7 Focus Visible (Level AA)** - Any keyboard operable interface has a visible focus indicator
- **1.4.1 Use of Color (Level A)** - Color is not used as the only visual means of conveying information
- **1.4.11 Non-text Contrast (Level AA)** - Visual presentation has contrast ratio of at least 3:1 against adjacent colors
- **2.4.11 Focus Appearance (Level AAA)** - Keyboard focus indicator has minimum area and contrast

### External Resources
- [WCAG 2.4.7 Understanding Doc](https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html)
- [WCAG 1.4.1 Understanding Doc](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html)
- [WCAG 1.4.11 Understanding Doc](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Color Blindness Statistics](https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness)

## Change Log

**2025-01-11** - Initial design document created
- Defined 5 error codes and 4 warning codes
- Documented detection logic and implementation requirements
- Created fixture design guidelines
- Established testing strategy

---

**Next Steps:**
1. Create comprehensive fixtures (18 files minimum)
2. Implement test_buttons.py with detection logic
3. Validate all fixtures pass/fail as expected
4. Document any edge cases discovered during testing
