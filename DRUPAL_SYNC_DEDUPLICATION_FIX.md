# Drupal Sync Deduplication Fix

## Problem Summary

When syncing automated test results to Drupal, the system was:
1. ✅ Correctly identifying common components
2. ✅ Correctly deduplicating violations by component
3. ❌ **Then uploading ALL violations anyway without using the deduplication**

This resulted in thousands of duplicate issues being uploaded to Drupal instead of the deduplicated set.

## Root Cause

In `auto_a11y/web/routes/drupal_sync.py`, lines 904-1037, the code had this problematic pattern:

```python
# Step 1: Deduplicate violations (CORRECT)
deduped_violations = deduplicate_violations_for_upload(report_data)
# Returns: {dedup_key: {'violation': violation_obj, 'affected_pages': [...]}}

# Step 2: Upload issues (INCORRECT - ignored deduplication!)
for dedup_key, entry in deduped_violations.items():
    for page_result in website_data_item.get('pages', []):  # ❌ Looping through pages again!
        for violation in all_violations:  # ❌ Looping through ALL violations!
            # Upload every single violation
```

**The bug**: After creating the deduplicated dict, the code ignored it and looped through all pages and all violations again, uploading everything.

## The Fix

Changed the upload loop to use the deduplicated entries directly:

```python
# Step 1: Deduplicate violations (CORRECT)
deduped_violations = deduplicate_violations_for_upload(report_data)

# Step 2: Upload ONLY deduplicated issues (FIXED!)
for dedup_key, entry in deduped_violations.items():
    # Extract the representative violation from the dedup entry
    violation = entry['violation']  # ✅ Single representative instance
    affected_pages = entry['affected_pages']  # ✅ List of all pages with this issue
    page_url = entry['page_url']  # ✅ Representative page URL

    # Upload once per unique issue (not once per page!)
    result = issue_exporter.export_issue(...)
```

## Deduplication Logic

The deduplication follows the same logic as the offline Excel/HTML reports:

### For Component Issues (discovered_page_id exists):
- **Dedup key**: `(discovered_page_id, violation_id, impact)`
- **Result**: One issue per component, with a list of affected pages
- **Example**: "Form (3 fields) signature abc123" appears on 5 pages → 1 issue with 5 affected pages

### For Page-Specific Issues (no discovered_page_id):
- **Dedup key**: `(violation_id, xpath, impact, page_url)`
- **Result**: One issue per unique violation location
- **Example**: Broken link at specific xpath on specific page → 1 issue for that page

## Benefits

### Before Fix:
- 17,000 violations on 10 pages → **17,000 issues uploaded to Drupal**
- Impossible to manage
- Duplicates the same component issue hundreds of times

### After Fix:
- 17,000 violations on 10 pages with 50 common components → **~200 issues uploaded to Drupal**
  - 50 component issues (each appearing on multiple pages)
  - ~150 page-specific issues
- Manageable issue count
- Each component issue includes list of affected pages

## Additional Enhancement

Added affected pages list to component issues:

```python
# Add information about affected pages to description if this is a component issue
if len(affected_pages) > 1:
    description += f"\n\n<h3>Affected Pages</h3>\n<p>This issue appears on {len(affected_pages)} pages:</p>\n<ul>\n"
    for page in affected_pages:
        description += f"<li>{html_module.escape(page)}</li>\n"
    description += "</ul>"
```

This makes it clear in Drupal which pages are affected by each component issue.

## Testing

To verify the fix:
1. Run automated tests on a project with common components
2. Sync to Drupal using the automated test filters
3. Check that:
   - Common component pages are created
   - Issues are deduplicated by component
   - Each component issue shows all affected pages
   - Total issue count matches the deduplicated offline report

## Files Modified

- `auto_a11y/web/routes/drupal_sync.py` (lines 904-1037)
  - Fixed the upload loop to use deduplicated violations
  - Added affected pages list to component issues

## Related Code

The deduplication logic is consistent with:
- `auto_a11y/reporting/formatters.py` - Excel/HTML report deduplication (lines 1944-2069)
- `auto_a11y/reporting/deduplication_service.py` - Component extraction service
- Offline deduplicated report generation

## Date
2025-12-01
