# Fixture Testing Guide

## Overview

The Auto A11y fixture testing system validates that accessibility tests correctly identify both violations and correct implementations. Each error code has multiple fixtures that must all pass before that test is enabled in production.

## Fixture Naming Convention

Fixtures follow a standardized naming pattern:

```
{ErrorCode}_{sequence}_{type}_{variant}.html
```

**Examples:**
- `ErrNoAltText_001_violations_basic.html` - Demonstrates violations
- `ErrNoAltText_002_correct_with_alt.html` - Demonstrates correct usage
- `AI_ErrAccordionWithoutARIA_001_violations_basic.html` - AI-detected issue violations
- `AI_ErrAccordionWithoutARIA_002_correct_with_aria.html` - Correct ARIA implementation

**Components:**
- **ErrorCode**: The issue identifier (e.g., `ErrNoAltText`, `WarnColorOnlyLink`, `AI_ErrAccordionWithoutARIA`)
- **Sequence**: Three-digit number (001, 002, 003...) for ordering
- **Type**: Usually `violations` or `correct`
- **Variant**: Describes the specific test case (e.g., `basic`, `with_aria`, `complex`)

## Fixture Content Structure

Each fixture is an HTML file with embedded metadata:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ErrorCode - Description</title>
    <script type="application/json" id="test-metadata">
{
    "id": "ErrorCode_001_violations_basic",
    "issueId": "ErrorCode",
    "expectedViolationCount": 3,
    "expectedPassCount": 0,
    "description": "Description of what this fixture tests",
    "wcag": "1.1.1",
    "impact": "High"
}
    </script>
</head>
<body>
    <img src="photo.jpg"
         data-expected-violation="true"
         data-violation-reason="Image missing alt attribute. Screen readers cannot describe this image to blind users...">
</body>
</html>
```

**Key elements:**
- **test-metadata**: JSON metadata describing expected results
- **data-expected-violation**: Marks elements that should trigger violations
- **data-violation-reason**: Explains why this is problematic and the user impact
- **data-expected-pass**: Marks correct implementations (in "correct" fixtures)
- **data-pass-reason**: Explains why this implementation is accessible

## Running Fixture Tests

### Basic Usage

```bash
# Run all fixtures
python test_fixtures.py

# Test specific category
python test_fixtures.py --category Images

# Test single fixture
python test_fixtures.py --fixture Images/ErrNoAltText_001_violations_basic.html

# View test history
python test_fixtures.py --history

# View specific test run details
python test_fixtures.py --run-id <run-id>
```

### Test Results

The test runner reports results at two levels:

1. **Fixture Level**: Individual HTML file pass/fail
2. **Error Code Level**: Aggregated pass/fail for all fixtures of a code

**Example output:**

```
📊 TEST SUMMARY
================================================================================
Total fixtures tested: 574
  ✅ Passed: 560
  ❌ Failed: 14
  Success rate: 97.6%

Unique error codes tested: 287
  ✅ Passing codes (all fixtures pass): 280
  ❌ Failing codes (one or more fixtures fail): 7
  Code success rate: 97.6%

❌ FAILED ERROR CODES
================================================================================

❌ ErrNoAltText
   Fixtures: 1/2 passed
   📄 Images/ErrNoAltText_002_correct_with_alt.html
      Expected: ErrNoAltText
      Found: None
      Note: Test did not detect absence of issue in correct implementation
