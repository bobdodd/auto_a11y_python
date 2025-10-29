# Input Field Focus Contrast Testing - Complete Design and Implementation

**Created:** 2025-10-25
**Author:** Claude Code
**Status:** Implementation Ready

## Executive Summary

This document describes the design and implementation plan for correcting and extending `ErrInputFocusContrastFail` to comprehensively test focus indicator contrast on input fields. Input fields are more complex than buttons because they commonly use **border-thickening** for focus indication, which requires contrast checking against multiple backgrounds.

## Current State Analysis

### What Exists Today

**Implementation Location:** `auto_a11y/testing/touchpoint_tests/test_forms.py` lines 1090-1120

**Current Capabilities:**
- ✅ Checks outline contrast against input background
- ✅ Checks box-shadow contrast against input background
- ✅ Detects color-only changes (no structural indicator)
- ✅ Detects insufficient border thickening
- ✅ Detects outline width < 2px

**Current Limitations:**
- ❌ **Does NOT check border contrast when border thickens**
- ❌ Does NOT handle outline-offset > 0 (comparing against parent background)
- ❌ Does NOT detect z-index complications
- ❌ Does NOT detect gradient/image backgrounds preventing contrast calculation
- ❌ Does NOT check if outline extends beyond parent bounds

### Test Results

**Fixture Success Rate:** 50% (1 of 2 fixtures passing)

**Status:** `[ ] ErrInputFocusContrastFail` - NOT WORKING

The primary issue is that the most common input focus pattern (border thickening) is detected but **never has its contrast validated**.

---

## Problem Statement

### Why Input Fields Are More Complex Than Buttons

| Aspect | Buttons | Input Fields |
|--------|---------|--------------|
| **Default visual** | No border or 0-1px subtle border | Prominent 1-2px border (core design element) |
| **Primary focus method** | Outline (outline: 2px solid) | **Border thickening** (1px → 3px) OR outline OR both |
| **Secondary focus method** | Box-shadow | Outline OR box-shadow |
| **Outline-offset** | Often > 0 (sits outside button) | Usually 0 or small (space constraints in forms) |
| **Color-only change** | Acceptable IF structural change exists | **ERROR** - violates WCAG 1.4.1 (already has visible border) |
| **Contrast check complexity** | Single target (outline) | **Dual targets** (border AND/OR outline) |

### The Critical Missing Feature: Border Contrast Validation

When an input field uses border thickening for focus:

```css
input {
    border: 1px solid #cccccc;  /* Gray border, 1px */
    background: white;
}

input:focus {
    border: 3px solid #dddddd;  /* Slightly darker gray, 3px */
}
```

**The Questions:**
1. What do the NEW 2px of border pixels (3px - 1px) need to contrast against?
2. How do we validate this programmatically?

**Current Implementation:** Detects the border changed, reports `ErrInputBorderChangeInsufficient` if < 1px, but **NEVER checks contrast**.

---

## Design Decisions

### Decision 1: What Should Border Contrast Against?

The new thickened border pixels must have adequate contrast against:

#### Option A: The old border color
**Rationale:** In the overlapping area (first 1px), the new border replaces the old border.

**Example:**
- Old: 1px solid #cccccc
- New: 3px solid #dddddd
- In the first 1px, #dddddd replaces #cccccc

**Contrast requirement:** `get_contrast_ratio(#dddddd, #cccccc) >= 3:1`

#### Option B: The input background
**Rationale:** The new border pixels (especially the additional 2px) sit on top of / adjacent to the input background.

**Example:**
- Background: white
- New border: 3px solid #f5f5f5
- The border must be visible against white

**Contrast requirement:** `get_contrast_ratio(#f5f5f5, white) >= 3:1`

#### **DECISION: Check BOTH**

We must verify contrast against BOTH the old border and the input background. Report the **worst case** (minimum of the two).

**Why both?**
- If new border vs old border fails: User can't see the change in the overlapping area
- If new border vs background fails: User can't see the additional thickness clearly

### Decision 2: Should We Reuse Button Logic for Outlines?

**YES.** The button focus contrast algorithm (`test_buttons.py` lines 639-747) is comprehensive and handles:

1. **Outline-offset > 0:** Compares outline against parent background
2. **Outline-offset ≤ 0:** Compares outline against button/input background
3. **Z-index complications:** Warns when elements float over varying backgrounds
4. **Outline exceeds parent:** Warns when outline extends beyond container
5. **Gradient backgrounds:** Warns when automatic contrast calculation impossible
6. **Image backgrounds:** Warns when automatic contrast calculation impossible
7. **Transparency:** Checks for semi-transparent indicators

**Adaptation Required:**
- Change error codes from `ErrButton*` to `ErrInput*`
- Change warning codes from `WarnButton*` to `WarnInput*`
- Use input background instead of button background

### Decision 3: How to Handle Hybrid Approach (Border + Outline)?

When an input uses BOTH border thickening AND outline:

```css
input:focus {
    border: 3px solid #0066cc;  /* Thickened border */
    outline: 2px solid #ff6600;  /* Separate outline */
    outline-offset: 2px;
}
```

**DECISION: Check BOTH independently and report ALL issues found.**

This follows the principle already established in `test_forms.py` (lines 1070-1130) where all checks run independently:

```python
issues_found = []

if condition1:
    issues_found.append(('Code1', reason))

if condition2:
    issues_found.append(('Code2', reason))

# All checks execute, all issues reported
```

---

## Proposed Error and Warning Codes

### Existing Codes (Already Implemented)

1. ✅ `ErrInputNoVisibleFocus` - No focus indicator at all
2. ✅ `ErrInputColorChangeOnly` → **RENAME TO:** `ErrInputFocusColorChangeOnly`
3. ✅ `ErrInputFocusContrastFail` - Contrast < 3:1 (currently incomplete)
4. ✅ `ErrInputSingleSideBoxShadow` - Box-shadow on one side only
5. ✅ `ErrInputBorderChangeInsufficient` - Border thickens < 1px
6. ✅ `ErrInputOutlineWidthInsufficient` - Outline < 2px
7. ✅ `WarnInputNoBorderOutline` - Outline-only (screen magnifier concern)
8. ✅ `WarnInputDefaultFocus` - Relies on browser defaults
9. ✅ `WarnInputFocusGradientBackground` - Gradient prevents contrast calc
10. ✅ `WarnInputTransparentFocus` - Semi-transparent indicator

### New Codes Required (Mirror Button Logic)

11. **`WarnInputFocusZIndexFloating`** (NEW)
    - Input has z-index, may float over varying backgrounds
    - Outline contrast cannot be automatically verified
    - Manual testing required

12. **`WarnInputFocusParentZIndexFloating`** (NEW)
    - Parent has z-index without solid background
    - Outline sits against transparent parent that may float
    - Manual testing required

13. **`WarnInputFocusOutlineExceedsParent`** (NEW)
    - Outline extends beyond parent container bounds
    - Cannot determine background beyond parent
    - Manual testing required

14. **`WarnInputFocusParentGradientBackground`** (NEW)
    - Parent has gradient, outline sits against varying colors
    - Automatic contrast calculation impossible
    - Manual verification against lightest and darkest gradient colors

15. **`WarnInputFocusParentImageBackground`** (NEW)
    - Parent has background image
    - Outline must be visible against all parts of image
    - Manual testing required

---

## Implementation Plan

### Phase 1: Rename ErrInputColorChangeOnly

**New Name:** `ErrInputFocusColorChangeOnly`

**Files to Update:**
1. `auto_a11y/reporting/issue_catalog.py` (line 220)
2. `auto_a11y/reporting/issue_descriptions_enhanced.py` (line 1879)
3. `auto_a11y/reporting/wcag_mapper.py` (line 117)
4. `auto_a11y/core/touchpoints.py` (if mapped)
5. `auto_a11y/testing/touchpoint_tests/test_forms.py` (line 1080)
6. Rename fixture files (2 files)
7. Update fixture metadata (id and issueId fields in both)
8. Delete old MongoDB entries

