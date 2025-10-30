# Script Architecture Redesign - Multi-Level Execution

**Date:** October 30, 2025
**Status:** Design Document - Replacing Simple Architecture

---

## Problem with Current Design

The Phase 1 implementation associates scripts with **individual pages**, meaning:
- ❌ Cookie notice dismissed on EVERY page test (wasteful)
- ❌ Can't run script once for entire website
- ❌ Can't detect violations (cookie banner reappearing)
- ❌ Can't conditionally execute based on element presence
- ❌ No concept of "run once per session"

---

## Requirements

### 1. Multi-Level Script Configuration

Scripts should be configurable at three levels:

| Level | When It Runs | Example Use Case |
|-------|--------------|------------------|
| **Website** | Once per test session (first page only) | Dismiss cookie notice on start page |
| **Test Run** | Before a specific batch of pages | Sign in before testing protected pages |
| **Page** | Every time a specific page is tested | Open specific dialog on one page |

### 2. Execution Triggers

Control when scripts execute:

| Trigger | Description | Example |
|---------|-------------|---------|
| **once_per_session** | Execute only once across all pages | Cookie notice (run on first page) |
| **once_per_page** | Execute every time page is tested | Open dialog on specific page |
| **conditional** | Execute only if element exists | Dismiss banner if found |
| **always** | Execute unconditionally | Authentication flow |

### 3. Violation Detection

Scripts should be able to **report violations**:

```
Example: Cookie notice dismissed on first page, but reappears on second page
→ Report as violation: "Cookie banner persists across pages"
```

### 4. Conditional Execution

Scripts should check for element presence before running:

```
If cookie banner exists → dismiss it
If already dismissed → skip (no violation)
If reappears after dismissal → report violation
```

---

## New Architecture

### Data Model Changes

#### 1. Script Scope (New Enum)

```python
class ScriptScope(Enum):
    """Where the script is configured"""
    WEBSITE = "website"      # Associated with website
    PAGE = "page"            # Associated with specific page
    TEST_RUN = "test_run"    # Associated with test batch
```

#### 2. Execution Trigger (New Enum)

```python
class ExecutionTrigger(Enum):
    """When the script should execute"""
    ONCE_PER_SESSION = "once_per_session"     # Run once for entire test session
    ONCE_PER_PAGE = "once_per_page"           # Run every time page is tested
    CONDITIONAL = "conditional"                # Run only if condition met
    ALWAYS = "always"                          # Run unconditionally
```

#### 3. Updated PageSetupScript Model

```python
@dataclass
class PageSetupScript:
    # Scope configuration
    scope: ScriptScope                    # website, page, or test_run
    website_id: Optional[str] = None      # If scope=WEBSITE
    page_id: Optional[str] = None         # If scope=PAGE
    test_run_id: Optional[str] = None     # If scope=TEST_RUN

    # Execution configuration
    trigger: ExecutionTrigger             # when to execute
    condition_selector: Optional[str] = None   # For conditional trigger

    # Violation detection
    report_violation_if_condition_met: bool = False
    violation_message: Optional[str] = None
    violation_code: Optional[str] = None

    # Existing fields...
    name: str
    description: str
    enabled: bool = True
    steps: List[ScriptStep] = field(default_factory=list)
    # ... rest of model
```

#### 4. Session State Tracking

```python
@dataclass
class ScriptExecutionSession:
    """Tracks script execution for a test session"""
    session_id: str                       # Unique session ID
    website_id: str
    started_at: datetime
    executed_scripts: Set[str] = field(default_factory=set)  # Script IDs
    conditions_checked: Dict[str, bool] = field(default_factory=dict)
```

---

## Usage Examples

### Example 1: Cookie Notice (Website-Level, Once Per Session)

```python
script = PageSetupScript(
    scope=ScriptScope.WEBSITE,
    website_id='website_123',
    trigger=ExecutionTrigger.ONCE_PER_SESSION,

    # Optionally check if banner exists first
    condition_selector='.cookie-banner',

    # Report violation if banner reappears after dismissal
    report_violation_if_condition_met=True,
    violation_message='Cookie banner persists after dismissal',
    violation_code='WarnCookieBannerPersists',

    name='Dismiss Cookie Notice',
    description='Click accept button on cookie banner (first page only)',
    steps=[
        ScriptStep(
            action_type=ActionType.WAIT_FOR_SELECTOR,
            selector='.cookie-banner',
            description='Wait for banner'
        ),
        ScriptStep(
            action_type=ActionType.CLICK,
            selector='button.accept',
            description='Click accept'
        ),
        ScriptStep(
            action_type=ActionType.WAIT,
            value='1000',
            description='Wait for banner to disappear'
        )
    ]
)
```

