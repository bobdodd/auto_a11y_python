# Touchpoint Mapping System

## Overview

The auto_a11y system organizes accessibility errors, warnings, and info messages into **touchpoints** - logical categories that group related accessibility concerns. This document explains how errors are mapped to touchpoints.

## Architecture

### Two-Layer Mapping System

The system uses a **two-layer approach** to map violations to touchpoints:

1. **Primary (Explicit Mapping)**: Check `ERROR_CODE_TO_TOUCHPOINT` dictionary for specific error code
2. **Fallback (Category Mapping)**: If not found, use the `category` field from the issue catalog via `CATEGORY_TO_TOUCHPOINT`

This is implemented in `TouchpointManager.map_violation_to_touchpoint()`:

```python
def map_violation_to_touchpoint(cls, violation: Dict[str, Any]) -> TouchpointID:
    """Map a violation to its appropriate touchpoint"""

    # First try to map by error code if available
    if 'id' in violation:
        touchpoint = cls.get_touchpoint_for_error_code(violation['id'])
        if touchpoint:
            return touchpoint

    # Fall back to category mapping
    category = violation.get('category', 'other')
    return cls.get_touchpoint_for_category(category)
```

## File Locations

All mapping configuration is in: `/auto_a11y/core/touchpoints.py`

- **Line ~20-50**: `TouchpointID` enum - defines all touchpoint identifiers
- **Line ~60-300**: `TOUCHPOINTS` dictionary - defines touchpoint metadata (name, description, tests)
- **Line ~310-370**: `CATEGORY_TO_TOUCHPOINT` - fallback category mappings
- **Line ~370-630**: `ERROR_CODE_TO_TOUCHPOINT` - explicit error code mappings

## TouchpointID Enum

All available touchpoints:

```python
class TouchpointID(Enum):
    ACCESSIBLE_NAMES = "accessible_names"
    ANIMATION = "animation"
    COLORS = "colors"
    DIALOGS = "dialogs"
    ELECTRONIC_DOCUMENTS = "electronic_documents"
    EVENT_HANDLING = "event_handling"
    FOCUS_MANAGEMENT = "focus_management"
    FONTS = "fonts"
    FORMS = "forms"
    HEADINGS = "headings"
    IMAGES = "images"
    LANDMARKS = "landmarks"
    LANGUAGE = "language"
    LINKS = "links"
    LISTS = "lists"
    MAPS = "maps"
    NAVIGATION = "navigation"
    PAGE = "page"
    READ_MORE_LINKS = "read_more_links"
    TABINDEX = "tabindex"
    TITLE_ATTRIBUTES = "title_attributes"
    TABLES = "tables"
    TIMERS = "timers"
    TOUCH_MOBILE = "touch_mobile"
    VIDEOS = "videos"
    STYLES = "styles"
```

## Category to Touchpoint Mappings

The `CATEGORY_TO_TOUCHPOINT` dictionary provides fallback mappings:

| Category | Maps To | Notes |
|----------|---------|-------|
| `headings` | HEADINGS | Heading structure and hierarchy |
| `images` | IMAGES | Image alt text and accessibility |
| `forms` | FORMS | Form fields and controls |
| `buttons` | FORMS | Buttons are part of forms |
| `landmarks` | LANDMARKS | ARIA landmarks and page structure |
| `color` | COLORS | Color usage and contrast |
| `colors` | COLORS | Alternative spelling |
| `colorcontrast` | COLORS | Legacy category name |
| `focus` | FOCUS_MANAGEMENT | Focus indicators and management |
| `focus_management` | FOCUS_MANAGEMENT | Alternative spelling |
| `language` | LANGUAGE | Language attributes and i18n |
| `lang` | LANGUAGE | Short form |
| `link` | LINKS | Link accessibility |
| `links` | LINKS | Alternative spelling |
| `page` | PAGE | Document-level page issues |
| `title` | TITLE_ATTRIBUTES | Title attributes for tooltips |
| `tabindex` | TABINDEX | Tabindex usage and keyboard nav |
| `aria` | ACCESSIBLE_NAMES | ARIA roles and labels |
| `svg` | IMAGES | SVG accessibility |
| `pdf` | ELECTRONIC_DOCUMENTS | PDF documents |
| `font` | FONTS | Font readability |
| `fonts` | FONTS | Alternative spelling |
| `javascript` | EVENT_HANDLING | JavaScript event handlers |
| `event_handling` | EVENT_HANDLING | Alternative spelling |
| `event_handlers` | EVENT_HANDLING | Alternative spelling |
| `style` | STYLES | Inline styles |
| `styles` | STYLES | Alternative spelling |
| `navigation` | NAVIGATION | Navigation menus and elements |
| `modal` | DIALOGS | Modal dialogs |
| `dialog` | DIALOGS | Alternative spelling |
| `animation` | ANIMATION | Animations and motion |
| `timer` | TIMERS | Time limits |
| `video` | VIDEOS | Video accessibility |
| `table` | TABLES | Data tables |
| `list` | LISTS | Lists structure |
| `map` | MAPS | Interactive maps |
| `other` | ACCESSIBLE_NAMES | Default fallback |

