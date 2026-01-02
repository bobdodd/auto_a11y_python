# Accessibility Test Result Processing Flow Investigation

## Problem Statement

The placeholder `%(animationName)s` is appearing literally in the UI instead of being substituted with the actual animation name like 'spin'. Debug logs show that substitution IS working in the translation wrapper, but somewhere between there and final display, the wrong text (with placeholder) is being used.

## Complete Flow Analysis

### 1. JavaScript Test Execution (test_animations.py)

**File**: `/auto_a11y/testing/touchpoint_tests/test_animations.py`

The JavaScript test detects infinite animations and creates violation data:

```javascript
results.warnings.push({
    err: 'WarnInfiniteAnimationSpinner',
    type: 'warn',
    cat: 'animation',
    element: item.tag,
    xpath: item.xpath,
    html: item.element.outerHTML.substring(0, 200),
    description: `Animation appears to be a loading/busy spinner but runs infinitely without controls`,
    animationCSS: cssLines,
    animationName: item.animation.name  // <-- KEY: Sets actual animation name (e.g., 'spin')
});
```

**Key Point**: The JavaScript correctly extracts the actual animation name and stores it as `animationName` in the violation data.

### 2. Result Processing (result_processor.py)

**File**: `/auto_a11y/testing/result_processor.py`

The ResultProcessor processes JavaScript results in `_process_violation()`:

```python
# Line 443-445: Calls translation wrapper
enhanced_desc = get_detailed_issue_description(violation_id, violation_data)

# Line 497-499: Metadata creation - KEY ISSUE AREA
metadata = {
    'title': test_title if test_title else (original_desc if use_original_as_title else enhanced_desc.get('title', '')),
    'what': original_desc if use_original_as_title else enhanced_desc.get('what', ''),
    'what_generic': generic_what,  # From catalog without placeholder replacement
    'why': enhanced_desc.get('why', ''),
    'who': enhanced_desc.get('who', ''),
    'impact_detail': enhanced_desc.get('impact', ''),
    'wcag_full': wcag_full,
    'full_remediation': enhanced_desc.get('remediation', ''),
    **violation_data,  # Include all original data from JS tests (includes animationName)
    **nested_metadata  # Flatten nested metadata to top level
}
```

**Analysis**: 
- The `enhanced_desc` comes from the translation wrapper with substituted values
- BUT the metadata assignment logic may overwrite these values
- The `**violation_data` spread includes the original `animationName`
- The final `title` and `what` fields in metadata come from `enhanced_desc`

### 3. Database Storage (database.py)

**File**: `/auto_a11y/core/database.py`

Results are stored using a split schema:
- Summary in `test_results` collection
- Individual violations in `test_result_items` collection

Key storage code (lines 445-462):
```python
items.append({
    'test_result_id': test_result_id,
    'page_id': test_result.page_id,
    'test_date': test_result.test_date,
    'item_type': 'violation',
    'issue_id': violation.id,
    'impact': violation.impact.value,
    'touchpoint': violation.touchpoint,
    'xpath': violation.xpath,
    'element': violation.element,
    'html': violation.html,
    'description': violation.description,
    'failure_summary': violation.failure_summary,
    'wcag_criteria': violation.wcag_criteria,
    'help_url': violation.help_url,
    'metadata': violation.metadata  # <-- ALL metadata stored here
})
```

**Analysis**: The complete violation metadata (including substituted descriptions) is stored in the database.

### 4. Data Retrieval (database.py)

When retrieving test results (lines 690-719), the system reconstructs violations:

```python
item_data = {
    'id': item.get('issue_id'),
    'impact': item.get('impact'),
    'touchpoint': item.get('touchpoint'),
    'xpath': item.get('xpath'),
    'element': item.get('element'),
    'html': item.get('html'),
    'description': item.get('description'),
    'metadata': item.get('metadata', {})  # <-- Retrieved as-is
}
```

**Analysis**: Metadata is retrieved exactly as stored.

### 5. Template Enrichment (pages.py)

**File**: `/auto_a11y/web/routes/pages.py`

The critical `enrich_test_result_with_catalog()` function (lines 16-266) processes retrieved violations:

```python
def enrich_test_result_with_catalog(test_result):
    # Line 44-45: CRITICAL - Always re-enrich for translations
    # (Previously skipped if metadata existed, but now re-enriches
    # to support runtime translation)
    
    # Get catalog info for this issue as fallback
    catalog_info = IssueCatalog.get_issue(error_code)
    
    # Only update if we got meaningful enriched data
    if catalog_info and catalog_info.get('description') != f"Issue {error_code} needs documentation":
        # Lines 54-58: Preserve title if it has specific details
        existing_title = violation.metadata.get('title', '')
        has_specific_title = existing_title and any(pattern in existing_title for pattern in [
            '".', '"#', 'missing role=', 'missing aria-',
            'px', ':1', 'alpha=', '°', '%'
        ])

        # Lines 60-64: Get templates from catalog
        title_template = catalog_info.get('title', '') or catalog_info.get('description', '')
        what_template = catalog_info['description']
        why_template = catalog_info['why_it_matters']
        how_template = catalog_info['how_to_fix']

        # Lines 66-84: Build placeholder values
        placeholder_values = {}
        if hasattr(violation, 'metadata') and violation.metadata:
            for key, value in violation.metadata.items():
                if value is not None and not isinstance(value, (dict, list)):
                    placeholder_values[key] = str(value)
                    
        # Lines 93-110: Apply placeholder substitution
        try:
            if not has_specific_title:
                violation.metadata['title'] = title_template % placeholder_values
            if not has_specific_what:
                violation.metadata['what'] = what_template % placeholder_values
            violation.metadata['why'] = why_template % placeholder_values
            violation.metadata['how'] = how_template % placeholder_values
        except (KeyError, ValueError, TypeError) as e:
            # If placeholder replacement fails, use templates as-is
            logger.warning(f"Placeholder substitution failed for {error_code}: {e}")
            if not has_specific_title:
                violation.metadata['title'] = title_template
            if not has_specific_what:
                violation.metadata['what'] = what_template
            violation.metadata['why'] = why_template
            violation.metadata['how'] = how_template
        
        # Line 117: Set generic description WITHOUT placeholders
        violation.metadata['what_generic'] = catalog_info.get('what_generic') or catalog_info.get('description_generic') or catalog_info['description']
```

### 6. Translation Wrapper Analysis

**File**: `/auto_a11y/reporting/issue_descriptions_translated.py`

The debug logs show this is working correctly:

```python
# Lines 69-77: Original description call WITH placeholder replacement
desc = _get_original_description(issue_code, metadata)

# Lines 74-80: Debug logging shows this works
if metadata and 'animationName' in metadata:
    logger.warning(f"DEBUG translate: animationName in metadata = '{metadata.get('animationName')}'")
    if desc and 'title' in desc:
        logger.warning(f"DEBUG translate: title after original = '{desc.get('title', '')[:100]}'")
```

**Key Finding**: The translation wrapper IS correctly substituting placeholders.

### 7. Issue Catalog Source

**File**: `/auto_a11y/reporting/issue_descriptions_enhanced.py` (lines 3036-3045)

```python
'WarnInfiniteAnimationSpinner': {
    'title': "Loading spinner animation '{animationName}' runs infinitely without controls",
    'what': "Loading spinner animation '{animationName}' runs infinitely without controls...",
    'what_generic': "Loading spinner animation runs infinitely without controls",  # NO placeholder
    # ...
}
```

**Critical Discovery**: The catalog has BOTH:
- Templated versions with `{animationName}` placeholders in 'title' and 'what'
- A generic version WITHOUT placeholders in 'what_generic'

## Root Cause Analysis

### The Bug Location

The issue is in `/auto_a11y/web/routes/pages.py` line 117:

```python
violation.metadata['what_generic'] = catalog_info.get('what_generic') or catalog_info.get('description_generic') or catalog_info['description']
```

**Problem**: This line sets `what_generic` to the RAW template from the catalog WITHOUT placeholder substitution. If the template contains `%(animationName)s` and no `what_generic` field exists in the catalog, it falls back to the raw `description` template.

### Template Usage in UI

The templates likely use `what_generic` for grouped accordion headers and other generic displays, while `what` is used for detailed instance views. If the UI is displaying `what_generic`, it will show the raw placeholder.

### Current Flow Issues

1. **Double Processing**: The result_processor.py calls the translation wrapper once during initial processing, but pages.py calls the catalog again during template rendering, potentially overwriting the correctly substituted values.

2. **Template Selection**: The UI may be using `what_generic` (unsubstituted) instead of `what` (substituted) in some contexts.

3. **Inconsistent Metadata**: Different fields in the metadata may have different substitution states.

## Recommended Fixes

### Option 1: Fix what_generic Substitution
```python
# In pages.py, line 117, after placeholder substitution:
generic_template = catalog_info.get('what_generic') or catalog_info.get('description_generic') or catalog_info['description']
try:
    violation.metadata['what_generic'] = generic_template % placeholder_values
except (KeyError, ValueError, TypeError):
    violation.metadata['what_generic'] = generic_template
```

### Option 2: Use Pre-Substituted Values
Stop re-enriching in pages.py if the metadata already has translated/substituted values from the result processor.

### Option 3: Template Field Consistency
Ensure templates consistently use `what` (substituted) instead of `what_generic` (unsubstituted) for displaying issue descriptions.

## Investigation Commands Used

1. Searched for placeholder patterns: `grep -r "animationName\|WarnInfiniteAnimationSpinner" .`
2. Examined JavaScript test output structure
3. Traced database storage and retrieval paths
4. Analyzed translation wrapper debug logs
5. Identified catalog template structure
6. Found template enrichment double-processing

## Next Steps

1. Verify which template field is being used in the UI
2. Implement fix for `what_generic` placeholder substitution
3. Review other similar placeholder issues
4. Add unit tests for placeholder substitution in all contexts