**Rationale:** Matches naming pattern of `ErrLinkColorChangeOnly`, `ErrTabindexColorChangeOnly`, `ErrHandlerColorChangeOnly` - makes it immediately clear this is about focus indication.

### Phase 2: Add New Warning Codes to Issue Catalog

**Location:** `auto_a11y/reporting/issue_catalog.py`

Add 5 new warning definitions (mirror button warnings, adapt for inputs).

**Template Structure:**
```python
"WarnInputFocusZIndexFloating": {
    "id": "WarnInputFocusZIndexFloating",
    "type": "Warning",
    "impact": "Medium",
    "wcag": ["2.4.7", "1.4.11"],
    "category": "Forms",
    "touchpoint": "forms",
    "what_it_checks": "...",
    "why_it_matters": "...",
    "who_it_affects": "...",
    "how_to_fix": "..."
}
```

### Phase 3: Extend JavaScript Data Extraction

**Location:** `auto_a11y/testing/touchpoint_tests/test_forms.py` (lines ~800-1050)

**Current extraction** gets:
- Normal border (width, color, style)
- Focus border (width, color, style)
- Focus outline (width, color, style, offset)
- Focus box-shadow
- Input background color
- Input background image

**Required additions:**
```javascript
// Parent information (for outline-offset > 0)
const parentElement = element.parentElement;
const parentStyle = window.getComputedStyle(parentElement);

// Parent background (walk up DOM tree to find first solid color)
const parentBgInfo = getEffectiveBackgroundColor(parentElement);
field.parentBackgroundColor = parentBgInfo.backgroundColor;
field.parentBgStoppedAtZIndex = parentBgInfo.stoppedAtZIndex;

// Parent background image/gradient
field.parentBackgroundImage = parentStyle.backgroundImage;
field.parentFullBackground = parentStyle.background;

// Parent bounds (for outline extent checking)
const parentBounds = parentElement.getBoundingClientRect();
field.parentBounds = {
    top: parentBounds.top,
    right: parentBounds.right,
    bottom: parentBounds.bottom,
    left: parentBounds.left,
    width: parentBounds.width,
    height: parentBounds.height
};

// Input bounds
const inputBounds = element.getBoundingClientRect();
field.inputBounds = {
    top: inputBounds.top,
    right: inputBounds.right,
    bottom: inputBounds.bottom,
    left: inputBounds.left,
    width: inputBounds.width,
    height: inputBounds.height
};

// Z-index detection
const zIndex = computedStyle.zIndex;
const position = computedStyle.position;
field.inputHasZIndex = (zIndex !== 'auto' && position !== 'static');
```

