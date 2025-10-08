# MongoDB Document Size Handling

## Overview

Auto A11y now includes automatic handling of MongoDB's 16MB document size limit. This prevents database errors when testing pages with extensive accessibility issues.

## Problem

MongoDB has a hard limit of **16MB per document**. Pages with many accessibility violations can exceed this limit, causing:
- Database insertion failures
- Data corruption
- Test result loss
- User frustration

### CVC-B Project Example
- 834 pages tested
- 698 test results saved
- Multiple documents exceeded 16MB limit
- Database corruption required manual cleanup

## Solution

Implemented a multi-layered approach:

### 1. Screenshot Quality Reduction
**Changed**: JPEG quality from 85 → 80
**Impact**: 10-20% file size reduction
**See**: [SCREENSHOT_OPTIMIZATION.md](SCREENSHOT_OPTIMIZATION.md)

### 2. Automatic Document Size Checking
**Module**: `auto_a11y/utils/document_size_handler.py`
**Function**: Validates document size before database insertion

### 3. Intelligent Data Truncation
**Strategy**: Progressive truncation prioritizing important data

### 4. Graceful Error Handling
**Result**: No test failures due to size limits

## How It Works

### Size Checking Process

```python
from auto_a11y.utils import validate_document_size_or_truncate

# Before saving to database
validated_doc, truncation_report = validate_document_size_or_truncate(
    document,
    document_type="test_result",
    max_size=SAFE_DOCUMENT_SIZE  # 14.4 MB (90% of 16MB for safety)
)
```

### Truncation Strategy

When a document exceeds size limits, data is truncated in this order:

#### 1. Passes List (Lowest Priority)
- **Original**: Can be 1000+ items
- **Truncated to**: 10 items
- **Reason**: Passes are good news; violations are more important
- **Impact**: Minimal - count is preserved

#### 2. HTML Snippets
- **Original**: Full HTML of violating elements
- **Truncated to**: 500 characters per snippet
- **Example**: `<div class="very-long-html">...` → `<div class="very-long-html">...[truncated]`
- **Reason**: XPath is sufficient for location; HTML is supplementary

#### 3. Info & Discovery Lists
- **Original**: Can be 100+ items
- **Truncated to**: 50 items each
- **Reason**: Informational, not critical violations

#### 4. Warnings List (Medium Priority)
- **Original**: Can be 500+ items
- **Truncated to**: 100 items (sorted by impact)
- **Priority**: High impact warnings kept first
- **Reason**: Less critical than errors

#### 5. Violations List (Highest Priority)
- **Original**: Can be 1000+ items
- **Truncated to**: 200 items (sorted by impact)
- **Priority**: High > Medium > Low impact
- **Reason**: Last resort - these are the most important

### Size Limits

```python
MONGODB_MAX_DOCUMENT_SIZE = 16 MB      # MongoDB hard limit
SAFE_DOCUMENT_SIZE        = 14.4 MB    # Our target (90% of max)
```

## Truncation Metadata

When truncation occurs, metadata is added to the document:

```json
{
  "_truncation_metadata": {
    "was_truncated": true,
    "truncation_report": {
      "original_size": 18874368,  // ~18 MB
      "final_size": 14680064,     // ~14 MB
      "actions_taken": [
        {
          "action": "truncated_passes",
          "from": 1200,
          "to": 10
        },
        {
          "action": "truncated_html_in_violations"
        },
        {
          "action": "truncated_warnings",
          "from": 450,
          "to": 100,
          "summary": {
            "original_count": 450,
            "kept_count": 100,
            "removed_count": 350,
            "removed_by_impact": {
              "high": 0,
              "medium": 50,
              "low": 300
            }
          }
        }
      ]
    },
    "note": "This test result was truncated to fit MongoDB size limits"
  }
}
```

## Logging

### Info Level
```
Test result truncated for page 507f1f77bcf86cd799439011: 18.00 MB -> 14.00 MB
  - {'action': 'truncated_passes', 'from': 1200, 'to': 10}
  - {'action': 'truncated_html_in_violations'}
```

### Warning Level
```
Test result exceeds size limit: 18.00 MB > 14.40 MB
```

### Error Level
```
Failed to save test result - too large even after truncation
```

## User Impact

### When Truncation Occurs

Users will see:
1. **In Web UI**: Warning banner on test result page
2. **In Logs**: Detailed truncation report
3. **In Reports**: Truncation notice with statistics

### What's Preserved

