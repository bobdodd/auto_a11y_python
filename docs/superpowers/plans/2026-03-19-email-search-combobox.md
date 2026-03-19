# Email Search Combobox Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the plain `<select>` dropdown for adding project members with a server-side search API and accessible combobox widget that scales to thousands of users.

**Architecture:** New `search_app_users()` database method with MongoDB regex queries, exposed via `GET /members/api/search-users` route. Frontend replaces the `<select>` with a custom ARIA combobox (text input + listbox) using debounced fetch. Hidden `<input>` preserves the existing `addMember()` contract.

**Tech Stack:** Python/Flask (backend), MongoDB regex queries (search), vanilla JavaScript (frontend combobox), Bootstrap 5 CSS (styling)

**Spec:** `docs/superpowers/specs/2026-03-19-email-search-combobox-design.md`

---

### Task 1: Database search method

**Files:**
- Modify: `auto_a11y/core/database.py:2502-2517` (after `get_app_users`)

- [ ] **Step 1: Add `search_app_users` method to Database class**

Add this method after the existing `get_app_users` method (line ~2517) in `auto_a11y/core/database.py`:

First, add `import re` to the top-level imports in `database.py` (it is not currently imported). Add it alongside the other stdlib imports.

Then add the method after `get_app_users` (line ~2517):

```python
def search_app_users(
    self,
    query: str,
    exclude_user_ids: Optional[List[str]] = None,
    limit: int = 10
) -> List[AppUser]:
    """Search active app users by email or display_name.

    Args:
        query: Search string, split into terms. Each term is matched
               as a case-insensitive substring against email and display_name.
               All terms must match (AND logic).
        exclude_user_ids: User IDs to exclude from results.
        limit: Maximum results to return (capped at 20).
    """
    limit = min(limit, 20)
    terms = query.strip().split()
    if not terms:
        return []

    mongo_query: dict = {"is_active": True}

    # Each term must match email OR display_name
    and_conditions = []
    for term in terms:
        escaped = re.escape(term)
        pattern = {"$regex": escaped, "$options": "i"}
        and_conditions.append({
            "$or": [
                {"email": pattern},
                {"display_name": pattern},
            ]
        })
    mongo_query["$and"] = and_conditions

    if exclude_user_ids:
        mongo_query["_id"] = {
            "$nin": [ObjectId(uid) for uid in exclude_user_ids]
        }

    docs = self.app_users.find(mongo_query).sort("email", 1).limit(limit)
    return [AppUser.from_dict(doc) for doc in docs]
```