**Reuse from button implementation:**
```javascript
// Copy getEffectiveBackgroundColor() from test_buttons.py
function getEffectiveBackgroundColor(element) {
    let currentElement = element;
    let backgroundColor = 'rgba(0, 0, 0, 0)';
    let stoppedAtZIndex = false;

    while (currentElement && backgroundColor === 'rgba(0, 0, 0, 0)') {
        const style = window.getComputedStyle(currentElement);
        backgroundColor = style.backgroundColor;

        // Stop if we hit z-index boundary
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

### Phase 4: Implement Border Contrast Checking

**Location:** `auto_a11y/testing/touchpoint_tests/test_forms.py` (new function after line 825)

```python
def check_input_border_contrast(field, font_size, root_font_size):
    """
    Check contrast of focus border when border thickens.

    The new thickened border must have adequate contrast against:
    1. The input background (what the border sits on)
    2. The old border color (what it replaces in overlapping area)

    Args:
        field: Dict with border/background information
        font_size: Element font size for unit conversion
        root_font_size: Root font size for rem conversion

    Returns:
        List of tuples: [(error_code, reason), ...]
    """
    issues = []

    # Parse border dimensions
    normal_border_width = parse_px(field.get('normalBorderWidth', '0px'), font_size, root_font_size)
    focus_border_width = parse_px(field.get('focusBorderWidth', '0px'), font_size, root_font_size)
    border_thickness_change = focus_border_width - normal_border_width

    # Only check if border actually thickens
    if border_thickness_change < 1.0:
        return issues

    # Parse colors
    focus_border_color = parse_color(field.get('focusBorderColor'))
    normal_border_color = parse_color(field.get('normalBorderColor'))
    input_bg_color = parse_color(field.get('backgroundColor'))

    # Check for gradient/image background
    has_gradient = has_gradient_background(field.get('fullBackground', 'none')) or \
                   has_gradient_background(field.get('backgroundImage', 'none'))
    has_image = has_image_background(field.get('fullBackground', 'none')) or \
                has_image_background(field.get('backgroundImage', 'none'))

    if has_gradient:
        issues.append(('WarnInputFocusGradientBackground',
                      'Input has gradient background - border contrast cannot be automatically verified'))
        return issues

    if has_image:
        issues.append(('WarnInputFocusImageBackground',
                      'Input has background image - border contrast cannot be automatically verified'))
        return issues

    # Check transparency
    if focus_border_color['a'] < 0.5:
        issues.append(('WarnInputTransparentFocus',
                      f'Input focus border is semi-transparent (alpha={focus_border_color["a"]:.2f})'))
        return issues

    # Calculate contrast against input background
    contrast_vs_bg = get_contrast_ratio(focus_border_color, input_bg_color)

    # Calculate contrast against old border
    contrast_vs_old_border = get_contrast_ratio(focus_border_color, normal_border_color)

    # Report worst case
    min_contrast = min(contrast_vs_bg, contrast_vs_old_border)

    if min_contrast < 3.0:
        if contrast_vs_bg < 3.0:
            issues.append(('ErrInputFocusContrastFail',
                          f'Input focus border has insufficient contrast ({contrast_vs_bg:.2f}:1) against input background, needs ≥3:1'))
        else:
            issues.append(('ErrInputFocusContrastFail',
                          f'Input focus border has insufficient contrast ({contrast_vs_old_border:.2f}:1) against normal border, needs ≥3:1'))

    return issues
