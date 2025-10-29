# Database Restructure Design: Handling Large Test Results

**Date:** 2025-10-27
**Issue:** MongoDB 16MB document limit exceeded with ~17,000 violations per page
**Requirement:** Preserve ALL raw data, no deduplication at storage time

---

## Current Schema (BROKEN)

### test_results Collection
```javascript
{
  _id: ObjectId,
  page_id: string,
  test_date: ISODate,
  duration_ms: number,
  violations: [      // ← PROBLEM: Can be 17,000+ items = 60+ MB
    {
      id: string,
      impact: string,
      description: string,
      xpath: string,
      html: string,     // HTML snippet
      element: string,
      touchpoint: string,
      wcag_criteria: []
    }
  ],
  warnings: [],       // Similar structure
  info: [],
  discovery: [],
  passes: [],
  ai_findings: [],
  screenshot_path: string
}
```

**Problems:**
- Single document contains ALL violations
- Pages with 17,000+ violations = 60MB+ document
- MongoDB limit: 16MB
- Result: Data lost, `ErrSizeLimitExceeded` error

---

## New Schema (SOLUTION)

### Principle
**Split test results into multiple collections:**
- **Summary data** (counts, metadata) in `test_results`
- **Individual findings** (violations, warnings, etc.) in `test_result_items`
- Each item is a separate document
- No single document exceeds 16MB
- ALL raw data preserved

---

### 1. test_results Collection (Summary)
```javascript
{
  _id: ObjectId("result_123"),
  page_id: "page_456",
  test_date: ISODate("2025-10-27T12:00:00Z"),
  duration_ms: 5000,

  // COUNTS ONLY (not arrays)
  violation_count: 17165,
  warning_count: 972,
  info_count: 2,
  discovery_count: 152,
  pass_count: 17,

  // AI findings (usually small, can stay here)
  ai_findings: [],

  // Screenshot info
  screenshot_path: "/path/to/screenshot.jpg",

  // Metadata
  test_run_id: "run_789",
  status: "completed",

  // NEW: References to detailed items
  _has_detailed_items: true,
  _items_collection: "test_result_items"
}
```

**Size:** ~1-2 KB (regardless of violation count)

---

### 2. test_result_items Collection (Detailed Findings)

Each violation/warning/etc. is a **separate document**:

```javascript
{
  _id: ObjectId("item_001"),
  test_result_id: ObjectId("result_123"),  // Links back to summary
  page_id: "page_456",                     // Denormalized for queries
  test_date: ISODate("2025-10-27T12:00:00Z"), // Denormalized for queries

  // Item type
  item_type: "violation",  // or "warning", "info", "discovery", "pass"

  // Issue details
  issue_id: "ErrTextContrastAA",
  impact: "high",
  touchpoint: "colors_contrast",

  // Location
  xpath: "/html/body/div[1]/p[5]",
  element: "P",
  html: "<p style='color:#777'>Text</p>",

  // Description
  description: "Text has insufficient contrast (2.5:1)",
  failure_summary: "Fix contrast ratio to meet WCAG AA",

  // WCAG
  wcag_criteria: ["1.4.3"],
  help_url: "https://www.w3.org/WAI/WCAG21/quickref/#contrast-minimum",

  // Metadata
  metadata: {
    contrast_ratio: 2.5,
    foreground: "#777777",
    background: "#ffffff"
  }
}
```

**Size:** ~500 bytes - 2 KB per item
**Total for 17,000 items:** ~8.5 - 34 MB (spread across 17,000 documents)

---

### 3. Indexes (Critical for Performance)

```javascript
// test_result_items indexes
db.test_result_items.createIndex({test_result_id: 1})
db.test_result_items.createIndex({page_id: 1, test_date: -1})
db.test_result_items.createIndex({item_type: 1, test_result_id: 1})
db.test_result_items.createIndex({issue_id: 1, test_result_id: 1})
db.test_result_items.createIndex({touchpoint: 1, test_result_id: 1})

// Compound indexes for common queries
db.test_result_items.createIndex({
  test_result_id: 1,
  item_type: 1,
  issue_id: 1
})
```

---

## Data Access Patterns

### Writing Test Results
```python
def create_test_result(test_result: TestResult) -> str:
    # 1. Create summary document
    summary = {
        'page_id': test_result.page_id,
        'test_date': test_result.test_date,
        'violation_count': len(test_result.violations),
        'warning_count': len(test_result.warnings),
        # ... other counts
        '_has_detailed_items': True
    }
    result = db.test_results.insert_one(summary)
    test_result_id = result.inserted_id

    # 2. Create individual item documents (batch insert)
    items = []

    for violation in test_result.violations:
        items.append({
            'test_result_id': test_result_id,
            'page_id': test_result.page_id,
            'test_date': test_result.test_date,
            'item_type': 'violation',
            'issue_id': violation.id,
            'impact': violation.impact,
            # ... all violation data
        })

    for warning in test_result.warnings:
        items.append({
            'test_result_id': test_result_id,
            'item_type': 'warning',
            # ... all warning data
        })

    # Batch insert (MongoDB can handle 1000s of documents efficiently)
    if items:
        db.test_result_items.insert_many(items, ordered=False)

    return str(test_result_id)
```

### Reading Test Results
```python
def get_test_result(result_id: str) -> TestResult:
    # 1. Get summary
    summary = db.test_results.find_one({'_id': ObjectId(result_id)})

    # 2. Get detailed items (only if needed)
    violations = list(db.test_result_items.find({
        'test_result_id': ObjectId(result_id),
        'item_type': 'violation'
    }))

    warnings = list(db.test_result_items.find({
        'test_result_id': ObjectId(result_id),
        'item_type': 'warning'
    }))

    # ... construct TestResult object
    return TestResult(...)
```

