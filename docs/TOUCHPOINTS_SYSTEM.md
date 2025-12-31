# Accessibility Touchpoints System

## Overview

The Auto A11y Python platform has transitioned from a simple category-based classification to a comprehensive **Touchpoints** system. Touchpoints represent specific areas where web content interfaces with accessibility requirements, going beyond traditional DOM testing to include visual, semantic, and interaction patterns.

## What are Touchpoints?

Touchpoints are comprehensive accessibility assessment areas that:
- **Unite** JavaScript DOM tests and AI visual analysis
- **Organize** issues by user interaction patterns rather than technical implementation
- **Map** directly to WCAG success criteria
- **Provide** clearer remediation paths for developers

## Complete List of Touchpoints

### 1. Accessible Names
- **Description**: Ensures all interactive elements have appropriate accessible names for assistive technology
- **JS Tests**: `accessibleName.js`, `ariaRoles.js`
- **AI Tests**: Visual accessible name detection
- **WCAG**: 4.1.2, 2.4.4, 1.1.1, 3.3.2

### 2. Animation
- **Description**: Detects and evaluates animations, auto-playing content, and motion that may cause issues
- **JS Tests**: None (visual detection only)
- **AI Tests**: Animation detection, auto-play content, parallax scrolling
- **WCAG**: 2.2.2, 2.3.1, 2.3.3

### 3. Color Contrast
- **Description**: Verifies text and UI components meet WCAG color contrast requirements
- **JS Tests**: `colorContrast.js`
- **AI Tests**: Visual contrast checking
- **WCAG**: 1.4.3, 1.4.6, 1.4.11

### 4. Color Use
- **Description**: Ensures color is not the only means of conveying information
- **JS Tests**: `color.js`
- **AI Tests**: Color-only information detection
- **WCAG**: 1.4.1

### 5. Dialogs
- **Description**: Evaluates modal dialogs, pop-ups, and overlay accessibility
- **JS Tests**: Detected through ARIA roles
- **AI Tests**: Modal accessibility, dialog focus trap
- **WCAG**: 2.1.2, 2.4.3, 1.3.1

### 6. Electronic Documents
- **Description**: Checks accessibility of PDFs, Word docs, and other downloadable documents
- **JS Tests**: `pdf.js`
- **AI Tests**: Document accessibility analysis
- **WCAG**: 1.1.1, 1.3.1, 2.4.2

### 7. Event Handling
- **Description**: Verifies keyboard and mouse event handling for interactive elements
- **JS Tests**: Covered by focus and forms tests
- **AI Tests**: Event handler detection
- **WCAG**: 2.1.1, 2.1.3, 2.5.1

### 8. Floating Content
- **Description**: Evaluates sticky headers, floating buttons, and fixed position elements
- **JS Tests**: None (visual detection)
- **AI Tests**: Floating element detection, sticky content analysis
- **WCAG**: 2.4.1, 1.4.10, 2.5.5

### 9. Focus Management
- **Description**: Ensures proper focus indicators, tab order, and keyboard navigation
- **JS Tests**: `focus.js`, `tabindex.js`
- **AI Tests**: Focus order visual check, focus indicator visibility
- **WCAG**: 2.4.3, 2.4.7, 2.1.1, 2.1.2

### 10. Fonts
- **Description**: Evaluates font readability, size, and icon fonts accessibility
- **JS Tests**: `fonts.js`
- **AI Tests**: Font readability, icon font detection
- **WCAG**: 1.4.4, 1.4.12

### 11. Forms
- **Description**: Comprehensive form accessibility including labels, errors, and validation
- **JS Tests**: `forms2.js`, `forms_enhanced.js`
- **AI Tests**: Form visual labels, error identification
- **WCAG**: 3.3.1, 3.3.2, 3.3.3, 3.3.4, 1.3.1, 4.1.2

### 12. Headings
- **Description**: Validates heading hierarchy, structure, and visual headings
- **JS Tests**: `headings.js`
- **AI Tests**: Visual heading detection, heading hierarchy
- **WCAG**: 1.3.1, 2.4.6