```

### Phase 5: Implement Outline Contrast Checking (Reuse Button Logic)

**Location:** `auto_a11y/testing/touchpoint_tests/test_forms.py` (new function after border contrast)

```python
def check_input_outline_contrast(field, font_size, root_font_size):
    """
    Check contrast of focus outline using button algorithm logic.

    Handles:
    - Positive outline-offset: Compare against parent background
    - Zero/negative offset: Compare against input background
    - Z-index complications
    - Outline exceeding parent bounds
    - Gradient/image backgrounds
    - Transparency

    Args:
        field: Dict with outline/background information
        font_size: Element font size for unit conversion
        root_font_size: Root font size for rem conversion

    Returns:
        List of tuples: [(error_code, reason), ...]
    """
    issues = []

    # Parse outline dimensions
    outline_width = parse_px(field.get('focusOutlineWidth', '0px'), font_size, root_font_size)
    outline_offset = parse_px(field.get('focusOutlineOffset', '0px'), font_size, root_font_size)

    # Outline should exist (caller checks this)
    if outline_width == 0:
        return issues

    # Determine which background to check based on outline-offset
    check_solid_contrast = False

    if outline_offset > 0:
        # Outline sits OUTSIDE input, compare against parent background

        # Check 1: Input has z-index
        input_has_z_index = field.get('inputHasZIndex', False)
        if input_has_z_index:
            issues.append(('WarnInputFocusZIndexFloating',
                          'Input has z-index positioning and may float over varying backgrounds - outline contrast cannot be automatically verified (manual testing required)'))
            return issues

        # Check 2: Parent has z-index without solid background
        parent_bg_stopped_at_z_index = field.get('parentBgStoppedAtZIndex', False)
        if parent_bg_stopped_at_z_index:
            issues.append(('WarnInputFocusParentZIndexFloating',
                          'Input parent has z-index without solid background - outline contrast cannot be automatically verified (manual testing required)'))
            return issues

        # Check 3: Outline extends beyond parent bounds
        input_bounds = field.get('inputBounds')
        parent_bounds = field.get('parentBounds')

        if input_bounds and parent_bounds:
            total_extent = outline_offset + outline_width

            exceeds_top = (input_bounds['top'] - total_extent) < parent_bounds['top']
            exceeds_bottom = (input_bounds['bottom'] + total_extent) > parent_bounds['bottom']
            exceeds_left = (input_bounds['left'] - total_extent) < parent_bounds['left']
            exceeds_right = (input_bounds['right'] + total_extent) > parent_bounds['right']

            if exceeds_top or exceeds_bottom or exceeds_left or exceeds_right:
                issues.append(('WarnInputFocusOutlineExceedsParent',
                              f'Input focus outline extends beyond parent container (offset: {outline_offset:.2f}px + width: {outline_width:.2f}px = {total_extent:.2f}px) - cannot verify contrast (manual testing required)'))
                return issues

        # Check 4: Parent has gradient
        parent_full_bg = field.get('parentFullBackground', 'none')
        parent_bg_image = field.get('parentBackgroundImage', 'none')

        if has_gradient_background(parent_full_bg) or has_gradient_background(parent_bg_image):
            issues.append(('WarnInputFocusParentGradientBackground',
                          'Input parent has gradient background - outline contrast cannot be automatically verified (manual testing required)'))
            return issues

        # Check 5: Parent has image
        if has_image_background(parent_full_bg) or has_image_background(parent_bg_image):
            issues.append(('WarnInputFocusParentImageBackground',
                          'Input parent has background image - outline contrast cannot be automatically verified (manual testing required)'))
            return issues

        # All checks passed, compare against parent background
        compare_bg = field.get('parentBackgroundColor', field.get('backgroundColor'))
        check_solid_contrast = True

    else:
        # Outline sits ON/INSIDE input, compare against input background

        # Check for gradient
        if has_gradient_background(field.get('fullBackground', 'none')) or \
           has_gradient_background(field.get('backgroundImage', 'none')):
            issues.append(('WarnInputFocusGradientBackground',
                          'Input has gradient background - outline contrast cannot be automatically verified'))
            return issues

        # Check for image
        if has_image_background(field.get('fullBackground', 'none')) or \
           has_image_background(field.get('backgroundImage', 'none')):
            issues.append(('WarnInputFocusImageBackground',
                          'Input has background image - outline contrast cannot be automatically verified'))
            return issues

        compare_bg = field.get('backgroundColor')
        check_solid_contrast = True

    # Calculate contrast against solid background
    if check_solid_contrast:
        outline_color = parse_color(field.get('focusOutlineColor'))
        bg_color = parse_color(compare_bg)

        # Check transparency
        if outline_color['a'] < 0.5:
            issues.append(('WarnInputTransparentFocus',
                          f'Input focus outline is semi-transparent (alpha={outline_color["a"]:.2f})'))
            return issues

        # Calculate contrast
        contrast = get_contrast_ratio(outline_color, bg_color)

        if contrast < 3.0:
            bg_type = "parent background" if outline_offset > 0 else "input background"
            issues.append(('ErrInputFocusContrastFail',
                          f'Input focus outline has insufficient contrast ({contrast:.2f}:1) against {bg_type}, needs ≥3:1'))

    return issues
```

### Phase 6: Integrate New Functions into Main Test

**Location:** `auto_a11y/testing/touchpoint_tests/test_forms.py` (modify lines 1090-1120)

**Current Code (Simplified):**
```python
# Check 6: Contrast and transparency checks
if not has_gradient:
    bg_color = parse_color(field['backgroundColor'])
    if has_outline:
        outline_color = parse_color(field['focusOutlineColor'])
        # Check transparency
        if outline_color['a'] < 0.5:
            issues_found.append(('WarnInputTransparentFocus', ...))
        # Check contrast
        contrast = get_contrast_ratio(outline_color, bg_color)
        if contrast < 3.0:
            issues_found.append(('ErrInputFocusContrastFail', ...))
```

**New Code (Comprehensive):**
```python
# Check 6: Contrast checking - COMPREHENSIVE
# Check border contrast (if border thickens)
if max_border_change >= 1.0:
    border_contrast_issues = check_input_border_contrast(field, font_size, root_font_size)
    issues_found.extend(border_contrast_issues)

