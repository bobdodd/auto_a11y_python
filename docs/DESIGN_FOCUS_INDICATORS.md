# Focus Indicator Detection - Complete Design Document

## Overview
This document covers the comprehensive focus indicator detection system across three main categories:
1. **Buttons** - Native button elements and elements with button role
2. **Forms** - Text input fields (input, textarea, select)
3. **Interactive Elements** - Elements made interactive via tabindex or event handlers

## Completed Work

### 1. Button Focus Indicators (✅ Complete)
**Location**: `auto_a11y/testing/touchpoint_tests/test_buttons.py`

**Error Codes** (8 total):
- `ErrButtonNoVisibleFocus` - Button lacks visible focus indicator
- `ErrButtonOutlineNoneNoBoxShadow` - outline:none without alternative
- `ErrButtonFocusContrastFail` - Focus contrast < 3:1
- `ErrButtonSingleSideBoxShadow` - Box-shadow on one side only
- `ErrButtonOutlineWidthInsufficient` - Outline < 2px (AAA)
- `ErrButtonOutlineOffsetInsufficient` - Outline offset too small
- `ErrButtonFocusObscured` - Focus indicator hidden by other elements
- `ErrButtonClipPathWithOutline` - clip-path cuts off outline
- `ErrButtonTransparentOutline` - Semi-transparent outline (alpha < 0.5)

**Status**: Fully implemented with fixtures and tests

---

### 2. Input Focus Indicators (✅ Complete)
**Location**: `auto_a11y/testing/touchpoint_tests/test_forms.py` (lines 408-738)

**Error Codes** (7 errors + 3 warnings = 10 total):

#### Errors:
1. `ErrInputNoVisibleFocus` - No visible focus indicator (violates WCAG 2.4.7)
2. `ErrInputColorChangeOnly` - Relies solely on border color change (violates WCAG 1.4.1)
3. `ErrInputFocusContrastFail` - Contrast < 3:1 (violates WCAG 1.4.11)
4. `ErrInputSingleSideBoxShadow` - Box-shadow on one side only (violates CR 5.2.4)
5. `ErrInputBorderChangeInsufficient` - Border thickens < 1px
6. `ErrInputOutlineWidthInsufficient` - Outline < 2px (WCAG 2.4.11 AAA)

#### Warnings:
7. `WarnInputNoBorderOutline` - Screen magnifier users may not see outline-only
8. `WarnInputDefaultFocus` - Relies on browser defaults (inconsistent)
9. `WarnInputFocusGradientBackground` - Gradient background prevents contrast calculation
10. `WarnInputTransparentFocus` - Semi-transparent focus (alpha < 0.5)

**Key Differences from Button Detection**:
- Input fields often have borders by default → border thickening ≥1px is acceptable
- Color-only changes violate WCAG 1.4.1 (buttons can use color if also structural change)
- Separate outlines recommended for screen magnifier users
- Detection logic runs independently (all issues reported, not just first match)

**Critical Fixes Applied**:
1. **Box-shadow parsing**: Browser returns color first (e.g., `rgb(0, 102, 204) -3px 0px`)
   - Fixed with regex: `re.sub(r'rgba?\([^)]+\)', '', focus_box_shadow)`

2. **Outline color parsing**: Rgba colors with spaces broke split-based parsing
   - Fixed to join all color parts: `colorParts.join(' ')`

3. **Independent test execution**: Changed from if/elif to independent checks
   ```python
   issues_found = []
   if condition1:
       issues_found.append(('Code1', reason))
   if condition2:
       issues_found.append(('Code2', reason))
   # All checks run independently
   ```

4. **WarnInputDefaultFocus logic**: Inverted from checking for default colors to checking for NO custom styles

5. **Transparency detection**: Added for both outline and box-shadow

**Fixtures**: 20 total (10 codes × 2 fixtures each)
**Test Status**: 100% pass rate (all 10 codes fully functional)

**WCAG Criteria**:
- 2.4.7 Focus Visible (Level AA)
- 1.4.1 Use of Color (Level A)
- 1.4.11 Non-text Contrast (Level AA)
- 2.4.11 Focus Appearance (Level AAA)
- Conformance Requirement 5.2.4