Note: `ObjectId` is already imported from `bson` at the top of `database.py`.

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/core/database.py
git commit -m "feat: add search_app_users database method for email/name search"
```

---

### Task 2: Search API endpoint

**Files:**
- Modify: `auto_a11y/web/routes/members.py:1-8` (imports, new route)

- [ ] **Step 1: Add search endpoint to members.py**

Add this route at the end of `auto_a11y/web/routes/members.py` (before the website member routes, around line 121):

```python
@members_bp.route('/members/api/search-users', methods=['GET'])
def search_users():
    """Search app users by email or display name for member autocomplete."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'users': []})

    exclude_project = request.args.get('exclude_project', '').strip()
    try:
        limit = min(int(request.args.get('limit', 10)), 20)
    except (ValueError, TypeError):
        limit = 10

    exclude_ids = []
    if exclude_project:
        project = current_app.db.get_project(exclude_project)
        if project:
            exclude_ids = [m.user_id for m in project.members]

    users = current_app.db.search_app_users(
        query=q,
        exclude_user_ids=exclude_ids if exclude_ids else None,
        limit=limit
    )

    return jsonify({
        'users': [
            {
                'user_id': str(u.get_id()),
                'email': u.email,
                'display_name': u.display_name,
            }
            for u in users
        ]
    })
```

This endpoint is protected by the global `before_request` login guard in `app.py` — no additional decorator is needed.

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/routes/members.py
git commit -m "feat: add GET /members/api/search-users endpoint"
```

---

### Task 3: Remove available_users from list_project_members

**Files:**
- Modify: `auto_a11y/web/routes/members.py:29-41`

- [ ] **Step 1: Remove the available_users block from list_project_members**

In `list_project_members()` (lines 29-41 of `members.py`), remove this code:

```python
    # Get all users for the "add member" dropdown (exclude current members)
    member_ids = {m.user_id for m in project.members}
    all_users = current_app.db.get_app_users()
    available_users = [
        {'user_id': str(u.get_id()), 'email': u.email, 'display_name': u.display_name}
        for u in all_users
        if str(u.get_id()) not in member_ids
    ]
```

And remove `'available_users': available_users,` from the return `jsonify()` call. The return should become:

```python
    return jsonify({
        'members': members,
        'roles': [r.value for r in UserRole],
    })
```

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/routes/members.py
git commit -m "refactor: remove available_users from list_project_members response"
```

---

### Task 4: Replace select with combobox HTML

**Files:**
- Modify: `auto_a11y/web/templates/projects/view.html:404-427` (the add-member-form div)

- [ ] **Step 1: Replace the select element with combobox markup**

Replace the `<!-- Add Member Form -->` div (lines 404-427 of `view.html`) with:

```html
            <!-- Add Member Form -->
            <div id="add-member-form" class="mb-3" style="display:none;">
                <div class="row g-2 align-items-end">
                    <div class="col-md-5">
                        <label for="member-search-input" class="form-label">{{ _('User') }}</label>
                        <div class="combobox-wrapper" id="member-combobox">
                            <div id="member-chip" class="combobox-chip" style="display:none;">
                                <span id="member-chip-text"></span>
                                <button type="button" class="combobox-chip-clear" aria-label="{{ _('Clear selection') }}" onclick="clearMemberSelection()">&times;</button>
                            </div>
                            <input type="text" id="member-search-input"
                                   class="form-control form-control-sm"
                                   role="combobox"
                                   aria-expanded="false"
                                   aria-controls="member-search-listbox"
                                   aria-activedescendant=""
                                   aria-autocomplete="list"
                                   autocomplete="off"
                                   placeholder="{{ _('Search by email or name...') }}" />
                            <div class="combobox-hint text-muted small" id="member-search-hint">{{ _('Type at least 2 characters to search') }}</div>
                            <ul id="member-search-listbox" class="combobox-listbox" role="listbox" hidden></ul>
                            <div id="member-search-live" aria-live="polite" class="visually-hidden"></div>
                            <input type="hidden" id="new-member-user" value="" />
                        </div>
                    </div>
                    <div class="col-md-4">
                        <label for="new-member-role" class="form-label">{{ _('Role') }}</label>
                        <select id="new-member-role" class="form-select form-select-sm">
                            <option value="admin">Admin</option>
                            <option value="auditor">Auditor</option>
                            <option value="client" selected>Client</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <button type="button" class="btn btn-sm btn-primary w-100" onclick="addMember()">
                            <i class="bi bi-plus-circle" aria-hidden="true"></i> {{ _('Add') }}
                        </button>
                    </div>
                </div>
            </div>
```

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/templates/projects/view.html
git commit -m "feat: replace select with combobox HTML markup for member search"
```

---

### Task 5: Add combobox CSS

**Files:**
- Modify: `auto_a11y/web/static/css/style.css` (append at end)

- [ ] **Step 1: Add combobox styles to style.css**

Append these styles at the end of `style.css`:

```css
/* === Combobox (member search) === */
.combobox-wrapper {
    position: relative;
}

.combobox-listbox {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    z-index: 1050;
    max-height: 260px;
    overflow-y: auto;
    margin: 0;
    padding: 0;
    list-style: none;
    background: var(--color-surface, var(--bs-body-bg));
    border: 1px solid var(--color-border, var(--bs-border-color));
    border-top: none;
    border-radius: 0 0 var(--bs-border-radius) var(--bs-border-radius);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.combobox-option {
    padding: 0.5rem 0.75rem;
    cursor: pointer;
    border-bottom: 1px solid var(--color-border-subtle, rgba(0, 0, 0, 0.05));
}

.combobox-option:last-child {
    border-bottom: none;
}

.combobox-option:hover,
.combobox-option.active {
    background: var(--color-bg-hover, rgba(var(--bs-primary-rgb), 0.1));
}

.combobox-option-name {
    font-weight: 500;
    color: var(--color-text, var(--bs-body-color));
}

.combobox-option-email {
    font-size: 0.85em;
    color: var(--color-text-muted, var(--bs-secondary-color));
}

.combobox-option mark {
    background: rgba(var(--bs-primary-rgb), 0.2);
    color: inherit;
    padding: 0;
    border-radius: 2px;
}

.combobox-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.625rem;
    background: var(--color-bg-hover, rgba(var(--bs-primary-rgb), 0.1));
    border: 1px solid var(--color-border, var(--bs-border-color));
    border-radius: 1rem;
    font-size: 0.85rem;
    color: var(--color-text, var(--bs-body-color));
    margin-bottom: 0.25rem;
}

.combobox-chip-clear {
    background: none;
    border: none;
    padding: 0;
    font-size: 1.1rem;
    line-height: 1;
    color: var(--color-text-muted, var(--bs-secondary-color));
    cursor: pointer;
    opacity: 0.7;
}

.combobox-chip-clear:hover {
    opacity: 1;
}

.combobox-hint {
    margin-top: 0.25rem;
}

.combobox-no-results {
    padding: 0.75rem;
    text-align: center;
    color: var(--color-text-muted, var(--bs-secondary-color));
    font-style: italic;
}
```

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/static/css/style.css
git commit -m "feat: add combobox CSS styles for member search dropdown"
```

---

### Task 6: Add combobox JavaScript

**Files:**
- Modify: `auto_a11y/web/templates/projects/view.html:620-714` (the `<script>` block)

- [ ] **Step 1: Update loadMembers() to remove available_users code and reset combobox**

In `view.html`, inside the `loadMembers()` function (lines 660-670), replace this block:

```javascript
        // Populate available users dropdown
        const sel = document.getElementById('new-member-user');
        sel.innerHTML = '<option value="">Select a user...</option>';
        data.available_users.forEach(u => {
            const opt = document.createElement('option');
            opt.value = u.user_id;
            opt.textContent = u.display_name || u.email;
            sel.appendChild(opt);
        });
```

With:

```javascript
        // Reset combobox state
        clearMemberSelection();
```

- [ ] **Step 2: Add combobox JavaScript functions**

Add the following functions inside the same `<script>` block, after the existing `removeMember()` function (after line 711) and before the `document.addEventListener('DOMContentLoaded', loadMembers);` line:

```javascript
// --- Member search combobox ---
let memberSearchTimeout = null;
let memberActiveIndex = -1;
let memberSearchResults = [];

function onMemberSearchInput() {
    const input = document.getElementById('member-search-input');
    const q = input.value.trim();
    const hint = document.getElementById('member-search-hint');

    clearTimeout(memberSearchTimeout);
    memberActiveIndex = -1;

    if (q.length < 2) {
        closeMemberListbox();
        hint.style.display = '';
        return;
    }

    hint.style.display = 'none';
    memberSearchTimeout = setTimeout(() => {
        showMemberSearching();
        fetchMemberSearch(q);
    }, 300);
}

function showMemberSearching() {
    const listbox = document.getElementById('member-search-listbox');
    const input = document.getElementById('member-search-input');
    listbox.innerHTML = '<li class="combobox-no-results" role="option" aria-disabled="true">Searching...</li>';
    listbox.hidden = false;
    input.setAttribute('aria-expanded', 'true');
}

async function fetchMemberSearch(q) {
    const params = new URLSearchParams({q, exclude_project: PROJECT_ID, limit: '10'});
    try {
        const resp = await fetch(`/members/api/search-users?${params}`);
        if (!resp.ok) return;
        const data = await resp.json();
        memberSearchResults = data.users;
        renderMemberResults(data.users, q);
    } catch (e) {
        console.error('Member search failed:', e);
    }
}

function renderMemberResults(users, query) {
    const listbox = document.getElementById('member-search-listbox');
    const input = document.getElementById('member-search-input');
    const liveRegion = document.getElementById('member-search-live');

    listbox.innerHTML = '';
    memberActiveIndex = -1;

    if (users.length === 0) {
        listbox.innerHTML = '<li class="combobox-no-results" role="option" aria-disabled="true">No users found</li>';
        listbox.hidden = false;
        input.setAttribute('aria-expanded', 'true');
        liveRegion.textContent = 'No users found';
        return;
    }

    const terms = query.trim().toLowerCase().split(/\s+/);

    users.forEach((u, i) => {
        const li = document.createElement('li');
        li.className = 'combobox-option';
        li.id = `member-opt-${i}`;
        li.setAttribute('role', 'option');
        li.onclick = () => selectMember(u);

        const nameText = u.display_name || '';
        const emailText = u.email;

        li.innerHTML = nameText
            ? `<div class="combobox-option-name">${highlightTerms(nameText, terms)}</div>
               <div class="combobox-option-email">${highlightTerms(emailText, terms)}</div>`
            : `<div class="combobox-option-name">${highlightTerms(emailText, terms)}</div>`;
        listbox.appendChild(li);
    });

    listbox.hidden = false;
    input.setAttribute('aria-expanded', 'true');
    liveRegion.textContent = `${users.length} user${users.length !== 1 ? 's' : ''} found`;
}

function highlightTerms(text, terms) {
    if (!text) return '';
    let result = escapeHtml(text);
    terms.forEach(term => {
        if (!term) return;
        const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escapedTerm})`, 'gi');
        result = result.replace(regex, '<mark>$1</mark>');
    });
    return result;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function onMemberSearchKeyDown(e) {
    const listbox = document.getElementById('member-search-listbox');
    if (listbox.hidden) return;

    const options = listbox.querySelectorAll('.combobox-option:not([aria-disabled])');
    if (options.length === 0) return;

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        memberActiveIndex = Math.min(memberActiveIndex + 1, options.length - 1);
        updateMemberActiveOption(options);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        memberActiveIndex = Math.max(memberActiveIndex - 1, 0);
        updateMemberActiveOption(options);
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (memberActiveIndex >= 0 && memberActiveIndex < memberSearchResults.length) {
            selectMember(memberSearchResults[memberActiveIndex]);
        }
    } else if (e.key === 'Escape') {
        e.preventDefault();
        closeMemberListbox();
        document.getElementById('member-search-input').value = '';
    } else if (e.key === 'Tab') {
        closeMemberListbox();
        // Don't preventDefault — let focus move naturally
    }
}

function updateMemberActiveOption(options) {
    const input = document.getElementById('member-search-input');
    options.forEach((opt, i) => {
        opt.classList.toggle('active', i === memberActiveIndex);
    });
    if (memberActiveIndex >= 0 && options[memberActiveIndex]) {
        input.setAttribute('aria-activedescendant', options[memberActiveIndex].id);
        options[memberActiveIndex].scrollIntoView({block: 'nearest'});
    }
}

function selectMember(user) {
    const hidden = document.getElementById('new-member-user');
    const input = document.getElementById('member-search-input');
    const chip = document.getElementById('member-chip');
    const chipText = document.getElementById('member-chip-text');

    hidden.value = user.user_id;
    const displayText = user.display_name
        ? `${user.display_name} (${user.email})`
        : user.email;
    chipText.textContent = displayText;

    chip.style.display = '';
    input.style.display = 'none';
    document.getElementById('member-search-hint').style.display = 'none';
    closeMemberListbox();
}

function clearMemberSelection() {
    const hidden = document.getElementById('new-member-user');
    const input = document.getElementById('member-search-input');
    const chip = document.getElementById('member-chip');
    const hint = document.getElementById('member-search-hint');

    if (hidden) hidden.value = '';
    if (input) {
        input.value = '';
        input.style.display = '';
    }
    if (chip) chip.style.display = 'none';
    if (hint) hint.style.display = '';
    closeMemberListbox();
    memberSearchResults = [];
}

function closeMemberListbox() {
    const listbox = document.getElementById('member-search-listbox');
    const input = document.getElementById('member-search-input');
    if (listbox) {
        listbox.hidden = true;
        listbox.innerHTML = '';
    }
    if (input) {
        input.setAttribute('aria-expanded', 'false');
        input.setAttribute('aria-activedescendant', '');
    }
    memberActiveIndex = -1;
}
```

- [ ] **Step 3: Wire up event listeners**

In the same `<script>` block, update the `DOMContentLoaded` handler. Replace:

```javascript
document.addEventListener('DOMContentLoaded', loadMembers);
```

With:

```javascript
document.addEventListener('DOMContentLoaded', () => {
    loadMembers();
    const searchInput = document.getElementById('member-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', onMemberSearchInput);
        searchInput.addEventListener('keydown', onMemberSearchKeyDown);
    }
});
```

- [ ] **Step 4: Close listbox on outside click**

Add this at the end of the `DOMContentLoaded` callback, after the event listener setup:

```javascript
    // Close combobox on outside click
    document.addEventListener('click', (e) => {
        const wrapper = document.getElementById('member-combobox');
        if (wrapper && !wrapper.contains(e.target)) {
            closeMemberListbox();
        }
    });
```

- [ ] **Step 5: Commit**

```bash
git add auto_a11y/web/templates/projects/view.html
git commit -m "feat: add combobox JavaScript for member email search"
```

---

### Task 7: Manual integration test

**Files:** None (verification only)

- [ ] **Step 1: Start the app**

```bash
python run.py --debug
```

- [ ] **Step 2: Test the combobox**

Navigate to a project view page. Verify:
1. The "User" field shows a text input (not a select dropdown)
2. Typing fewer than 2 characters shows the hint, no dropdown
3. Typing 2+ characters triggers search after a brief delay
4. Results show display name and email with highlighted matches
5. Clicking a result shows the chip and hides the input
6. Clicking the chip's x clears the selection
7. Arrow keys navigate results, Enter selects, Escape closes
8. Adding a member (chip + role + Add button) works and resets the combobox
9. The live region announces result count (check with screen reader or browser devtools)

- [ ] **Step 3: Test edge cases**

1. Search for a user who doesn't exist — should show "No users found"
2. Add a member, then search again — the added member should not appear in results
3. Search with multiple terms (e.g. "jane smi") — should find matching users
4. Clear browser tab and reopen — combobox should initialize correctly on page load
