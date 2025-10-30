# Interactive Page Training Feature Design

## Overview
Add capability to interactively train the accessibility testing tool by manually interacting with pages through Puppeteer/Pyppeteer. This allows handling dynamic content, cookie notices, authentication, and other page-specific interactions before running accessibility tests.

## Use Cases

### 1. Cookie/Privacy Notices
- **Problem**: Cookie banners block content and affect test results
- **Solution**: Train the app to click "Accept" or "Reject" before testing
- **Example**: Click button with selector `.cookie-banner button.accept`

### 2. Authentication/Sign-In
- **Problem**: Content requires login to test authenticated pages
- **Solution**: Record sign-in flow (enter username, password, submit)
- **Example**: Fill `#username`, fill `#password`, click `button[type="submit"]`, wait for redirect

### 3. Opening Dynamic Dialogs/Modals
- **Problem**: Modal content loads dynamically after button click
- **Solution**: Click trigger button, wait for content to load, then test
- **Example**: Click `.help-button`, wait 2000ms for AJAX content, then test modal

### 4. Multi-Step Wizards
- **Problem**: Need to navigate through multiple steps to test each
- **Solution**: Record navigation clicks and waits between steps
- **Example**: Click "Next", wait for animation, test step 2, click "Next", test step 3

### 5. Accordion/Dropdown Interactions
- **Problem**: Collapsed content isn't in DOM until expanded
- **Solution**: Click to expand, wait for content, then test
- **Example**: Click each `.accordion-header`, wait 500ms for expansion

## Proposed Architecture

### A. Training Recorder Interface

#### UI Location
Add "Train Page" button to page detail view (`/pages/{page_id}`) next to "Test Page" button

#### Recording Interface
- Launch interactive browser window (Puppeteer headed mode)
- Record user interactions in sequence
- Display recorded steps in real-time
- Allow editing/reordering steps
- Save as "Page Setup Script"

#### Recordable Actions
1. **Click**: Click element by selector
2. **Type**: Enter text into input field
3. **Wait**: Wait for duration (ms) or element to appear
4. **Wait for Navigation**: Wait for page navigation/reload
5. **Wait for Network Idle**: Wait for AJAX/network requests to complete
6. **Scroll**: Scroll to element or position
7. **Select**: Choose dropdown option
8. **Hover**: Hover over element (for hover states)
9. **Screenshot**: Capture screenshot at this step (debugging)

### B. Data Model

#### Page Setup Script (stored in MongoDB)
```json
{
  "page_id": "ObjectId",
  "name": "Accept Cookie Notice and Sign In",
  "description": "Handles cookie banner and logs in as test user",
  "created_by": "user_id",
  "created_date": "2025-10-30T10:00:00",
  "last_modified": "2025-10-30T12:30:00",
  "enabled": true,
  "steps": [
    {
      "step_number": 1,
      "action_type": "click",
      "selector": ".cookie-banner button.accept",
      "description": "Accept cookie notice",
      "wait_after": 500,
      "screenshot_after": false
    },
    {
      "step_number": 2,
      "action_type": "wait_for_selector",
      "selector": "input#username",
      "timeout": 5000,
      "description": "Wait for login form"
    },
    {
      "step_number": 3,
      "action_type": "type",
      "selector": "input#username",
      "value": "testuser@example.com",
      "description": "Enter username"
    },
    {
      "step_number": 4,
      "action_type": "type",
      "selector": "input#password",
      "value": "${ENV:TEST_PASSWORD}",
      "description": "Enter password (from environment)"
    },
    {
      "step_number": 5,
      "action_type": "click",
      "selector": "button[type='submit']",
      "description": "Submit login form",
      "wait_after": 0
    },
    {
      "step_number": 6,
      "action_type": "wait_for_navigation",
      "timeout": 10000,
      "description": "Wait for login redirect"
    }
  ],
  "validation": {
    "success_selector": ".user-profile",
    "success_text": "Welcome back",
    "failure_selectors": [".error-message", ".login-failed"]
  }
}
```

### C. Implementation Components

#### 1. Training Recorder (Frontend)
**File**: `auto_a11y/web/static/js/page-trainer.js`
- Opens WebSocket connection to backend
- Displays live browser feed (VNC-style or screenshots)
- Records user clicks/types in browser
- Sends actions to backend for storage
- Displays recorded steps with edit/delete options

