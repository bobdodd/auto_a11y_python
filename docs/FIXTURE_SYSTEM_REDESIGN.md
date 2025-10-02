# Fixture System Redesign Proposal

## Problem Statement

The current fixture validation system has significant limitations:

1. **One fixture per error code** - Only validates that the test detects the issue, not that it's accurate
2. **No false positive testing** - Doesn't verify tests correctly identify valid code as passing
3. **No structured metadata** - Can't validate expected violation counts or locations
4. **Missing edge cases** - No comprehensive coverage of boundary conditions
5. **Manual validation only** - No automated verification of violation accuracy

## Proposed Enhanced System

### Core Improvements

1. **Multiple fixtures per test** covering:
   - Basic violations (should fail)
   - Correct usage (should pass)
   - Edge cases and complex scenarios
   - Both semantic HTML and ARIA equivalents

2. **Structured JSON metadata** for validation:
   - Expected violation/pass counts
   - WCAG references
   - Impact levels
   - Descriptions

3. **Data attributes for precise validation**:
   - Mark which elements should trigger violations
   - Mark which elements should pass
   - Include reasons for expected results

4. **Passive design**:
   - No executable JavaScript (unless JS itself is under test)
   - Pure HTML/CSS for reliable testing

---

## New Fixture Format

### Metadata Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{IssueId} - {Description}</title>

    <!-- Test Metadata (non-executable JSON) -->
    <script type="application/json" id="test-metadata">
    {
        "id": "heading_ErrNoH1_001_violations_basic",
        "issueId": "ErrNoH1",
        "expectedViolationCount": 1,
        "expectedPassCount": 3,
        "description": "Page with no H1 heading, only H2-H4",
        "wcag": "1.3.1",
        "impact": "High",
        "testType": "violations"
    }
    </script>
</head>
<body>
    <!-- Violation: Missing H1 -->
    <div data-expected-violation="true"
         data-violation-id="ErrNoH1"
         data-violation-reason="Page has no H1 element">

        <h2 data-expected-pass="true"
            data-pass-reason="H2 has proper content">
            Section Heading
        </h2>

        <p>Content paragraph</p>

        <h3 data-expected-pass="true"
            data-pass-reason="H3 has proper content">
            Subsection
        </h3>

        <h4 data-expected-pass="true"
            data-pass-reason="H4 has proper content">
            Detail Section
        </h4>
    </div>
</body>
</html>
```

### Naming Convention

**Pattern:** `{IssueId}_{sequence}_{type}_{variant}.html`

**Examples:**
- `ErrNoH1_001_violations_basic.html` - Basic violation case
- `ErrNoH1_002_correct_with_h1.html` - Correct usage example
- `ErrNoH1_003_edge_aria_heading.html` - ARIA heading level 1
- `ErrMultipleH1_001_violations_two_h1s.html` - Multiple H1 elements
- `ErrMultipleH1_002_correct_single_h1.html` - Correct single H1

**Type Values:**
- `violations` - Contains issues that should be detected
- `correct` - Shows proper implementation (should pass)
- `edge` - Edge cases and complex scenarios
- `aria` - ARIA role equivalents

---

## Fixture Types Required

### For Each Issue Code:

#### 1. Basic Violations Fixture
- Simple, clear example of the violation
- Single violation instance
- Minimal HTML for clarity

#### 2. Correct Usage Fixture
- Shows proper implementation
- All elements should pass validation
- Demonstrates best practices

#### 3. Multiple Violations Fixture
- Multiple instances of the same issue
- Tests violation count accuracy
- Validates all violations are detected

#### 4. Edge Cases Fixture
- Boundary conditions
- Unusual but valid markup
- Complex nesting scenarios

#### 5. ARIA Equivalents Fixture (where applicable)
- Tests both semantic HTML and ARIA roles
- Validates ARIA role="heading" aria-level="1" etc.
- Tests hybrid approaches

#### 6. Mixed Pass/Fail Fixture
- Contains both violations and correct usage
- Tests precision of detection
- Validates no false positives

---

## Enhanced test_fixtures.py

### New Validation Logic

```python
def validate_fixture(self, fixture_path: Path, test_result) -> Dict:
    """
    Enhanced validation with metadata checking

    Returns:
        {
            "fixture": str,
            "metadata": {
                "issueId": str,
                "expectedViolationCount": int,
                "expectedPassCount": int,
                ...
            },
            "validation": {
                "violation_count_match": bool,
                "pass_count_match": bool,
                "marked_violations_detected": bool,
                "no_false_positives": bool
            },
            "success": bool,
            "notes": [str]
        }
    """

    # 1. Load and parse JSON metadata
    metadata = self.load_fixture_metadata(fixture_path)

    # 2. Parse data attributes from HTML
    expected_violations = self.parse_expected_violations(fixture_path)
    expected_passes = self.parse_expected_passes(fixture_path)

    # 3. Extract test results
    actual_violations = self.extract_violations(test_result, metadata['issueId'])
    actual_passes = self.extract_passes(test_result)

    # 4. Validate counts
    violation_count_match = (
        len(actual_violations) == metadata['expectedViolationCount']
    )

    pass_count_match = (
        len(actual_passes) >= metadata['expectedPassCount']
    )

    # 5. Validate specific elements
    marked_violations_detected = self.check_marked_elements_detected(
        expected_violations, actual_violations
    )

    # 6. Check for false positives
    no_false_positives = self.check_no_false_positives(
        expected_passes, actual_violations
    )

    # 7. Combine results
    success = all([
        violation_count_match,
        pass_count_match,
        marked_violations_detected,
        no_false_positives
    ])

    return {
        "fixture": str(fixture_path),
        "metadata": metadata,
        "validation": {
            "violation_count_match": violation_count_match,
            "pass_count_match": pass_count_match,
            "marked_violations_detected": marked_violations_detected,
            "no_false_positives": no_false_positives
        },
        "success": success,
        "notes": self.generate_validation_notes(...)
    }