**Execution Flow:**
1. **First page tested**: Cookie banner found → Execute script → Mark as executed
2. **Second page tested**: Check if banner exists
   - Banner NOT found → Skip (good)
   - Banner found → Report violation (cookie persists)
3. **Subsequent pages**: Script marked as executed → Skip

### Example 2: Authentication (Test Run Level)

```python
script = PageSetupScript(
    scope=ScriptScope.TEST_RUN,
    test_run_id='run_456',  # Specific batch of pages
    trigger=ExecutionTrigger.ALWAYS,  # Always authenticate

    name='Sign In',
    description='Authenticate before testing protected pages',
    steps=[
        ScriptStep(action_type=ActionType.TYPE,
                   selector='#username', value='testuser'),
        ScriptStep(action_type=ActionType.TYPE,
                   selector='#password', value='${ENV:TEST_PASSWORD}'),
        ScriptStep(action_type=ActionType.CLICK,
                   selector='button[type="submit"]'),
        ScriptStep(action_type=ActionType.WAIT_FOR_NAVIGATION)
    ]
)
```

**Execution Flow:**
1. Before testing ANY page in this test run → Execute script once
2. All pages tested with authenticated session

### Example 3: Page-Specific Dialog (Page Level)

```python
script = PageSetupScript(
    scope=ScriptScope.PAGE,
    page_id='page_789',
    trigger=ExecutionTrigger.ONCE_PER_PAGE,  # Every time this page is tested

    name='Open Help Dialog',
    description='Open help dialog to test its accessibility',
    steps=[
        ScriptStep(action_type=ActionType.CLICK,
                   selector='button.help'),
        ScriptStep(action_type=ActionType.WAIT_FOR_SELECTOR,
                   selector='.help-dialog')
    ]
)
```

**Execution Flow:**
1. Every time page_789 is tested → Execute script
2. Tests run on page with dialog open

### Example 4: Conditional Execution (No Violation)

```python
script = PageSetupScript(
    scope=ScriptScope.WEBSITE,
    website_id='website_123',
    trigger=ExecutionTrigger.CONDITIONAL,
    condition_selector='.newsletter-popup',  # Only run if popup exists

    # Don't report violation if popup found (it's optional)
    report_violation_if_condition_met=False,

    name='Dismiss Newsletter Popup',
    description='Close newsletter popup if present',
    steps=[
        ScriptStep(action_type=ActionType.CLICK,
                   selector='.newsletter-popup .close')
    ]
)
```

**Execution Flow:**
1. Check if `.newsletter-popup` exists
2. If YES → Execute script
3. If NO → Skip (no violation, popup is optional)

---

## Database Schema Changes

### Collection: `page_setup_scripts`

```javascript
{
  _id: ObjectId,

  // NEW: Scope configuration
  scope: String,                   // "website", "page", "test_run"
  website_id: ObjectId,            // If scope=website or test_run
  page_id: ObjectId,               // If scope=page
  test_run_id: ObjectId,           // If scope=test_run

  // NEW: Execution configuration
  trigger: String,                 // "once_per_session", "once_per_page", "conditional", "always"
  condition_selector: String,      // For conditional trigger

  // NEW: Violation detection
  report_violation_if_condition_met: Boolean,
  violation_message: String,
  violation_code: String,

  // Existing fields
  name: String,
  description: String,
  enabled: Boolean,
  steps: [...],
  validation: {...},
  created_by: String,
  created_date: Date,
  last_modified: Date,
  execution_stats: {...}
}
```

### New Collection: `script_execution_sessions`

```javascript
{
  _id: ObjectId,
  session_id: String,              // Unique session identifier
  website_id: ObjectId,
  started_at: Date,
  ended_at: Date,

  // Track executed scripts
  executed_scripts: [
    {
      script_id: ObjectId,
      executed_at: Date,
      page_id: ObjectId,           // Page where it was executed
      success: Boolean,
      duration_ms: Number
    }
  ],

  // Track condition checks (for violation detection)
  condition_checks: [
    {
      script_id: ObjectId,
      page_id: ObjectId,
      checked_at: Date,
      condition_selector: String,
      condition_met: Boolean,
      violation_reported: Boolean
    }
  ]
}
```

---

## Implementation Changes

### 1. Session State Manager (New Class)

