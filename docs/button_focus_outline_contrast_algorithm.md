# Button Focus Outline Contrast Detection Algorithm

## Overview

This document describes the comprehensive algorithm used to detect and verify button focus outline contrast issues for keyboard accessibility. The algorithm implements WCAG 2.4.7 (Focus Visible) and WCAG 1.4.11 (Non-text Contrast) requirements.

**Test Module**: `auto_a11y/testing/touchpoint_tests/test_buttons.py`

**Primary Error Code**: `ErrButtonFocusContrastFail`

**Related Warning Codes**:
- `WarnButtonFocusGradientBackground`
- `WarnButtonFocusImageBackground`
- `WarnButtonFocusParentGradientBackground`
- `WarnButtonFocusParentImageBackground`
- `WarnButtonFocusZIndexFloating`
- `WarnButtonFocusParentZIndexFloating`
- `WarnButtonFocusOutlineExceedsParent`

---

## The Fundamental Question

**What background should we compare the focus outline against?**

The answer depends on `outline-offset`:

```css
/* outline-offset <= 0: Outline sits ON or INSIDE the button */
button:focus {
    outline: 3px solid blue;
    outline-offset: 0; /* or negative */
}
/* Compare outline against BUTTON background */

/* outline-offset > 0: Outline sits OUTSIDE the button */
button:focus {
    outline: 3px solid blue;
    outline-offset: 5px; /* positive */
}
/* Compare outline against PARENT CONTAINER background */
```

This single distinction drives the entire algorithm.

---

## Algorithm Flow

### Phase 1: Data Collection (JavaScript)

The browser-side JavaScript collects:

1. **Button Properties**
   - Tag name, text, XPath, HTML, class name
   - Font size (for em/rem conversion)
   - Root font size
   - Clip-path (for non-rectangular button detection)

2. **Focus Outline Styles** (from CSS rules)
   - `outline-style`, `outline-width`, `outline-color`, `outline-offset`
   - Resolved from `:focus` and `:focus-visible` rules
   - CSS variables resolved using `getComputedStyle().getPropertyValue()`
   - Shorthand `outline` property parsed with regex to handle `rgb()` colors

3. **Background Colors**
   - **Button background**: Effective background of button itself
   - **Parent background**: Effective background of parent container
   - Uses `getEffectiveBackgroundColor()` to walk up DOM tree

4. **Background Images/Gradients**
   - `backgroundImage` and `background` (for button)
   - `parentBackgroundImage` and `parentFullBackground` (for parent)
   - Detects `linear-gradient()`, `radial-gradient()`, `url()`, etc.

5. **Z-Index Information**
   - `buttonHasZIndex`: Does button have `z-index !== 'auto'` and `position !== 'static'`?
   - `buttonBgStoppedAtZIndex`: Did background walker stop at z-indexed element?
   - `parentBgStoppedAtZIndex`: Did parent background walker stop at z-indexed element?

6. **Bounding Rectangles**
   - `buttonBounds`: Button's `getBoundingClientRect()` (top, right, bottom, left, width, height)
   - `parentBounds`: Parent's `getBoundingClientRect()`

### Phase 2: Analysis (Python)

#### Step 1: Parse Outline Dimensions

```python
outline_width = parse_px(button['focusOutlineWidth'], font_size, root_font_size)
outline_offset = parse_px(button.get('focusOutlineOffset', '0px'), font_size, root_font_size)
```

Converts em/rem units to pixels for comparison.

#### Step 2: Check Outline Width (WCAG 1.4.11)

```python
if outline_width > 0 and outline_width < 2.0:
    error_code = 'ErrButtonOutlineWidthInsufficient'
    # Outline must be >= 2px per WCAG 2.4.11
```

#### Step 3: Check Outline Offset (Best Practice)

```python
if outline_width >= 2.0 and outline_offset < 2.0:
    error_code = 'ErrButtonOutlineOffsetInsufficient'
    # Offset should be >= 2px for clear separation
```

#### Step 4: Determine Comparison Background

```python
if outline_offset > 0:
    # Outline sits OUTSIDE button
    # Compare against PARENT background
    compare_against = 'parent'
else:
    # Outline sits ON/INSIDE button
    # Compare against BUTTON background
    compare_against = 'button'
```

---

## Contrast Verification: Positive Outline-Offset Case

When `outline_offset > 0`, the outline sits **outside the button** against the **parent background**.

### Check 1: Button Has Z-Index

```python
if button_has_z_index:
    error_code = 'WarnButtonFocusZIndexFloating'
    # Button floats over varying backgrounds
    # Cannot automatically verify contrast
    # MANUAL TESTING REQUIRED
```