```

---

## Complete Error Code Inventory

### Currently Have Fixtures (62 files):

**Focus** (2):
- ErrContentObscuring
- ErrOutlineIsNoneOnInteractiveElement

**Headings** (15):
- AI_ErrSkippedHeading_01, AI_ErrSkippedHeading_02
- DiscoHeadingWithID
- ErrEmptyHeading, ErrHeadingEmpty
- ErrHeadingOrder
- ErrIncorrectHeadingLevel
- ErrModalMissingHeading
- ErrMultipleH1
- ErrNoH1
- ErrSkippedHeadingLevel
- InfoHeadingNearLengthLimit
- WarnHeadingInsideDisplayNone
- WarnHeadingOver60CharsLong
- WarnVisualHierarchy

**IFrames** (1):
- ErrVideoIframeMissingTitle

**Images** (13):
- DiscoFoundInlineSvg, DiscoFoundSvgImage
- ErrAltOnElementThatDoesntTakeIt
- ErrAltTooLong
- ErrImageAltContainsHTML
- ErrImageWithEmptyAlt
- ErrImageWithImgFileExtensionAlt
- ErrImageWithNoAlt
- ErrImageWithURLAsAlt
- ErrNoAlt
- ErrRedundantAlt
- ErrSVGNoAccessibleName, ErrSvgImageNoLabel
- WarnSVGNoRole, WarnSvgPositiveTabindex

**Keyboard** (9):
- ErrMissingTabindex
- ErrNoFocusIndicator
- ErrNonInteractiveZeroTabindex
- ErrPositiveTabindex
- ErrTabOrderViolation
- WarnHighTabindex
- WarnMissingNegativeTabindex
- WarnModalNoFocusableElements
- WarnNegativeTabindex

**Links** (5):
- ErrInvalidGenericLinkName
- WarnAnchorTargetTabindex
- WarnColorOnlyLink
- WarnGenericDocumentLinkText
- WarnGenericLinkNoImprovement

**Lists** (2):
- ErrEmptyList
- ErrFakeListImplementation

**Maps** (2):
- ErrDivMapMissingAttributes
- ErrMapMissingTitle

**Media** (2):
- ErrNativeVideoMissingControls
- ErrVideoIframeMissingTitle

**Reading Order** (2):
- AI_InfoContentOrder
- AI_WarnPossibleReadingOrderIssue

**Semantic** (3):
- ErrEmptyPageTitle
- ErrMultiplePageTitles
- ErrNoPageTitle

**Tables** (2):
- ErrHeaderMissingScope
- ErrTableNoColumnHeaders

**Timing** (1):
- ErrAutoStartTimers

**Typography** (2):
- ErrSmallText
- WarnItalicText

### Missing Fixtures (Estimated 100+ more needed):

Based on ISSUE_CATALOG_BY_TOUCHPOINT.md and JavaScript test files, we need fixtures for:

**ARIA** (7+):
- AI_ErrAccordionWithoutARIA
- AI_ErrCarouselWithoutARIA
- AI_ErrDropdownWithoutARIA
- AI_ErrMissingInteractiveRole
- ErrFoundAriaLevelButNoRoleAppliedAtAll
- ErrInvalidAriaLevel
- ErrMapAriaHidden

**Forms** (7):
- forms_DiscoNoSubmitButton
- forms_DiscoPlaceholderAsLabel
- forms_ErrInputMissingLabel
- forms_ErrNoButtonText
- forms_WarnGenericButtonText
- forms_WarnNoFieldset
- forms_WarnRequiredNotIndicated

**Buttons** (2):
- AI_ErrNonSemanticButton
- (other button tests)

**Colors/Contrast** (multiple):
- Color contrast tests
- WarnColorOnlyLink (exists)

**Dialogs/Modals** (5):
- AI_ErrDialogWithoutARIA
- AI_WarnModalMissingLabel
- ErrModalMissingHeading (exists)
- AI_ErrModalFocusTrap
- AI_WarnModalWithoutFocusTrap

**Interactive Elements** (5):
- AI_ErrClickableWithoutKeyboard
- AI_ErrMissingFocusIndicator
- AI_ErrToggleWithoutState
- AI_ErrInteractiveElementIssue
- AI_ErrTabsWithoutARIA

**Language** (1):
- AI_WarnMixedLanguage

**Links** (2 more):
- AI_ErrAmbiguousLinkText
- AI_ErrLinkWithoutText

**Navigation/Menus** (1):
- AI_ErrMenuWithoutARIA

**Reading Order** (1 more):
- AI_ErrReadingOrderMismatch

**Animation** (1):
- AI_WarnProblematicAnimation

**Headings** (2 more):
- AI_ErrHeadingLevelMismatch
- AI_ErrVisualHeadingNotMarked

**And many more from JavaScript test files...**

---

## Implementation Plan

### Phase 1: Infrastructure Update
1. Update `test_fixtures.py` to support new metadata format
2. Add HTML parsing for data attributes
3. Implement enhanced validation logic
4. Update database schema for detailed results

### Phase 2: Fixture Template Creation
1. Create fixture template generator
2. Document naming conventions
3. Create example fixtures for each type
4. Build fixture generation prompts for Claude

### Phase 3: Systematic Fixture Generation
1. **Prioritize by usage** - Start with most commonly triggered issues
2. **Generate by category** - Complete one touchpoint at a time
3. **Test as we go** - Validate each fixture works correctly
4. **Document patterns** - Note common patterns for reuse

### Phase 4: Legacy Fixture Migration
1. Review existing 62 fixtures
2. Add metadata to fixtures that work
3. Enhance fixtures that need improvement
4. Create missing companion fixtures (violations need correct, etc.)

---

## Fixture Generation Workflow

### For Each Error Code:

1. **Gather Information**:
   - Issue ID, Type, Impact, WCAG
   - Description, Why it matters, How to fix
   - Extract from ISSUE_CATALOG_BY_TOUCHPOINT.md or JavaScript tests

2. **Generate Fixtures Using Claude**:
   ```
   System Prompt: [Your provided system prompt]
   User Prompt: [Your provided user prompt with issue details]
   ```

3. **Test Fixtures**:
   ```bash
   ./test_fixtures.py --fixture <category>/<fixture_name>.html
   ```

4. **Validate Results**:
   - Check violation counts match
   - Verify marked elements detected
   - Confirm no false positives
   - Review edge cases covered

5. **Iterate if Needed**:
   - Adjust fixture if tests don't work
   - Fix test code if fixture is correct
   - Add more fixtures for gaps

---

## Success Metrics

1. **Coverage**: Fixture for every error code (100+ total)
2. **Accuracy**: 95%+ success rate on fixture tests
3. **Completeness**: Every fixture has violations, correct, and edge cases
4. **Reliability**: Tests consistently detect issues with no false positives
5. **Documentation**: Every fixture has clear metadata and explanations

---

## Next Steps

1. **Review and approve this proposal**
2. **Update test_fixtures.py for new format**
3. **Create fixture generation templates**
4. **Begin systematic fixture generation**
   - Start with Headings (most complete already)
   - Move to Forms (high priority)
   - Continue through all touchpoints

This redesign will create a robust, comprehensive test validation system that ensures the accuracy and reliability of all accessibility tests.
