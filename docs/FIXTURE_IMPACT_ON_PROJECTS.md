# Fixture Test Impact on Projects

## Overview

This document explains how fixture test validation affects accessibility testing projects, both new and existing.

## How Fixture Validation Works

### During Project Creation/Editing

When creating or editing a project, fixture test results determine which accessibility tests are **available for selection**:

```
✅ All Pass (21 tests)    → Available for selection
⚠️  Partial Pass (91 tests) → Disabled (grayed out)
❌ All Fail (240 tests)   → Disabled (grayed out)
```

**Debug Mode Override:** When debug mode is enabled, ALL tests become available regardless of fixture status. Use this for development and testing purposes only.

### During Scanning

When scanning pages for accessibility issues:

1. The test runner loads the **project's saved configuration** from the database
2. Only tests that were **enabled at project creation time** run
3. Results are stored with their error codes (e.g., `ErrNoAltText`, `WarnColorOnlyLink`)
4. No filtering occurs based on current fixture status

## Impact on Existing Projects

### ✅ What Does NOT Change

Existing projects are **NOT affected** by fixture test changes:

- **Saved Configuration:** Project settings are frozen at creation time
- **Historical Data:** All past scan results remain unchanged
- **Ongoing Scans:** Use the project's saved test configuration
- **Issue Storage:** All violations are stored with their error codes intact

### ⚠️ What DOES Change

Fixture test status changes affect:

- **New Projects:** Can only select tests with "All Pass" status
- **Project Edits:** When modifying test selection, only passing tests are available
- **UI Indicators:** Create/edit pages show current test availability

## Example Scenarios

### Scenario 1: Adding New Tests

```
Timeline:
  Day 1: Create "Acme Corp Website" project
    - Enable: ErrNoAltText (All Pass ✅)
    - Cannot enable: ErrColorContrast (Partial Pass ⚠️)

  Day 2: Developer fixes ErrColorContrast test
    - Fixture status: Partial Pass → All Pass ✅

  Day 3: "Acme Corp Website" project
    - Still only tests for ErrNoAltText
    - Does NOT automatically add ErrColorContrast
    - To add it: Edit project and enable the test

  Day 4: Create new "XYZ Company" project
    - Can now enable both tests ✅
```

**Recommendation:** Periodically review and update project configurations when new tests become available.

### Scenario 2: Degraded Test Quality (⚠️ IMPORTANT)

```
Timeline:
  Day 1: Create "Healthcare Portal" project
    - Enable: ErrNoAltText (All Pass ✅)
    - Run 100 scans, find 500 violations

  Day 2: Developer accidentally breaks ErrNoAltText test
    - Fixture status: All Pass → Partial Pass ⚠️
    - Now produces false positives on some pages

  Day 3: "Healthcare Portal" project
    - STILL runs ErrNoAltText (config frozen)
    - May produce INCORRECT results! ⚠️
    - No automatic warning for existing projects

  Day 4: New projects
    - Cannot enable ErrNoAltText anymore ❌
    - Protected from broken test
```

**This is a critical edge case:** Existing projects can continue using tests that later fail fixtures, potentially producing unreliable results.

## Recommendations

### For Development Teams

1. **Run Fixture Tests Regularly**
   ```bash
   python test_fixtures.py
   ```
   - After code changes to test implementations
   - Before deploying new versions
   - Weekly as part of CI/CD pipeline

2. **Monitor the Fixture Status Dashboard**
   - http://localhost:5001/testing/fixture-status
   - Watch for tests moving from "All Pass" to "Partial Pass"
   - Investigate immediately if active tests degrade

3. **Version Control for Project Configs**
   - Document which tests were enabled at project creation
   - Track fixture test results in version control
   - Include in release notes when tests change status

4. **Consider Project Health Checks**
   - Periodically audit existing projects
   - Compare project configs against current fixture status
   - Notify users if their projects use degraded tests

### For Project Administrators

1. **Review New Test Availability**
   - Check fixture status dashboard monthly
   - Update project configurations when new tests pass
   - Take advantage of improved test coverage

2. **Understand Debug Mode**
   - Debug mode enables ALL tests (bypasses fixture validation)
   - Use only for: development, testing, troubleshooting
   - Never use in production scanning projects

3. **Archive Old Data Carefully**
   - Test results include the error code that detected them
   - If a test later fails fixtures, historical data may be suspect
   - Consider re-scanning critical pages when tests degrade

## Technical Details

### Where Configuration is Stored

```python
# Project document in MongoDB
{
  "_id": ObjectId("..."),
  "name": "My Website Project",
  "config": {
    "touchpoints": {
      "images": {
        "enabled": true,
        "tests": ["ErrNoAltText", "ErrAltTooLong"]  # Frozen at creation
      },
      "colors_contrast": {
        "enabled": false,  # Disabled at creation
        "tests": []
      }
    },
    "wcag_level": "AA",
    "enable_ai_testing": false
  }
}
```

### Where Fixture Validation Happens

1. **Project Creation/Edit UI** (`auto_a11y/web/templates/projects/create.html`)
   - Calls: `current_app.test_config.get_all_test_statuses()`
   - Gets: `passing_tests`, `debug_mode`
   - Disables tests that don't pass fixtures

2. **Runtime Testing** (`auto_a11y/testing/test_runner.py`)
   - Loads: `project.config['touchpoints']`
   - Uses: Frozen configuration from project creation
   - Does NOT check current fixture status

3. **Result Processing** (`auto_a11y/testing/result_processor.py`)
   - Stores: All violations with error codes
   - No filtering based on fixture status
   - All data preserved in database

### Fixture Validation Levels

| Status | Meaning | Project Impact |
|--------|---------|----------------|
| **All Pass** | Every fixture passes | ✅ Available for selection |
| **Partial Pass** | Some fixtures pass, some fail | ❌ Disabled (unreliable) |
| **All Fail** | No fixtures pass | ❌ Disabled (not implemented) |

## Future Improvements

Consider implementing:

1. **Project Health Monitoring**
   - Background job to check if project configs use degraded tests
   - Email notifications when tests fail fixtures
   - Dashboard indicator for affected projects

2. **Fixture Version Tracking**
   - Record fixture test results at project creation time
   - Compare current vs. creation-time fixture status
   - Flag projects using tests that have degraded

3. **Automatic Test Updates**
   - Optional: Auto-enable newly passing tests
   - Optional: Auto-disable newly failing tests
   - Configurable per-project

4. **Migration Tools**
   - Script to update all projects when test status improves
   - Bulk re-scan when critical tests are fixed
   - Historical data quality assessment

## Questions?

- Fixture testing guide: [FIXTURE_TESTING_GUIDE.md](../FIXTURE_TESTING_GUIDE.md)
- Dashboard: http://localhost:5001/testing/fixture-status
- Configuration: [auto_a11y/config/test_config.py](../auto_a11y/config/test_config.py)
