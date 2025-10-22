# Generic Descriptions Guide

## Purpose

This guide explains how to write proper generic descriptions for accessibility issue catalog entries to ensure grouped accordion headers never display instance-specific information.

## The Problem

When multiple instances of the same accessibility issue exist on a page (e.g., 2 duplicate landmarks, 5 empty headings), they are grouped in an outer accordion with individual instances shown in inner accordions.

**UI Principle:** The outer accordion header must show **generic** text that applies to all instances, never specific values like counts, element names, xpaths, or measured values.

### Bad Examples (Specific Information)

❌ "Found 2 <header> elements with role="banner"..." (shows count and element type)
❌ "Found {totalCount} <{element}> elements with role="{role}"..." (shows unreplaced placeholders)
❌ "Text size is 14px..." (shows specific measurement)
❌ "Button at /html/body/div[1]/button..." (shows specific xpath)

### Good Examples (Generic Descriptions)

✅ "Multiple landmarks of the same type exist, but this instance lacks a unique accessible name"
✅ "Heading element contains no text content"
✅ "Text size is below the recommended minimum for comfortable reading"
✅ "Interactive element is missing an accessible name"

---

## Solution: The `what_generic` Field

### Two-Tier Description System

Each catalog entry can have multiple description fields:

1. **`what`** - Instance-specific description (with placeholders like `{totalCount}`, `{element}`)
   - Used for individual instances
   - Placeholders get replaced with actual values
   - Shows specific details

2. **`what_generic`** - Generic description (no placeholders, no specific values)
   - Used for grouped accordion headers
   - Manually written generic text
   - Never shows specific instance details

### Example Catalog Entry

```python
'ErrDuplicateLandmarkWithoutName': {
    'title': "Found {totalCount} {role} landmarks - this one lacks unique accessible name",
    'what': "Found {totalCount} <{element}> elements with role=\"{role}\" on this page, but this instance lacks a unique accessible name to distinguish it from the others",
    'what_generic': "Multiple landmarks of the same type exist, but this instance lacks a unique accessible name to distinguish it from the others",
    'why': "When multiple {role} landmarks exist without unique names, screen reader users cannot distinguish between them...",
    'who': "Screen reader users who navigate by landmarks...",
    'impact': ImpactScale.MEDIUM.value,
    'wcag': ['1.3.1'],
    'remediation': "Add unique aria-label attributes to each {role} landmark..."
},
```

**How it works:**
- Outer accordion uses `what_generic`: "Multiple landmarks of the same type exist..."
- Inner accordion (Instance 1) uses `what` with placeholders replaced: "Found 2 <header> elements with role="banner"..."
- Inner accordion (Instance 2) uses `what` with placeholders replaced: "Found 2 <header> elements with role="banner"..."

---

## Writing Guidelines

### 1. Remove All Specific Values

Generic descriptions should never mention:
- **Counts** (`2 elements`, `{totalCount}`)
- **Specific element types** (`<header>`, `<div>`, `{element}`)
- **Specific roles/values** (`role="banner"`, `{role}`)
- **Measurements** (`14px`, `{fontSize}`)
- **XPaths or selectors**
- **Specific text content** (`"Click here"`, `{linkText}`)

### 2. Use General Language

Instead of specific values, use:
- "Multiple..." instead of "2 ..." or "{count} ..."
- "This element..." instead of "<div>" or "{element}"
- "... of the same type..." instead of "... with role='banner'"
- "... below the recommended minimum..." instead of "... is 14px..."
- "This instance..." instead of "The element at /html/body..."

### 3. Focus on the Issue Type

Describe **what kind of problem it is**, not **which specific element has it**:

❌ "Button at /html/body/main/button[3] has text 'Click here'"
✅ "Interactive element has generic or ambiguous text"

❌ "Found 3 <nav> elements with role='navigation' but 2 lack names"
✅ "Multiple navigation landmarks exist, but some lack unique accessible names"

❌ "Text color #666666 on background #FFFFFF has ratio 3.5:1"
✅ "Text contrast ratio does not meet WCAG requirements"

### 4. Keep It Concise