#### 2. Training Controller (Backend)
**File**: `auto_a11y/training/page_trainer.py`
```python
class PageTrainer:
    async def start_training_session(page_id: str) -> str:
        """Launch headed browser, return session_id"""

    async def record_action(session_id: str, action: dict):
        """Record user action during training"""

    async def save_training_script(session_id: str, name: str, description: str):
        """Save recorded actions as Page Setup Script"""

    async def execute_script(page, script_id: str):
        """Execute saved script on page before testing"""
```

#### 3. Script Executor (Integration Point)
**File**: `auto_a11y/testing/script_executor.py`
- Executes saved setup scripts before running tests
- Handles errors gracefully (retry, skip, fail test)
- Logs execution for debugging
- Supports environment variables for secrets

**Integration into TestRunner**:
```python
# In test_runner.py test_page() method
async def test_page(self, page: Page, ...):
    # After browser.goto()
    if page.setup_script_id:
        script = self.db.get_page_setup_script(page.setup_script_id)
        if script and script.enabled:
            await self.script_executor.execute(browser_page, script)

    # Then run accessibility tests as normal
```

#### 4. Database Schema
**Collection**: `page_setup_scripts`
```javascript
{
  _id: ObjectId,
  page_id: ObjectId,
  name: String,
  description: String,
  enabled: Boolean,
  steps: Array,
  validation: Object,
  created_by: String,
  created_date: Date,
  last_modified: Date,
  execution_stats: {
    last_executed: Date,
    success_count: Number,
    failure_count: Number,
    average_duration_ms: Number
  }
}
```

**Page Model Update**:
```python
# Add to Page model
class Page:
    # ... existing fields ...
    setup_script_id: Optional[str] = None  # Reference to page_setup_scripts._id
```

### D. User Interface Flow

#### Training Page
```
┌─────────────────────────────────────────────────────────────┐
│ Page: https://example.com/dashboard                        │
│ ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐ │
│ │ Test Page       │  │ Train Page   │  │ View Scripts   │ │
│ └─────────────────┘  └──────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────┘

When "Train Page" clicked:
┌─────────────────────────────────────────────────────────────┐
│ Recording New Page Setup Script                             │
│                                                               │
│ Browser Window (Live View):                                  │
│ ┌───────────────────────────────────────────────────────┐   │
│ │  [Browser renders actual page, user can interact]     │   │
│ │                                                         │   │
│ │  (Headed Puppeteer instance)                           │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                               │
│ Recorded Steps:                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 1. [Click] .cookie-accept        [Edit] [Delete] [↑↓]  │ │
│ │ 2. [Wait]  500ms                 [Edit] [Delete] [↑↓]  │ │
│ │ 3. [Type]  input#username        [Edit] [Delete] [↑↓]  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ [⏸ Pause Recording]  [➕ Add Manual Step]  [💾 Save Script] │
└─────────────────────────────────────────────────────────────┘
```

#### Script Management
```
┌─────────────────────────────────────────────────────────────┐
│ Page Setup Scripts for: https://example.com/dashboard      │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ✓ Accept Cookie & Sign In                              │ │
│ │   6 steps · Last modified: 2 days ago                   │ │
│ │   [✓ Enabled] [Edit] [Test] [Duplicate] [Delete]      │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ ✗ Open Help Dialog                                      │ │
│ │   3 steps · Last modified: 1 week ago                   │ │
│ │   [  Disabled] [Edit] [Test] [Duplicate] [Delete]     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ [+ Create New Script]                                        │
└─────────────────────────────────────────────────────────────┘
```

### E. Technical Considerations

#### Security
- **Environment Variables**: Support `${ENV:VAR_NAME}` for passwords
- **Secrets Storage**: Never store plaintext passwords in scripts
- **Access Control**: Only project owners can create/edit scripts
- **Audit Log**: Track who creates/modifies scripts

#### Error Handling
- **Selector Not Found**: Retry with timeout, then fail gracefully
- **Navigation Timeout**: Log warning, continue or abort based on config
- **Script Execution Failure**: Mark test as "Setup Failed", don't mark page as failed
- **Partial Success**: Allow tests to run even if setup partially fails (configurable)

#### Performance
- **Script Caching**: Cache compiled scripts in memory
- **Parallel Execution**: Scripts run in same Puppeteer instance as tests (no extra browser launch)
- **Timeout Limits**: Max total script execution time (default: 60s)

#### Debugging
- **Screenshot on Failure**: Auto-capture screenshot if step fails
- **Step Logging**: Log each step execution with timing
- **Dry Run Mode**: Execute script without running tests to verify it works
- **Selector Inspector**: Highlight matched elements during recording

### F. Alternative Approaches Considered

