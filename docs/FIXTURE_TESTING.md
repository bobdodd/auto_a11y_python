# Fixture Testing Guide

## Overview

The fixture testing system validates that Auto A11y correctly identifies accessibility issues by testing against known HTML fixtures. Each fixture contains a specific accessibility issue (or correct implementation) that the system should detect.

**Only tests that pass ALL their fixtures are enabled in production** - this ensures the system reports accurate, reliable results without false positives.

## Quick Start

### Test All Fixtures (Full Test Suite)
```bash
source venv/bin/activate
python test_fixtures.py
```
⚠️ **Warning:** This tests all ~900 fixtures and takes approximately 1 hour.

### Test Discovery Fixtures Only (Recommended for Quick Validation)
```bash
python test_fixtures.py --type Disco
```
✅ Takes ~5 minutes instead of 1 hour

## Filtering Options

The fixture test suite supports powerful filtering to test specific subsets of fixtures during development.

### Filter by Issue Type

Test only fixtures of a specific severity/type:

```bash
# Test only Error fixtures (high-severity violations)
python test_fixtures.py --type Err

# Test only Warning fixtures (medium-severity issues)
python test_fixtures.py --type Warn

# Test only Info fixtures (informational notices)
python test_fixtures.py --type Info

# Test only Discovery fixtures (element detection)
python test_fixtures.py --type Disco

# Test only AI fixtures (requires CLAUDE_API_KEY)
python test_fixtures.py --type AI
```

### Filter by Category (Touchpoint)

Test only fixtures from a specific accessibility touchpoint:

```bash
# Test only form-related fixtures
python test_fixtures.py --category Forms

# Test only image-related fixtures
python test_fixtures.py --category Images

# Test only heading-related fixtures
python test_fixtures.py --category Headings

# Test only color/contrast fixtures
python test_fixtures.py --category ColorsAndContrast
```

**Available categories:**
- AccessibleNames
- Animation
- ARIA
- Buttons
- ColorsAndContrast
- Focus
- Fonts
- Forms
- Headings
- IFrames
- Images
- Interactive
- JavaScript
- Keyboard
- Landmarks
- Language
- Links
- Lists
- Maps
- Media
- Metadata
- Modals
- Navigation
- Page
- PDF
- ReadingOrder
- Style
- SVG
- Tabindex
- Tables
- Typography

### Filter by Specific Error Code

Test only fixtures for a single error code:

```bash
# Test only DiscoFormOnPage fixtures
python test_fixtures.py --code DiscoFormOnPage

# Test only ErrNoAlt fixtures
python test_fixtures.py --code ErrNoAlt

# Test only WarnHeadingOver60CharsLong fixtures
python test_fixtures.py --code WarnHeadingOver60CharsLong
```

### Limit Number of Fixtures

Run a quick smoke test with a limited number of fixtures:

```bash
# Test only first 20 fixtures
python test_fixtures.py --limit 20

# Test only first 5 Error fixtures
python test_fixtures.py --type Err --limit 5
```

### Combine Filters

Filters can be combined for precise testing:

```bash
# Test only Discovery fixtures in the Forms category
python test_fixtures.py --type Disco --category Forms

# Test only first 10 Warning fixtures in Images category
python test_fixtures.py --type Warn --category Images --limit 10

# Test only Error fixtures, limited to 50
python test_fixtures.py --type Err --limit 50
```

## Understanding Test Results

### Fixture Status Categories

Each error code is categorized based on its fixture test results:

#### ✅ All Pass (Green)
- **Status:** All fixtures for this error code passed
- **Production:** ✅ **ENABLED** - Available for use in projects
- **Meaning:** The test correctly identifies violations AND doesn't report false positives
- **Example:** If `ErrNoAlt` has 3 fixtures and all 3 pass, it's enabled

#### ⚠️ Partial Pass (Yellow)
- **Status:** Some fixtures passed, others failed
- **Production:** ❌ **DISABLED** - Not available in projects
- **Meaning:** Test implementation is incomplete or has bugs
- **Action Needed:** Fix the test so all fixtures pass
- **Common Issue:** Test works for violations but flags correct implementations (false positives)