```python
class ScriptSessionManager:
    """Manages script execution state across test sessions"""

    def __init__(self, db: Database):
        self.db = db
        self.current_session = None

    def start_session(self, website_id: str) -> str:
        """Start new test session"""
        session_id = str(uuid.uuid4())
        self.current_session = ScriptExecutionSession(
            session_id=session_id,
            website_id=website_id,
            started_at=datetime.now()
        )
        # Save to database
        self.db.create_script_session(self.current_session)
        return session_id

    def has_executed(self, script_id: str) -> bool:
        """Check if script already executed in this session"""
        return script_id in self.current_session.executed_scripts

    def mark_executed(self, script_id: str, page_id: str, success: bool, duration_ms: int):
        """Mark script as executed"""
        self.current_session.executed_scripts.add(script_id)
        # Save execution record
        self.db.add_script_execution_record(
            self.current_session.session_id,
            script_id, page_id, success, duration_ms
        )

    def check_condition_violation(
        self, script: PageSetupScript, page_id: str, condition_met: bool
    ) -> Optional[Violation]:
        """Check if condition constitutes a violation"""

        # If condition met and we should report it
        if condition_met and script.report_violation_if_condition_met:
            # Check if script was already executed (condition should NOT reappear)
            if self.has_executed(script.id):
                # VIOLATION: Condition reappeared after script execution
                return Violation(
                    id=script.violation_code or 'WarnScriptConditionPersists',
                    message=script.violation_message or f'Condition persists: {script.condition_selector}',
                    severity='warning',
                    # ... violation details
                )

        return None

    def end_session(self):
        """End current test session"""
        if self.current_session:
            self.current_session.ended_at = datetime.now()
            self.db.update_script_session(self.current_session)
            self.current_session = None
```

### 2. Updated Script Executor

```python
class ScriptExecutor:

    def should_execute(
        self,
        script: PageSetupScript,
        page_id: str,
        session_manager: ScriptSessionManager
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if script should execute

        Returns:
            (should_execute, skip_reason)
        """

        # Check if enabled
        if not script.enabled:
            return False, "Script disabled"

        # Check trigger conditions
        if script.trigger == ExecutionTrigger.ONCE_PER_SESSION:
            if session_manager.has_executed(script.id):
                return False, "Already executed this session"

        elif script.trigger == ExecutionTrigger.CONDITIONAL:
            # Will check element existence before execution
            pass

        elif script.trigger == ExecutionTrigger.ONCE_PER_PAGE:
            # Always execute for page-level scripts
            pass

        elif script.trigger == ExecutionTrigger.ALWAYS:
            # Always execute
            pass

        return True, None

    async def execute_with_session(
        self,
        page,
        script: PageSetupScript,
        page_id: str,
        session_manager: ScriptSessionManager
    ) -> Dict[str, Any]:
        """
        Execute script with session awareness
        """

        # Check if should execute
        should_run, skip_reason = self.should_execute(script, page_id, session_manager)
        if not should_run:
            return {
                'success': True,
                'skipped': True,
                'skip_reason': skip_reason,
                'duration_ms': 0
            }

        # For conditional trigger, check if element exists
        if script.trigger == ExecutionTrigger.CONDITIONAL:
            condition_met = await self._check_condition(page, script.condition_selector)

            # Check for violation (condition reappeared)
            violation = session_manager.check_condition_violation(
                script, page_id, condition_met
            )
            if violation:
                # Return violation instead of executing
                return {
                    'success': True,
                    'skipped': True,
                    'skip_reason': 'Condition violation detected',
                    'violation': violation,
                    'duration_ms': 0
                }

            # If condition not met, skip execution
            if not condition_met:
                return {
                    'success': True,
                    'skipped': True,
                    'skip_reason': 'Condition not met',
                    'duration_ms': 0
                }

        # Execute script
        result = await self.execute_script(page, script)

        # Mark as executed
        if result['success']:
            session_manager.mark_executed(
                script.id, page_id, True, result['duration_ms']
            )

        return result

    async def _check_condition(self, page, selector: str) -> bool:
        """Check if condition selector exists"""
        try:
            element = await page.querySelector(selector)
            return element is not None
        except:
            return False
```

### 3. Updated Test Runner

