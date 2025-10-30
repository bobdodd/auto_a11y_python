# Multi-State Testing - UI/API Integration

**Date:** October 30, 2025
**Status:** Complete - Ready for Testing

---

## Overview

This document describes the UI and API changes to support multi-state testing. Users can now test pages in multiple states and view/compare results through the web interface and API.

---

## API Endpoints

### 1. Test Page with Multi-State Support

**Endpoint:** `POST /pages/<page_id>/test`

**Request Body:**
```json
{
  "enable_multi_state": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Page queued for testing (multi-state enabled)",
  "job_id": "test_page_123_1234567890.123",
  "multi_state": true,
  "status_url": "/pages/123/test-status"
}
```

**Behavior:**
- If `enable_multi_state=true` (default), uses `test_page_multi_state()` method
- Checks for scripts with `test_before_execution` or `test_after_execution` enabled
- Returns list of TestResult objects (one per state)
- Falls back to single-state if no multi-state scripts configured

### 2. Get Related Test Result States

**Endpoint:** `GET /api/v1/test-results/<result_id>/states`

**Description:** Get all test results from the same session (all states)

**Response:**
```json
{
  "success": true,
  "result_id": "507f1f77bcf86cd799439011",
  "total_states": 2,
  "states": [
    {
      "result_id": "507f1f77bcf86cd799439011",
      "state_sequence": 0,
      "page_state": {
        "state_id": "page123_state_0",
        "description": "Initial page state (before script execution)",
        "scripts_executed": [],
        "elements_visible": [".cookie-banner"]
      },
      "session_id": "session456",
      "test_date": "2025-10-30T10:30:00",
      "violation_count": 15,
      "warning_count": 5,
      "info_count": 2,
      "pass_count": 42,
      "duration_ms": 3500
    },
    {
      "result_id": "507f1f77bcf86cd799439012",
      "state_sequence": 1,
      "page_state": {
        "state_id": "page123_state_1",
        "description": "After executing script: Dismiss Cookie Notice",
        "scripts_executed": ["cookie_script_id"],
        "elements_hidden": [".cookie-banner"]
      },
      "session_id": "session456",
      "test_date": "2025-10-30T10:30:05",
      "violation_count": 12,
      "warning_count": 5,
      "info_count": 2,
      "pass_count": 42,
      "duration_ms": 2800
    }
  ]
}
```

**Use Cases:**
- View all states tested in a session
- Display state progression timeline
- Show before/after script execution results

### 3. Get Latest Test States for Page

**Endpoint:** `GET /api/v1/pages/<page_id>/test-states`

**Description:** Get the most recent test result for each state

**Response:**
```json
{
  "success": true,
  "page_id": "page123",
  "page_url": "https://example.com/page",
  "total_states": 2,
  "states": {
    "0": {
      "result_id": "507f1f77bcf86cd799439011",
      "state_sequence": 0,
      "page_state": { ... },
      "test_date": "2025-10-30T10:30:00",
      "violation_count": 15,
      ...
    },
    "1": {
      "result_id": "507f1f77bcf86cd799439012",
      "state_sequence": 1,
      "page_state": { ... },
      "test_date": "2025-10-30T10:30:05",
      "violation_count": 12,
      ...
    }
  }
}
```

**Use Cases:**
- Quick overview of current state results
- Dashboard displaying state-specific metrics
- Identify which states need attention

### 4. Get All Test Sessions for Page

**Endpoint:** `GET /api/v1/pages/<page_id>/test-sessions`

**Description:** Get all testing sessions with state counts

**Response:**
```json
{
  "success": true,
  "page_id": "page123",
  "page_url": "https://example.com/page",
  "total_sessions": 3,
  "sessions": [
    {
      "session_id": "session789",
      "test_date": "2025-10-30T14:00:00",
      "state_count": 2,
      "states": [
        {
          "result_id": "...",
          "state_sequence": 0,
          "state_description": "Initial page state",
          "violation_count": 15,
          "warning_count": 5
        },
        {
          "result_id": "...",
          "state_sequence": 1,
          "state_description": "After dismissing cookie",
          "violation_count": 12,
          "warning_count": 5
        }
      ],
      "total_violations": 27,
      "total_warnings": 10
    },
    ...
  ]
}
```

**Use Cases:**
- View testing history
- Track violation trends across sessions
- Identify when issues were introduced/fixed

### 5. Compare Two Test Results

**Endpoint:** `POST /api/v1/test-results/compare`

**Request Body:**
```json
{
  "result_id_1": "507f1f77bcf86cd799439011",
  "result_id_2": "507f1f77bcf86cd799439012"
}
```