#### ❌ All Fail (Red)
- **Status:** No fixtures passed
- **Production:** ❌ **DISABLED** - Not available in projects
- **Meaning:** Test isn't implemented or has critical bugs
- **Action Needed:** Implement the test or fix critical issues

### Test Output Example

```
🧪 ACCESSIBILITY FIXTURE TEST SUITE
📝 Test Run ID: c5768dad-e5d3-43ed-83fe-b1fea7ab6722

🔍 ACTIVE FILTERS:
   • Type: Disco

Found 21 fixtures to test

============================================================
📁 Category: Forms (3 fixtures)
============================================================

[1/21] 📄 Testing: Forms/DiscoFormOnPage_001_discovery_basic.html
   Expected: DiscoFormOnPage
   ✅ Success! Found expected code: DiscoFormOnPage

[2/21] 📄 Testing: Forms/DiscoFormOnPage_002_discovery_login.html
   Expected: DiscoFormOnPage
   ✅ Success! Found expected code: DiscoFormOnPage

   ➡️  Progress: 2/21 tested | ✅ 2 passed | ❌ 0 failed

================================================================================
📊 SUMMARY
================================================================================

Total Fixtures Tested:      21
✅ Passed:                  21 (100.0%)
❌ Failed:                   0 (0.0%)

Available Issues (All Pass): 10
- DiscoFormOnPage
- DiscoFoundInlineSvg
- DiscoFoundSvgImage
- DiscoFontFound
- DiscoPDFLinksFound
- DiscoStyleAttrOnElements
- DiscoStyleElementOnPage
- DiscoFoundJS
- DiscoHeadingWithID
```

## Viewing Results

### Command Line
Results are displayed in real-time during test execution and saved to:
- `fixture_test_results.json` - Detailed JSON results
- MongoDB database - For web interface access

### Web Interface
View fixture status at: http://localhost:5001/testing/fixture-status

Features:
- Filter by status (All Pass, Partial Pass, All Fail)
- Filter by type (Err, Warn, Info, Disco)
- Search by error code name
- See which fixtures passed/failed for each error code
- View test timestamps and notes

## Typical Development Workflow

### 1. Fixing a Broken Test

When a test shows "Partial Pass" (some fixtures fail):

```bash
# Step 1: Test just that error code to see current status
python test_fixtures.py --code ErrNoAlt

# Step 2: Fix the test implementation in Python
# Edit: auto_a11y/testing/touchpoint_tests/test_images.py

# Step 3: Restart Flask to load new code
# (Flask auto-reloads with --reload flag)

# Step 4: Retest just that error code
python test_fixtures.py --code ErrNoAlt

# Step 5: If all pass, the test is now enabled in production!
```

### 2. Implementing a New Discovery Test

```bash
# Step 1: Check current status of Discovery fixtures
python test_fixtures.py --type Disco

# Step 2: Implement the discovery logic in appropriate test file
# Example: Add DiscoFormOnPage to test_forms.py

# Step 3: Test just Discovery fixtures to verify
python test_fixtures.py --type Disco

# Step 4: View results in web interface
# Navigate to: http://localhost:5001/testing/fixture-status
# Filter by: Type = Disco
```

### 3. Testing a Specific Touchpoint

When working on forms accessibility:

```bash
# Test all Forms fixtures
python test_fixtures.py --category Forms

# Or test only Form errors
python test_fixtures.py --category Forms --type Err

# Or test only Form warnings
python test_fixtures.py --category Forms --type Warn
```

### 4. Quick Smoke Test

Before committing changes:

```bash
# Test a sample of each type
python test_fixtures.py --limit 50

# Or test just the categories you changed
python test_fixtures.py --category Forms --category Images
```

## Fixture Naming Convention

Fixtures must follow this naming pattern:

```
{ErrorCode}_{SequenceNumber}_{Type}_{Description}.html
```

**Examples:**
- `ErrNoAlt_001_violations_basic.html` - First fixture showing violation
- `ErrNoAlt_002_correct_with_alt.html` - Second fixture showing correct usage
- `DiscoFormOnPage_001_discovery_basic.html` - Discovery fixture
- `WarnHeadingOver60CharsLong_003_correct_concise.html` - Correct implementation