# Check outline contrast (if outline exists)
if has_outline:
    outline_contrast_issues = check_input_outline_contrast(field, font_size, root_font_size)
    issues_found.extend(outline_contrast_issues)

# Check box-shadow contrast (existing logic - keep as-is)
elif box_shadow_changed and focus_box_shadow:
    # Existing box-shadow contrast code (lines 1105-1120)
    # ... keep unchanged ...
```

### Phase 7: Create/Update Fixtures

#### Rename Existing Fixtures

1. **Old:** `Fixtures/Forms/ErrInputColorChangeOnly_001_violations_color_only.html`
   **New:** `Fixtures/Forms/ErrInputFocusColorChangeOnly_001_violations_color_only.html`

2. **Old:** `Fixtures/Forms/ErrInputColorChangeOnly_002_correct_color_plus_structure.html`
   **New:** `Fixtures/Forms/ErrInputFocusColorChangeOnly_002_correct_color_plus_structure.html`

Update metadata in both files:
```json
{
    "id": "ErrInputFocusColorChangeOnly_001_violations_color_only",
    "issueId": "ErrInputFocusColorChangeOnly",
    ...
}
```

#### Create New Fixtures for ErrInputFocusContrastFail

3. **`ErrInputFocusContrastFail_003_violations_border_low_contrast.html`**
   - Border thickens from 1px to 3px
   - Border color has poor contrast against input background
   - Expected: 3-4 violations

4. **`ErrInputFocusContrastFail_004_correct_border_high_contrast.html`**
   - Border thickens with excellent contrast
   - Expected: 3-4 passes

5. **`ErrInputFocusContrastFail_005_violations_outline_exceeds_parent.html`**
   - Large outline-offset extends beyond parent
   - Should trigger `WarnInputFocusOutlineExceedsParent`
   - Expected: 2-3 warnings

6. **`ErrInputFocusContrastFail_006_correct_hybrid_both_pass.html`**
   - Both border thickening AND outline
   - Both have excellent contrast
   - Expected: 3-4 passes

#### Create New Warning Fixtures

7. **`WarnInputFocusZIndexFloating_001_warnings.html`**
8. **`WarnInputFocusParentZIndexFloating_001_warnings.html`**
9. **`WarnInputFocusParentGradientBackground_001_warnings.html`**
10. **`WarnInputFocusParentImageBackground_001_warnings.html`**
11. **`WarnInputFocusOutlineExceedsParent_001_warnings.html`** (covered by #5)

### Phase 8: Database Cleanup

```javascript
// Delete old entries for renamed code
db.fixture_test_results.deleteMany({
    "issue_code": "ErrInputColorChangeOnly"
})

// Should remove ~4-8 old entries
```

### Phase 9: Testing and Validation

1. **Run renamed fixtures:**
   ```bash
   python test_fixtures.py --code ErrInputFocusColorChangeOnly
   ```
   Expected: 100% pass rate (2 fixtures)

2. **Run border contrast fixtures:**
   ```bash
   python test_fixtures.py --code ErrInputFocusContrastFail
   ```
   Expected: 100% pass rate (6 fixtures)

3. **Run new warning fixtures:**
   ```bash
   python test_fixtures.py --code WarnInputFocusZIndexFloating
   python test_fixtures.py --code WarnInputFocusParentZIndexFloating
   # etc.
   ```
   Expected: 100% pass rate for each

4. **Run all form fixtures:**
   ```bash
   python test_fixtures.py --touchpoint forms
   ```
   Expected: No regressions in other tests

---

## Detailed Algorithm: Border Contrast Calculation

### Visual Example

```
Normal State:
┌─────────────────────────┐
│ 1px #ccc border         │  ← Old border
│  ┌───────────────────┐  │
│  │                   │  │
│  │ white background  │  │  ← Input background
│  │                   │  │
│  └───────────────────┘  │
└─────────────────────────┘

Focus State:
┌─────────────────────────┐
│ 3px #ddd border         │  ← New border (3px total)
│   ├─ 1px replaces old   │     (overlaps with old border area)
│   └─ 2px additional     │     (new pixels)
│  ┌───────────────────┐  │
│  │                   │  │
│  │ white background  │  │  ← Input background (unchanged)
│  │                   │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