**Response:**
```json
{
  "success": true,
  "comparison": {
    "result_1": {
      "id": "507f1f77bcf86cd799439011",
      "state_sequence": 0,
      "state_description": "Initial page state",
      "violation_count": 15,
      "test_date": "2025-10-30T10:30:00"
    },
    "result_2": {
      "id": "507f1f77bcf86cd799439012",
      "state_sequence": 1,
      "state_description": "After dismissing cookie",
      "violation_count": 12,
      "test_date": "2025-10-30T10:30:05"
    },
    "new_violations": [
      {
        "id": "ErrNewIssue",
        "impact": "high",
        "touchpoint": "forms",
        "description": "...",
        "element": "input#email"
      }
    ],
    "fixed_violations": [
      {
        "id": "ErrCookieBanner",
        "impact": "medium",
        "touchpoint": "page_structure",
        "description": "...",
        "element": ".cookie-banner"
      }
    ],
    "persistent_violations": [ ... ],
    "summary": {
      "new_count": 1,
      "fixed_count": 4,
      "persistent_count": 11,
      "net_change": -3
    }
  }
}
```

**Use Cases:**
- Compare before/after script execution
- Identify violations introduced by state changes
- Track violation fixes
- Generate diff reports

---

## UI Changes

### Page Testing Interface

**File:** `auto_a11y/web/routes/pages.py`

**Changes:**
- Test endpoint now accepts `enable_multi_state` parameter
- Defaults to `true` (multi-state testing enabled)
- Automatically uses `test_page_multi_state()` if scripts configured
- Falls back to single-state if no multi-state scripts present

**User Flow:**
```
1. User clicks "Test Page" button
2. System checks for multi-state scripts
3. If found: Runs multi-state test (multiple results)
4. If not found: Runs single-state test (one result)
5. All results saved to database with state metadata
```

### JavaScript Integration Example

**Testing a Page:**
```javascript
// Test page with multi-state enabled (default)
fetch(`/pages/${pageId}/test`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    enable_multi_state: true
  })
})
.then(r => r.json())
.then(data => {
  console.log(`Testing started: ${data.message}`);
  console.log(`Multi-state: ${data.multi_state}`);
  // Poll status_url for completion
});
```

**Getting State Results:**
```javascript
// Get all states for a test result
fetch(`/api/v1/test-results/${resultId}/states`)
  .then(r => r.json())
  .then(data => {
    console.log(`Found ${data.total_states} states`);
    data.states.forEach(state => {
      console.log(`State ${state.state_sequence}: ${state.page_state.description}`);
      console.log(`  Violations: ${state.violation_count}`);
    });
  });
```

**Comparing States:**
```javascript
// Compare two states
fetch('/api/v1/test-results/compare', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    result_id_1: state0ResultId,
    result_id_2: state1ResultId
  })
})
.then(r => r.json())
.then(data => {
  const summary = data.comparison.summary;
  console.log(`New violations: ${summary.new_count}`);
  console.log(`Fixed violations: ${summary.fixed_count}`);
  console.log(`Net change: ${summary.net_change}`);
});
```

---

## UI Enhancement Ideas (Future)

### 1. State Selector Widget

Display state tabs for test results:

```
┌─────────────────────────────────────────┐
│ Test Results - Page: example.com/home  │
├─────────────────────────────────────────┤
│ [State 0] [State 1] [Compare]          │
│ Initial   After Cookie                  │
│ 15 issues 12 issues                     │
├─────────────────────────────────────────┤
│ State 0: Initial page state             │
│ Test Date: Oct 30, 2025 10:30 AM       │
│                                         │
│ ✗ 15 Violations                         │
│ ⚠  5 Warnings                           │
│ ✓ 42 Passes                             │
└─────────────────────────────────────────┘
```

### 2. State Comparison View

Show side-by-side diff:

```
┌───────────────────────────────────────────────────────┐
│ Compare States                                        │
├─────────────────────┬─────────────────────────────────┤
│ State 0             │ State 1                         │
│ Initial             │ After Cookie Dismissal          │
├─────────────────────┼─────────────────────────────────┤
│ 15 violations       │ 12 violations (-3)              │
│ 5 warnings          │ 5 warnings (=)                  │
├─────────────────────┴─────────────────────────────────┤
│ New Issues (1):                                       │
│ • ErrNewIssue - Input missing label                   │
│                                                       │
│ Fixed Issues (4):                                     │
│ • ErrCookieBanner - Cookie banner violations          │
│ • ErrModalFocus - Modal focus trap                    │
│ • ErrHeadingOrder - Heading order in banner           │
│ • WarnColorContrast - Banner button contrast          │
└───────────────────────────────────────────────────────┘
```