## Explicit Error Code Mappings

The `ERROR_CODE_TO_TOUCHPOINT` dictionary provides explicit mappings for specific error codes. As of the latest update:

- **Total error codes in catalog**: 205
- **Explicitly mapped**: 189 (92%)
- **Using category fallback**: 16 (8%)

### Examples of Explicit Mappings

```python
ERROR_CODE_TO_TOUCHPOINT = {
    # Heading errors
    'ErrEmptyHeading': TouchpointID.HEADINGS,
    'ErrHeadingLevelsSkipped': TouchpointID.HEADINGS,

    # Image errors
    'ErrImageMissingAlt': TouchpointID.IMAGES,
    'ErrImageEmptyAlt': TouchpointID.IMAGES,

    # Link errors (all explicitly mapped)
    'ErrAnchorTargetTabindex': TouchpointID.LINKS,
    'ErrLinkButtonMissingSpaceHandler': TouchpointID.LINKS,
    'ErrLinkTextNotDescriptive': TouchpointID.LINKS,
    'ErrLinkOpensNewWindowNoWarning': TouchpointID.LINKS,

    # Navigation errors (all explicitly mapped)
    'ErrNavMissingAccessibleName': TouchpointID.NAVIGATION,
    'AI_ErrAccordionWithoutARIA': TouchpointID.NAVIGATION,

    # Form errors
    'ErrFormMissingLabel': TouchpointID.FORMS,
    'ErrFieldsetMissingLegend': TouchpointID.FORMS,

    # ... 189 total mappings
}
```

## When to Use Explicit vs Category Mapping

### Use Explicit Mapping When:

1. **Cross-category errors**: An error could belong to multiple categories
   - Example: `ErrAnchorTargetTabindex` has category "links" but could also be "tabindex"
   - Explicitly mapped to `LINKS` for clarity

2. **Specific routing needed**: You want precise control over categorization
   - Example: Link errors explicitly mapped to ensure they don't fall back to ACCESSIBLE_NAMES

3. **New error codes**: When adding new error codes, explicit mapping is clearer

### Use Category Fallback When:

1. **Clear category alignment**: Error clearly belongs to one category
   - Example: 60 landmark errors with category "landmarks" → LANDMARKS

2. **Bulk errors**: Many related errors that all map the same way
   - Example: Form field errors with category "forms" → FORMS

## Current Mapping Statistics

### Codes Using Category Fallback (16 total)

| Category | Count | Maps To | Example Codes |
|----------|-------|---------|---------------|
| aria | 1 | ACCESSIBLE_NAMES | ErrLabelMismatchOfAccessibleNameAndLabelText |
| buttons | 5 | FORMS | ErrButtonTextLowContrast, WarnButtonGenericText |
| color | 5 | COLORS | ErrTextContrast, ErrColorStyleDefinedExplicitly |
| event_handling | 18 | EVENT_HANDLING | ErrHandlerNoVisibleFocus, ErrTabindexFocusContrastFail |
| focus | 6 | FOCUS_MANAGEMENT | ErrPositiveTabIndex, ErrNegativeTabIndex |
| fonts | 1 | FONTS | WarnFontNotInRecommenedListForA11y |
| forms | 23 | FORMS | ErrInputNoVisibleFocus, ErrLabelContainsMultipleFields |
| headings | 10 | HEADINGS | ErrFoundAriaLevelButNoRoleAppliedAtAll |
| landmarks | 60 | LANDMARKS | ErrMultipleMainLandmarksOnPage, WarnNavLandmarkHasNoLabel |
| language | 11 | LANGUAGE | ErrPrimaryLangUnrecognized, ErrEmptyLanguageAttribute |
| title | 1 | TITLE_ATTRIBUTES | ErrIframeWithNoTitleAttr |

### Fully Explicitly Mapped Categories

These categories have ALL their error codes explicitly mapped:

- **links**: 14 codes (all in ERROR_CODE_TO_TOUCHPOINT)
- **navigation**: 6 codes (all in ERROR_CODE_TO_TOUCHPOINT)
- **images**: ~20 codes (all explicitly mapped)
- **colors**: Most codes explicitly mapped

## Adding New Error Codes

When adding a new error code, follow this workflow:

### 1. Add to Issue Catalog

First, add the error to `/auto_a11y/reporting/issue_catalog.py`:

```python
"ErrNewAccessibilityIssue": {
    "id": "ErrNewAccessibilityIssue",
    "type": "Error",
    "impact": "High",
    "wcag": ["1.3.1"],
    "wcag_full": "1.3.1 Info and Relationships",
    "category": "forms",  # ← Choose appropriate category
    "description": "Description of the issue",
    "why_it_matters": "Why this matters to users",
    "who_it_affects": "Which users are affected",
    "how_to_fix": "How to fix the issue"
}
```

### 2. Decide on Mapping Strategy

**Option A: Use Category Fallback** (Recommended for most cases)

If the category clearly indicates the touchpoint, no additional mapping needed. The error will automatically fall back to the category mapping.

Example: `category: "forms"` → automatically maps to FORMS touchpoint

**Option B: Add Explicit Mapping** (Recommended for precision)

Add to `ERROR_CODE_TO_TOUCHPOINT` in `/auto_a11y/core/touchpoints.py`:

```python
ERROR_CODE_TO_TOUCHPOINT = {
    # ... existing mappings ...

    # New error code
    'ErrNewAccessibilityIssue': TouchpointID.FORMS,
}
```

### 3. Update Touchpoint Tests Config (Optional)

If you want the error to show on the "Create Project" page for test selection, add it to `/auto_a11y/config/touchpoint_tests.py`:

```python
TOUCHPOINT_TESTS = {
    # ... existing touchpoints ...

    'forms': [
        # ... existing form tests ...
        'ErrNewAccessibilityIssue',  # Add here
    ],
}
```

### 4. Create Fixtures

Create test fixtures in `/Fixtures/{category}/` to validate the error detection.

### 5. Verify Mapping

Run this command to verify the mapping is working:

```bash
python3 -c "
from auto_a11y.core.touchpoints import TouchpointManager
violation = {'id': 'ErrNewAccessibilityIssue', 'category': 'forms'}
touchpoint = TouchpointManager.map_violation_to_touchpoint(violation)
print(f'ErrNewAccessibilityIssue maps to: {touchpoint.value}')
"
```

## Adding New Touchpoints

To add a completely new touchpoint:

### 1. Add to TouchpointID Enum

```python
class TouchpointID(Enum):
    # ... existing touchpoints ...
    NEW_TOUCHPOINT = "new_touchpoint"
```

### 2. Add Touchpoint Definition

```python
TOUCHPOINTS = {
    # ... existing touchpoints ...

    TouchpointID.NEW_TOUCHPOINT: Touchpoint(
        id=TouchpointID.NEW_TOUCHPOINT,
        name="New Touchpoint",
        description="Description of what this touchpoint covers",
        js_tests=["new_test.js"],
        ai_tests=["new_ai_test"],
        wcag_criteria=["1.3.1", "2.4.6"]
    ),
}
```

### 3. Add Category Mapping (Optional)

```python
CATEGORY_TO_TOUCHPOINT = {
    # ... existing mappings ...
    'new_category': TouchpointID.NEW_TOUCHPOINT,
}
```

### 4. Add Error Code Mappings

```python
ERROR_CODE_TO_TOUCHPOINT = {
    # ... existing mappings ...
    'ErrNewTouchpointIssue1': TouchpointID.NEW_TOUCHPOINT,
    'ErrNewTouchpointIssue2': TouchpointID.NEW_TOUCHPOINT,
}
```

### 5. Create Test Configuration

Add to `/auto_a11y/config/touchpoint_tests.py`:

```python
TOUCHPOINT_TESTS = {
    # ... existing touchpoints ...

    'new_touchpoint': [
        'ErrNewTouchpointIssue1',
        'ErrNewTouchpointIssue2',
    ],
}
```

## Troubleshooting

### Error Shows Under Wrong Touchpoint

**Problem**: `ErrLinkTextNotDescriptive` appears under "Accessible Names" instead of "Links"

**Diagnosis**:
1. Check if error code is in `ERROR_CODE_TO_TOUCHPOINT` - if not, it's using category fallback
2. Check the `category` field in issue catalog
3. Check what the category maps to in `CATEGORY_TO_TOUCHPOINT`

**Solution**:
```python
# Option 1: Add explicit mapping
ERROR_CODE_TO_TOUCHPOINT = {
    'ErrLinkTextNotDescriptive': TouchpointID.LINKS,
}

# Option 2: Fix category in issue catalog
"ErrLinkTextNotDescriptive": {
    "category": "links",  # Ensure correct category
}

# Option 3: Fix category mapping
CATEGORY_TO_TOUCHPOINT = {
    'links': TouchpointID.LINKS,  # Not ACCESSIBLE_NAMES
}
```

### All Errors Appear Under "Accessible Names"

**Problem**: Many unrelated errors show under "Accessible Names"