### Contrast Requirements

**New border (#ddd) must contrast with:**

1. **Input background (white)**
   - The 2px of additional border sit on/adjacent to white
   - Contrast: `get_contrast_ratio(#ddd, white)`
   - Must be ≥ 3:1

2. **Old border (#ccc)**
   - The first 1px of new border replaces old border
   - User must perceive the change from #ccc to #ddd
   - Contrast: `get_contrast_ratio(#ddd, #ccc)`
   - Must be ≥ 3:1

**Report worst case:**
```python
min_contrast = min(
    get_contrast_ratio(#ddd, white),    # vs background
    get_contrast_ratio(#ddd, #ccc)      # vs old border
)

if min_contrast < 3.0:
    # Report which comparison failed
```

---

## Detailed Algorithm: Outline Contrast with Positive Offset

### Visual Example: Outline-Offset > 0

```
Input field with outline-offset: 5px

Parent Container (gray background #f0f0f0)
┌─────────────────────────────────────┐
│                                     │
│   ┌─────────────────────────────┐   │  ← 5px gap
│   │ 2px outline (blue #0066cc)  │   │
│   │  ┌───────────────────────┐  │   │
│   │  │ Input (white bg)      │  │   │
│   │  │                       │  │   │
│   │  └───────────────────────┘  │   │
│   └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Outline sits OUTSIDE the input, in the parent container area.**

**Contrast check:** Blue outline (#0066cc) vs gray parent background (#f0f0f0)

**Complications:**
- If parent has z-index: May float over other content → **WarnInputFocusParentZIndexFloating**
- If outline extends beyond parent: Don't know what's beyond → **WarnInputFocusOutlineExceedsParent**
- If parent has gradient: Can't calculate single contrast → **WarnInputFocusParentGradientBackground**

---

## WCAG Compliance Matrix

| Code | WCAG 2.4.7 (AA) | WCAG 1.4.1 (A) | WCAG 1.4.11 (AA) | WCAG 2.4.11 (AAA) |
|------|----------------|---------------|-----------------|------------------|
| ErrInputNoVisibleFocus | ✅ | | | |
| ErrInputFocusColorChangeOnly | ✅ | ✅ | | |
| ErrInputFocusContrastFail | ✅ | | ✅ | |
| ErrInputSingleSideBoxShadow | ✅ | | ✅ | |
| ErrInputBorderChangeInsufficient | ✅ | | | |
| ErrInputOutlineWidthInsufficient | | | | ✅ |
| WarnInputNoBorderOutline | ✅ | | | |
| WarnInputDefaultFocus | ✅ | | | |
| WarnInputFocusGradientBackground | ✅ | | ✅ | |
| WarnInputTransparentFocus | ✅ | | ✅ | |

**Coverage:**
- ✅ WCAG 2.4.7 Focus Visible (Level AA) - Comprehensive
- ✅ WCAG 1.4.1 Use of Color (Level A) - Color-only detection
- ✅ WCAG 1.4.11 Non-text Contrast (Level AA) - Full contrast validation
- ✅ WCAG 2.4.11 Focus Appearance (Level AAA) - Width recommendations

---

## Testing Strategy

### Unit Testing (Helper Functions)

Test the new helper functions with known inputs:

```python
def test_check_input_border_contrast():
    # Test case 1: Good contrast
    field = {
        'normalBorderWidth': '1px',
        'focusBorderWidth': '3px',
        'normalBorderColor': 'rgb(204, 204, 204)',
        'focusBorderColor': 'rgb(0, 102, 204)',
        'backgroundColor': 'rgb(255, 255, 255)',
        'fullBackground': 'rgb(255, 255, 255)',
        'backgroundImage': 'none'
    }
    issues = check_input_border_contrast(field, 16, 16)
    assert len(issues) == 0  # Should pass

    # Test case 2: Poor contrast against background
    field['focusBorderColor'] = 'rgb(245, 245, 245)'
    issues = check_input_border_contrast(field, 16, 16)
    assert len(issues) == 1
    assert issues[0][0] == 'ErrInputFocusContrastFail'
```

### Integration Testing (Fixtures)

Run all fixtures and verify expected counts:

```bash
# Should show 100% pass rate
python test_fixtures.py --touchpoint forms --verbose
```

### Manual Testing (Real Forms)

Test against real-world forms:
1. Bootstrap forms
2. Material UI inputs
3. Tailwind CSS forms
4. Custom CSS frameworks

**Expected results:**
- Detect low-contrast borders
- Detect missing focus indicators
- Warn about gradient/image backgrounds
- Handle z-index complications correctly

---

## Performance Considerations

### Computational Cost

**New operations per input field:**
1. Parse parent background (DOM tree walk) - O(depth)
2. Calculate parent bounds - O(1)
3. Check outline extent vs parent bounds - O(1)
4. Calculate 2 contrast ratios (border) - O(1)
5. Calculate 1 contrast ratio (outline) - O(1)

**Total additional cost:** ~5-10ms per input field

**Page with 20 inputs:** ~100-200ms additional

**Verdict:** Acceptable overhead for comprehensive validation.

### Optimization Opportunities

1. **Cache parent background lookups** - Same parent for multiple inputs
2. **Skip bounds checking** if outline-offset ≤ 0
3. **Early exit** on z-index warnings (skip further checks)

---

## Future Enhancements

### Not Included in This Design

1. **Multi-layer box-shadow contrast** - Complex shadow stacks
2. **CSS filters on focus** - blur(), brightness(), contrast()
3. **CSS transforms** - scale(), rotate() affecting perceived thickness
4. **Animated focus transitions** - Contrast during animation frames
5. **Dark mode detection** - Auto-test both light and dark themes
6. **Print style focus** - Ensuring focus visible in print media

### Research Areas

1. **Computer vision for image backgrounds** - Use image analysis to sample colors
2. **Gradient sampling** - Sample gradient at multiple points for worst-case contrast
3. **Viewport-relative calculations** - Account for zoom levels and viewport sizes

---

## Success Criteria

### Definition of Done

✅ All code renamed from `ErrInputColorChangeOnly` to `ErrInputFocusColorChangeOnly`
✅ 5 new warning codes added to issue catalog
✅ Border contrast checking implemented
✅ Outline contrast checking uses button algorithm
✅ Parent background extraction added to JavaScript
✅ Z-index detection implemented
✅ Outline extent checking implemented
✅ All fixtures pass at 100%
✅ No regressions in other form tests
✅ Documentation updated

### Validation Metrics

| Metric | Target | Current |
|--------|--------|---------|
| ErrInputFocusContrastFail pass rate | 100% | 50% |
| Total input focus codes tested | 10 | 10 |
| Border contrast validated | Yes | No |
| Outline offset handled | Yes | No |
| Z-index complications detected | Yes | No |

---

## References

### Internal Documentation
- [button_focus_testing_design.md](button_focus_testing_design.md) - Comprehensive button focus algorithm
- [button_focus_outline_contrast_algorithm.md](button_focus_outline_contrast_algorithm.md) - Detailed button contrast calculation
- [DESIGN_FOCUS_INDICATORS.md](DESIGN_FOCUS_INDICATORS.md) - Overall focus indicator strategy
- [ERRFOCUSBACKGROUNDCOLORONLY_IMPLEMENTATION.md](ERRFOCUSBACKGROUNDCOLORONLY_IMPLEMENTATION.md) - Background-color-only focus detection

### WCAG Success Criteria
- [2.4.7 Focus Visible (AA)](https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html)
- [1.4.1 Use of Color (A)](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html)
- [1.4.11 Non-text Contrast (AA)](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html)
- [2.4.11 Focus Appearance (AAA)](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html)

### External Resources
- [WebAIM: Keyboard Accessibility](https://webaim.org/techniques/keyboard/)
- [CSS Tricks: Styling Form Inputs](https://css-tricks.com/styling-form-inputs/)
- [MDN: :focus pseudo-class](https://developer.mozilla.org/en-US/docs/Web/CSS/:focus)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-25
**Implementation Status:** Ready for Development
