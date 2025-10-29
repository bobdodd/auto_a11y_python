# Maps Testing Requirements

## Overview
Maps testing must distinguish between interactive and non-interactive maps, each with different accessibility requirements.

## Interactive vs Non-Interactive Maps

### Interactive Maps
**Definition**: Maps containing elements that can receive keyboard focus through:
- Semantic HTML elements (buttons, links, inputs)
- Interactive ARIA roles
- Elements with tabindex explicitly set

**Critical Requirements**:
1. **CANNOT have aria-hidden="true"** 
   - Violation: WCAG 1.3.1 Info and Relationships (Level A)
   - Creates "silent focus trap" - users can tab to elements but get no screen reader feedback
   
2. **CANNOT have role="presentation"**
   - Violation: WCAG 4.1.2 Name, Role, Value (Level A)
   - Removes semantic meaning while elements remain focusable

3. **Warning for potential content hiding**
   - Warning: WCAG 1.1.1 Non-text Content (Level A) - AT RISK
   - Cannot automatically verify if map information is provided elsewhere

### Non-Interactive Maps
Maps without focusable elements can have aria-hidden or role="presentation" if equivalent information is provided elsewhere.

## Naming Requirements

### Iframe Maps
**Must have accessible name via:**
- title attribute
- aria-label attribute
- aria-labelledby attribute

**Violation if missing**: WCAG 4.1.2 Name, Role, Value (Level A)

### SVG Maps
**Must have accessible name via:**
- `<title>` element as first child
- aria-label attribute
- aria-labelledby attribute
- Proper role attribute (role="img" or role="graphics-document")

**Violation if missing**: WCAG 4.1.2 Name, Role, Value (Level A)

### Div-based Maps (Collection of Elements)
**Must have proper structure:**
- **Best**: Contained within a landmark region with descriptive label
- **Acceptable**: Preceded by an appropriate heading describing the map

**Violations**:
- No landmark AND no heading: FAIL - WCAG 1.3.1 Info and Relationships (Level A)
- No landmark but has heading: WARNING - Best practice issue

## Quality of Names

### Meaningful Names Required
- Names must be descriptive, not generic
- Fail examples: "map", "image", "graphic"
- Pass examples: "Map of downtown Seattle", "Office location map"

## Test Cases to Implement

### 1. Interactive Map Tests
- [ ] Detect focusable elements within maps
- [ ] Flag aria-hidden on interactive maps as FAIL (1.3.1)
- [ ] Flag role="presentation" on interactive maps as FAIL (4.1.2)
- [ ] Issue warning about potential 1.1.1 violation

### 2. Naming Tests
- [ ] Check iframe maps for title/aria-label/aria-labelledby
- [ ] Check SVG maps for proper naming and role
- [ ] Check div-based maps for landmark or heading structure
- [ ] Validate names are meaningful (not generic)

### 3. Structure Tests
- [ ] Detect if div-based map is in landmark
- [ ] Detect if div-based map has associated heading
- [ ] Proper severity assignment (FAIL vs WARNING)

## Implementation Tasks

1. **Enhance Interactivity Detection**
   - Scan map contents for focusable elements
   - Check for tabindex attributes
   - Detect interactive ARIA roles

2. **Improve Naming Validation**
   - Generic name detection
   - Meaningful name heuristics

3. **Add Structure Detection**
   - Landmark detection for div maps
   - Heading association logic

4. **Update Violation Mapping**
   - Correct WCAG references
   - Proper severity levels
   - Clear remediation for each scenario