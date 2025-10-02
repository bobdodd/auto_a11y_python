# Fixture Generation Guide

This directory contains everything needed to generate comprehensive test fixtures using Claude.

## Current Status

- **Total Issues**: 314 unique accessibility issues
- **Need New Fixtures**: 173 issues (55%)
- **Have Old Fixtures**: 141 issues (45%) - need enhancement with new format

## Files

### SYSTEM_PROMPT.md
The system prompt to use with Claude. Contains:
- Fixture requirements (passive HTML, metadata format, data attributes)
- Naming conventions
- Expected fixture types (violations, correct, edge cases, ARIA)

### issues_needing_fixtures.txt
173 issues that have NO fixtures yet. Priority for generation.

### issues_to_replace_fixtures.txt
141 issues with old-style fixtures that need enhancement:
- Add JSON metadata
- Add data-expected-violation and data-expected-pass attributes
- Create multiple test cases (violations + correct + edge)

### by_touchpoint/*.txt
Issues organized by touchpoint for systematic generation.
43 touchpoint files covering all accessibility areas.

### generation_summary.json
Statistics and metadata about fixture coverage.

## How to Generate Fixtures

### Method 1: Using Claude Chat (Recommended for Starting)

1. **Set up Claude**:
   - System prompt: Copy content from `SYSTEM_PROMPT.md`
   - Model: Claude Sonnet or Opus for best quality

2. **Start with a touchpoint**:
   ```
   User prompt: "Generate fixtures for the following issues:"
   [Paste content from by_touchpoint/headings.txt]
   ```

3. **Save generated fixtures**:
   - Create directory: `../Fixtures/[Touchpoint]/`
   - Save each fixture as: `{IssueId}_{seq}_{type}_{variant}.html`
   - Examples:
     - `ErrNoH1_001_violations_basic.html`
     - `ErrNoH1_002_correct_with_h1.html`
     - `ErrNoH1_003_edge_aria_heading.html`

4. **Test the fixtures**:
   ```bash
   ./test_fixtures.py --fixture Headings/ErrNoH1_001_violations_basic.html
   ```

### Method 2: Batch Generation via API

For automated generation at scale, use the Claude API:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

system_prompt = open('fixture_generation/SYSTEM_PROMPT.md').read()
touchpoint_prompt = open('fixture_generation/by_touchpoint/headings.txt').read()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=system_prompt,
    messages=[{
        "role": "user",
        "content": touchpoint_prompt
    }]
)

# Parse and save fixtures from response
```

### Method 3: Incremental by Issue

For single issues or small batches:

1. Extract one issue from a touchpoint file
2. Use as user prompt with the system prompt
3. Generate all fixture types for that issue
4. Move to next issue

## Fixture Requirements Checklist

Each issue should have:

- [ ] **Violations fixture** - Shows the error (001_violations_*)
- [ ] **Correct usage fixture** - Shows proper implementation (002_correct_*)
- [ ] **Edge case fixture** - Boundary conditions (003_edge_*)
- [ ] **ARIA equivalent fixture** (if applicable) - Tests ARIA roles (004_aria_*)
- [ ] **Mixed fixture** - Both violations and correct usage (005_mixed_*)

Each fixture must have:

- [ ] JSON metadata in `<script type="application/json" id="test-metadata">`
- [ ] `data-expected-violation` attributes on elements that should fail
- [ ] `data-expected-pass` attributes on elements that should pass
- [ ] Exactly ONE h1 element
- [ ] Complete, valid HTML5 document
- [ ] No executable JavaScript (unless testing JS itself)

## Priority Order

Generate fixtures in this order:

1. **High Priority** - Error-level issues affecting WCAG A/AA:
   - headings (16 issues)
   - forms (38 issues)
   - images (15 issues)
   - keyboard_navigation (12 issues)

2. **Medium Priority** - Warning-level and common issues:
   - landmarks (59 issues)
   - links (5 issues)
   - buttons (5 issues)
   - aria (7 issues)

3. **Lower Priority** - Info/Discovery level:
   - language (22 issues)
   - Other touchpoints

## Validation Workflow

After generating fixtures:

1. **Run fixture tests**:
   ```bash
   ./test_fixtures.py
   ```

2. **Check success rate**:
   - Should be >90% pass rate
   - Review any failures

3. **Fix issues**:
   - If test fails but fixture is correct → Fix the test code
   - If fixture is wrong → Regenerate fixture

4. **Commit fixtures**:
   ```bash
   git add Fixtures/
   git commit -m "Add fixtures for [touchpoint]"
   ```

## Tips for Quality Fixtures

1. **Keep it simple** - Each fixture should demonstrate ONE clear issue
2. **Be explicit** - Use data attributes to mark expectations
3. **Test both ways** - Violation AND correct usage
4. **Consider context** - Realistic HTML structure
5. **Document well** - Clear descriptions in metadata
6. **Test ARIA** - Include ARIA role equivalents where applicable

## Troubleshooting

**Problem**: Fixture test fails but fixture looks correct
- Check if test code needs updating
- Verify error code matches exactly
- Check if test is looking for specific element patterns

**Problem**: Too many false positives
- Add more specific data attributes
- Create separate fixtures for edge cases
- Review test implementation

**Problem**: Not sure what correct usage looks like
- Review "How to fix" in ISSUE_CATALOG.md
- Check WCAG success criteria
- Look at similar existing fixtures

## Progress Tracking

Track progress by touchpoint:

- [ ] accessible_names (9 issues)
- [ ] animation (6 issues)
- [ ] aria (7 issues)
- [x] ~buttons (5 issues)~ - Has old fixtures, needs enhancement
- [ ] color_contrast (9 issues)
- [ ] color_use (1 issue)
- [ ] dialogs (8 issues)
- [ ] documents (9 issues)
- [ ] event_handling (1 issue)
- [ ] floating_content (1 issue)
- [x] ~focus_management (13 issues)~ - Has old fixtures, needs enhancement
- [ ] fonts (3 issues)
- [ ] forms (38 issues)
- [x] ~headings (16 issues)~ - Has old fixtures, needs enhancement
- [ ] iframes (2 issues)
- [x] ~images (15 issues)~ - Has old fixtures, needs enhancement
- [x] ~keyboard_navigation (12 issues)~ - Has old fixtures, needs enhancement
- [ ] landmarks (59 issues)
- [ ] language (22 issues)
- [x] ~links (5 issues)~ - Has old fixtures, needs enhancement
- [x] ~lists (4 issues)~ - Has old fixtures, needs enhancement
- [x] ~maps (2 issues)~ - Has old fixtures, needs enhancement
- [ ] media (4 issues)
- [ ] navigation (7 issues)
- [ ] page_title (3 issues)
- [ ] read_more_links (1 issue)
- [x] ~reading_order (3 issues)~ - Has old fixtures, needs enhancement
- [ ] semantic_structure (9 issues)
- [ ] style (2 issues)
- [x] ~tables (4 issues)~ - Has old fixtures, needs enhancement
- [ ] timers (3 issues)
- [ ] title_attributes (9 issues)
- [x] ~typography (5 issues)~ - Has old fixtures, needs enhancement
- [ ] videos (1 issue)

## Next Steps

1. Start with high-priority touchpoints
2. Generate 5-10 fixtures at a time
3. Test immediately after generation
4. Commit working fixtures
5. Track progress above
6. Continue until all 314 issues have comprehensive fixtures