✅ **Always Preserved**:
- Test metadata (date, duration, URL)
- Violation counts (exact numbers)
- Top priority violations (up to 200)
- High-impact warnings
- AI findings
- Screenshot paths
- WCAG criteria mappings

⚠️ **May Be Truncated**:
- Full passes list (count preserved)
- Long HTML snippets
- Low-priority warnings
- Info/Discovery items beyond 50
- Low-impact violations beyond 200

❌ **What's Lost**:
- Full HTML context for all violations (shortened to 500 chars)
- Complete passes details (only first 10 kept)
- Less important violations (sorted by impact)

## Error Recovery

### If Truncation Fails

When document is too large even after truncation, a minimal result is saved:

```json
{
  "page_id": "507f1f77bcf86cd799439011",
  "test_date": "2025-01-08T12:00:00Z",
  "duration_ms": 45000,
  "error": "Test result too large to store",
  "violations": [],
  "warnings": [],
  "_size_error": true,
  "_error_details": "Document size 20.5 MB exceeds limit even after truncation"
}
```

## Best Practices

### For Developers

1. **Monitor truncation logs**: Check for frequent truncations
2. **Optimize test output**: Reduce unnecessary data in violations
3. **Consider pagination**: For pages with 1000+ violations, consider splitting results

### For Users

1. **Review high-impact violations first**: These are always preserved
2. **Use filters**: Focus on specific violation types
3. **Export data**: Download full reports before truncation if needed
4. **Fix top issues**: Reducing violations prevents truncation

## Monitoring

### Check for Truncated Results

```python
from auto_a11y.core.database import Database

db = Database('mongodb://localhost:27017/', 'auto_a11y')

# Find truncated results
truncated = db.test_results.find({'_truncation_metadata': {'$exists': True}})

for result in truncated:
    print(f"Page {result['page_id']}: {result['_truncation_metadata']['truncation_report']}")
```

### Statistics Query

```javascript
// MongoDB shell
db.test_results.aggregate([
  {
    $project: {
      page_id: 1,
      was_truncated: { $ifNull: ["$_truncation_metadata.was_truncated", false] },
      violation_count: { $size: "$violations" },
      warning_count: { $size: "$warnings" }
    }
  },
  {
    $group: {
      _id: "$was_truncated",
      count: { $sum: 1 },
      avg_violations: { $avg: "$violation_count" }
    }
  }
])
```

## Configuration

### Custom Size Limits

```python
# In your code
from auto_a11y.utils import validate_document_size_or_truncate

# Use stricter limit
validated, report = validate_document_size_or_truncate(
    document,
    max_size=10 * 1024 * 1024  # 10 MB instead of 14.4 MB
)
```

### Disable Truncation (Not Recommended)

If you want to disable automatic truncation and handle errors yourself:

```python
# This will raise DocumentSizeError instead of truncating
from auto_a11y.utils import check_document_size, DocumentSizeError

is_valid, size = check_document_size(document)
if not is_valid:
    raise DocumentSizeError(f"Document too large: {size} bytes")
```

## Testing

### Test with Large Documents

```bash
# Run fixture tests to ensure handler works
python test_fixtures.py

# Test specific large pages
python -c "
from auto_a11y.testing import TestRunner
from auto_a11y.core.database import Database

db = Database('mongodb://localhost:27017/', 'auto_a11y')
runner = TestRunner(db, {})

# Test a page known to have many violations
page = db.get_page('your-page-id')
result = await runner.test_page(page)
"
```

## Performance Impact

- **Size checking**: ~1-5ms per document
- **Truncation**: ~10-50ms when needed
- **Overall impact**: Negligible (<0.1% of test time)

## Future Enhancements

Potential improvements:
1. **GridFS storage**: Store very large results in GridFS
2. **Streaming results**: Stream violations to database incrementally
3. **Compression**: BSON compression for large text fields
4. **Pagination**: Split results across multiple documents
5. **Configurable limits**: Per-project size limits

## Related Documentation

- [SCREENSHOT_OPTIMIZATION.md](SCREENSHOT_OPTIMIZATION.md) - Screenshot quality reduction
- [FIXTURE_TESTING.md](docs/FIXTURE_TESTING.md) - Testing framework
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture

## Support

For issues related to document size handling:

1. Check logs for truncation reports
2. Review truncation metadata in database
3. Consider reducing violation output
4. Contact development team if truncation is too aggressive

## Date
January 2025
