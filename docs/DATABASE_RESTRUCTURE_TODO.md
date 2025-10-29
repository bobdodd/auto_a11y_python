# Database Restructure Implementation - TODO List

**Created:** 2025-10-27
**Issue:** MongoDB 16MB document limit with ~17,000 violations per page
**Solution:** Split test results into summary + detailed items collections

---

## Implementation Checklist

### Phase 1: Create New Collections & Indexes ✅ COMPLETE
- [x] Create `test_result_items` collection in Database class
- [x] Add indexes for `test_result_items`:
  - [x] `test_result_id` (primary lookup)
  - [x] `page_id, test_date` (for page history)
  - [x] `item_type, test_result_id` (for filtering violations/warnings)
  - [x] `issue_id, test_result_id` (for issue-specific queries)
  - [x] `touchpoint, test_result_id` (for touchpoint reports)
  - [x] Compound index: `test_result_id, item_type, issue_id`
- [x] Test index creation on clean database

**Result:** All 7 indexes created successfully. Collection ready for use.

### Phase 2: Update Database Layer - Write Path ✅ COMPLETE
- [x] Update `Database.__init__()` to add `test_result_items` collection
- [x] Create `_create_test_result_items()` helper method
  - [x] Takes test_result_id and TestResult object
  - [x] Converts violations array to individual documents
  - [x] Converts warnings array to individual documents
  - [x] Converts info array to individual documents
  - [x] Converts discovery array to individual documents
  - [x] Converts passes array to individual documents
  - [x] Batch insert items using `insert_many()`
- [x] Update `create_test_result()` method:
  - [x] Create summary document (counts only, no arrays)
  - [x] Insert summary document first
  - [x] Get inserted test_result_id
  - [x] Call `_create_test_result_items()` with items
  - [x] Handle errors gracefully (if items fail, summary still exists)
- [x] Add `_has_detailed_items: true` flag to summary documents
- [x] Test write path with small test result (2 violations)
- [x] Test write path with large test result (1000 violations)

**Result:** Successfully created test with 1000 violations. Old schema would have failed at ~60MB. New schema: 1 summary doc + 1000 item docs = no size limit!

### Phase 3: Update Database Layer - Read Path ✅ COMPLETE
- [x] Create `_get_test_result_items()` helper method
  - [x] Takes test_result_id and optional item_type filter
  - [x] Queries `test_result_items` collection
  - [x] Returns items as dictionaries
- [x] Update `get_test_result()` method:
  - [x] Get summary document
  - [x] Check if `_has_detailed_items` flag exists
  - [x] If true: load items from `test_result_items`
  - [x] If false: use old arrays from summary (backward compat)
  - [x] Construct TestResult object with all data
- [x] Update `get_latest_test_result()` method (same logic)
- [x] Test read path with new schema test results
- [x] Test read path with old schema test results (backward compat)

**Result:** Successfully read back test result with 1000 violations. All data preserved. Backward compatibility maintained.

### Phase 4: Update Models ⏳
- [ ] Review `TestResult` model in `models/test_result.py`
- [ ] Ensure `to_dict()` works with both schemas
- [ ] Ensure `from_dict()` works with both schemas
- [ ] Add `_has_detailed_items` field handling
- [ ] Test model serialization/deserialization

### Phase 5: Update Query Methods ⏳
- [ ] Create `get_violations_by_issue()` method
  - [ ] Query `test_result_items` by issue_id
  - [ ] Return grouped violations
- [ ] Create `get_violations_by_touchpoint()` method
  - [ ] Query `test_result_items` by touchpoint
  - [ ] Return grouped violations
- [ ] Create `count_violations_by_type()` aggregation method
  - [ ] Use MongoDB aggregation pipeline
  - [ ] Group by issue_id, count occurrences
- [ ] Update `get_project_stats()` to work with new schema
- [ ] Update `get_website_stats()` to work with new schema

### Phase 6: Update Reporting Layer ⏳
- [ ] Review `ReportGenerator` class
- [ ] Update to fetch items from new collection
- [ ] Implement deduplication at render time:
  - [ ] Group violations by issue_id
  - [ ] Count occurrences
  - [ ] Keep first 10 as samples
  - [ ] Display: "ErrTextContrastAA: 5,234 instances" + samples
- [ ] Update HTML report generation
- [ ] Update JSON report generation
- [ ] Update CSV report generation
- [ ] Test reports with high-violation pages