### 13. Images
- **Description**: Checks image alt text, decorative images, and complex graphics
- **JS Tests**: `images.js`, `svg.js`
- **AI Tests**: Image text detection, complex image analysis
- **WCAG**: 1.1.1, 1.4.5, 1.4.9

### 14. Landmarks
- **Description**: Evaluates ARIA landmarks and page regions
- **JS Tests**: `landmarks.js`
- **AI Tests**: Landmark visual mapping
- **WCAG**: 1.3.1, 2.4.1, 4.1.2

### 15. Language
- **Description**: Verifies language declarations and changes
- **JS Tests**: `language.js`
- **AI Tests**: Language change detection
- **WCAG**: 3.1.1, 3.1.2

### 16. Lists
- **Description**: Validates list structure and semantics
- **JS Tests**: To be added (`lists.js`)
- **AI Tests**: Visual list detection
- **WCAG**: 1.3.1

### 17. Maps
- **Description**: Evaluates interactive maps and geographic content accessibility
- **JS Tests**: None (specialized content)
- **AI Tests**: Map accessibility, map alternative text
- **WCAG**: 1.1.1, 2.1.1, 1.4.1

### 18. Read More Links
- **Description**: Identifies and evaluates ambiguous link text
- **JS Tests**: Covered in accessible names
- **AI Tests**: Ambiguous link detection
- **WCAG**: 2.4.4, 2.4.9

### 19. Tabindex
- **Description**: Validates tabindex usage and keyboard navigation order
- **JS Tests**: `tabindex.js`
- **AI Tests**: Tab order visual check
- **WCAG**: 2.4.3, 2.1.1

### 20. Title Attributes
- **Description**: Evaluates proper use of title attributes and page titles
- **JS Tests**: `titleAttr.js`, `pageTitle.js`
- **AI Tests**: None
- **WCAG**: 2.4.2, 3.3.2

### 21. Tables
- **Description**: Validates data table structure, headers, and relationships
- **JS Tests**: To be added (`tables.js`)
- **AI Tests**: Table structure analysis, table header detection
- **WCAG**: 1.3.1, 1.3.2

### 22. Timers
- **Description**: Detects and evaluates time limits and session timeouts
- **JS Tests**: None (behavioral detection)
- **AI Tests**: Timer detection, timeout warning
- **WCAG**: 2.2.1, 2.2.3, 2.2.6

### 23. Videos
- **Description**: Checks video accessibility including captions, controls, and audio descriptions
- **JS Tests**: To be added (`video.js`)
- **AI Tests**: Video caption detection, video control accessibility
- **WCAG**: 1.2.1, 1.2.2, 1.2.3, 1.2.5, 1.4.2

## Migration from Categories

### Mapping Table

| Old Category | New Touchpoint |
|-------------|----------------|
| heading/headings | Headings |
| image/images | Images |
| form/forms | Forms |
| landmark/landmarks | Landmarks |
| color | Color Use |
| contrast/colorContrast | Color Contrast |
| focus | Focus Management |
| language/lang | Language |
| button/buttons | Forms |
| link/links | Accessible Names |
| page | Title Attributes |
| title | Title Attributes |
| tabindex | Tabindex |
| aria | Accessible Names |
| svg | Images |
| pdf | Electronic Documents |
| font/fonts | Fonts |
| other | Accessible Names |

### Database Migration

The system maintains backward compatibility:
- **category** field is preserved (legacy support)
- **touchpoint** field is added (new system)
- Migration script available: `scripts/migrate_to_touchpoints.py`

## Implementation Details

### Core Module
Located at: `auto_a11y/core/touchpoints.py`

Key classes:
- **TouchpointID**: Enum of all touchpoint identifiers
- **Touchpoint**: Data class for touchpoint definition
- **TouchpointMapper**: Maps violations and AI findings to touchpoints

### Usage in Code

```python
from auto_a11y.core.touchpoints import TouchpointMapper, get_touchpoint

# Map a violation to touchpoint
touchpoint_id = TouchpointMapper.map_violation_to_touchpoint(violation_dict)

# Get touchpoint details
touchpoint = get_touchpoint(TouchpointID.HEADINGS)
print(touchpoint.name)  # "Headings"
print(touchpoint.wcag_criteria)  # ["1.3.1", "2.4.6"]
```

### In Test Results

