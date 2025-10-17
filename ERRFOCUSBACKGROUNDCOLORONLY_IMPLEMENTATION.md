# ErrFocusBackgroundColorOnly Implementation Summary

## Overview
Created comprehensive error code `ErrFocusBackgroundColorOnly` to detect when interactive elements rely solely on background-color changes for focus indication without using CSS outline property, violating WCAG 2.4.7 Focus Visible and conformance requirement 5.2.4.

## Real-World Problem
The issue identified from user's example:
- Button with black background contains SVG icon with spacing/margin
- Focus indication achieved only by background-color change (black to #333333) visible in gaps around icon
- No CSS outline property used
- Fails WCAG 2.4.7 because:
  - Screen magnifier users at 200-400% zoom cannot see edge gaps to detect color change
  - Users who look away and return cannot identify focus state without examining entire button surface
  - Background-color alone requires viewing entire element; outline provides persistent boundary marker

## Implementation Status

### ✅ Completed

1. **Issue Catalog Entry** - Added to `/ISSUE_CATALOG.md` (line 2411-2419)
   - Complete WCAG 2.4.7 and 5.2.4 Conformance Requirement documentation
   - Comprehensive "Why it matters" explanation for magnification users
   - Detailed "Who it affects" covering screen magnifier users, attention/memory disabilities, low vision, keyboard users
   - Clear remediation steps with code examples

2. **Comprehensive Fixtures** (7 total)

   **Violation Fixtures (4):**
   - `ErrFocusBackgroundColorOnly_001_violations_button_basic.html` - Basic button with background-color only focus
   - `ErrFocusBackgroundColorOnly_002_violations_link.html` - Navigation links with background-color focus (2 violations)
   - `ErrFocusBackgroundColorOnly_003_violations_input.html` - Form inputs with subtle background tint focus (2 violations)
   - `ErrFocusBackgroundColorOnly_004_violations_complex_button.html` - Complex icon buttons using spacing trick (3 violations)

   **Passing Fixtures (3):**
   - `ErrFocusBackgroundColorOnly_005_correct_button_with_outline.html` - Buttons with proper outline focus
   - `ErrFocusBackgroundColorOnly_006_correct_links_with_outline.html` - Links with outline-based focus (3 passing)
   - `ErrFocusBackgroundColorOnly_007_correct_inputs_with_outline.html` - Inputs with outline focus indicators (3 passing)

   All fixtures include:
   - Proper test metadata with expected counts
   - data-expected-violation and data-violation-reason attributes
   - Comprehensive accessibility explanations in comments
   - Real-world examples matching user's scenario

3. **JavaScript Test Logic** - Added to `/auto_a11y/scripts/tests/focus.js`
   - Created `checkFocusBackgroundColorOnly()` helper function (lines 1-102)
   - Parses all stylesheets to detect :focus rules
   - Checks for background-color/background properties without outline
   - Integrated into main `focusScrape()` logic (lines 197-220)
   - Prioritizes ErrFocusBackgroundColorOnly over ErrNoFocusIndicator

### ⚠️ Needs Work - CSS Detection Challenge

**JavaScript Detection Logic Status:**
The CSS rule parsing in `checkFocusBackgroundColorOnly()` is not successfully detecting `:focus` styles with background-color. Current test results:
- **Passing fixtures: 3/7 ✅** (all "correct" fixtures pass - no false positives)
- **Violation fixtures: 0/4 ❌** (all violations being caught by ErrNoFocusIndicator instead)

**Important Note:** Both `ErrNoFocusIndicator` and `ErrFocusBackgroundColorOnly` SHOULD fire for these cases:
- `ErrNoFocusIndicator` = generic "no outline found in computed styles"
- `ErrFocusBackgroundColorOnly` = specific "CSS has :focus with background-color but no outline rule"

**Root Cause Analysis:**

The function `checkFocusBackgroundColorOnly()` returns `false` for all elements, even though:
1. CSS rules exist in `<style>` tags in fixtures (e.g., `.search-button:focus { background-color: #333333; }`)
2. Pyppeteer SHOULD provide access via `document.styleSheets`
3. Selector matching with `.matches()` is standard JavaScript

**Attempted Approaches:**

1. **Stylesheet Parsing (current - lines 8-107)**
   - Iterate `document.styleSheets` array
   - Filter rules with `:focus` in `selectorText`
   - Strip `:focus` to get base selector, use `element.matches(baseSelector)`
   - Check `rule.style.getPropertyValue()` for background/outline properties
   - **Result:** Returns false - likely stylesheet access or property retrieval issue

2. **Temporary Focus Approach (rejected)**
   - Would focus elements and compare computed styles
   - Problem: Headless browser `:focus` behavior; user wants CSS-based detection

**Diagnostic Needed:**

Add logging to determine which step fails:
```javascript
console.log('Total stylesheets:', document.styleSheets.length);
console.log('Rules with :focus:',
    Array.from(document.styleSheets[0]?.cssRules || [])
        .filter(r => r.selectorText?.includes(':focus'))
        .map(r => r.selectorText));
console.log('Matched element classes:', element.className);
```

**Likely Issues:**

1. **`document.styleSheets` may be empty** - Pyppeteer timing? Scripts run before CSS parsed?
2. **`getPropertyValue()` returns empty** - Try `rule.style.backgroundColor` or `rule.cssText`
3. **Selector matching fails** - Cleaned selector syntax invalid after `:focus` removal
4. **Style tag rules inaccessible** - Browser security or Pyppeteer limitation

**Recommended Solutions:**

**Option A: Add Debug Logging (Quick)**
- Insert console.log statements in `checkFocusBackgroundColorOnly()`
- Run single fixture test
- Check Pyppeteer console output to see what's actually available

**Option B: Alternative CSS Access (Medium)**
- Instead of `getPropertyValue()`, check `rule.cssText.includes('background')`
- Parse CSS text directly if style properties don't work
- May be more reliable for detecting rules

**Option C: Python-Side CSS Parsing (Robust)**
- Parse CSS files/tags in Python before injecting JavaScript
- Pass matched rules as data structure to test script
- Most reliable but adds complexity

**Option D: Mark as Manual Review (Temporary)**
- Keep comprehensive fixtures and documentation
- Mark error code as "Manual detection - automated detection in development"
- Still provides value for training and manual audits

**Current Value Despite Detection Issue:**

✅ Comprehensive WCAG 2.4.7 documentation in catalog
✅ 7 detailed fixtures demonstrating problem and solutions
✅ No false positives (passing fixtures correctly identified)
✅ Clear remediation guidance for developers
✅ Real-world example matching user's exact scenario

## Testing

```bash
# Test all ErrFocusBackgroundColorOnly fixtures
source venv/bin/activate
python test_fixtures.py --code ErrFocusBackgroundColorOnly

# Current Results:
# - Total: 7 fixtures
# - Passed: 3/7 (42.9%) - all "correct" fixtures
# - Failed: 4/7 (57.1%) - all "violation" fixtures
# - No false positives ✅
# - Detection logic needs debugging ⚠️
```

## Files Modified

1. `/ISSUE_CATALOG.md` - Added ErrFocusBackgroundColorOnly entry
2. `/auto_a11y/scripts/tests/focus.js` - Added detection logic
3. `/Fixtures/Focus/` - Created 7 comprehensive test fixtures

## WCAG References

- **WCAG 2.4.7 Focus Visible (Level AA):** Focus indicator must be visible
- **WCAG 5.2.4 Accessible Documentation (Conformance Requirement):** Focus must be detectable with assistive technology
- **WCAG 2.4.11 Focus Appearance (Level AAA):** 3:1 contrast ratio for focus indicators

## Key Technical Points

1. **Why outline is required:**
   - Provides persistent boundary marker visible at any zoom level
   - Independent of element fill color or size
   - Visible when user returns attention to page
   - Works for screen magnifier users seeing only portion of element

2. **Why background-color alone fails:**
   - Requires viewing entire element surface to detect
   - Subtle color shifts hard to perceive (black to #333333)
   - Invisible to magnified users seeing only cursor or icon
   - No persistent indicator when attention returns

3. **The spacing/gap technique specifically fails:**
   - Relies on seeing thin border area between icon and button edge
   - At high magnification, users see only icon itself
   - Creates false sense of compliance while violating WCAG

## Recommended Fix Pattern

```css
/* WRONG - Background color only */
.button:focus {
    background-color: #333333;
}

/* CORRECT - Outline with optional background color */
.button:focus {
    background-color: #333333;  /* Optional supplement */
    outline: 3px solid #ffffff; /* Required */
    outline-offset: 2px;         /* Recommended */
}
```

## Documentation Quality

All fixtures include detailed explanations suitable for:
- Developer training on focus indicator requirements
- Understanding magnification use cases
- Learning WCAG 2.4.7 compliance specifics
- Real-world examples from actual inaccessible patterns

## Next Action Items

1. **Debug JavaScript detection** - Add logging and test selector matching
2. **Test CSS access** - Verify stylesheet iteration captures `<style>` tag rules
3. **Consider alternative detection** - May need to actually focus elements to test
4. **Validate with real pages** - Test against user's actual button example
5. **Document limitations** - May need to note cases that can't be auto-detected

## Success Criteria

- [ ] All 7 fixtures pass (currently 3/7)
- [ ] No false positives (✅ already achieved)
- [ ] Detection works for inline styles, `<style>` tags, and external CSS
- [ ] Works with class selectors, ID selectors, and tag selectors
- [ ] Handles complex selectors with multiple pseudo-classes

## Contact

For questions about this implementation or to report issues with the detection logic, review the fixtures in `/Fixtures/Focus/ErrFocusBackgroundColorOnly_*.html` which contain comprehensive examples and explanations.