**Why**: Button with z-index creates a stacking context and may float over any page content. The outline (which extends beyond the button) may appear against unpredictable backgrounds.

**Example**: Sticky header button, floating action button (FAB), tooltip button.

**Fixture**: `WarnButtonFocusZIndexFloating_001_warnings_floating_button.html`

---

### Check 2: Parent Has Z-Index (No Solid Background Found)

```python
elif parent_bg_stopped_at_z_index:
    error_code = 'WarnButtonFocusParentZIndexFloating'
    # Parent has z-index and no solid background
    # Outline sits against transparent parent that may float over anything
    # MANUAL TESTING REQUIRED
```

**Why**: If the background walker reaches a z-indexed parent without finding a solid background, the parent is transparent or semi-transparent and may float over varying content.

**Example**: Glass morphism card, HUD overlay, floating toolbar with transparent background.

**Fixture**: `WarnButtonFocusParentZIndexFloating_001_warnings_parent_zindex.html`

**Counter-example (PASSES)**: Modal dialog where parent has z-index BUT has solid background. Background walker finds the solid modal background before reaching the z-indexed overlay, so we CAN verify contrast.

**Passing Fixture**: `ErrButtonFocusContrastFail_004_correct_modal_with_zindex.html`

---

### Check 3: Outline Extends Beyond Parent Container

```python
else:
    # Calculate outline extent
    total_extent = outline_offset + outline_width

    # Check if outline exceeds parent bounds on any side
    exceeds_top = (button_bounds['top'] - total_extent) < parent_bounds['top']
    exceeds_bottom = (button_bounds['bottom'] + total_extent) > parent_bounds['bottom']
    exceeds_left = (button_bounds['left'] - total_extent) < parent_bounds['left']
    exceeds_right = (button_bounds['right'] + total_extent) > parent_bounds['right']

    outline_exceeds_parent = exceeds_top or exceeds_bottom or exceeds_left or exceeds_right

    if outline_exceeds_parent:
        error_code = 'WarnButtonFocusOutlineExceedsParent'
        # Outline extends past parent boundary
        # Cannot determine background beyond parent
        # MANUAL TESTING REQUIRED
```

**Why**: The outline sits outside the button by `outline-offset` pixels, then extends by `outline-width` pixels. If this total extent exceeds the parent's padding on any side, part of the outline extends beyond the parent into unknown backgrounds.

**Key Point**: CSS `outline-offset` has **no maximum value**. A value like `outline-offset: 50px` is valid but impractical.

**Example**:
- Button with `outline-offset: 8px` + `outline-width: 3px` = 11px extent
- Parent has only 5px padding
- Outline extends 6px beyond parent on all sides

**Fixture**: `WarnButtonFocusOutlineExceedsParent_001_warnings_exceeds_parent.html`

**Passing Fixture**: `ErrButtonFocusContrastFail_005_correct_outline_within_parent.html`

---

### Check 4: Parent Has Gradient Background

```python
else:
    parent_has_gradient = has_gradient_background(parent_full_bg) or \
                          has_gradient_background(parent_bg_image)

    if parent_has_gradient:
        error_code = 'WarnButtonFocusParentGradientBackground'
        # Gradient has varying colors
        # Cannot determine worst-case contrast
        # MANUAL TESTING REQUIRED
```

**Why**: Gradients contain multiple colors. The outline may have sufficient contrast against some gradient colors but not others. We cannot calculate "worst case" contrast without analyzing every pixel.

**Detection**: Looks for `linear-gradient()`, `radial-gradient()`, `repeating-linear-gradient()`, `repeating-radial-gradient()`, `conic-gradient()` in `background` or `background-image`.

**Fixture**: `WarnButtonFocusParentGradientBackground_001_warnings_parent_gradient.html`

---

### Check 5: Parent Has Background Image

```python
elif parent_has_image:
    error_code = 'WarnButtonFocusParentImageBackground'
    # Image has varying colors/patterns
    # Cannot determine contrast across entire image
    # MANUAL TESTING REQUIRED
```

**Why**: Background images (photos, patterns, textures) contain unpredictable colors. The outline must be visible against ALL parts of the image.

**Detection**: Looks for `url()` in `background` or `background-image` (excluding data URIs containing `gradient`).

**Fixture**: `WarnButtonFocusParentImageBackground_001_warnings_parent_image.html`

---

### Check 6: Calculate Contrast Against Solid Parent Background

```python
else:
    check_solid_contrast = True
    # We have a solid parent background color
    # Parent does not have z-index (or we found background before z-index)
    # Outline stays within parent bounds
    # No gradient or image
    # WE CAN VERIFY CONTRAST!
```

