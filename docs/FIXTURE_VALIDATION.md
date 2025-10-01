# Fixture-Based Test Validation System

## Overview

The auto_a11y_python project uses a **fixture-based validation system** to ensure accessibility tests are working correctly before they're used in production. This prevents false positives/negatives and ensures test reliability.

---

## System Architecture

### 1. Fixture Files (`Fixtures/` directory)

HTML files demonstrating specific accessibility issues, organized by touchpoint categories.

**Naming Convention:**
- `Err*` - Error-level violations (WCAG failures)
- `Warn*` - Warning-level issues (potential problems)
- `Info*` - Informational findings
- `Disco*` - Discovery items (patterns found)
- `AI_*` - Issues requiring AI visual analysis

**Structure Example:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>No H1 Test - ErrNoH1</title>
</head>
<body>
    <h2>Secondary Heading</h2>
    <p>This page is missing an h1 element.</p>
</body>
</html>
```

**File Organization:**
```
Fixtures/
├── Headings/
│   ├── ErrNoH1.html
│   ├── ErrMultipleH1.html
│   ├── AI_ErrSkippedHeading_01.html
│   └── ...
├── Images/
│   ├── ErrImageWithNoAlt.html
│   ├── ErrSVGNoAccessibleName.html
│   └── ...
├── Links/
│   ├── ErrInvalidGenericLinkName.html
│   └── ...
└── [23 touchpoint categories]
```

### 2. Test Runner (`test_fixtures.py`)

Automated script that tests all fixtures to validate the accessibility test suite.

**How It Works:**

```python
# 1. Discovers all fixture files
fixtures = get_all_fixtures()  # Finds *.html in Fixtures/

# 2. For each fixture:
#    - Extracts expected error code from filename
#    - Creates temporary project/website/page in database
#    - Runs accessibility tests on the fixture
#    - Checks if expected code appears in results

# 3. Records results in MongoDB:
#    - fixture_tests collection (individual test results)
#    - fixture_test_runs collection (summary of each run)
```

**Key Methods:**
- `test_fixture()` - Tests single fixture with 30s timeout
- `run_all_tests()` - Tests all fixtures by category
- `save_fixture_result_to_db()` - Stores results in MongoDB
- `save_test_run_summary()` - Stores run metadata

**Usage:**
```bash
# Test all fixtures
./test_fixtures.py

# Test specific category
./test_fixtures.py --category Headings

# Test single fixture
./test_fixtures.py --fixture Headings/ErrNoH1.html

# View history
./test_fixtures.py --history

# View specific run details
./test_fixtures.py --run-id <test-run-id>
```

### 3. Database Schema

**Collection: `fixture_test_runs`**
```javascript
{
  _id: "uuid",                    // Unique test run ID
  started_at: DateTime,
  completed_at: DateTime,
  duration_seconds: 125.4,
  total_fixtures: 62,
  passed: 58,
  failed: 4,
  success_rate: 93.5,
  fixture_results: ["id1", "id2", ...]  // References to fixture_tests
}
```

**Collection: `fixture_tests`**
```javascript
{
  _id: ObjectId,
  fixture_path: "Headings/ErrNoH1.html",
  expected_code: "ErrNoH1",
  found_codes: ["ErrNoH1", "WarnVisualHierarchy"],
  success: true,                  // Expected code was found
  notes: ["Additional issues found: WarnVisualHierarchy"],
  tested_at: DateTime,
  test_run_id: "uuid"             // Links to fixture_test_runs
}
```

### 4. FixtureValidator (`auto_a11y/utils/fixture_validator.py`)

Runtime class that checks which tests have passed their fixtures.

**Key Methods:**

```python
get_passing_tests(force_refresh=False) -> Set[str]
    # Returns set of error codes that passed fixture tests
    # Cached for 5 minutes
    # Example: {'ErrNoH1', 'ErrImageWithNoAlt', ...}

is_test_available(error_code: str, debug_mode: bool) -> bool
    # Check if test should be used
    # Returns True if:
    #   - debug_mode=True (all tests available), OR
    #   - error_code passed its fixture test