Generic descriptions should be:
- One or two sentences maximum
- Clear and direct
- Focused on the accessibility issue, not technical details

---

## Examples by Category

### Multiple/Duplicate Issues

**Pattern:** Multiple instances of same element type

```python
# Bad
'what': "Found {count} {elementType} elements on this page"

# Good
'what_generic': "Multiple elements of the same type exist on this page"
```

**Examples:**
- "Multiple landmarks of the same type exist, but this instance lacks a unique accessible name"
- "Multiple headings exist at the top level, but only one should identify the main topic"
- "Multiple navigation regions have identical accessible names"

### Empty/Missing Content Issues

**Pattern:** Element exists but lacks required content

```python
# Bad
'what': "The {elementType} element at {xpath} contains no text"

# Good
'what_generic': "Element contains no text content"
```

**Examples:**
- "Heading element contains no text content"
- "Label element is empty or contains only whitespace"
- "Interactive element is missing an accessible name"

### Measurement/Threshold Issues

**Pattern:** Value doesn't meet threshold

```python
# Bad
'what': "Text size is {fontSize}px, which is below the recommended minimum of 16px"

# Good
'what_generic': "Text size is below the recommended minimum for comfortable reading"
```

**Examples:**
- "Text size is below the recommended minimum for comfortable reading"
- "Text contrast ratio does not meet WCAG requirements"
- "Focus indicator outline is not sufficiently visible"

### Structure/Hierarchy Issues

**Pattern:** Order or structure is wrong

```python
# Bad
'what': "Heading structure jumps from h{from} to h{to}, skipping h{expected}"

# Good
'what_generic': "Heading structure skips intermediate levels, breaking document hierarchy"
```

**Examples:**
- "Heading structure skips intermediate levels, breaking document hierarchy"
- "Tab order does not follow visual reading order"
- "First heading should be h1 but is a different level"

### Attribute/Markup Issues

**Pattern:** Wrong or missing attribute/markup

```python
# Bad
'what': "The {elementType} element uses onclick but lacks tabindex"

# Good
'what_generic': "Interactive element has mouse event handler but is not keyboard accessible"
```

**Examples:**
- "Interactive element has mouse event handler but is not keyboard accessible"
- "Element references non-existent ID in ARIA attribute"
- "Form control lacks associated label"

---

## When to Add `what_generic`

### High Priority (Must Have)

Add `what_generic` when the issue is **likely to appear multiple times** on a page:

- ✅ Element-level checks (empty headings, missing alt text, etc.)
- ✅ Multiple/duplicate patterns (`ErrMultiple*`, `ErrDuplicate*`)
- ✅ Discovery items (`Disco*` codes)
- ✅ Any issue with placeholders in `what` field

### Lower Priority (Nice to Have)

Less urgent for:

- ⚠️ Page-level checks (no page title, no h1) - only one per page
- ⚠️ Issues that rarely group (unique edge cases)

### Not Needed

Skip `what_generic` when:

- ❌ `what` field has no placeholders
- ❌ Issue can only occur once per page
- ❌ Issue is discovery/informational and grouping doesn't matter

---

## Implementation Process

### For New Catalog Entries

When adding a new catalog entry:

1. Write the `what` field with placeholders for specific values
2. Immediately write `what_generic` field with generic text
3. Ensure `what_generic` follows all guidelines above

```python
'NewErrorCode': {
    'title': "...",
    'what': "Found {count} {elementType} elements...",  # With placeholders
    'what_generic': "Multiple elements of this type...",  # Generic version
    'why': "...",
    'who': "...",
    'impact': ImpactScale.HIGH.value,
    'wcag': ['...'],
    'remediation': "..."
},
```

### For Existing Catalog Entries

To add `what_generic` to existing entry:

1. Identify entries with placeholders in `what`:
   ```bash
   grep "'what':" auto_a11y/reporting/issue_descriptions_enhanced.py | grep "{"
   ```

2. For each entry, write generic version following guidelines

3. Add `what_generic` field after `what` field in catalog:
   ```python
   'ExistingCode': {
       'title': "...",
       'what': "Found {count}...",  # Keep existing
       'what_generic': "Multiple...",  # Add this line
       'why': "...",
       # ... rest unchanged
   },
   ```

