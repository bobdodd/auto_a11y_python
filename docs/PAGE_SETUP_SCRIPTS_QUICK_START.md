# Page Setup Scripts - Quick Start Guide

**Status:** Phase 1 Complete (Core Infrastructure)
**Next:** Phase 2 (Recording UI)

---

## What Are Page Setup Scripts?

Page setup scripts allow you to interact with pages **before** running accessibility tests. Common use cases:

- ✅ **Dismiss cookie notices** that block content
- ✅ **Authenticate** to test protected pages
- ✅ **Open dynamic dialogs** triggered by buttons
- ✅ **Navigate multi-step wizards** to test each step
- ✅ **Expand accordions** to test hidden content

---

## Current Status (Phase 1)

### What Works ✅

- **Backend fully functional** - Store, retrieve, and execute scripts
- **10 action types** - Click, type, wait, scroll, hover, select, etc.
- **Environment variables** - Secure password handling with `${ENV:VAR_NAME}`
- **Validation rules** - Detect success/failure conditions
- **Execution stats** - Track success rate and performance
- **Test integration** - Scripts run automatically before tests

### What's Missing ⏳

- **Recording UI** (Phase 2) - Currently must create scripts programmatically
- **Script manager** (Phase 3) - UI to view, edit, and manage scripts
- **Templates** (Phase 4) - Pre-built scripts for common scenarios

---

## Quick Start: Create Your First Script

### 1. Cookie Notice Dismissal

```python
from auto_a11y.core.database import Database
from auto_a11y.models import PageSetupScript, ScriptStep, ActionType

db = Database('mongodb://localhost:27017/', 'auto_a11y')

# Create script
script = PageSetupScript(
    page_id='YOUR_PAGE_ID',
    name='Dismiss Cookie Notice',
    description='Clicks accept on cookie banner',
    enabled=True,
    steps=[
        ScriptStep(
            step_number=1,
            action_type=ActionType.WAIT_FOR_SELECTOR,
            selector='.cookie-banner',
            description='Wait for banner',
            timeout=5000
        ),
        ScriptStep(
            step_number=2,
            action_type=ActionType.CLICK,
            selector='button.accept',
            description='Click accept',
            wait_after=1000
        )
    ]
)

# Save and associate with page
script_id = db.create_page_setup_script(script)
page = db.get_page('YOUR_PAGE_ID')
page.setup_script_id = script_id
db.update_page(page)
```

### 2. Authentication

```python
script = PageSetupScript(
    page_id='YOUR_PAGE_ID',
    name='Sign In',
    description='Log in with test credentials',
    enabled=True,
    steps=[
        ScriptStep(
            step_number=1,
            action_type=ActionType.TYPE,
            selector='input#username',
            value='testuser@example.com',
            description='Enter username'
        ),
        ScriptStep(
            step_number=2,
            action_type=ActionType.TYPE,
            selector='input#password',
            value='${ENV:TEST_PASSWORD}',  # From environment
            description='Enter password'
        ),
        ScriptStep(
            step_number=3,
            action_type=ActionType.CLICK,
            selector='button[type="submit"]',
            description='Submit form'
        ),
        ScriptStep(
            step_number=4,
            action_type=ActionType.WAIT_FOR_NAVIGATION,
            description='Wait for redirect',
            timeout=10000
        )
    ]
)
```

---

## Action Types Reference

| Action | Description | Required Fields | Example |
|--------|-------------|-----------------|---------|
| **CLICK** | Click an element | `selector` | Click button |
| **TYPE** | Enter text | `selector`, `value` | Fill input field |
| **WAIT** | Wait for duration | `value` (milliseconds) | Wait 2 seconds |
| **WAIT_FOR_SELECTOR** | Wait for element to appear | `selector`, `timeout` | Wait for dialog |
| **WAIT_FOR_NAVIGATION** | Wait for page navigation | `timeout` | Wait for redirect |
| **WAIT_FOR_NETWORK_IDLE** | Wait for AJAX to complete | `timeout` | Wait for data load |
| **SCROLL** | Scroll to element | `selector` | Scroll to footer |
| **SELECT** | Choose dropdown option | `selector`, `value` | Select country |
| **HOVER** | Hover over element | `selector` | Show tooltip |
| **SCREENSHOT** | Take debug screenshot | None | Capture state |

---

## Environment Variables (Security)

**Never store passwords in scripts!** Use environment variables:

```python
# In script
ScriptStep(
    action_type=ActionType.TYPE,
    selector='input#password',
    value='${ENV:TEST_PASSWORD}',  # Will be replaced
    description='Enter password'
)

# Set environment variable
import os
os.environ['TEST_PASSWORD'] = 'your_secure_password'

# Or in shell
export TEST_PASSWORD='your_secure_password'
```

---

## Validation Rules (Optional)

Detect if script succeeded or failed:

```python
from auto_a11y.models import ScriptValidation

script.validation = ScriptValidation(
    success_selector='.user-profile',     # Must be present
    success_text='Welcome back',          # Must be in page
    failure_selectors=[                   # Must NOT be present
        '.error-message',
        '.login-failed'
    ]
)
```

---

## Database Operations

### Create Script

```python
script_id = db.create_page_setup_script(script)
```

### Get Script

```python
script = db.get_page_setup_script(script_id)
```

### Get All Scripts for Page

```python
scripts = db.get_page_setup_scripts_for_page(page_id)
```

### Get Enabled Script

```python
script = db.get_enabled_script_for_page(page_id)
```

### Update Script