get_test_status() -> Dict[str, Dict]
    # Returns detailed status for all tests
    # Example:
    {
      "ErrNoH1": {
        "success": True,
        "found_codes": ["ErrNoH1"],
        "notes": [],
        "tested_at": DateTime,
        "fixture_path": "Headings/ErrNoH1.html"
      }
    }

get_fixture_run_summary() -> Optional[Dict]
    # Returns summary of latest fixture test run
```

### 5. TestConfiguration (`auto_a11y/config/test_config.py`)

Integrates fixture validation into test configuration system.

**Key Features:**

```python
def __init__(self, config_file=None, database=None, debug_mode=False):
    # debug_mode=True bypasses fixture validation
    # database connection enables fixture validation

def is_test_available_by_fixture(self, error_code: str) -> bool
    # Check if test passed fixtures or debug mode is on

def get_test_fixture_status(self, error_code: str) -> Dict
    # Get detailed status:
    {
      "available": True,
      "passed_fixture": True,
      "fixture_path": "...",
      "tested_at": DateTime,
      "debug_override": False  # True if available only due to debug
    }
```

**Configuration Hierarchy:**
1. **Debug Mode** - All tests available (overrides everything)
2. **Fixture Validation** - Tests must pass fixtures to be available
3. **Touchpoint Enable/Disable** - Can disable entire touchpoints
4. **Individual Test Enable/Disable** - Can disable specific tests

---

## How Test Availability is Determined

### Decision Tree:

```
Is debug_mode enabled?
├─ YES → Test is AVAILABLE (debug override)
└─ NO → Check fixture validation
    │
    ├─ No fixture_validator (no database)?
    │   └─ Test is AVAILABLE (assume OK)
    │
    └─ fixture_validator exists?
        │
        ├─ Query latest fixture_test_runs
        ├─ Find fixture_tests for this run
        ├─ Check if error_code has success=True
        │
        ├─ YES → Test is AVAILABLE
        └─ NO → Test is UNAVAILABLE
```

### Code Flow:

```python
# 1. App initialization
app.test_config = get_test_config(
    database=app.db,
    debug_mode=config.DEBUG  # From environment
)

# 2. When creating project (shows test status)
test_statuses = app.test_config.get_all_test_statuses()
passing_tests = app.test_config.fixture_validator.get_passing_tests()

# 3. When running tests (filters available tests)
if app.test_config.is_test_available_by_fixture(error_code):
    run_test(error_code)
else:
    skip_test(error_code)  # Not validated yet
```

---

## Integration Points

### 1. Flask App Initialization

**File:** `auto_a11y/web/app.py:49-54`

```python
app.test_config = get_test_config(
    database=app.db,
    debug_mode=config.DEBUG
)
```

### 2. Project Creation UI

**File:** `auto_a11y/web/routes/projects.py:177-182`

Shows which tests are available based on fixture status:

```python
test_statuses = current_app.test_config.get_all_test_statuses()
passing_tests = current_app.test_config.fixture_validator.get_passing_tests()
return render_template('projects/create.html',
                     test_statuses=test_statuses,
                     passing_tests=passing_tests,
                     debug_mode=debug_mode)
```

### 3. Fixture Status API

**File:** `auto_a11y/web/routes/api.py:17-77`

```python
GET /api/v1/fixture-tests/status
    # Returns all test statuses and fixture run summary

GET /api/v1/fixture-tests/check/<error_code>
    # Returns availability for specific test