Violations and AI findings now include:
```json
{
  "id": "headings_ErrEmptyHeading",
  "category": "heading",  // Legacy field
  "touchpoint": "headings",  // New field
  "description": "Heading is empty",
  "wcag_criteria": ["1.3.1", "2.4.6"]
}
```

## Benefits of Touchpoints

### For Developers
- **Clear organization**: Issues grouped by interaction pattern
- **Better context**: Understanding why something is an issue
- **Actionable fixes**: Touchpoint-specific remediation guidance

### For Testers
- **Comprehensive coverage**: DOM + visual testing combined
- **Reduced duplication**: One touchpoint covers multiple test types
- **WCAG alignment**: Direct mapping to success criteria

### For Users
- **Better accessibility**: More thorough testing coverage
- **Consistent experience**: Issues fixed holistically
- **Complete solutions**: Both technical and visual aspects addressed

## Future Enhancements

### Planned JavaScript Tests
- `lists.js`: List structure validation
- `tables.js`: Data table accessibility
- `video.js`: Video player accessibility

### Additional AI Analysis
- Advanced reading order detection
- Complex interaction pattern analysis
- Dynamic content change detection
- Visual hierarchy validation

### Touchpoint Extensions
- **Audio Content**: Audio player accessibility
- **Charts & Graphs**: Data visualization accessibility
- **Gaming Elements**: Interactive game accessibility
- **Virtual Reality**: VR/AR content accessibility

## API Reference

### Get All Touchpoints
```python
from auto_a11y.core.touchpoints import get_all_touchpoints

touchpoints = get_all_touchpoints()
for tp in touchpoints:
    print(f"{tp.name}: {tp.description}")
```

### Map Error Codes
```python
from auto_a11y.core.touchpoints import TouchpointMapper

# Map specific error code
touchpoint = TouchpointMapper.get_touchpoint_for_error_code('ErrEmptyHeading')
# Returns: TouchpointID.HEADINGS

# Map category
touchpoint = TouchpointMapper.get_touchpoint_for_category('form')
# Returns: TouchpointID.FORMS

# Map AI finding
touchpoint = TouchpointMapper.get_touchpoint_for_ai_type('visual_heading')
# Returns: TouchpointID.HEADINGS
```

### Filter by Touchpoint
```python
# In reporting
violations_by_touchpoint = {}
for violation in test_result.violations:
    tp = violation.touchpoint or 'unknown'
    if tp not in violations_by_touchpoint:
        violations_by_touchpoint[tp] = []
    violations_by_touchpoint[tp].append(violation)
```

## Best Practices

1. **Always assign touchpoints**: Ensure all new violations get touchpoint assignment
2. **Use TouchpointMapper**: Don't hardcode touchpoint assignments
3. **Maintain mappings**: Update mapper when adding new error codes
4. **Document changes**: Update this file when adding touchpoints
5. **Test migrations**: Run migration script in dry-run mode first

## Support

For questions about touchpoints:
1. Check the mapping in `TouchpointMapper` class
2. Review error code definitions in issue catalogs
3. Consult WCAG criteria for touchpoint scope
4. Contact development team for clarifications

## Technical Improvements (Future)

### Pyppeteer Request Interception for Resource Capture

Currently, `test_event_handlers.py` fetches external JavaScript files using `aiohttp` to analyze them for escape key handlers. This works but has limitations:

- Requires separate HTTP requests
- May face CORS restrictions
- Duplicates work the browser already does

**Recommended improvement**: Use Pyppeteer's built-in request interception to capture resources as the browser loads them:

```python
# Example: Capture all JS content as browser loads it
js_content = {}

async def intercept_response(response):
    if response.request.resourceType == 'script':
        try:
            content = await response.text()
            js_content[response.url] = content
        except:
            pass

page.on('response', intercept_response)
await page.goto(url)

# Now js_content contains all loaded JavaScript
all_js = '\n'.join(js_content.values())
```

This approach:
- Captures content as browser naturally loads it
- Avoids CORS issues (browser has already fetched it)
- Works for dynamically loaded scripts
- Can capture other resources too (CSS, images, PDFs, etc.)

**Files to update**: `auto_a11y/testing/touchpoint_tests/test_event_handlers.py`