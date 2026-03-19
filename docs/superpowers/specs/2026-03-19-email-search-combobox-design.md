# Email Search Combobox for Member Management

**Date:** 2026-03-19
**Status:** Approved

## Problem

The current member management UI uses a plain `<select>` dropdown populated with all non-member users on page load. The `GET /projects/<id>/members` endpoint returns every user via `db.get_app_users()` (limit 100). This doesn't scale beyond a few dozen users — with thousands of users the dropdown is unusable and the payload is excessive.

## Solution

Replace the `<select>` with a server-side search API and an accessible combobox widget. Users type an email or name, the frontend debounces and queries the API, and results appear in a keyboard-navigable dropdown.

## Design

### Backend: Search API

**Endpoint:** `GET /members/api/search-users`

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| `q` | Yes | Search string, minimum 2 characters |
| `exclude_project` | No | Project ID — excludes current members from results |
| `limit` | No | Max results, default 10, cap 20 |

**Query logic:**
- Split `q` into terms by whitespace (e.g., `"jane smi"` → `["jane", "smi"]`)
- Each term becomes a case-insensitive regex against `email` OR `display_name`
- All terms must match (AND) — `"jane smi"` finds `jane.smith@...` but not `bob.smith@...`
- Regex input is escaped with `re.escape()` to prevent ReDoS
- MongoDB query structure: `{"$and": [{"$or": [{"email": /term/i}, {"display_name": /term/i}]}, ...]}`

**Response:**
```json
{
  "users": [
    {"user_id": "abc123", "email": "jane.smith@co.com", "display_name": "Jane Smith"}
  ]
}
```

**Security:** Protected by the global `before_request` login guard in `app.py` (no per-route decorator needed). This endpoint is intentionally not project-scoped — any authenticated user can search for other users by email, since the search results contain only public profile info (email, display name). The `exclude_project` parameter is a convenience filter, not a security boundary.

**Filters:**
- Only returns active users (`is_active: True`) — deactivated accounts are excluded
- `display_name` may be `None` (password-based users without SSO). Response includes it as `null`; frontend falls back to email when display_name is absent.

**Database:** At thousands of users, MongoDB handles regex collection scans in single-digit milliseconds. No special index beyond the default `_id` is needed, though an index on `email` exists for login lookups. When `exclude_project` is provided, the endpoint first fetches the project's member list to build an exclusion set, then passes those user IDs to the search query (two DB calls total).

**Location:** New route in `auto_a11y/web/routes/members.py` at path `/members/api/search-users` (consistent with blueprint-relative `/...` path convention used by other blueprints like `projects_bp`).

### Frontend: Accessible Combobox

**Location:** `auto_a11y/web/templates/projects/view.html` (replaces existing `<select id="new-member-user">`).

**Interaction states:**

1. **Empty** — Text input with placeholder "Search by email or name..." and hint text "Type at least 2 characters to search"
2. **Typing** — After 2+ characters and 300ms debounce, fires API request. Shows searching indicator.
3. **Results** — Dropdown appears below input with up to 10 matches. Each result shows display name and email with matched substring highlighted. Keyboard navigable (↑↓ arrows, Enter to select, Esc to close).
4. **Selected** — Selected user shown as a chip (name + email + × clear button). Hidden input holds `user_id` for the existing `addMember()` function.

**HTML structure:**
```html
<div class="combobox-wrapper">
  <input type="text" role="combobox"
         aria-expanded="false"
         aria-controls="user-listbox"
         aria-activedescendant=""
         aria-autocomplete="list"
         autocomplete="off"
         placeholder="Search by email or name..." />
  <ul id="user-listbox" role="listbox" hidden>
    <li role="option" id="user-opt-0">...</li>
  </ul>
  <div aria-live="polite" class="visually-hidden"><!-- announces result count --></div>
  <input type="hidden" id="new-member-user" />
</div>
```

**ARIA combobox pattern:**
- `role="combobox"` on the text input
- `role="listbox"` on the results dropdown
- `role="option"` on each result item
- `aria-activedescendant` tracks the keyboard-focused option
- `aria-expanded` reflects dropdown visibility
- Live region announces result count on each search

**Keyboard interaction:**
- ↑/↓ arrows: navigate options (with visual and `aria-activedescendant` tracking)
- Enter: select the active option
- Escape: close dropdown, clear input if no selection
- Tab: close dropdown, preserve selection if made

**JavaScript functions** (inline in view.html, matching existing pattern):
- `onSearchInput()` — debounce handler, calls API after 300ms when 2+ chars
- `renderResults(users)` — populates listbox, highlights matched text, updates live region
- `onKeyDown(e)` — ↑↓/Enter/Esc handling
- `selectUser(user)` — shows chip, sets hidden input, collapses listbox
- `clearSelection()` — resets to empty input state

**`addMember()` contract preserved** — it already reads `#new-member-user` value. The hidden input is a drop-in replacement. After `addMember()` calls `loadMembers()`, the combobox resets to the empty state (clear chip, clear hidden input).

**`loadMembers()` update** — remove the existing code that populates the `<select>` from `data.available_users` (lines 661-668). The combobox handles user selection independently via the search API. The `available_users` field is no longer returned from the endpoint.

**CSS additions** in `style.css`:
- `.combobox-wrapper` — positioning context
- `.combobox-listbox` — absolute dropdown below input
- `.combobox-option` — result items with hover/focus styles
- `.combobox-chip` — selected user pill with clear button
- Uses existing Bootstrap `.visually-hidden` class for the live region (no new utility class needed)

### What Changes

| File | Change |
|------|--------|
| `auto_a11y/web/routes/members.py` | Add `GET /members/api/search-users` endpoint |
| `auto_a11y/core/database.py` | Add `search_app_users(query, exclude_ids, limit)` method |
| `auto_a11y/web/templates/projects/view.html` | Replace `<select>` with combobox HTML + JS; update `loadMembers()` to remove `available_users` population code and reset combobox state |
| `auto_a11y/web/static/css/style.css` | Add combobox CSS classes |
| `auto_a11y/web/routes/members.py` (`list_project_members`) | Remove `available_users` from response (no longer needed) |

### What Doesn't Change

- `addMember()` function — hidden input preserves the existing interface
- `updateMemberRole()`, `removeMember()` — untouched
- Member list table rendering — untouched
- Backend member CRUD endpoints — untouched
- Database schema — no new collections or fields