#### 1. Puppeteer Recording Tools
**Option**: Use existing tools like Puppeteer Recorder (Chrome DevTools)
- **Pros**: Already built, mature, well-tested
- **Cons**: External dependency, harder to integrate, no database storage

#### 2. Selenium-style Test Scripts
**Option**: Write Python scripts using Pyppeteer directly
- **Pros**: Full programming power, version controlled
- **Cons**: Requires coding knowledge, not user-friendly, harder to maintain

#### 3. Visual Recording (Image-based)
**Option**: Record screen coordinates and images instead of selectors
- **Pros**: Works even without stable selectors
- **Cons**: Fragile, breaks on layout changes, resolution-dependent

**Recommendation**: **Custom recorder with selector-based recording** (proposed approach) balances usability, maintainability, and robustness.

### G. Implementation Phases

#### Phase 1: Core Infrastructure - COMPLETE ✅
- [x] Database schema for `page_setup_scripts` collection
- [x] `ScriptExecutor` class to run saved scripts
- [x] Integration into `TestRunner.test_page()`
- [x] Page model updated with `setup_script_id` field
- [x] All CRUD operations for scripts
- [x] Environment variable support
- [x] Execution statistics tracking

**Completed:** October 30, 2025
**See:** `docs/INTERACTIVE_PAGE_TRAINING_IMPLEMENTATION.md` for details

#### Phase 2: Recording UI (Week 2)
- [ ] "Train Page" button on page detail view
- [ ] WebSocket connection for live recording
- [ ] Display recorded steps in UI
- [ ] Basic edit/delete functionality

#### Phase 3: Script Management (Week 3)
- [ ] Script list view
- [ ] Enable/disable scripts
- [ ] Test script execution (dry run)
- [ ] Duplicate/clone scripts

#### Phase 4: Advanced Features (Week 4)
- [ ] Environment variable support for secrets
- [ ] Validation selectors (success/failure detection)
- [ ] Screenshot on step execution
- [ ] Execution statistics and monitoring

#### Phase 5: Polish & Documentation (Week 5)
- [ ] Error handling improvements
- [ ] User documentation
- [ ] Video tutorials
- [ ] Performance optimization

### H. Open Questions

1. **Browser Display**: How to show live browser to user?
   - Option A: VNC-like streaming (complex but real-time)
   - Option B: Screenshot polling every 500ms (simpler, slight lag)
   - Option C: Puppeteer CDP screenshots (middle ground)
   - **Recommendation**: Start with Option C, consider Option A later

2. **Recording Scope**: Record at website or page level?
   - Website level: Share scripts across pages (e.g., login once)
   - Page level: Each page has own scripts
   - **Recommendation**: Page level initially, add website-level inheritance later

3. **Concurrent Training**: Allow multiple users to train simultaneously?
   - **Recommendation**: No initially (too complex), add later if needed

4. **Script Versioning**: Keep history of script changes?
   - **Recommendation**: Nice to have, not critical for MVP

5. **Selector Stability**: How to handle changing selectors?
   - Option A: Try multiple selector strategies (ID > data-testid > class)
   - Option B: AI-based element finding
   - **Recommendation**: Option A for MVP

### I. Success Metrics

- **Adoption**: % of pages with setup scripts
- **Reliability**: % of script executions that succeed
- **Time Savings**: Reduction in manual pre-test setup time
- **Test Coverage**: Increase in testable pages (e.g., authenticated areas)

### J. Future Enhancements

1. **AI-Powered Recording**: Auto-detect common patterns (cookie banners, login forms)
2. **Script Templates**: Pre-built scripts for popular CMSs (WordPress, Drupal, etc.)
3. **Conditional Logic**: If/else branching in scripts
4. **Data-Driven Tests**: Run same script with different inputs
5. **Cross-Page Scripts**: Navigate through multiple pages
6. **Integration Testing**: Test multi-page workflows
7. **Visual Regression**: Compare screenshots before/after script execution
8. **Performance Monitoring**: Track page load times during script execution

## Recommendation

**Proceed with phased implementation** starting with Phase 1 (Core Infrastructure). This provides immediate value by solving the cookie banner and authentication problems while laying groundwork for more advanced features.

**Priority Use Case**: Cookie banner dismissal (highest ROI, simplest to implement)

**Technology Stack**:
- Backend: Python with Pyppeteer (already in use)
- Frontend: JavaScript with WebSocket for live updates
- Storage: MongoDB (existing database)
- Browser: Chromium (via Puppeteer, already in use)

**Estimated Timeline**: 5 weeks for full implementation, 1 week for MVP (cookie banners only)