### 3. State Timeline

Visual timeline of state transitions:

```
State 0 ────► Script ────► State 1
Initial       Dismiss      After
15 issues     Cookie       12 issues
              Banner

Timeline: 3.5s    2.8s
```

### 4. Session History

Table showing all test sessions:

```
┌─────────────┬──────────┬───────────┬────────────┐
│ Date        │ States   │ Total     │ Action     │
├─────────────┼──────────┼───────────┼────────────┤
│ Oct 30 2PM  │ 2 states │ 27 issues │ [View]     │
│ Oct 30 10AM │ 2 states │ 30 issues │ [View]     │
│ Oct 29 3PM  │ 1 state  │ 25 issues │ [View]     │
└─────────────┴──────────┴───────────┴────────────┘
```

---

## Testing Checklist

### API Endpoints

- [ ] Test `POST /pages/<page_id>/test` with `enable_multi_state=true`
- [ ] Test `POST /pages/<page_id>/test` with `enable_multi_state=false`
- [ ] Test `GET /api/v1/test-results/<result_id>/states`
- [ ] Test `GET /api/v1/pages/<page_id>/test-states`
- [ ] Test `GET /api/v1/pages/<page_id>/test-sessions`
- [ ] Test `POST /api/v1/test-results/compare`
- [ ] Verify error handling for missing results
- [ ] Verify error handling for missing pages
- [ ] Check response JSON structure
- [ ] Test with pages having no multi-state scripts

### Integration

- [ ] Create cookie dismissal script via UI
- [ ] Enable `test_before_execution` and `test_after_execution`
- [ ] Run test on page with cookie banner
- [ ] Verify 2 TestResult records created
- [ ] Check state_sequence values (0, 1)
- [ ] Verify page_state metadata
- [ ] Call states API endpoint
- [ ] Call comparison API endpoint
- [ ] Verify related_result_ids are set
- [ ] Test with existing (non-multi-state) pages

### Browser Testing

- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

---

## Example Usage Scenarios

### Scenario 1: Cookie Banner Testing

```bash
# 1. Create multi-state script (via UI or API)
# Set test_before_execution=true, test_after_execution=true

# 2. Test the page
curl -X POST http://localhost:5001/pages/123/test \
  -H "Content-Type: application/json" \
  -d '{"enable_multi_state": true}'

# 3. Wait for test completion, then get states
curl http://localhost:5001/api/v1/pages/123/test-states

# 4. Compare states
curl -X POST http://localhost:5001/api/v1/test-results/compare \
  -H "Content-Type: application/json" \
  -d '{
    "result_id_1": "state0_result_id",
    "result_id_2": "state1_result_id"
  }'
```

### Scenario 2: Tab Testing

```bash
# 1. Create script to click tabs
# 2. Test page (automatically tests all tabs)
# 3. View all session states
curl http://localhost:5001/api/v1/pages/123/test-sessions

# Response shows 4 states: initial + 3 tabs
```

### Scenario 3: Modal Testing

```bash
# 1. Create script to open modal
# 2. Test page (tests before and after modal opens)
# 3. Compare states to see modal-specific violations
```

---

## Backward Compatibility

✅ **Fully backward compatible:**

- Old pages without scripts work exactly as before
- Single-state testing still available (`enable_multi_state=false`)
- Existing test results display normally
- No UI changes required for basic functionality
- Multi-state features are additive only

---

## Files Modified

1. **`auto_a11y/web/routes/pages.py`**
   - Updated `test_page()` endpoint to support multi-state
   - Added `enable_multi_state` parameter (defaults to `true`)
   - Uses `test_page_multi_state()` when enabled

2. **`auto_a11y/web/routes/api.py`**
   - Added 4 new API endpoints:
     - `GET /api/v1/test-results/<result_id>/states`
     - `GET /api/v1/pages/<page_id>/test-states`
     - `GET /api/v1/pages/<page_id>/test-sessions`
     - `POST /api/v1/test-results/compare`

3. **`docs/UI_MULTI_STATE_TESTING.md`** (this file)
   - Complete API documentation
   - Usage examples
   - UI integration guide

---

## Next Steps

1. **Test the API endpoints** using curl or Postman
2. **Create multi-state scripts** via the UI
3. **Run tests** on pages with cookie banners
4. **Verify** multiple TestResult records are created
5. **Use the comparison API** to analyze differences

---

## Support

For issues or questions:
- Review this document
- Check `MULTI_STATE_TESTING_IMPLEMENTATION.md`
- Run example: `examples/multi_state_testing_example.py`
- Test API endpoints with curl

---

**Status:** ✅ Complete - Ready for UI Testing
**Date:** October 30, 2025
