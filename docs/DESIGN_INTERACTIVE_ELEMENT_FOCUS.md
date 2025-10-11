# Interactive Element Focus Indicator Detection

## Overview
Elements can be made interactive (and thus keyboard-focusable) through:
1. Adding `tabindex` attribute (≥ -1)
2. Adding event handlers (inline or via addEventListener)

These elements need visible focus indicators just like native interactive elements (buttons, links, inputs).

## Detection Strategy

### 1. Tabindex Detection
**Simple approach**: Find all elements with `tabindex >= -1` that don't have semantic interactive roles.

**Non-interactive elements include**:
- `<div>`, `<span>`, `<p>`, `<h1>`-`<h6>`, `<section>`, `<article>`, `<li>`, `<ul>`, `<ol>`, etc.
- Elements without ARIA roles like `button`, `link`, `checkbox`, `radio`, `tab`, etc.

**Interactive elements to exclude**:
- Native: `<a>`, `<button>`, `<input>`, `<select>`, `<textarea>`, `<summary>`
- ARIA roles: `button`, `link`, `checkbox`, `radio`, `tab`, `menuitem`, `option`, etc.

### 2. Event Handler Detection
**Inline handlers**: Parse HTML for `on<event>` attributes:
- `onclick`, `onkeydown`, `onkeyup`, `onkeypress`, `onmousedown`, `onmouseup`

**Script-based handlers**: Parse `<script>` blocks for:
- `element.addEventListener('click', ...)`
- `element.addEventListener('keydown', ...)`
- `element.onclick = ...`
- jQuery: `$(selector).on('click', ...)`, `$(selector).click(...)`

**Challenges**:
- Need to match event registrations to specific elements via selectors
- Complex JS logic may be hard to trace
- Event delegation (handlers on parent elements) is difficult to detect

**Practical approach**:
- Focus on inline handlers (100% accurate)
- Detect addEventListener/on() calls in scripts (best effort)
- Flag elements with event handlers that lack focus indicators

## Error Codes

### Tabindex-based Interactive Elements
Following button focus indicator pattern:

1. **ErrTabindexNoVisibleFocus** - Element with tabindex has no visible focus indicator
2. **ErrTabindexFocusContrastFail** - Focus indicator has insufficient contrast (< 3:1)
3. **ErrTabindexOutlineNoneNoBoxShadow** - outline:none with no alternative indicator
4. **ErrTabindexSingleSideBoxShadow** - Box-shadow only on one side (violates CR 5.2.4)
5. **ErrTabindexOutlineWidthInsufficient** - Outline < 2px (WCAG 2.4.11 AAA)
6. **ErrTabindexColorChangeOnly** - Focus relies solely on color change (violates WCAG 1.4.1)
7. **ErrTabindexTransparentOutline** - Focus outline is semi-transparent (alpha < 0.5)

### Event Handler-based Interactive Elements
Same pattern:

1. **ErrHandlerNoVisibleFocus** - Element with event handler has no visible focus indicator
2. **ErrHandlerFocusContrastFail** - Focus indicator has insufficient contrast
3. **ErrHandlerOutlineNoneNoBoxShadow** - outline:none with no alternative
4. **ErrHandlerSingleSideBoxShadow** - Box-shadow only on one side
5. **ErrHandlerOutlineWidthInsufficient** - Outline < 2px
6. **ErrHandlerColorChangeOnly** - Focus relies solely on color change
7. **ErrHandlerTransparentOutline** - Focus outline is semi-transparent

### Warning Codes

1. **WarnTabindexDefaultFocus** - Element relies on default browser focus styles
2. **WarnHandlerDefaultFocus** - Element relies on default browser focus styles
3. **WarnTabindexNoBorderOutline** - Screen magnifier users may not see comparison
4. **WarnHandlerNoBorderOutline** - Screen magnifier users may not see comparison

## WCAG Criteria
- **2.4.7 Focus Visible (Level AA)**: Focus indicator must be visible
- **1.4.1 Use of Color (Level A)**: Can't rely solely on color change
- **1.4.11 Non-text Contrast (Level AA)**: Focus indicator needs 3:1 contrast
- **2.4.11 Focus Appearance (Level AAA)**: Focus indicator should be ≥2px
- **Conformance Requirement 5.2.4**: UI components must have sufficient focus indicator area

## Implementation Plan

### Phase 1: Tabindex Detection
1. Extract all elements with `tabindex` attribute
2. Filter to those with `tabindex >= -1`
3. Exclude semantic interactive elements
4. Exclude elements with interactive ARIA roles
5. Extract focus styles from stylesheets (reuse button logic)
6. Apply button focus indicator checks
7. Report errors/warnings

### Phase 2: Event Handler Detection
1. Parse HTML for inline event handlers (`on<event>` attributes)
2. Parse `<script>` blocks for addEventListener/on() calls
3. Match handlers to elements (selector-based)
4. Filter to non-interactive elements
5. Extract focus styles from stylesheets
6. Apply button focus indicator checks
7. Report errors/warnings

### Phase 3: Testing
1. Create 2 fixtures per error code (1 positive, 1 negative)
2. Test and debug to 100% pass rate
3. Add to EventHandling touchpoint

## Touchpoint: event_handling

Location: `auto_a11y/testing/touchpoint_tests/test_event_handling.py`

This test will be part of the Event Handling touchpoint, as these issues relate to interactive behavior added via JavaScript.

## Notes
- Reuse button focus detection logic where possible
- Consider performance impact of parsing all scripts
- May need to limit scope to inline handlers initially
- Complex JS frameworks (React, Vue, Angular) may be harder to analyze