### Querying by Issue Type (for Reports)
```python
# Get all contrast violations for a page
violations = db.test_result_items.find({
    'page_id': page_id,
    'item_type': 'violation',
    'issue_id': 'ErrTextContrastAA'
})

# Get violation counts by issue type (aggregation)
pipeline = [
    {'$match': {'test_result_id': ObjectId(result_id), 'item_type': 'violation'}},
    {'$group': {'_id': '$issue_id', 'count': {'$sum': 1}}},
    {'$sort': {'count': -1}}
]
counts = db.test_result_items.aggregate(pipeline)
```

---

## Migration Strategy

### Phase 1: Add New Collections (Non-Breaking)
1. Create `test_result_items` collection
2. Add indexes
3. Update `Database` class to have both old and new logic
4. New test results use new schema
5. Old test results remain readable

### Phase 2: Dual-Write Period
1. Write to BOTH old schema (if it fits) AND new schema
2. Read attempts old schema first, falls back to new
3. Monitor for issues

### Phase 3: Migration Script
1. For existing test results that fit in 16MB:
   - Read from `test_results` collection
   - Extract violations/warnings/etc.
   - Write to `test_result_items`
   - Update summary document
2. For `ErrSizeLimitExceeded` results:
   - Already in error state, can be reprocessed

### Phase 4: Switch Over
1. Update read logic to use new schema first
2. Stop writing to old schema format
3. Deprecate old array fields

### Phase 5: Cleanup (Optional)
1. Remove old `violations`, `warnings` arrays from `test_results`
2. Keep only summary counts

---

## Benefits

### 1. No Data Loss
- ALL raw violations stored, even 17,000+
- No truncation, no sampling at storage time
- MongoDB limit never hit (each item < 16MB)

### 2. Flexible Querying
- Query by issue type without loading all violations
- Aggregate counts efficiently
- Filter by touchpoint, impact, etc.

### 3. Scalable
- Pages with 100 violations: Works fine
- Pages with 100,000 violations: Works fine
- No architectural changes needed later

### 4. Efficient Storage
- MongoDB stores related documents efficiently
- WiredTiger compression still applies
- Indexes enable fast queries

### 5. Backward Compatible (During Migration)
- Old test results still readable
- New results use better schema
- Gradual migration possible

---

## Deduplication (Reporting Layer Only)

Deduplication happens at **report generation time**, not storage:

```python
def generate_report(test_result_id):
    # Get all violations (raw data)
    violations = db.test_result_items.find({
        'test_result_id': ObjectId(test_result_id),
        'item_type': 'violation'
    })

    # Group by issue_id for display
    grouped = {}
    for v in violations:
        key = v['issue_id']
        if key not in grouped:
            grouped[key] = {
                'issue_id': key,
                'count': 0,
                'samples': [],
                'touchpoint': v['touchpoint'],
                'impact': v['impact']
            }

        grouped[key]['count'] += 1

        # Keep first 10 as samples
        if len(grouped[key]['samples']) < 10:
            grouped[key]['samples'].append({
                'xpath': v['xpath'],
                'html': v['html'],
                'description': v['description']
            })

    # Display:
    # "ErrTextContrastAA: 5,234 instances"
    # + 10 example violations
```

**Raw data preserved, reporting is clean.**

---

## Performance Considerations

### Write Performance
- **Batch inserts:** MongoDB handles 10,000+ documents in seconds
- **No transaction needed:** Summary insert + items insert (acceptable if items fail)
- **Ordered=False:** Parallel insertion for speed

### Read Performance
- **Indexes critical:** Query by test_result_id is indexed
- **Pagination:** Can load violations in batches (1000 at a time)
- **Aggregation:** MongoDB aggregation framework for counts/grouping

### Storage
- **Overhead:** Minimal (~10-20% for document metadata)
- **Compression:** WiredTiger compresses similar documents efficiently
- **Indexes:** ~5-10% storage overhead, worth it for query speed

---

## Implementation Checklist

- [ ] Create `test_result_items` collection
- [ ] Add indexes to `test_result_items`
- [ ] Update `Database` class with new methods:
  - [ ] `_create_test_result_items()`
  - [ ] `_get_test_result_items()`
  - [ ] `_migrate_test_result_to_items()`
- [ ] Update `TestResult.to_dict()` to support both schemas
- [ ] Update `create_test_result()` to use new schema
- [ ] Update `get_test_result()` to read from new schema
- [ ] Update reporting to deduplicate at render time
- [ ] Create migration script for existing data
- [ ] Test with high-violation pages (17,000+)
- [ ] Monitor storage size and query performance
- [ ] Document new schema in codebase

---

## Estimated Implementation Time

- **Database schema changes:** 2 hours
- **Write logic update:** 3 hours
- **Read logic update:** 3 hours
- **Migration script:** 2 hours
- **Reporting layer updates:** 4 hours
- **Testing & validation:** 4 hours

**Total:** ~18 hours (2-3 days)

---

## Risk Mitigation

### Risk: Migration breaks existing functionality
**Mitigation:** Dual-write period, gradual rollout

### Risk: Query performance degradation
**Mitigation:** Comprehensive indexes, test with production data

### Risk: Storage explosion
**Mitigation:** Monitor storage, compression helps, minimal overhead

### Risk: Complex code maintenance
**Mitigation:** Clear abstraction in `Database` class, good documentation

---

## Success Criteria

1. ✅ Pages with 17,000+ violations can be stored
2. ✅ No data loss (all raw violations preserved)
3. ✅ Query performance acceptable (<1s for typical queries)
4. ✅ Reporting shows deduplicated view
5. ✅ Existing functionality continues to work
6. ✅ Migration completed for all existing data

---

**Status:** Design Complete, Ready for Implementation
