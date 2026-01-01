# Cleanup Plan: Remove Categories, Use Touchpoints Only

**Created:** 2026-01-01  
**Status:** In Progress  
**Purpose:** Remove the legacy "category" system and use only "touchpoints" for grouping accessibility tests and results.

## Background

The codebase originally used a `cat:` (category) field in test results to group errors. Later, a more developer-centric "touchpoint" system was introduced, but it became an overlay rather than a replacement. This cleanup will remove the category system entirely.

## Current State

- **Categories**: Old grouping system using values like `heading`, `img`, `form`, `landmark`, etc.
- **Touchpoints**: New grouping system using IDs like `headings`, `images`, `forms`, `landmarks`, etc.
- **Mapping**: `TouchpointMapper` in `touchpoints.py` translates categories to touchpoints
- **Hybrid**: Both systems coexist, causing confusion and maintenance overhead

## Cleanup Phases

### Phase 1: Python Test Files (Low Risk)
**Status:** Pending

Update `cat:` values in Python touchpoint tests (`auto_a11y/testing/touchpoint_tests/`) to use touchpoint IDs instead of old category names.

**Files to update:**
- All `test_*.py` files in `auto_a11y/testing/touchpoint_tests/`

**Change pattern:**
```python
# Before
'cat': 'heading'  # old category name

# After  
'cat': 'headings'  # touchpoint ID
```

**Rollback:** `git revert <commit>`

---

### Phase 2: Result Processor (Medium Risk)
**Status:** Pending

Simplify `result_processor.py` to use touchpoint directly without category fallback logic.

**File:** `auto_a11y/testing/result_processor.py`

**Changes:**
- Remove category-to-touchpoint translation logic
- Use touchpoint ID directly from test results

**Rollback:** `git revert <commit>`

---

### Phase 3: Remove Legacy JS Test Files (Low Risk)
**Status:** Pending

Since all tests are now Python-based, archive or remove the JS test files entirely.

**Directory:** `auto_a11y/scripts/tests/`

**Files to remove/archive:**
- `headings.js`, `images.js`, `forms2.js`, `landmarks.js`, etc.
- Keep only utility scripts: `accessibleName.js`, `ariaRoles.js`, `colorContrast.js`, `xpath.js`

**Rollback:** `git revert <commit>` or restore from git history

---

### Phase 4: Clean Up Mapping Code (Low Risk)
**Status:** Pending

Remove `CATEGORY_TO_TOUCHPOINT` mapping from `touchpoints.py` once nothing uses categories.

**File:** `auto_a11y/core/touchpoints.py`

**Changes:**
- Remove `CATEGORY_TO_TOUCHPOINT` dictionary
- Remove `get_touchpoint_for_category()` method
- Remove any category-related helper functions

**Rollback:** `git revert <commit>`

---

### Phase 5: Database Migration (Higher Risk - Optional)
**Status:** Pending

Migrate any stored data with old category values to touchpoints.

**Considerations:**
- Check MongoDB collections for `category` fields
- May need migration script
- Consider backward compatibility for historical data

**Rollback:** Database restore from backup

---

## Commit Strategy

All commits will use the `CLEANUP:` prefix for easy identification:
```
CLEANUP: Phase 1 - Update cat values in Python test files
CLEANUP: Phase 2 - Simplify result_processor category handling
CLEANUP: Phase 3 - Remove legacy JS test files
CLEANUP: Phase 4 - Remove CATEGORY_TO_TOUCHPOINT mapping
```

## Verification Steps

After each phase:
1. Run the test suite
2. Test against demo website
3. Verify reports group correctly by touchpoint
4. Check web UI filtering works

## Rollback Commands

If issues arise, revert specific phases:
```bash
# Find cleanup commits
git log --oneline --grep="CLEANUP:"

# Revert a specific commit
git revert <commit-hash>

# Revert multiple commits (oldest to newest order)
git revert <oldest-commit>..<newest-commit>
```

## Files Reference

### Python Test Files (Phase 1)
- `auto_a11y/testing/touchpoint_tests/test_*.py`

### Result Processing (Phase 2)
- `auto_a11y/testing/result_processor.py`

### JS Test Files (Phase 3)
- `auto_a11y/scripts/tests/*.js`

### Touchpoint Configuration (Phase 4)
- `auto_a11y/core/touchpoints.py`
- `auto_a11y/config/touchpoint_tests.py`

### Other Related Files
- `auto_a11y/models/test_result.py`
- `auto_a11y/reporting/comprehensive_report.py`
- `scripts/migrate_to_touchpoints.py`
