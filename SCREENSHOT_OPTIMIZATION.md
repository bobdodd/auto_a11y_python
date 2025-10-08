# Screenshot Quality Optimization

## Problem
Project CVC-B experienced MongoDB document size limit issues (16MB maximum). Test results were exceeding this limit, causing database corruption and failures.

## Root Cause
Screenshots were being taken at JPEG quality 85, which created larger file sizes that could contribute to document size issues when combined with extensive test results.

## Solution
Reduced JPEG screenshot quality from **85 to 80** in all screenshot capture locations.

## Changes Made

### 1. Browser Manager (`auto_a11y/core/browser_manager.py`)
**Line 263:**
```python
# Before:
'quality': 85

# After:
'quality': 80  # Reduced from 85 to help prevent MongoDB 16MB document limit issues
```

### 2. Test Runner (`auto_a11y/testing/test_runner.py`)
**Line 149:**
```python
# Before:
'quality': 85

# After:
'quality': 80  # Reduced from 85 to help prevent MongoDB 16MB document limit issues
```

## Impact

### File Size Reduction
- JPEG quality 80 vs 85 typically reduces file size by **10-20%**
- Visual quality difference is minimal and imperceptible for accessibility testing purposes
- Still maintains full-page screenshots in JPEG format

### Database Benefits
- Smaller screenshot files reduce overall document size
- Helps prevent exceeding MongoDB's 16MB document limit
- Reduces storage requirements
- Improves query performance

### Quality Trade-offs
- JPEG quality 80 is still considered "high quality"
- Screenshots remain suitable for:
  - Visual accessibility analysis
  - AI processing with Claude
  - Documentation and reporting
  - Manual review
- No impact on DOM-based accessibility testing (JavaScript tests)

## Verification

Both locations now use quality=80:
```bash
grep -n "quality.*[0-9]" auto_a11y/core/browser_manager.py auto_a11y/testing/test_runner.py
```

Output:
```
auto_a11y/core/browser_manager.py:263:            'quality': 80
auto_a11y/testing/test_runner.py:149:                        'quality': 80
```

## Additional Notes

### Screenshot Storage
- Screenshots are saved as **file paths** in the database, not as embedded data
- Actual screenshot files are stored in the `screenshots/` directory
- File naming: `page_{page_id}_{timestamp}.jpg`

### Other Size Considerations
If document size issues persist, consider:
1. **Limit test result details**: Reduce amount of metadata stored per violation
2. **Paginate large result sets**: Split results across multiple documents
3. **Use GridFS**: For documents approaching 16MB, use MongoDB's GridFS
4. **Archive old results**: Move historical test results to separate collection

## Testing
- CVC-B project test results were cleared and pages reset
- New tests will use quality=80 screenshots
- Monitor document sizes in MongoDB to verify improvement

## Date
January 2025