---

## In Progress Work

### 3. Interactive Element Focus Indicators (🔄 In Progress)
**Location**: `auto_a11y/testing/touchpoint_tests/test_event_handling.py` (to be created)

Elements can be made interactive (keyboard-focusable) through:
1. **Tabindex attribute** (≥ -1) on non-interactive elements
2. **Event handlers** (inline or addEventListener) on non-interactive elements

These elements need visible focus indicators just like native interactive elements.

---

## Error Codes Defined (✅ Issue Catalog Complete)

### Tabindex Interactive Elements (9 codes)

#### Errors (7):
1. **ErrTabindexNoVisibleFocus**
   - Description: Element with tabindex has no visible focus indicator
   - WCAG: 2.4.7 Focus Visible (Level AA)
   - Impact: High
   - Fix: Add :focus style with outline, box-shadow, or border change

2. **ErrTabindexFocusContrastFail**
   - Description: Focus indicator contrast < 3:1
   - WCAG: 1.4.11, 2.4.7
   - Impact: High
   - Fix: Increase contrast to ≥ 3:1

3. **ErrTabindexOutlineNoneNoBoxShadow**
   - Description: outline:none without alternative indicator
   - WCAG: 2.4.7
   - Impact: High
   - Fix: Provide box-shadow, border, or background change alternative

4. **ErrTabindexSingleSideBoxShadow**
   - Description: Box-shadow on only one side
   - WCAG: CR 5.2.4
   - Impact: High
   - Fix: Use uniform box-shadow on all sides

5. **ErrTabindexOutlineWidthInsufficient**
   - Description: Outline < 2px
   - WCAG: 2.4.11 (Level AAA)
   - Impact: Medium
   - Fix: Increase to ≥ 2px

6. **ErrTabindexColorChangeOnly**
   - Description: Relies solely on color change
   - WCAG: 1.4.1 Use of Color (Level A)
   - Impact: High
   - Fix: Add structural change (outline, border, shape)

7. **ErrTabindexTransparentOutline**
   - Description: Semi-transparent (alpha < 0.5) focus indicator
   - WCAG: 1.4.11, 2.4.7
   - Impact: Medium
   - Fix: Use fully opaque colors (alpha = 1.0)

#### Warnings (2):
8. **WarnTabindexDefaultFocus**
   - Description: Relies on default browser focus styles
   - Impact: Low
   - Recommendation: Define custom :focus styles for consistency

9. **WarnTabindexNoBorderOutline**
   - Description: Outline-only focus (screen magnifier concern)
   - Impact: Low
   - Recommendation: Combine outline with border/size change

### Event Handler Interactive Elements (9 codes)

Same pattern as tabindex, but for elements with event handlers:

1. **ErrHandlerNoVisibleFocus**
2. **ErrHandlerFocusContrastFail**
3. **ErrHandlerOutlineNoneNoBoxShadow**
4. **ErrHandlerSingleSideBoxShadow**
5. **ErrHandlerOutlineWidthInsufficient**
6. **ErrHandlerColorChangeOnly**
7. **ErrHandlerTransparentOutline**
8. **WarnHandlerDefaultFocus**
9. **WarnHandlerNoBorderOutline**

**Total New Error Codes**: 18 (9 tabindex + 9 event handler)

---

## Implementation Plan

### Phase 1: Tabindex Detection

#### Detection Strategy:
1. Extract all elements with `tabindex` attribute
2. Filter to `tabindex >= -1` (focusable elements)
3. Exclude semantic interactive elements:
   - Native: `<a>`, `<button>`, `<input>`, `<select>`, `<textarea>`, `<summary>`
   - ARIA roles: `button`, `link`, `checkbox`, `radio`, `tab`, `menuitem`, `option`, etc.
4. Extract focus styles from stylesheets (reuse button logic)
5. Apply button focus indicator checks
6. Report errors/warnings independently