**Sequence Numbers:**
- `001`, `002`, `003` - Fixtures demonstrating violations
- `002`, `003` - Fixtures demonstrating correct implementation (pass cases)

## Fixture Metadata

Each fixture should include metadata in a `<script type="application/json" id="test-metadata">` tag:

```html
<script type="application/json" id="test-metadata">
{
    "id": "DiscoFormOnPage_001_discovery_basic",
    "issueId": "DiscoFormOnPage",
    "expectedViolationCount": 0,
    "expectedPassCount": 0,
    "description": "Basic form detected requiring manual accessibility testing",
    "wcag": "N/A",
    "impact": "N/A"
}
</script>
```

## Understanding Discovery Tests

Discovery tests (prefixed with `Disco`) are special:

- **Purpose:** Detect elements on the page for manual review (forms, SVGs, fonts, PDFs, etc.)
- **Not Violations:** They don't report errors, just presence of elements
- **Expected Behavior:** Should detect elements on ALL fixtures (both violation and correct fixtures)
- **Use Case:** Flag content that requires human review for accessibility

**Example Discovery Tests:**
- `DiscoFormOnPage` - Detects any `<form>` elements
- `DiscoFoundInlineSvg` - Detects inline `<svg>` elements
- `DiscoFontFound` - Detects unique fonts used on page
- `DiscoPDFLinksFound` - Detects links to PDF files
- `DiscoFoundJS` - Detects JavaScript on page

## Troubleshooting

### Test Takes Too Long
```bash
# Use filters to test smaller subsets
python test_fixtures.py --type Disco  # ~5 minutes
python test_fixtures.py --category Forms  # Varies by category
python test_fixtures.py --limit 20  # Quick smoke test
```

### Fixture Not Being Tested
Check the naming convention:
- Must start with `Err`, `Warn`, `Info`, `Disco`, or `AI_`
- Must be in `Fixtures/` directory
- Must have `.html` extension

### Test Passes Locally But Shows Failed in Web Interface
```bash
# Clear old test results and rerun
python test_fixtures.py --code YourErrorCode

# Results are saved to MongoDB with a unique test run ID
# The web interface shows the LATEST test run
```

### AI Tests Are Skipped
```bash
# AI tests require CLAUDE_API_KEY environment variable
export CLAUDE_API_KEY=your_key_here
python test_fixtures.py --type AI
```

## Advanced Usage

### Test History
```bash
# View previous test runs
python test_fixtures.py --history
```

### Test Specific Run Details
```bash
# View details of a specific test run
python test_fixtures.py --run-id <test-run-id>
```

### Test Single Fixture
```bash
# Test just one fixture file
python test_fixtures.py --fixture Forms/DiscoFormOnPage_001_discovery_basic.html
```

## Integration with Development

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Run quick smoke test before committing
python test_fixtures.py --limit 20
if [ $? -ne 0 ]; then
    echo "Fixture tests failed. Fix issues before committing."
    exit 1
fi
```

### CI/CD Pipeline
```bash
# Run full test suite in CI
python test_fixtures.py

# Or run category-specific tests for faster feedback
python test_fixtures.py --category Forms
python test_fixtures.py --category Images
python test_fixtures.py --type Err
```

## Related Documentation

- [FIXTURE_VALIDATION.md](FIXTURE_VALIDATION.md) - How fixture validation works
- [FIXTURE_IMPACT_ON_PROJECTS.md](FIXTURE_IMPACT_ON_PROJECTS.md) - How passing fixtures enable features
- [FIXTURE_TESTING_GUIDE.md](../FIXTURE_TESTING_GUIDE.md) - Original testing guide

## Summary

The fixture testing system ensures Auto A11y provides accurate, reliable accessibility testing by validating every test against known fixtures. With the new filtering capabilities, you can:

- ✅ Test specific subsets during development (5 min instead of 1 hour)
- ✅ Quickly validate bug fixes for individual tests
- ✅ Focus on specific touchpoints or issue types
- ✅ Run quick smoke tests before committing
- ✅ Enable only thoroughly tested features in production

**Remember:** Only tests that pass ALL their fixtures are enabled in production - this prevents false positives and ensures user trust.