```

## Test Enablement Logic

An error code test is **only enabled in production** if:

1. ✅ ALL fixtures for that code pass their tests
2. ✅ The test correctly identifies violations in violation fixtures
3. ✅ The test correctly identifies NO violations in correct usage fixtures

If ANY fixture fails, the entire error code is disabled.

### AI_ Prefixed Tests (Partially Implemented)

**Note:** AI_ prefixed error codes (e.g., `AI_ErrAccordionWithoutARIA`, `AI_WarnProblematicAnimation`) test AI-detected accessibility issues using Claude AI analysis.

**Implementation Status:**
- ✅ 182 AI_ fixtures exist in the repository (91 unique error codes)
- ✅ 20 AI_ error codes are implemented in the Claude analyzer
- ⚠️ 71 AI_ error codes have fixtures but no implementation yet
- ⚠️ Most AI_ fixtures will fail until their corresponding analyzers are implemented

**Currently Implemented AI_ Tests:**
- `AI_ErrAccordionWithoutARIA`, `AI_ErrCarouselWithoutARIA`, `AI_ErrClickableWithoutKeyboard`
- `AI_ErrDialogWithoutARIA`, `AI_ErrDropdownWithoutARIA`, `AI_ErrEmptyHeading`
- `AI_ErrHeadingLevelMismatch`, `AI_ErrInteractiveElementIssue`, `AI_ErrMenuWithoutARIA`
- `AI_ErrModalFocusTrap`, `AI_ErrNonSemanticButton`, `AI_ErrReadingOrderMismatch`
- `AI_ErrSkippedHeading`, `AI_ErrTabsWithoutARIA`, `AI_ErrToggleWithoutState`
- `AI_ErrVisualHeadingNotMarked`, `AI_WarnMixedLanguage`, `AI_WarnProblematicAnimation`
- `AI_WarnTooltipIssue`, `AI_InfoVisualCue`

**Running AI Tests:**
AI analysis requires an API key and incurs costs. Configure via `RUN_AI_ANALYSIS` in config. AI tests have a 60-second timeout (vs 30s for regular tests).

### Why This Matters

Consider `ErrNoAltText` with two fixtures:

- `ErrNoAltText_001_violations_basic.html` - Images without alt ✅ PASS
- `ErrNoAltText_002_correct_with_alt.html` - Images with proper alt ❌ FAIL

Even though the test detects violations correctly, it might also falsely flag correct implementations. This would cause too many false positives, so the test remains disabled until both fixtures pass.

## Viewing Test Status in Web UI

Navigate to: **Testing > Fixture Status** (`/testing/fixture-status`)

The UI shows:

- **Debug Mode**: Whether all tests are enabled regardless of fixture status
- **Total Tests**: Number of unique error codes with fixtures
- **Passing Tests**: Error codes with all fixtures passing (enabled)
- **Failed Tests**: Error codes with one or more failing fixtures (disabled)

The table displays:
- **Error Code**: Issue identifier
- **Status**: "✓ All Pass" (green) or "✗ Failed" (red)
- **Fixtures**: Pass ratio (e.g., "2/2", "1/3")
- **Notes**: Details about which fixtures failed
- **Tested At**: Last test run timestamp

## Debug Mode

Set `debug_mode=True` in the test configuration to enable all tests regardless of fixture status. Useful for:

- Development and testing
- Validating new test implementations
- Troubleshooting false negatives

**Warning**: Debug mode may produce false positives. Only use in non-production environments.

## Database Storage

Fixture test results are stored in MongoDB:

### Collections

**fixture_test_runs**: Test run summaries
```json
{
    "_id": "uuid",
    "started_at": "2024-01-15T10:00:00Z",
    "completed_at": "2024-01-15T10:05:30Z",
    "duration_seconds": 330,
    "total_fixtures": 574,
    "passed": 560,
    "failed": 14,
    "success_rate": 97.6
}
```

**fixture_tests**: Individual fixture results
```json
{
    "fixture_path": "Images/ErrNoAltText_001_violations_basic.html",
    "expected_code": "ErrNoAltText",
    "found_codes": ["ErrNoAltText"],
    "success": true,
    "notes": [],
    "tested_at": "2024-01-15T10:01:23Z",
    "test_run_id": "uuid"
}
```

## Creating New Fixtures

### 1. Identify the Issue

Find the error code in `ISSUE_CATALOG.md`:

```markdown
## ErrNoAltText

**Description**: Image missing alt attribute
**WCAG**: 1.1.1 Non-text Content (Level A)
**Impact**: High
**Category**: Images
```

### 2. Create Violations Fixture

File: `Fixtures/Images/ErrNoAltText_001_violations_basic.html`

- Include 2-3 examples of the violation
- Add `data-expected-violation="true"` to violating elements
- Add `data-violation-reason` with detailed explanation
- Include test metadata with `expectedViolationCount`

### 3. Create Correct Usage Fixture

File: `Fixtures/Images/ErrNoAltText_002_correct_with_alt.html`

- Show 2-3 correct implementations
- Add `data-expected-pass="true"` to correct elements
- Add `data-pass-reason` explaining why it's accessible
- Include test metadata with `expectedPassCount`

### 4. Test Your Fixtures

```bash
python test_fixtures.py --fixture Images/ErrNoAltText_001_violations_basic.html
python test_fixtures.py --fixture Images/ErrNoAltText_002_correct_with_alt.html
```

### 5. Commit Both Fixtures Together

```bash
git add Fixtures/Images/ErrNoAltText_*.html
git commit -m "Add fixtures for ErrNoAltText (2 fixtures)

- violations: Images without alt attribute
- correct: Images with proper alt text