#### JavaScript Extraction Code:
```javascript
const tabindexElements = [];
const allElements = document.querySelectorAll('[tabindex]');

allElements.forEach(element => {
    const tabindex = parseInt(element.getAttribute('tabindex'));
    if (tabindex < -1) return; // Skip non-focusable

    const tagName = element.tagName.toLowerCase();
    const role = element.getAttribute('role');

    // Skip semantic interactive elements
    const interactiveTags = ['a', 'button', 'input', 'select', 'textarea', 'summary'];
    if (interactiveTags.includes(tagName)) return;

    const interactiveRoles = ['button', 'link', 'checkbox', 'radio', 'tab',
                              'menuitem', 'option', 'switch', 'textbox'];
    if (role && interactiveRoles.includes(role)) return;

    // Extract computed styles (normal and :focus)
    const computed = window.getComputedStyle(element);
    // ... extract focus styles from stylesheets ...

    tabindexElements.push({
        tag: tagName,
        id: element.id,
        className: element.className,
        tabindex: tabindex,
        role: role,
        // ... style properties ...
    });
});

return tabindexElements;
```

### Phase 2: Event Handler Detection

#### 2A: Inline Event Handlers (Simple)
Parse HTML for `on<event>` attributes:
- `onclick`, `onkeydown`, `onkeyup`, `onkeypress`
- `onmousedown`, `onmouseup`, `onmouseover`

```javascript
const handlerElements = [];
const eventAttrs = ['onclick', 'onkeydown', 'onkeyup', 'onkeypress',
                    'onmousedown', 'onmouseup'];

document.querySelectorAll('*').forEach(element => {
    const hasHandler = eventAttrs.some(attr => element.hasAttribute(attr));
    if (!hasHandler) return;

    // Skip if already interactive
    const tagName = element.tagName.toLowerCase();
    const interactiveTags = ['a', 'button', 'input', 'select', 'textarea'];
    if (interactiveTags.includes(tagName)) return;

    // Extract focus styles...
    handlerElements.push({...});
});
```

#### 2B: Script-based Event Handlers (Complex - Best Effort)

**Approach**: Parse `<script>` blocks for event registration patterns:
```javascript
// Patterns to detect:
element.addEventListener('click', ...)
element.onclick = ...
$(selector).on('click', ...)
$(selector).click(...)
```

**Challenges**:
- Need to match selectors to actual elements
- Event delegation (handlers on parent) is hard to trace
- Dynamic handlers in complex frameworks (React, Vue) are difficult
- Variable-based selectors are hard to resolve

**Practical Scope**:
- Focus on inline handlers initially (100% accurate)
- Add simple addEventListener detection (best effort)
- May need to limit to direct selectors (IDs, classes)
- Document limitations clearly

### Phase 3: Focus Indicator Checks

Reuse button focus detection logic:
1. Check for visible focus indicator (outline, border change, box-shadow)
2. Verify contrast ≥ 3:1
3. Check for outline:none without alternative
4. Detect single-side box-shadow
5. Verify outline width ≥ 2px (AAA)
6. Ensure not color-only changes
7. Check transparency < 0.5
8. Warn about default browser styles
9. Warn about outline-only (screen magnifier concern)

---

## Fixtures Required

### Tabindex Fixtures (18 total)
Each code needs 2 fixtures:
- `_001_violations_*` - Positive test (should detect error)
- `_002_correct_*` - Negative test (should NOT detect error)

Example naming:
- `EventHandling/ErrTabindexNoVisibleFocus_001_violations_no_indicator.html`
- `EventHandling/ErrTabindexNoVisibleFocus_002_correct_with_indicator.html`
- `EventHandling/ErrTabindexFocusContrastFail_001_violations_low_contrast.html`
- `EventHandling/ErrTabindexFocusContrastFail_002_correct_high_contrast.html`
- ... (18 total)

### Event Handler Fixtures (18 total)
Same pattern:
- `EventHandling/ErrHandlerNoVisibleFocus_001_violations_onclick_no_focus.html`
- `EventHandling/ErrHandlerNoVisibleFocus_002_correct_onclick_with_focus.html`
- ... (18 total)

**Total Fixtures**: 36 (18 tabindex + 18 event handler)

---

## Fixture Metadata Format

