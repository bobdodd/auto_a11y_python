# Multi-State Testing Architecture

**Date:** October 30, 2025
**Status:** Design Document - Addresses Multiple States Per Page

---

## Problem Statement

The current v2.0 architecture assumes **one test per page**, but real-world testing requires:

1. **Test page WITH cookie notice visible**
2. **Dismiss cookie notice**
3. **Test page WITHOUT cookie notice** (verify it's gone)

More generally:
- Test page in **initial state**
- Click button A → Test page in **state A**
- Reload page → Click button B → Test page in **state B**
- Iterate through all interactive elements

### Requirements

1. **Multiple test results per page per session** - Different states = different results
2. **State metadata** - Record what buttons were clicked, what's visible
3. **Test result grouping** - Associate all results for same page/session
4. **Violation context** - "Cookie notice still visible after dismissal" needs context
5. **Database design** - Store multiple results without duplication

---

## Proposed Architecture

### Core Concept: Page States

A **page state** is defined by:
- Which scripts have been executed
- Which buttons have been clicked
- Which elements are visible/hidden
- Any other page modifications

### Execution Flow

```
Page Load
    ↓
Test #1: Initial State (cookie notice visible)
    ↓
Execute Script: Dismiss cookie notice
    ↓
Test #2: Post-Script State (cookie notice hidden)
    ↓
Check: Is cookie notice gone? (validation)
    ↓
Reload Page
    ↓
Click Button A
    ↓
Test #3: State with Button A active
    ↓
Reload Page
    ↓
Click Button B
    ↓
Test #4: State with Button B active
```

---

## Data Model Changes

### 1. PageTestState Model (New)

```python
@dataclass
class PageTestState:
    """Represents the state of a page during testing"""

    state_id: str                          # Unique identifier for this state
    description: str                       # "Initial state", "After cookie dismissal", etc.

    # Scripts executed to reach this state
    scripts_executed: List[str] = field(default_factory=list)  # Script IDs

    # Buttons/elements clicked
    elements_clicked: List[dict] = field(default_factory=list)  # [{selector, description}]

    # Expected conditions
    elements_visible: List[str] = field(default_factory=list)   # Selectors that should be visible
    elements_hidden: List[str] = field(default_factory=list)    # Selectors that should be hidden

    # Timestamp
    captured_at: datetime = field(default_factory=datetime.now)
```

### 2. Updated TestResult Model

```python
@dataclass
class TestResult:
    # Existing fields
    page_id: str
    test_date: datetime
    violations: List[Violation]
    # ...

    # NEW: State information
    page_state: Optional[PageTestState] = None
    state_sequence: int = 0  # Order: 0=initial, 1=after first script, 2=after button A, etc.

    # NEW: Reference to parent session
    session_id: Optional[str] = None

    # NEW: Reference to related test results (same page, same session, different states)
    related_result_ids: List[str] = field(default_factory=list)
```

### 3. Updated PageSetupScript Model

```python
@dataclass
class PageSetupScript:
    # Existing fields...

    # NEW: Test strategy
    test_before_execution: bool = False  # Test page BEFORE running script
    test_after_execution: bool = True    # Test page AFTER running script

    # NEW: Validation expectations (what should change)
    expect_visible_after: List[str] = field(default_factory=list)   # Selectors
    expect_hidden_after: List[str] = field(default_factory=list)    # Selectors
```

---

## Implementation Strategy

### Pattern 1: Cookie Notice Testing

```python
script = PageSetupScript(
    name='Dismiss Cookie Notice',
    scope=ScriptScope.WEBSITE,
    trigger=ExecutionTrigger.ONCE_PER_SESSION,

    # NEW: Test both before and after
    test_before_execution=True,   # Test WITH cookie notice
    test_after_execution=True,    # Test WITHOUT cookie notice

    # NEW: Validation expectations
    condition_selector='.cookie-banner',
    expect_hidden_after=['.cookie-banner'],  # Banner should be gone

    steps=[
        ScriptStep(action_type=ActionType.CLICK, selector='button.accept')
    ]
)
```

**Execution Flow:**
```
1. Navigate to page
2. TEST #1: Initial state (state_sequence=0)
   - page_state.description = "Initial state (cookie notice visible)"
   - page_state.elements_visible = ['.cookie-banner']
   - Run accessibility tests
   - Save TestResult #1

3. Execute script: Click accept button
   - Record in page_state.scripts_executed

4. TEST #2: Post-script state (state_sequence=1)
   - page_state.description = "After cookie dismissal"
   - page_state.elements_hidden = ['.cookie-banner']
   - page_state.scripts_executed = [script_id]
   - Run accessibility tests
   - Save TestResult #2

5. Validate: Check if .cookie-banner is hidden
   - If still visible → Add violation to TestResult #2
   - violation.context = "Expected cookie banner to be hidden after dismissal"
```

### Pattern 2: Multi-Button Testing

```python
# Define button test configurations
button_tests = [
    {
        'selector': 'button.tab-1',
        'description': 'Tab 1 active',
        'expect_visible': ['.tab-1-content'],
        'expect_hidden': ['.tab-2-content', '.tab-3-content']
    },
    {
        'selector': 'button.tab-2',
        'description': 'Tab 2 active',
        'expect_visible': ['.tab-2-content'],
        'expect_hidden': ['.tab-1-content', '.tab-3-content']
    },
    {
        'selector': 'button.tab-3',
        'description': 'Tab 3 active',
        'expect_visible': ['.tab-3-content'],
        'expect_hidden': ['.tab-1-content', '.tab-2-content']
    }
]

# Test runner will:
for i, button_test in enumerate(button_tests):
    # Reload page to reset state
    await page.reload()

    # Click button
    await page.click(button_test['selector'])
    await page.waitForSelector(button_test['expect_visible'][0])

    # Test in this state
    test_result = await run_accessibility_tests(
        page,
        page_state=PageTestState(
            state_id=f"button_test_{i}",
            description=button_test['description'],
            elements_clicked=[{
                'selector': button_test['selector'],
                'description': button_test['description']
            }],
            elements_visible=button_test['expect_visible'],
            elements_hidden=button_test['expect_hidden']
        ),
        state_sequence=i+1
    )
```

**Execution Flow:**
```
1. TEST #1: Initial state (state_sequence=0)
   - Default tab visible
   - Save TestResult #1

2. Click Tab 1 button
3. TEST #2: Tab 1 active (state_sequence=1)
   - page_state.description = "Tab 1 active"
   - page_state.elements_clicked = [{'selector': 'button.tab-1', ...}]
   - page_state.elements_visible = ['.tab-1-content']
   - Save TestResult #2

4. Reload page
5. Click Tab 2 button
6. TEST #3: Tab 2 active (state_sequence=2)
   - page_state.description = "Tab 2 active"
   - Save TestResult #3

... and so on
```

---

## Database Schema Changes

### Updated: test_results Collection

```javascript
{
  _id: ObjectId,
  page_id: ObjectId,
  test_date: Date,

  // NEW: State information
  page_state: {
    state_id: String,              // "initial", "after_cookie_dismissal", "tab_1_active"
    description: String,
    scripts_executed: [ObjectId],
    elements_clicked: [
      {
        selector: String,
        description: String,
        timestamp: Date
      }
    ],
    elements_visible: [String],
    elements_hidden: [String],
    captured_at: Date
  },
  state_sequence: Number,          // 0, 1, 2, ...

  // NEW: Session and grouping
  session_id: String,              // Links to script_execution_sessions
  related_result_ids: [ObjectId],  // Other results for same page/session

  // Existing fields
  violations: [...],
  warnings: [...],
  passes: [...],
  duration_ms: Number,
  screenshot_path: String
}
```

### Query Examples

```javascript
// Get all test results for a page in a session
db.test_results.find({
  page_id: ObjectId("..."),
  session_id: "session_uuid",
}).sort({ state_sequence: 1 })

// Get initial state test
db.test_results.findOne({
  page_id: ObjectId("..."),
  session_id: "session_uuid",
  state_sequence: 0
})

// Get test after cookie dismissal
db.test_results.findOne({
  page_id: ObjectId("..."),
  session_id: "session_uuid",
  "page_state.scripts_executed": { $in: [ObjectId("cookie_script_id")] },
  state_sequence: 1
})
```

---

## UI/Reporting Changes

### Test Results Display

```
Page: Homepage (https://example.com)
Session: 2025-10-30 14:30:00

┌─────────────────────────────────────────────────────────────┐
│ Test #1: Initial State                                      │
├─────────────────────────────────────────────────────────────┤
│ State: Cookie notice visible                                │
│ Violations: 15                                              │
│ - ErrInsufficientContrast: Cookie banner text (4)          │
│ - WarnMissingAriaLabel: Cookie accept button               │
│ - ... (10 more)                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Test #2: After Cookie Dismissal                             │
├─────────────────────────────────────────────────────────────┤
│ State: Cookie notice hidden                                 │
│ Scripts executed: Dismiss Cookie Notice                     │
│ Violations: 10                                              │
│ - ErrInsufficientContrast: Navigation links (5)            │
│ - ... (5 more)                                              │
│                                                              │
│ ✅ Cookie banner successfully dismissed                     │
│ ✅ 5 violations resolved (cookie-related issues gone)      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Test #3: Tab 1 Active                                       │
├─────────────────────────────────────────────────────────────┤
│ State: Tab 1 content visible                                │
│ Buttons clicked: Tab 1 (button.tab-1)                      │
│ Violations: 3                                               │
│ - ... (tab 1 specific issues)                               │
└─────────────────────────────────────────────────────────────┘
```

### Comparison View

```
Violation Comparison Across States:

┌──────────────────────┬────────┬──────────┬─────────┐
│ Violation            │ State1 │  State2  │ State3  │
├──────────────────────┼────────┼──────────┼─────────┤
│ Cookie banner issues │   5    │    0     │    0    │  ← Resolved!
│ Navigation contrast  │   5    │    5     │    5    │  ← Persistent
│ Tab 1 content issues │   0    │    0     │    3    │  ← State-specific
│ Tab 2 content issues │   0    │    0     │    0    │
└──────────────────────┴────────┴──────────┴─────────┘
```

---

## Implementation Components

### 1. MultiStateTestRunner (New Class)

```python
class MultiStateTestRunner:
    """Runs accessibility tests across multiple page states"""

    async def test_page_multi_state(
        self,
        page: Page,
        scripts: List[PageSetupScript],
        button_configs: Optional[List[dict]] = None
    ) -> List[TestResult]:
        """
        Test page in multiple states

        Returns:
            List of TestResult objects (one per state)
        """
        results = []
        state_sequence = 0
        session_id = self.session_manager.current_session.session_id

        # Test #1: Initial state
        initial_result = await self._test_in_state(
            page=page,
            state=PageTestState(
                state_id="initial",
                description="Initial page load"
            ),
            state_sequence=state_sequence,
            session_id=session_id
        )
        results.append(initial_result)
        state_sequence += 1

        # Execute scripts with before/after testing
        for script in scripts:
            if script.test_before_execution:
                # Already tested in previous state
                pass

            # Execute script
            await self.script_executor.execute_script(page, script)

            if script.test_after_execution:
                # Test in post-script state
                post_result = await self._test_in_state(
                    page=page,
                    state=PageTestState(
                        state_id=f"after_{script.name.lower().replace(' ', '_')}",
                        description=f"After {script.name}",
                        scripts_executed=[script.id]
                    ),
                    state_sequence=state_sequence,
                    session_id=session_id
                )
                results.append(post_result)
                state_sequence += 1

        # Test button states
        if button_configs:
            for i, config in enumerate(button_configs):
                # Reload page
                await page.reload()

                # Click button
                await page.click(config['selector'])
                await page.waitFor(1000)

                # Test in button state
                button_result = await self._test_in_state(
                    page=page,
                    state=PageTestState(
                        state_id=f"button_{i}",
                        description=config['description'],
                        elements_clicked=[config]
                    ),
                    state_sequence=state_sequence,
                    session_id=session_id
                )
                results.append(button_result)
                state_sequence += 1

        # Link all results together
        result_ids = [r.id for r in results]
        for result in results:
            result.related_result_ids = [rid for rid in result_ids if rid != result.id]
            self.db.update_test_result(result)

        return results
```

### 2. State Validator

```python
class StateValidator:
    """Validates page state after script execution"""

    async def validate_state(
        self,
        page,
        expected_state: PageTestState
    ) -> List[Violation]:
        """
        Validate that page is in expected state

        Returns:
            List of violations if expectations not met
        """
        violations = []

        # Check elements that should be visible
        for selector in expected_state.elements_visible:
            element = await page.querySelector(selector)
            if not element:
                violations.append(Violation(
                    id='WarnExpectedElementNotVisible',
                    message=f'Expected element to be visible: {selector}',
                    selector=selector,
                    impact='medium'
                ))

        # Check elements that should be hidden
        for selector in expected_state.elements_hidden:
            element = await page.querySelector(selector)
            if element:
                # Check if actually visible
                is_visible = await page.evaluate(
                    '(el) => el.offsetParent !== null',
                    element
                )
                if is_visible:
                    violations.append(Violation(
                        id='WarnExpectedElementStillVisible',
                        message=f'Expected element to be hidden: {selector}',
                        selector=selector,
                        impact='medium',
                        context=f'Element should be hidden in state: {expected_state.description}'
                    ))

        return violations
```

---

## Configuration Examples

### Example 1: Cookie Notice (Test Before & After)

```python
{
    'type': 'script',
    'script': PageSetupScript(
        name='Dismiss Cookie Notice',
        test_before_execution=True,
        test_after_execution=True,
        expect_hidden_after=['.cookie-banner'],
        steps=[...]
    )
}
```

### Example 2: Tab Testing

```python
{
    'type': 'button_iteration',
    'buttons': [
        {
            'selector': 'button[aria-controls="tab1"]',
            'description': 'Features tab',
            'expect_visible': ['#tab1'],
            'expect_hidden': ['#tab2', '#tab3']
        },
        {
            'selector': 'button[aria-controls="tab2"]',
            'description': 'Pricing tab',
            'expect_visible': ['#tab2'],
            'expect_hidden': ['#tab1', '#tab3']
        }
    ]
}
```

### Example 3: Multi-Step Wizard

```python
{
    'type': 'wizard',
    'steps': [
        {
            'action': 'click',
            'selector': 'button.next',
            'description': 'Step 2: Personal Info',
            'test_after': True
        },
        {
            'action': 'click',
            'selector': 'button.next',
            'description': 'Step 3: Payment',
            'test_after': True
        }
    ]
}
```

---

## Migration Strategy

### Phase 1: Add Fields (Non-Breaking)
- Add `page_state`, `state_sequence`, `session_id` to TestResult
- Default values maintain backward compatibility
- Existing results have `state_sequence=0`, `page_state=None`

### Phase 2: Implement Multi-State Testing
- Add MultiStateTestRunner class
- Add StateValidator class
- Update script execution to support before/after testing

### Phase 3: UI Updates
- Display multiple results per page
- Show state comparison view
- Filter by state

---

## Benefits

### ✅ Accurate Testing
- Test cookie notice visibility issues BEFORE dismissing
- Test content that becomes visible after interactions
- Comprehensive coverage of all page states

### ✅ Better Violation Detection
- Know if violations exist in initial state only
- Track which violations are resolved by scripts
- Detect state-specific issues

### ✅ Complete Coverage
- Test all tabs/accordions/wizards systematically
- Don't miss dynamic content
- Verify interactive elements work correctly

### ✅ Actionable Reports
- "Cookie banner has 5 contrast issues (resolved after dismissal)"
- "Tab 2 content has 3 heading issues (only visible when tab active)"
- Clear context for each violation

---

## Next Steps

1. Update TestResult model with state fields
2. Implement PageTestState model
3. Create MultiStateTestRunner class
4. Create StateValidator class
5. Update UI to display multiple results
6. Update reporting to show state comparisons

---

**Status:** Design Complete - Ready for Implementation
**Estimated Effort:** 2-3 days
**Priority:** High (required for accurate cookie notice testing)