WCAG 1.1.1: Non-text Content
Impact: High"
```

## Fixture Categories

Fixtures are organized by accessibility touchpoint:

- **Images/**: Image alt text, decorative images, complex images
- **Forms/**: Form labels, required fields, error messages
- **Headings/**: Heading hierarchy, skipped levels, empty headings
- **Landmarks/**: ARIA landmarks, region labels, duplicate landmarks
- **Links/**: Link text, link purpose, empty links
- **Focus/**: Focus indicators, focus order, keyboard traps
- **Color/**: Color contrast, color-only information
- **ARIA/**: ARIA roles, states, properties
- **Navigation/**: Navigation menus, skip links, breadcrumbs
- **Tables/**: Table headers, captions, complex tables
- **Media/**: Video captions, audio descriptions, autoplay
- **Interactive/**: Accordions, carousels, modals, tooltips
- **Typography/**: Text sizing, line height, justified text
- **Lists/**: List semantics, nested lists, definition lists
- **Semantic/**: Semantic HTML, document structure
- **Keyboard/**: Keyboard navigation, tab order, shortcuts
- **Timing/**: Session timeouts, timed content, auto-refresh

## Best Practices

### Fixture Quality

1. **Realistic Examples**: Use realistic content and markup patterns
2. **Clear Violations**: Make violations obvious and unambiguous
3. **Multiple Cases**: Cover edge cases and variations
4. **Detailed Reasons**: Explain the user impact, not just the technical issue
5. **Self-Contained**: Each fixture should work standalone (no external dependencies)

### Testing Approach

1. **Test Both Paths**: Always create violations AND correct usage fixtures
2. **Run Frequently**: Run fixture tests after any test implementation changes
3. **Fix Failures Promptly**: Don't let failing fixtures accumulate
4. **Review Test Logic**: If fixtures fail unexpectedly, the test logic may need fixing

### Naming Consistency

1. **Use Three Digits**: `001`, `002`, `003` (allows up to 999 fixtures per code)
2. **Descriptive Variants**: `basic`, `complex`, `edge_case`, `with_aria`, etc.
3. **Consistent Prefixes**: `violations_`, `correct_`
4. **Match Error Code**: Filename must start with exact error code

## Troubleshooting

### Fixture Not Found by Test Runner

- Check filename follows naming convention
- Ensure error code prefix matches catalog
- Verify file has `.html` extension
- Check file is in `Fixtures/` directory or subdirectory

### Test Not Detecting Expected Code

- Verify test implementation is registered and loaded
- Check test is enabled in test configuration
- Review test logic for bugs
- Ensure metadata `issueId` matches error code

### False Positives in Correct Fixtures

- Test logic may be too aggressive
- Review selector specificity
- Check for edge cases in detection logic
- Consider adding more specific conditions

### All Fixtures Pass but Test Still Disabled

- Check `fixture_test_runs` collection has recent run
- Verify database connection in application
- Force refresh fixture cache (restart app)
- Check debug mode is not mistakenly disabled

## API Endpoints

### Get Fixture Test Status

```bash
GET /api/v1/fixture-tests/status
```

Response:
```json
{
    "success": true,
    "debug_mode": false,
    "fixture_run_summary": {
        "run_id": "uuid",
        "completed_at": "2024-01-15T10:05:30Z",
        "total": 574,
        "passed": 560,
        "failed": 14,
        "success_rate": 97.6
    },
    "passing_tests": ["ErrNoAltText", "WarnColorOnlyLink", ...],
    "test_statuses": {
        "ErrNoAltText": {
            "success": true,
            "total_fixtures": 2,
            "passed_fixtures": 2,
            "fixture_paths": ["Images/...", "Images/..."],
            "notes": [],
            "tested_at": "2024-01-15T10:01:23Z"
        }
    },
    "total_tests": 287,
    "passing_count": 280
}
```

### Check Specific Test Availability

```bash
GET /api/v1/fixture-tests/check/ErrNoAltText
```

Response:
```json
{
    "success": true,
    "error_code": "ErrNoAltText",
    "available": true,
    "passed_fixture": true,
    "debug_override": false,
    "fixture_path": "2 fixtures",
    "tested_at": "2024-01-15T10:01:23Z"
}
```

## Contributing

When contributing new fixtures:

1. Follow the naming convention exactly
2. Include comprehensive `data-violation-reason` and `data-pass-reason` attributes
3. Add test metadata with accurate expected counts
4. Test both violation and correct usage paths
5. Run full fixture test suite before committing
6. Document WCAG success criteria in commit message

## Additional Resources

- **ISSUE_CATALOG.md**: Complete list of error codes and descriptions
- **WCAG 2.1 Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
- **ARIA Authoring Practices**: https://www.w3.org/WAI/ARIA/apg/
- **WebAIM**: https://webaim.org/ (Excellent accessibility testing resources)