```

### 4. Fixture Status UI

**File:** `auto_a11y/web/templates/testing/fixture_status.html`

Dashboard showing fixture test health (accessible via Settings → Fixture Status).

---

## Benefits of This System

1. **Prevents False Positives** - Tests must prove they can detect issues before use
2. **Test Validation** - Ensures tests work as expected on known-bad HTML
3. **Continuous Validation** - Re-run fixtures to verify tests after changes
4. **Debug Mode** - Developers can bypass validation during development
5. **Historical Tracking** - Database stores all test runs for trend analysis
6. **Granular Control** - Can enable/disable tests at multiple levels

---

## Typical Workflow

### Test Development:
1. Write new accessibility test (JavaScript/AI)
2. Create fixture HTML demonstrating the issue
3. Name fixture with error code: `Err<TestName>.html`
4. Run `./test_fixtures.py` to validate
5. If test passes ✅ → Available in production
6. If test fails ❌ → Fix test, repeat

### Production Use:
1. User creates project with selected touchpoints
2. UI shows which tests are available (green) vs unavailable (gray)
3. Only validated tests run during page testing
4. Debug mode bypass available for testing new tests

---

## Running Fixture Tests

### Full Test Suite

```bash
./test_fixtures.py
```

Expected output:
```
🧪 ACCESSIBILITY FIXTURE TEST SUITE
📝 Test Run ID: abc-123-def-456

Found 62 fixtures to test

====================================================
📁 Category: Headings (17 fixtures)
====================================================

[1/62] 📄 Testing: Headings/ErrNoH1.html
   Expected: ErrNoH1
   Running accessibility tests...
   ✅ Success! Found expected code: ErrNoH1

...

📊 TEST SUMMARY
Total fixtures tested: 62
✅ Passed: 58
❌ Failed: 4
Success rate: 93.5%
```

### Category-Specific Testing

```bash
# Test only heading-related fixtures
./test_fixtures.py --category Headings

# Test only image-related fixtures
./test_fixtures.py --category Images
```

### Single Fixture Testing

```bash
# Test a specific fixture file
./test_fixtures.py --fixture Headings/ErrNoH1.html
```

### View Test History

```bash
# Show last 10 test runs
./test_fixtures.py --history
```

Output:
```
📊 FIXTURE TEST HISTORY

🔹 Test Run: abc-123-def-456
   Date: 2025-01-15 14:30:00
   Duration: 125.4 seconds
   Results: 58/62 passed (93.5%)
   ❌ 4 fixtures failed
```

### View Specific Run Details

```bash
./test_fixtures.py --run-id abc-123-def-456
```

---

## Key Files Summary

| File | Purpose |
|------|---------|
| `Fixtures/**/*.html` | 60+ test fixture files |
| `test_fixtures.py` | Automated fixture test runner |
| `auto_a11y/utils/fixture_validator.py` | Runtime fixture status checker |
| `auto_a11y/config/test_config.py` | Test configuration with fixture integration |
| `auto_a11y/web/routes/api.py` | Fixture status API endpoints |
| `auto_a11y/web/templates/testing/fixture_status.html` | Fixture status dashboard |

---

## Troubleshooting

### All Tests Show as Unavailable

**Cause:** No fixture test runs in database

**Solution:** Run the fixture test suite:
```bash
./test_fixtures.py
```

### Tests Available in Debug Mode Only

**Cause:** Tests haven't passed fixture validation yet

**Check:** View fixture status at Settings → Fixture Status in the UI

**Solution:** Run fixture tests and fix any failing tests

### Debug Mode Override

To enable debug mode (makes all tests available):

1. Set environment variable: `DEBUG=True`
2. Or in `config.py`: Set `DEBUG = True`
3. Restart Flask application

**Note:** Debug mode should only be used during development, not in production.

---

## Best Practices

1. **Run Fixtures Regularly** - After any test changes, re-run fixtures
2. **Create Fixtures for New Tests** - Every new test should have a fixture
3. **Keep Fixtures Simple** - Focus on demonstrating one issue per fixture
4. **Document Complex Fixtures** - Add HTML comments explaining edge cases
5. **Review Failed Tests** - Failed fixtures indicate test problems, not fixture problems
6. **Use Debug Mode Sparingly** - Only during active development

---

## Future Enhancements

- Automatic fixture testing on commit (CI/CD integration)
- Fixture coverage reports (which tests lack fixtures)
- Performance tracking (test execution speed over time)
- Fixture versioning (track changes to fixtures over time)
- Automated fixture generation from real-world issues

---

This system ensures **test reliability** through automated validation against known accessibility issues!