```python
class TestRunner:

    def __init__(self, database: Database, browser_config: Dict[str, Any]):
        self.db = database
        self.browser_manager = BrowserManager(browser_config)
        self.script_injector = ScriptInjector()
        self.result_processor = ResultProcessor()
        self.script_executor = ScriptExecutor()
        self.session_manager = ScriptSessionManager(database)  # NEW
        self.screenshot_dir = Path(browser_config.get('SCREENSHOTS_DIR', 'screenshots'))
        self.screenshot_dir.mkdir(exist_ok=True, parents=True)

    async def test_website(self, website):
        """Test all pages for a website"""

        # Start script execution session
        session_id = self.session_manager.start_session(website.id)
        logger.info(f"Started script session: {session_id}")

        try:
            # Test each page
            pages = self.db.get_pages_for_website(website.id)
            for page in pages:
                await self.test_page(page)
        finally:
            # End session
            self.session_manager.end_session()

    async def test_page(
        self,
        page: Page,
        take_screenshot: bool = True,
        run_ai_analysis: bool = False,
        ai_api_key: Optional[str] = None
    ) -> TestResult:
        """Test single page"""

        # ... existing page navigation code ...

        # Get scripts for this page (multiple scopes)
        scripts_to_execute = []

        # 1. Website-level scripts
        website_scripts = self.db.get_scripts_for_website(
            page.website_id,
            scope=ScriptScope.WEBSITE
        )
        scripts_to_execute.extend(website_scripts)

        # 2. Page-level scripts
        page_scripts = self.db.get_scripts_for_page(
            page.id,
            scope=ScriptScope.PAGE
        )
        scripts_to_execute.extend(page_scripts)

        # Execute scripts
        script_violations = []
        for script in scripts_to_execute:
            result = await self.script_executor.execute_with_session(
                browser_page,
                script,
                page.id,
                self.session_manager
            )

            # Check for violations
            if 'violation' in result:
                script_violations.append(result['violation'])

        # ... continue with accessibility testing ...

        # Add script violations to test result
        test_result.violations.extend(script_violations)

        return test_result
```

---

## Migration Path

### Phase 1.5: Add New Fields (Non-Breaking)

1. Add new fields to `PageSetupScript` model with defaults
2. Keep existing `page_id` field for backward compatibility
3. Add new database methods for scope-based queries
4. Keep existing methods working

### Phase 2: Update Existing Scripts

1. Run migration script to convert:
   - Existing scripts → `scope=PAGE`, `trigger=ONCE_PER_PAGE`
   - Keep all existing functionality working

### Phase 3: Enable New Features

1. Allow creating website-level scripts
2. Enable session tracking
3. Enable violation detection

---

## New Database Methods

```python
# Get scripts by scope
def get_scripts_for_website(
    self,
    website_id: str,
    scope: ScriptScope = None,
    enabled_only: bool = True
) -> List[PageSetupScript]:
    """Get scripts for a website (any scope)"""

def get_scripts_for_page(
    self,
    page_id: str,
    scope: ScriptScope = ScriptScope.PAGE,
    enabled_only: bool = True
) -> List[PageSetupScript]:
    """Get scripts for a specific page"""

# Session management
def create_script_session(self, session: ScriptExecutionSession) -> str:
    """Create new execution session"""

def get_script_session(self, session_id: str) -> Optional[ScriptExecutionSession]:
    """Get session by ID"""

def add_script_execution_record(
    self, session_id: str, script_id: str,
    page_id: str, success: bool, duration_ms: int
):
    """Add execution record to session"""
```

---

## Updated Examples

### Example: Cookie Notice with Violation Detection

```python
# Step 1: Create script to dismiss cookie notice
cookie_script = PageSetupScript(
    scope=ScriptScope.WEBSITE,
    website_id='website_123',
    trigger=ExecutionTrigger.ONCE_PER_SESSION,
    condition_selector='.cookie-banner',
    report_violation_if_condition_met=True,
    violation_message='Cookie banner persists after initial dismissal',
    violation_code='WarnCookieBannerPersists',
    name='Dismiss Cookie Notice',
    steps=[
        ScriptStep(action_type=ActionType.CLICK, selector='button.accept')
    ]
)

# Execution flow:
# Page 1: Banner found → Execute script → Mark as executed
# Page 2: Banner found → Report violation (should be gone)
# Page 3: Banner not found → Skip (good)
```

---

## Benefits of New Architecture

✅ **Flexible**: Scripts at website, test-run, or page level
✅ **Efficient**: Run cookie dismissal once, not per page
✅ **Smart**: Conditional execution based on element presence
✅ **Violation Detection**: Report when conditions persist
✅ **Session-Aware**: Track state across test runs
✅ **Backward Compatible**: Existing scripts still work

---

## Summary of Changes

| Component | Change | Impact |
|-----------|--------|--------|
| **PageSetupScript model** | Add scope, trigger, violation fields | Non-breaking (defaults) |
| **Database** | Add session collection, new indexes | Additive only |
| **ScriptSessionManager** | New class for session tracking | New functionality |
| **ScriptExecutor** | Add session awareness | Enhanced logic |
| **TestRunner** | Start/end sessions per website | Workflow change |

---

**Next Steps:**
1. Review and approve this design
2. Implement Phase 1.5 changes (add fields with defaults)
3. Test backward compatibility
4. Implement session manager
5. Update documentation

**Status:** ⏳ Awaiting Review