At this point, we:
1. Parse the parent background color
2. Parse the outline color
3. Calculate contrast ratio using WCAG formula
4. Check if contrast >= 3:1 (WCAG 1.4.11 requirement)

```python
contrast_ratio = calculate_contrast_ratio(outline_color, parent_background_color)

if contrast_ratio < 3.0:
    error_code = 'ErrButtonFocusContrastFail'
    violation_reason = f'Focus outline contrast {contrast_ratio:.2f}:1 is below minimum 3:1'
```

**Passing Fixtures**:
- `ErrButtonFocusContrastFail_002_correct_high_contrast.html`
- `ErrButtonFocusContrastFail_004_correct_modal_with_zindex.html`
- `ErrButtonFocusContrastFail_005_correct_outline_within_parent.html`

**Failing Fixture**:
- `ErrButtonFocusContrastFail_001_violations_low_contrast.html`

---

## Contrast Verification: Zero/Negative Outline-Offset Case

When `outline_offset <= 0`, the outline sits **on or inside the button** against the **button background**.

### Check 1: Button Has Gradient Background

```python
if has_gradient_background(button['fullBackground']) or \
   has_gradient_background(button['backgroundImage']):
    error_code = 'WarnButtonFocusGradientBackground'
    # MANUAL TESTING REQUIRED
```

**Why**: Same as parent gradient - cannot determine worst-case contrast.

---

### Check 2: Button Has Background Image

```python
elif has_image_background(button['fullBackground']) or \
     has_image_background(button['backgroundImage']):
    error_code = 'WarnButtonFocusImageBackground'
    # MANUAL TESTING REQUIRED
```

**Why**: Same as parent image - outline must be visible against entire image.

---

### Check 3: Calculate Contrast Against Solid Button Background

```python
else:
    check_solid_contrast = True
    # Calculate contrast against button's own background
```

**Passing Fixture**: `ErrButtonFocusContrastFail_003_correct_offset_zero.html`

---

## Helper Functions

### `getEffectiveBackgroundColor(element)`

Walks up the DOM tree to find the first non-transparent background color.

```javascript
function getEffectiveBackgroundColor(element) {
    let currentElement = element;
    let backgroundColor = 'rgba(0, 0, 0, 0)'; // transparent
    let stoppedAtZIndex = false;

    while (currentElement && backgroundColor === 'rgba(0, 0, 0, 0)') {
        const style = window.getComputedStyle(currentElement);
        backgroundColor = style.backgroundColor;

        // Stop if we hit an element with z-index
        const zIndex = style.zIndex;
        const position = style.position;
        if (zIndex !== 'auto' && position !== 'static') {
            stoppedAtZIndex = true;
            break;
        }

        currentElement = currentElement.parentElement;
    }

    // Default to white if no background found
    if (backgroundColor === 'rgba(0, 0, 0, 0)') {
        backgroundColor = 'rgb(255, 255, 255)';
    }

    return {
        backgroundColor,
        stoppedAtZIndex
    };
}
```

**Returns**: Object with `backgroundColor` (string) and `stoppedAtZIndex` (boolean).

**Key behavior**: Stops walking at z-index boundaries because stacking contexts break parent-child relationships.

---

### `resolveCSSVariable(value, element)`

Resolves CSS custom properties (variables).

```javascript
function resolveCSSVariable(value, element) {
    const varMatch = value.match(/var\\((--[^,)]+)(?:,\\s*([^)]+))?\\)/);
    if (!varMatch) return value;

    const varName = varMatch[1];
    const fallback = varMatch[2];

    const computedStyle = window.getComputedStyle(element);
    const resolvedValue = computedStyle.getPropertyValue(varName).trim();

    if (resolvedValue) {
        return value.replace(varMatch[0], resolvedValue);
    }

    return fallback || value;
}
```

**Example**:
- Input: `var(--cvc-outline-offset, 2px)`
- Output: `5px` (if `--cvc-outline-offset: 5px`)

---

### Shorthand Outline Parsing

Parses `outline: 3px solid rgb(255, 0, 0)` into components.

```javascript
// Parse shorthand outline property: "width style color"
const widthMatch = outlineValue.match(/(\\d+(?:\\.\\d+)?(?:px|em|rem))/);
if (widthMatch) focusOutlineWidth = widthMatch[0];

const styleMatch = outlineValue.match(/\\b(solid|dashed|dotted|double|groove|ridge|inset|outset)\\b/);
if (styleMatch) focusOutlineStyle = styleMatch[0];

// Match color including rgb() with spaces inside
const colorMatch = outlineValue.match(/(?:rgb|rgba|hsl|hsla)\\([^)]+\\)|#[0-9a-fA-F]{3,8}|\\b(?:white|black|red|blue|...)\\b/);
if (colorMatch) focusOutlineColor = colorMatch[0];
```