```html
<script type="application/json" id="test-metadata">
{
    "id": "ErrTabindexNoVisibleFocus_001_violations_no_indicator",
    "issueId": "ErrTabindexNoVisibleFocus",
    "expectedViolationCount": 5,
    "expectedPassCount": 0,
    "description": "Elements with tabindex but no focus indicators",
    "wcag": "2.4.7",
    "impact": "High"
}
</script>
```

---

## Testing Strategy

1. **Create fixtures** for one code at a time
2. **Test individually**: `python test_fixtures.py --code ErrTabindexNoVisibleFocus`
3. **Debug** until 100% pass rate
4. **Repeat** for all 18 codes
5. **Final test**: Run all fixtures together

**Success Criteria**: 100% pass rate for all 18 codes (36 fixtures)

---

## WCAG Compliance Summary

All focus indicator detection ensures compliance with:

**Level A** (Required):
- 1.4.1 Use of Color - Color cannot be the only visual means

**Level AA** (Standard):
- 2.4.7 Focus Visible - Focus must have visible indicator
- 1.4.11 Non-text Contrast - 3:1 minimum contrast for UI components

**Level AAA** (Enhanced):
- 2.4.11 Focus Appearance - Recommends ≥2px indicators

**WCAG 2.2**:
- Conformance Requirement 5.2.4 - Focus indicator must have sufficient area (no single-sided)

---

## Code Locations

### Completed:
- **Button focus**: `auto_a11y/testing/touchpoint_tests/test_buttons.py`
- **Input focus**: `auto_a11y/testing/touchpoint_tests/test_forms.py` (lines 408-738)
- **Issue catalog**: `auto_a11y/reporting/issue_catalog.py` (all codes defined)

### To Create:
- **Event handling test**: `auto_a11y/testing/touchpoint_tests/test_event_handling.py`
- **WCAG mapper**: Add mappings to `auto_a11y/reporting/wcag_mapper.py`
- **Fixtures**: `Fixtures/EventHandling/` directory (36 HTML files)
- **Touchpoint registration**: Update `auto_a11y/testing/touchpoint_tests/__init__.py`

---

## Next Steps

1. ✅ Define all 18 error codes in issue_catalog.py (COMPLETE)
2. ⏭️ Add WCAG mappings to wcag_mapper.py
3. ⏭️ Create test_event_handling.py with detection logic
4. ⏭️ Implement tabindex detection
5. ⏭️ Implement inline event handler detection
6. ⏭️ Implement script-based handler detection (optional/best-effort)
7. ⏭️ Create all 36 fixtures (18 tabindex + 18 event handler)
8. ⏭️ Test and debug to 100% pass rate
9. ⏭️ Register event_handling touchpoint in __init__.py
10. ⏭️ Final integration testing

---

## Notes and Considerations

### Performance:
- Parsing all scripts may be slow on large sites
- Consider limiting scope to first N script tags
- May need timeout for complex JS parsing

### Limitations:
- Cannot detect event delegation (handlers on parent elements)
- Cannot trace dynamic handlers in frameworks (React hooks, Vue methods)
- Variable-based selectors are hard to resolve
- May need to document "best effort" detection for script handlers

### Best Practices:
- Recommend using semantic HTML (`<button>`, `<a>`) instead of div/span with handlers
- If non-semantic elements are necessary, require `tabindex="0"` and `role="button"`
- Always provide custom focus indicators for interactive elements
- Test with keyboard navigation and screen readers

### Future Enhancements:
- Detect React onClick handlers
- Parse JSX/framework templates
- Detect Vue @click handlers
- More sophisticated JS analysis
- Integration with build tools to analyze source pre-bundling

---

## References

- [WCAG 2.4.7 Focus Visible](https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html)
- [WCAG 1.4.1 Use of Color](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html)
- [WCAG 1.4.11 Non-text Contrast](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html)
- [WCAG 2.4.11 Focus Appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html)
- [Making Div Clickable](https://www.w3.org/WAI/WCAG21/Techniques/client-side-script/SCR35)
- [Keyboard Accessibility](https://webaim.org/techniques/keyboard/)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-11
**Status**: Input focus complete (100%), Interactive element focus in progress (issue codes defined)