4. Test by running affected fixtures to ensure both versions work

---

## Testing

### Manual Testing

1. Create a test page with multiple instances of the issue
2. Run accessibility test
3. Check the page results view:
   - Outer accordion should show `what_generic` text
   - Inner accordions should show `what` text with values replaced

### Fixture Testing

The fixture system validates that tests correctly identify issues. After adding `what_generic`:

```bash
# Test specific error code
python test_fixtures.py --code ErrYourCode

# Test entire category
python test_fixtures.py --category YourCategory
```

---

## Code Flow

### How `what_generic` Gets Used

1. **Test runs** - JavaScript/Python test finds issues, creates violations
2. **Result processing** ([result_processor.py](../auto_a11y/testing/result_processor.py:446-450))
   ```python
   # Get instance-specific description (placeholders replaced)
   enhanced_desc = get_detailed_issue_description(violation_id, violation_data)

   # Get generic description (what_generic preferred, or what without placeholders)
   generic_desc = get_detailed_issue_description(violation_id, {})
   generic_what = generic_desc.get('what_generic') or generic_desc.get('what', '')

   metadata = {
       'what': enhanced_desc.get('what'),  # Specific
       'what_generic': generic_what,  # Generic
       # ...
   }
   ```

3. **Template rendering** ([view.html](../auto_a11y/web/templates/pages/view.html))
   ```jinja2
   {% if group_list|length > 1 %}
       {# Multiple instances - use generic description #}
       {{ first_violation.metadata.what_generic }}
   {% else %}
       {# Single instance - use specific description #}
       {{ first_violation.metadata.what }}
   {% endif %}
   ```

---

## Common Mistakes

### ❌ Mistake 1: Leaving Placeholders in what_generic

```python
# WRONG
'what_generic': "Found {count} elements..."  # Still has placeholder!

# RIGHT
'what_generic': "Multiple elements exist..."  # No placeholders
```

### ❌ Mistake 2: Too Specific

```python
# WRONG
'what_generic': "Header element at top of page lacks unique name"  # Too specific about location

# RIGHT
'what_generic': "Landmark element lacks unique accessible name"  # Generic
```

### ❌ Mistake 3: Just Removing Values

```python
# WRONG - Just removed the count but kept structure
'what_generic': "Found multiple <header> elements with role='banner'..."  # Still mentions header and banner

# RIGHT - Rewrote to be truly generic
'what_generic': "Multiple landmarks of the same type exist..."
```

### ❌ Mistake 4: Too Vague

```python
# WRONG - Too vague, doesn't describe the issue
'what_generic': "Accessibility issue detected"

# RIGHT - Generic but still descriptive
'what_generic': "Landmark element lacks unique accessible name"
```

---

## Summary

### Quick Checklist

When adding `what_generic`:

- [ ] Removed all counts, measurements, specific values
- [ ] Removed all element-specific references
- [ ] Removed all xpath/location references
- [ ] Used general language ("multiple...", "this element...")
- [ ] Focused on the issue type, not specific instance
- [ ] Kept it concise (1-2 sentences)
- [ ] Tested with grouped accordion display
- [ ] Verified no unreplaced placeholders show in UI

### Key Principles

1. **Generic applies to all instances** - Text should be true for every instance in the group
2. **No specific values** - Never mention counts, elements, locations, measurements
3. **Descriptive but general** - Explain the issue type without instance details
4. **Properly written prose** - Not template strings with unreplaced placeholders

---

## Related Documentation

- [Latest Test Results UI](./LATEST_TEST_RESULTS_UI.md) - Complete UI documentation
- [Issue Catalog](./ISSUE_CATALOG_BY_TOUCHPOINT.md) - Master catalog of all issues
- [Fixture System](./FIXTURE_SYSTEM_REDESIGN.md) - Testing framework

---

## Questions?

If you're unsure whether a description is sufficiently generic, ask:

1. Does it mention any specific values that change between instances?
2. Could I use this exact text for ALL instances in a group?
3. Would this make sense if I saw 10 instances grouped under it?

If the answer to #1 is yes, or #2 or #3 is no, it's not generic enough.