### Phase 7: Migration Script ⏳
- [ ] Create `scripts/migrate_test_results_to_items.py`
- [ ] Script steps:
  - [ ] Connect to MongoDB
  - [ ] Find all test_results with violations/warnings arrays
  - [ ] For each test result:
    - [ ] Check if already migrated (`_has_detailed_items` flag)
    - [ ] If not migrated:
      - [ ] Extract violations/warnings/etc arrays
      - [ ] Create item documents
      - [ ] Insert into `test_result_items`
      - [ ] Update summary with `_has_detailed_items: true`
      - [ ] Optionally remove old arrays (save space)
    - [ ] Log progress every 100 records
    - [ ] Handle errors gracefully
  - [ ] Report migration statistics
- [ ] Add dry-run mode
- [ ] Add progress bar
- [ ] Test migration on sample data

### Phase 8: Handle ErrSizeLimitExceeded Pages ⏳
- [ ] Find all pages with `ErrSizeLimitExceeded` error
- [ ] Create script to re-test these pages
- [ ] Verify new results stored successfully
- [ ] Delete old error-only results
- [ ] Update page statistics

### Phase 9: Testing & Validation ⏳
- [ ] Test with page that has 100 violations
- [ ] Test with page that has 1,000 violations
- [ ] Test with page that has 10,000 violations
- [ ] Test with page that has 17,000+ violations (known failure case)
- [ ] Verify no MongoDB DocumentTooLarge errors
- [ ] Verify all raw data preserved
- [ ] Verify reporting shows deduplicated view
- [ ] Performance test: query time for large result sets
- [ ] Performance test: write time for large result sets
- [ ] Storage analysis: compare old vs new schema size

### Phase 10: Update Web UI ⏳
- [ ] Update page detail view to handle new schema
- [ ] Update violation list rendering
- [ ] Update touchpoint breakdown
- [ ] Update issue count displays
- [ ] Test all web pages that display test results

### Phase 11: Documentation ⏳
- [ ] Update ARCHITECTURE.md with new schema
- [ ] Document new database methods
- [ ] Add migration instructions to README
- [ ] Document deduplication strategy
- [ ] Add troubleshooting guide

### Phase 12: Cleanup (Optional) ⏳
- [ ] Remove old violation/warning arrays from migrated documents
- [ ] Archive or delete old error-only results
- [ ] Optimize indexes based on actual query patterns
- [ ] Monitor storage usage over time

---

## Progress Tracking

**Started:** 2025-10-28
**Last Updated:** 2025-10-28
**Current Phase:** Phase 4 - Update Models (Phase 1-3 Complete!)
**Overall Progress:** 3/12 phases complete (25%)

---

## Notes & Decisions

### Design Decisions Made:
1. ✅ No deduplication at storage time - preserve all raw data
2. ✅ Split into two collections: summary + items
3. ✅ Each violation/warning = separate document
4. ✅ Backward compatible during migration
5. ✅ Deduplication only at reporting layer

### Issues Encountered:
- [To be filled in during implementation]

### Performance Metrics:
- [To be filled in during testing]

---

## Rollback Plan

If issues occur during implementation:

1. **Phase 1-2 (Write Path):**
   - New writes go to new schema
   - Old data still readable
   - Can pause new schema writes, continue with old

2. **Phase 3-4 (Read Path):**
   - Backward compatibility ensures old data readable
   - Can toggle between schemas with feature flag

3. **Phase 7 (Migration):**
   - Migration script has dry-run mode
   - Can pause/resume migration
   - Original data preserved until explicitly deleted

4. **Emergency Rollback:**
   - Revert code changes via git
   - Keep new collection (no harm if exists)
   - System continues with old schema

---

## Success Criteria

- [ ] Pages with 17,000+ violations store successfully
- [ ] No MongoDB DocumentTooLarge errors
- [ ] All raw data preserved (spot check samples)
- [ ] Query performance < 1 second for typical pages
- [ ] Write performance < 5 seconds for 10,000 violations
- [ ] Reports show clean deduplicated view
- [ ] Backward compatibility maintained
- [ ] Zero data loss during migration
- [ ] Storage overhead < 20%

---

## Estimated Timeline

- Phase 1: 1 hour
- Phase 2: 3 hours
- Phase 3: 3 hours
- Phase 4: 1 hour
- Phase 5: 2 hours
- Phase 6: 4 hours
- Phase 7: 2 hours
- Phase 8: 1 hour
- Phase 9: 3 hours
- Phase 10: 2 hours
- Phase 11: 1 hour
- Phase 12: 1 hour

**Total: ~24 hours (3 days)**

---

**See also:** [DATABASE_RESTRUCTURE_DESIGN.md](DATABASE_RESTRUCTURE_DESIGN.md) for detailed schema design