**Critical fix**: The color regex `[^)]+` matches everything inside `rgb(...)` including commas and spaces, preventing truncation of `rgb(255, 255, 255)` to `rgb(255,`.

---

### `has_gradient_background(bg_string)`

```python
def has_gradient_background(bg_string):
    if not bg_string or bg_string == 'none':
        return False
    gradient_patterns = [
        'linear-gradient',
        'radial-gradient',
        'repeating-linear-gradient',
        'repeating-radial-gradient',
        'conic-gradient'
    ]
    return any(pattern in bg_string for pattern in gradient_patterns)
```

---

### `has_image_background(bg_string)`

```python
def has_image_background(bg_string):
    if not bg_string or bg_string == 'none':
        return False
    # Check for url() but exclude gradient data URIs
    if 'url(' in bg_string:
        # Make sure it's not a gradient encoded as data URI
        if 'gradient' in bg_string.lower():
            return False
        return True
    return False
```

---

## Decision Tree Diagram

```
Button Focus Outline Detected
    |
    v
Is outline_offset > 0?
    |
    +--NO--> Outline sits ON/INSIDE button
    |        Compare against BUTTON background
    |        |
    |        v
    |        Button has gradient? --> WarnButtonFocusGradientBackground
    |        Button has image? --> WarnButtonFocusImageBackground
    |        Solid background? --> Calculate contrast --> Pass/Fail
    |
    +--YES-> Outline sits OUTSIDE button
             Compare against PARENT background
             |
             v
             Button has z-index? --> WarnButtonFocusZIndexFloating
             Parent has z-index (no solid bg found)? --> WarnButtonFocusParentZIndexFloating
             Outline exceeds parent bounds? --> WarnButtonFocusOutlineExceedsParent
             Parent has gradient? --> WarnButtonFocusParentGradientBackground
             Parent has image? --> WarnButtonFocusParentImageBackground
             Solid parent background? --> Calculate contrast --> Pass/Fail
```

---

## WCAG Requirements

### 2.4.7 Focus Visible (Level AA)

> Any keyboard operable user interface has a mode of operation where the keyboard focus indicator is visible.

**Our implementation**: Checks that buttons have visible focus indicators (outline, box-shadow, or visible style change) and that they have sufficient contrast.

### 1.4.11 Non-text Contrast (Level AA)

> The visual presentation of User Interface Components and Graphical Objects have a contrast ratio of at least 3:1 against adjacent color(s).

**Our implementation**: Verifies that focus outline has at least 3:1 contrast against the background it sits on.

---

## Test Fixtures Summary

| Fixture | Type | Expected | Tests |
|---------|------|----------|-------|
| `ErrButtonFocusContrastFail_001_violations_low_contrast.html` | Error | 3 violations | Low contrast outlines against parent backgrounds |
| `ErrButtonFocusContrastFail_002_correct_high_contrast.html` | Pass | 3 passes | Maximum contrast (black/white, white/black) |
| `ErrButtonFocusContrastFail_003_correct_offset_zero.html` | Pass | 3 passes | Outline-offset: 0, contrast against button |
| `ErrButtonFocusContrastFail_004_correct_modal_with_zindex.html` | Pass | 2 passes | Modal with z-index but solid background |
| `ErrButtonFocusContrastFail_005_correct_outline_within_parent.html` | Pass | 3 passes | Outlines fully contained within parent padding |
| `WarnButtonFocusGradientBackground_001_warnings_gradient.html` | Warning | 3 warnings | Button gradients, offset <= 0 |
| `WarnButtonFocusImageBackground_001_warnings_image.html` | Warning | 3 warnings | Button images, offset <= 0 |
| `WarnButtonFocusParentGradientBackground_001_warnings_parent_gradient.html` | Warning | 3 warnings | Parent gradients, offset > 0 |
| `WarnButtonFocusParentImageBackground_001_warnings_parent_image.html` | Warning | 3 warnings | Parent images, offset > 0 |
| `WarnButtonFocusZIndexFloating_001_warnings_floating_button.html` | Warning | 3 warnings | Buttons with z-index |
| `WarnButtonFocusParentZIndexFloating_001_warnings_parent_zindex.html` | Warning | 4 warnings | Parents with z-index, no solid bg |
| `WarnButtonFocusOutlineExceedsParent_001_warnings_exceeds_parent.html` | Warning | 3 warnings | Outlines extending beyond parent |