**Cause**: The `'other'` category maps to `ACCESSIBLE_NAMES` as the default fallback.

**Solution**: Ensure error codes have proper `category` values in the issue catalog, or add explicit mappings.

### Error Code Not Recognized

**Problem**: Error shows as "Issue {code} needs documentation"

**Cause**: Error code not in issue catalog

**Solution**: Add error to `/auto_a11y/reporting/issue_catalog.py`

### Category Not Mapped

**Problem**: `ValueError: Category 'xyz' is not mapped to a touchpoint`

**Solution**: Add category mapping:
```python
CATEGORY_TO_TOUCHPOINT = {
    'xyz': TouchpointID.APPROPRIATE_TOUCHPOINT,
}
```

## Best Practices

### 1. Prefer Explicit Mappings for Clarity

While category fallback works well, explicit mappings make the system more maintainable:

```python
# GOOD: Clear and explicit
'ErrLinkTextNotDescriptive': TouchpointID.LINKS,

# OK: Relies on category="links" → LINKS
# (No explicit mapping needed, but less clear)
```

### 2. Keep Categories Consistent

Use consistent category names in the issue catalog:
- Use `links` not `link` or `hyperlinks`
- Use `forms` not `form` or `inputs`
- Use `event_handling` not `javascript` or `events`

### 3. Group Related Errors

Keep related error codes together in `ERROR_CODE_TO_TOUCHPOINT`:

```python
# Link errors
'ErrLinkTextNotDescriptive': TouchpointID.LINKS,
'ErrLinkOpensNewWindowNoWarning': TouchpointID.LINKS,
'ErrLinkFocusContrastFail': TouchpointID.LINKS,

# Navigation errors
'ErrNavMissingAccessibleName': TouchpointID.NAVIGATION,
'ErrDuplicateNavNames': TouchpointID.NAVIGATION,
```

### 4. Document Special Cases

Add comments for non-obvious mappings:

```python
# Skip link errors map to LANDMARKS, not LINKS
'ErrSkipLinkMissing': TouchpointID.LANDMARKS,  # Skip links are navigation structure
'ErrBrokenSkipLink': TouchpointID.LANDMARKS,   # Not regular links
```

### 5. Test After Changes

After modifying touchpoint mappings:

1. **Restart Flask** - Changes require application restart
2. **Check fixture tests** - Run `python3 test_fixtures.py`
3. **Verify in UI** - Check page test results to ensure correct categorization
4. **Run syntax check** - `python3 -m py_compile auto_a11y/core/touchpoints.py`

## Migration History

### January 2025 - Links and Navigation Touchpoint Fix

**Problem**: Link and navigation errors were appearing under "Accessible Names" touchpoint on page test results.

**Root Cause**:
- Category mappings: `'link'/'links' → ACCESSIBLE_NAMES` ❌
- Category mappings: `'navigation' → LANDMARKS` ❌

**Fix Applied**:
1. Added `TouchpointID.LINKS` and `TouchpointID.NAVIGATION` enums
2. Created Touchpoint definitions for both
3. Added 14 link error codes to `ERROR_CODE_TO_TOUCHPOINT → LINKS`
4. Added 6 navigation error codes to `ERROR_CODE_TO_TOUCHPOINT → NAVIGATION`
5. Updated category mappings: `'links' → LINKS` ✅
6. Updated category mappings: `'navigation' → NAVIGATION` ✅

**Result**: All link and navigation errors now correctly categorized.

**Affected Error Codes**:
- ErrAnchorTargetTabindex
- ErrLinkButtonMissingSpaceHandler
- ErrLinkColorChangeOnly
- ErrLinkFocusContrastFail
- ErrLinkImageNoFocusIndicator
- ErrLinkOpensNewWindowNoWarning
- ErrLinkOutlineWidthInsufficient
- ErrLinkTextNotDescriptive
- All navigation error codes

## Related Documentation

- **Issue Catalog**: `/auto_a11y/reporting/issue_catalog.py` - All error code definitions
- **Touchpoint Tests**: `/auto_a11y/config/touchpoint_tests.py` - Test selection for Create Project page
- **Fixture Validator**: `/auto_a11y/testing/fixture_validator.py` - Validates which tests are available
- **Test Runner**: `/auto_a11y/testing/test_runner.py` - Runs accessibility tests
- **Page View Template**: `/auto_a11y/web/templates/pages/view.html` - Displays test results by touchpoint

## Support

For questions about touchpoint mapping:
1. Review this documentation
2. Check the code in `/auto_a11y/core/touchpoints.py`
3. Search for similar error codes in `ERROR_CODE_TO_TOUCHPOINT`
4. Review the issue catalog for category assignments
5. Test changes with fixture tests before deploying

---

**Last Updated**: January 2025
**Maintained By**: auto_a11y development team