```python
script.name = 'New Name'
script.enabled = False
db.update_page_setup_script(script)
```

### Delete Script

```python
db.delete_page_setup_script(script_id)
```

### Enable/Disable Script

```python
db.enable_page_setup_script(script_id, enabled=True)
```

---

## Execution Flow

When you test a page with a setup script:

```
1. Navigate to page
2. Wait for DOM ready
   ↓
3. Check if page has setup script
   ↓
4. Execute script (if exists)
   - Run each step in order
   - Wait after each step if specified
   - Take screenshots on error
   - Update execution stats
   ↓
5. Run accessibility tests
   (Even if script fails)
```

---

## Execution Statistics

Scripts track performance automatically:

```python
script = db.get_page_setup_script(script_id)
stats = script.execution_stats

print(f"Last executed: {stats.last_executed}")
print(f"Success count: {stats.success_count}")
print(f"Failure count: {stats.failure_count}")
print(f"Average duration: {stats.average_duration_ms}ms")

# Calculate success rate
total = stats.success_count + stats.failure_count
rate = (stats.success_count / total * 100) if total > 0 else 0
print(f"Success rate: {rate:.1f}%")
```

---

## Debugging

### Debug Screenshots

Enable screenshots after each step:

```python
ScriptStep(
    step_number=1,
    action_type=ActionType.CLICK,
    selector='button',
    screenshot_after=True  # Take screenshot after clicking
)
```

Screenshots saved to: `screenshots/script_debug/`

### Check Execution Log

Scripts return detailed execution logs:

```python
result = await script_executor.execute_script(page, script)

for step_log in result['execution_log']:
    print(f"Step {step_log['step_number']}: {step_log['description']}")
    print(f"  Success: {step_log['success']}")
    print(f"  Duration: {step_log['duration_ms']}ms")
    if 'error' in step_log:
        print(f"  Error: {step_log['error']}")
```

---

## Common Patterns

### Pattern 1: Cookie Notice with Multiple Selectors

```python
# Try multiple possible selectors
ScriptStep(
    action_type=ActionType.WAIT_FOR_SELECTOR,
    selector='.cookie-banner, #cookie-notice, [data-cookie]',
    description='Wait for any cookie banner variant'
)
```

### Pattern 2: Wait Then Validate

```python
steps = [
    ScriptStep(
        action_type=ActionType.CLICK,
        selector='button.open-dialog',
        description='Open dialog'
    ),
    ScriptStep(
        action_type=ActionType.WAIT,
        value='2000',  # Wait 2 seconds
        description='Wait for animation'
    ),
    ScriptStep(
        action_type=ActionType.WAIT_FOR_SELECTOR,
        selector='.dialog-content',
        description='Verify dialog appeared'
    )
]
```

### Pattern 3: Sequential Form Fill

```python
steps = [
    ScriptStep(action_type=ActionType.TYPE, selector='#name', value='John Doe'),
    ScriptStep(action_type=ActionType.TYPE, selector='#email', value='john@example.com'),
    ScriptStep(action_type=ActionType.SELECT, selector='#country', value='US'),
    ScriptStep(action_type=ActionType.CLICK, selector='button[type="submit"]')
]
```

---

## Best Practices

### ✅ DO

- Use **specific selectors** (IDs, data attributes)
- Add **wait_after** for animations
- Use **WAIT_FOR_SELECTOR** instead of hardcoded waits
- Set reasonable **timeouts** (5-10 seconds)
- Use **environment variables** for sensitive data
- Add **validation rules** to detect failures
- Enable **screenshot_after** for debugging

### ❌ DON'T

- Don't use **brittle selectors** (nth-child, complex paths)
- Don't store **passwords** in script values
- Don't use **excessive waits** (slow down tests)
- Don't assume **immediate results** (add waits)
- Don't skip **error handling** (validate success)

---

## Troubleshooting

### Script Not Running

1. Check script is enabled: `script.enabled == True`
2. Check page has script ID: `page.setup_script_id is not None`
3. Check database connection
4. Check logs: `tail -f logs/auto_a11y.log`

### Script Failing

1. Enable debug screenshots: `screenshot_after=True`
2. Check execution log in database
3. Verify selectors: Use browser DevTools
4. Increase timeouts if needed
5. Check validation rules aren't too strict

### Environment Variables Not Working

1. Format: `${ENV:VAR_NAME}` (uppercase, underscores only)
2. Set before running: `export VAR_NAME=value`
3. Check spelling matches exactly
4. Test: `echo $VAR_NAME` in shell

---

## Example Script

See `examples/create_cookie_script.py` for complete examples:

```bash
python examples/create_cookie_script.py
```

---

## Next Steps

Once Phase 2 (Recording UI) is complete:

1. Click "Train Page" button on page detail view
2. Interact with page in live browser
3. Review recorded steps
4. Save script
5. Script runs automatically on next test

Until then, create scripts programmatically using the API above.

---

## API Reference

Full documentation:
- **Design:** `docs/INTERACTIVE_PAGE_TRAINING_DESIGN.md`
- **Implementation:** `docs/INTERACTIVE_PAGE_TRAINING_IMPLEMENTATION.md`
- **Models:** `auto_a11y/models/page_setup_script.py`
- **Executor:** `auto_a11y/testing/script_executor.py`
- **Database:** `auto_a11y/core/database.py` (search "Page Setup Script Methods")

---

## Support

- **Issues:** GitHub Issues
- **Questions:** Project Documentation
- **Examples:** `examples/create_cookie_script.py`