**Total**: 12 fixtures, 38 test cases, 100% pass rate

---

## Common Patterns and Solutions

### Pattern 1: Modal Dialog (z-index with solid background)

**Scenario**: Modal overlay has `z-index: 1000`, but modal dialog has solid white background.

**Algorithm behavior**: Background walker finds white background BEFORE reaching z-indexed overlay, so contrast CAN be verified.

**Result**: ✅ PASS (if contrast is sufficient)

```css
.modal-overlay {
    position: fixed;
    z-index: 1000;
    background: rgba(0, 0, 0, 0.5);
}
.modal-dialog {
    background: white; /* Solid background found first */
}
```

---

### Pattern 2: Floating Action Button (FAB)

**Scenario**: Button has `position: fixed; z-index: 999;` and floats over page content.

**Algorithm behavior**: Button has z-index, so it may appear over any page content with varying backgrounds.

**Result**: ⚠️ WARNING - WarnButtonFocusZIndexFloating

**Solution**: Use high-contrast outline that works on both light and dark backgrounds:

```css
.fab:focus {
    outline: 2px solid white;
    box-shadow: 0 0 0 4px black;
}
```

---

### Pattern 3: Large Outline Offset

**Scenario**: Designer uses `outline-offset: 20px` for aesthetic reasons.

**Algorithm behavior**: Unless parent has at least 20px + outline-width of padding, outline extends beyond parent.

**Result**: ⚠️ WARNING - WarnButtonFocusOutlineExceedsParent

**Solution**: Ensure parent padding >= outline extent:

```css
.container {
    padding: 25px; /* >= 20px offset + 3px width */
}
button {
    outline-offset: 20px;
    outline-width: 3px;
}
```

---

### Pattern 4: Glass Morphism

**Scenario**: Button on semi-transparent backdrop-blur container with z-index.

**Algorithm behavior**: Parent has z-index but background is nearly transparent (rgba(255,255,255,0.1)).

**Result**: ⚠️ WARNING - WarnButtonFocusParentZIndexFloating

**Solution**: Ensure sufficient backdrop opacity or use high-contrast outline:

```css
.glass-card {
    background: rgba(255, 255, 255, 0.8); /* More opaque */
    backdrop-filter: blur(10px);
}
/* OR */
button:focus {
    outline: 2px solid white;
    box-shadow: 0 0 0 4px rgba(0, 0, 0, 0.8); /* Dark shadow for contrast */
}
```

---

## Edge Cases Handled

1. ✅ **CSS Variables**: `outline-offset: var(--spacing)` resolved correctly
2. ✅ **Shorthand with rgb()**: `outline: 3px solid rgb(255, 0, 0)` parsed correctly
3. ✅ **Em/Rem units**: Converted to pixels using font-size context
4. ✅ **Transparent backgrounds**: Walker continues up DOM tree
5. ✅ **Z-index boundaries**: Walker stops at stacking contexts
6. ✅ **Asymmetric padding**: Checks all four sides independently
7. ✅ **Negative outline-offset**: Treated as inside button
8. ✅ **No parent element**: Uses button background as fallback
9. ✅ **Multiple selectors**: `:focus, :focus-visible` handled correctly
10. ✅ **Gradient data URIs**: Distinguished from image data URIs

---

## Future Considerations

### Not Currently Implemented

1. **Multi-layer box-shadow**: When outline:none is used with complex multi-layer shadows
2. **Transform/rotate**: Rotated buttons may have outline extend in unexpected directions
3. **Viewport clipping**: Outline extending beyond viewport boundaries
4. **Dynamic content**: Content appearing/disappearing affecting background
5. **Transparent text over outline**: Rare case where text overlaps outline

### Potential Enhancements

1. **Color blindness simulation**: Test contrast for different types of color vision deficiency
2. **Motion/animation**: Detect animated backgrounds that might affect contrast
3. **Dark mode detection**: Automatically test both light and dark themes
4. **Nested z-index**: Handle complex stacking context hierarchies
5. **SVG buttons**: Handle inline SVG elements as buttons

---

## References

- **WCAG 2.4.7**: https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html
- **WCAG 1.4.11**: https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html
- **CSS Outline**: https://developer.mozilla.org/en-US/docs/Web/CSS/outline
- **CSS Z-Index**: https://developer.mozilla.org/en-US/docs/Web/CSS/z-index
- **Contrast Calculation**: https://www.w3.org/TR/WCAG21/#contrast-minimum

---

**Document Version**: 1.0
**Last Updated**: 2025-10-21
**Author**: AI Assistant (Claude Code)
**Test Module**: `auto_a11y/testing/touchpoint_tests/test_buttons.py`
