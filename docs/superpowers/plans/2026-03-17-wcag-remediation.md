# WCAG 2.2 AA Remediation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring both admin and public interfaces of Auto A11y to WCAG 2.2 Level AA conformance, with a focus on blind/VI users and APG patterns.

**Architecture:** Template-by-template layered approach — fix shared base templates and JS/CSS first (cascading to all pages), then sweep individual templates. No framework change; fix issues within Bootstrap 5.1.3.

**Tech Stack:** Flask/Jinja2 templates, Bootstrap 5.1.3, vanilla JavaScript, CSS

**Spec:** `docs/superpowers/specs/2026-03-17-wcag-remediation-design.md`

---

### Task 1: Admin base template — skip link, main ID, navbar toggler

**Files:**
- Modify: `auto_a11y/web/templates/base.html:19-28` (body opening, nav, toggler)
- Modify: `auto_a11y/web/templates/base.html:171` (main element)

- [ ] **Step 1: Add skip link before `<nav>`**

In `base.html`, insert a skip link as the first child of `<body>`, before the `<!-- Navigation -->` comment on line 20:

```html
    <a class="skip-link" href="#main-content">{{ _('Skip to main content') }}</a>

    <!-- Navigation -->
```

- [ ] **Step 2: Add `id="main-content"` to `<main>`**

Change line 171 from:

```html
    <main class="container-fluid mt-4">
```

to:

```html
    <main id="main-content" class="container-fluid mt-4">
```

- [ ] **Step 3: Fix navbar toggler — add `aria-controls`, `aria-expanded`, `aria-label`**

Change line 26 from:

```html
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
```

to:

```html
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="{{ _('Toggle navigation') }}">
```

- [ ] **Step 4: Verify in browser**

Open `http://localhost:5001/dashboard`. Tab from the address bar — the first focusable element should be the skip link. Pressing Enter should jump focus to `<main>`. The hamburger button should now have an accessible name.

- [ ] **Step 5: Commit**

```bash
git add auto_a11y/web/templates/base.html
git commit -m "fix(a11y): add skip link, main ID, and navbar toggler ARIA to admin base"
```

---

### Task 2: Admin base template — dropdown ARIA, active nav, spinner label, live region

**Files:**
- Modify: `auto_a11y/web/templates/base.html:88,106` (dropdowns)
- Modify: `auto_a11y/web/templates/base.html:33-42` (nav links)
- Modify: `auto_a11y/web/templates/base.html:145` (spinner)
- Modify: `auto_a11y/web/templates/base.html:173` (after main, before footer)

- [ ] **Step 1: Fix settings dropdown — add `aria-expanded="false"`**

Change line 88 from:

```html
                        <a class="nav-link dropdown-toggle py-2 px-2" href="#" id="settingsDropdown" role="button" data-bs-toggle="dropdown" aria-label="{{ _('Settings') }}">
```

to:

```html
                        <a class="nav-link dropdown-toggle py-2 px-2" href="#" id="settingsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false" aria-label="{{ _('Settings') }}">
```

- [ ] **Step 2: Fix user dropdown — add `aria-expanded="false"`**

Change line 106 from:

```html
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
```

to:

```html
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
```

- [ ] **Step 3: Add `aria-current="page"` to active nav links**

Change the Dashboard nav link (line 33) from:

```html
                        <a class="nav-link" href="{{ url_for('dashboard') }}">
```

to:

```html
                        <a class="nav-link" href="{{ url_for('dashboard') }}" {% if request.endpoint == 'dashboard' %}aria-current="page"{% endif %}>
```

Change the Projects nav link (line 39) from:

```html
                        <a class="nav-link" href="{{ url_for('projects.list_projects') }}">
```

to:

```html
                        <a class="nav-link" href="{{ url_for('projects.list_projects') }}" {% if request.endpoint and request.endpoint.startswith('projects.') %}aria-current="page"{% endif %}>
```

Also add `aria-current="page"` to the mobile bottom nav links (lines 187-227) that already have the `active` class conditional. For example, line 187:

```html
                <a href="{{ url_for('dashboard') }}" {% if request.endpoint == 'dashboard' %}class="active" aria-current="page"{% endif %}>
```

Apply the same pattern to all 7 mobile bottom nav links.

- [ ] **Step 4: Fix spinner — add visually-hidden label**

Change line 145 from:

```html
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
```

to:

```html
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">{{ _('Loading...') }}</span>
                    </div>
```

- [ ] **Step 5: Add notification live region**

After the closing `</main>` tag (line 173) and before the footer, add:

```html
    <div id="notification-live-region" class="visually-hidden" aria-live="polite" aria-atomic="true"></div>
```

- [ ] **Step 6: Verify in browser**

Inspect the rendered HTML to confirm `aria-expanded`, `aria-current`, spinner label, and live region are present.

- [ ] **Step 7: Commit**

```bash
git add auto_a11y/web/templates/base.html
git commit -m "fix(a11y): add dropdown ARIA, active nav indicators, spinner label, live region"
```

---

### Task 3: Admin base template — decorative icons and alert dismiss buttons

**Files:**
- Modify: `auto_a11y/web/templates/base.html` (all `<i class="bi ...">` icons, `btn-close` buttons)

- [ ] **Step 1: Add `aria-hidden="true"` to all decorative icons in base template**

All `<i class="bi ...">` icons in the navbar are decorative (they have adjacent text labels). Add `aria-hidden="true"` to each one. There are approximately 20 icon elements in the base template.

Examples:

```html
<i class="bi bi-universal-access-circle" aria-hidden="true"></i>
<i class="bi bi-speedometer2" aria-hidden="true"></i>
<i class="bi bi-folder" aria-hidden="true"></i>
```

Apply to ALL `<i class="bi ...">` elements in the file, including those in the mobile bottom nav (lines 188-226).

- [ ] **Step 2: Add `aria-label` to alert dismiss buttons**

Change the global test status dismiss button (line 151) from:

```html
                <button type="button" class="btn-close btn-sm" data-bs-dismiss="alert" onclick="pauseGlobalTestTracking()"></button>
```

to:

```html
                <button type="button" class="btn-close btn-sm" data-bs-dismiss="alert" aria-label="{{ _('Dismiss') }}" onclick="pauseGlobalTestTracking()"></button>
```

Change the flash message dismiss button (line 163) from:

```html
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
```

to:

```html
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="{{ _('Dismiss') }}"></button>
```

- [ ] **Step 3: Verify with screen reader or aXe**

Run browser devtools accessibility audit or aXe extension on `/dashboard`. Confirm icons are hidden from AT and dismiss buttons have accessible names.

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/templates/base.html
git commit -m "fix(a11y): hide decorative icons from AT, label dismiss buttons"
```

---

### Task 4: Admin base template — showNotification live region integration

**Files:**
- Modify: `auto_a11y/web/templates/base.html:524-541` (showNotification function)

- [ ] **Step 1: Update `showNotification()` to populate live region**

In the inline `<script>` block, find the `showNotification` function (around line 524) and add the live region announcement. Change:

```javascript
    if (typeof showNotification === 'undefined') {
        window.showNotification = function(title, message, type) {
            // Simple notification using Bootstrap toast or alert
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
            alertDiv.style.zIndex = '9999';
            alertDiv.innerHTML = `
                <strong>${title}</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(alertDiv);

            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        };
    }
```

to:

```javascript
    if (typeof showNotification === 'undefined') {
        window.showNotification = function(title, message, type) {
            // Simple notification using Bootstrap toast or alert
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
            alertDiv.style.zIndex = '9999';
            alertDiv.setAttribute('role', 'alert');
            alertDiv.innerHTML = `
                <strong>${title}</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Dismiss"></button>
            `;
            document.body.appendChild(alertDiv);

            // Announce to screen readers via live region
            var liveRegion = document.getElementById('notification-live-region');
            if (liveRegion) {
                liveRegion.textContent = title + ': ' + message;
            }

            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        };
    }
```

- [ ] **Step 2: Verify by triggering a notification**

Start a page test from the UI. When it completes, the notification should both appear visually and be announced by screen readers through the live region.

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/templates/base.html
git commit -m "fix(a11y): announce notifications via ARIA live region"
```

---

### Task 5: Public base template — flash message fix

**Files:**
- Modify: `auto_a11y/web/templates/public/public_base.html:46-54`

- [ ] **Step 1: Wrap flash messages in `role="alert"` container**

Change lines 46-54 from:

```html
        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        <ul class="flash-messages" role="alert">
            {% for category, message in messages %}
            <li class="flash-{{ category }}">{{ message }}</li>
            {% endfor %}
        </ul>
        {% endif %}
        {% endwith %}
```

to:

```html
        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        <div role="alert">
            <ul class="flash-messages">
                {% for category, message in messages %}
                <li class="flash-{{ category }}">{{ message }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        {% endwith %}
```

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/templates/public/public_base.html
git commit -m "fix(a11y): wrap flash messages in proper alert container"
```

---

### Task 6: CSS — focus-visible, skip link z-index, reduced motion

**Files:**
- Modify: `auto_a11y/web/static/css/style.css:116-140` (focus styles, skip link)
- Modify: `auto_a11y/web/static/css/style.css` (end of file — add reduced motion)

- [ ] **Step 1: Upgrade focus styles to `:focus-visible` with fallback**

Replace lines 116-124 (the `/* Accessibility improvements */` section) with:

```css
/* Accessibility improvements */
a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* Fallback for browsers without :focus-visible */
a:focus,
button:focus,
input:focus,
select:focus,
textarea:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* Remove outline on mouse click for :focus-visible browsers */
a:focus:not(:focus-visible),
button:focus:not(:focus-visible) {
    outline: none;
}
```

- [ ] **Step 2: Fix skip link z-index**

Change the `.skip-link:focus` rule (lines 138-140) from:

```css
.skip-link:focus {
    top: 0;
}
```

to:

```css
.skip-link:focus {
    top: 0;
    z-index: 1100;
}
```

- [ ] **Step 3: Add `prefers-reduced-motion` at end of file**

Append to the end of `style.css`:

```css
/* Respect reduced motion preferences (WCAG 2.3.3) */
@media (prefers-reduced-motion: reduce) {
    .card {
        transition: none;
    }

    .alert {
        animation: none;
    }

    .status-indicator.active {
        animation: none;
    }

    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

- [ ] **Step 4: Verify skip link appears above navbar**

Tab to the skip link in the browser. It should appear on top of the navbar (z-index 1100 > navbar 1030).

- [ ] **Step 5: Commit**

```bash
git add auto_a11y/web/static/css/style.css
git commit -m "fix(a11y): focus-visible, skip link z-index, prefers-reduced-motion"
```

---

### Task 7: CSS — help system modal touch target and reduced motion

**Files:**
- Modify: `auto_a11y/web/static/css/help-system.css:50-68` (close button size)
- Modify: `auto_a11y/web/static/css/help-system.css` (end of file — add reduced motion)

- [ ] **Step 1: Increase close button touch target to 44px**

Change lines 50-64 from:

```css
.help-modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #666;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: background-color 0.2s;
}
```

to:

```css
.help-modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #666;
    padding: 0;
    width: 44px;
    height: 44px;
    min-width: 44px;
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: background-color 0.2s;
}
```

- [ ] **Step 2: Add reduced motion at end of file**

Append to the end of `help-system.css`:

```css
@media (prefers-reduced-motion: reduce) {
    .help-modal {
        animation: none;
    }

    .help-modal-content {
        animation: none;
    }

    .help-icon {
        transition: none;
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/static/css/help-system.css
git commit -m "fix(a11y): increase help modal close button to 44px, add reduced motion"
```

---

### Task 8: Help system JS — APG dialog pattern with focus trap

**Files:**
- Modify: `auto_a11y/web/static/js/help-system.js:214-295` (modal creation, show/hide, event listeners)

- [ ] **Step 1: Add `role="dialog"`, `aria-modal`, `aria-labelledby` to modal**

Change the `createHelpModal()` method (line 214) — update the modal's outer `div` and add focus trap support:

```javascript
    createHelpModal() {
        const modal = document.createElement('div');
        modal.id = 'help-modal';
        modal.className = 'help-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'help-modal-title');
        modal.innerHTML = `
            <div class="help-modal-content">
                <div class="help-modal-header">
                    <h2 id="help-modal-title">Help</h2>
                    <button class="help-modal-close" aria-label="Close help">&times;</button>
                </div>
                <div class="help-modal-body" id="help-modal-body">
                </div>
                <div class="help-modal-footer">
                    <button class="btn btn-primary help-modal-close">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
```

- [ ] **Step 2: Update `showHelp()` to save focus and focus the modal**

Replace the `showHelp()` method:

```javascript
    showHelp(topicPath) {
        const topics = topicPath.split('.');
        let content = this.helpContent;

        for (const topic of topics) {
            if (content[topic]) {
                content = content[topic];
            } else {
                return;
            }
        }

        const modal = document.getElementById('help-modal');
        const title = document.getElementById('help-modal-title');
        const body = document.getElementById('help-modal-body');

        // Save the element that triggered the modal
        this.previousFocus = document.activeElement;

        title.textContent = content.title || 'Help';
        body.innerHTML = content.detailed || content.brief || 'No help available for this topic.';

        modal.classList.add('show');

        // Focus the first close button inside the modal
        var closeBtn = modal.querySelector('.help-modal-close');
        if (closeBtn) {
            closeBtn.focus();
        }

        // Add focus trap
        this._trapFocus = this._createFocusTrap(modal);
        modal.addEventListener('keydown', this._trapFocus);
    }
```

- [ ] **Step 3: Update `hideHelp()` to restore focus and remove trap**

Replace the `hideHelp()` method:

```javascript
    hideHelp() {
        const modal = document.getElementById('help-modal');
        modal.classList.remove('show');

        // Remove focus trap
        if (this._trapFocus) {
            modal.removeEventListener('keydown', this._trapFocus);
            this._trapFocus = null;
        }

        // Return focus to the trigger element
        if (this.previousFocus && this.previousFocus.focus) {
            this.previousFocus.focus();
        }
    }
```

- [ ] **Step 4: Add `_createFocusTrap()` method**

Add this new method to the `HelpSystem` class, after `hideHelp()`:

```javascript
    _createFocusTrap(container) {
        return function(e) {
            if (e.key !== 'Tab') return;

            var focusable = container.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            if (focusable.length === 0) return;

            var first = focusable[0];
            var last = focusable[focusable.length - 1];

            if (e.shiftKey) {
                if (document.activeElement === first) {
                    e.preventDefault();
                    last.focus();
                }
            } else {
                if (document.activeElement === last) {
                    e.preventDefault();
                    first.focus();
                }
            }
        };
    }
```

- [ ] **Step 5: Verify modal behavior**

Open any page with a help icon. Click it. Verify:
1. Focus moves into the modal
2. Tab cycles within the modal (focus trap)
3. Escape closes the modal
4. Focus returns to the help icon that opened it

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/static/js/help-system.js
git commit -m "fix(a11y): implement APG dialog pattern for help modal"
```

---

### Task 9: Navigation JS — remove bare key shortcuts

**Files:**
- Modify: `auto_a11y/web/static/js/navigation.js:82-124` (keyboard shortcuts)
- Modify: `auto_a11y/web/static/js/navigation.js:152-168` (back to top button)

- [ ] **Step 1: Remove all bare key shortcuts from `initializeKeyboardShortcuts()`**

Replace the entire `initializeKeyboardShortcuts()` method (lines 82-124) with an empty method that only guards against input fields:

```javascript
    initializeKeyboardShortcuts() {
        // Keyboard shortcuts removed: bare letter keys (i, s, g), arrow keys,
        // and Home key conflict with screen reader navigation (NVDA, JAWS).
        // Navigation is available via the nav links and Back to Top button.
    }
```

- [ ] **Step 2: Add `aria-label` to Back to Top button**

In `addBackToTopButton()` (line 152), change:

```javascript
        button.title = 'Back to top';
```

to:

```javascript
        button.setAttribute('aria-label', 'Back to top');
```

And add `aria-hidden="true"` to the icon inside the button. Change:

```javascript
        button.innerHTML = '<i class="bi bi-arrow-up"></i>';
```

to:

```javascript
        button.innerHTML = '<i class="bi bi-arrow-up" aria-hidden="true"></i>';
```

- [ ] **Step 3: Verify**

Open a static report page. Verify that pressing `i`, `s`, `g`, arrow keys, and `Home` no longer navigate away. Verify the Back to Top button still works.

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/static/js/navigation.js
git commit -m "fix(a11y): remove bare key shortcuts that conflict with screen readers"
```

---

### Task 10: Search JS — highlight contrast and live region

**Files:**
- Modify: `auto_a11y/web/static/js/search.js:329-344` (highlight CSS)
- Modify: `auto_a11y/web/static/js/search.js:308-319` (updateSearchUI)

- [ ] **Step 1: Fix search highlight contrast**

Change lines 331-336 from:

```javascript
    .search-highlight {
        background-color: #ffeb3b;
        padding: 0 2px;
        border-radius: 2px;
    }
```

to:

```javascript
    .search-highlight {
        background-color: #fff3cd;
        outline: 2px solid #b3860a;
        padding: 0 2px;
        border-radius: 2px;
    }
```

- [ ] **Step 2: Make search counter a live region**

In the `initializeSearchUI()` method, add at the end (before the closing brace):

```javascript
        // Make search results count a live region for screen readers
        var counter = document.getElementById('search-results-count');
        if (counter) {
            counter.setAttribute('aria-live', 'polite');
            counter.setAttribute('aria-atomic', 'true');
        }
```

- [ ] **Step 3: Verify contrast**

Search for something in a static report. The highlighted text should now have a visible outline with sufficient contrast rather than a barely-visible yellow background.

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/static/js/search.js
git commit -m "fix(a11y): fix search highlight contrast, add live region for result count"
```

---

### Task 11: Filters JS — live region announcements

**Files:**
- Modify: `auto_a11y/web/static/js/filters.js:214-229` (`updateStatistics` method)
- Modify: `auto_a11y/web/static/js/issue-filters.js:650-661` (`updateStatistics` method)

Note: Both files define a class called `IssueFilterManager` but they are loaded on different pages. Both need the same fix applied independently.

- [ ] **Step 1: Add live region announcement to `filters.js` `updateStatistics()`**

In `filters.js`, the `updateStatistics(visible, total)` method (line 214) already receives the visible/total counts. Add a live region announcement at the end of this method, after line 228 (before the method's closing brace):

```javascript
        // Announce filter results to screen readers
        var liveRegion = document.getElementById('live-region') || document.getElementById('notification-live-region');
        if (liveRegion) {
            liveRegion.textContent = 'Showing ' + visible + ' of ' + total + ' issues';
        }
```

- [ ] **Step 2: Add live region announcement to `issue-filters.js` `updateStatistics()`**

In `issue-filters.js`, the `updateStatistics(visible, total, visibleByType)` method (line 650) also receives the visible/total counts. Add a live region announcement at the end of this method, after line 661 (before the method's closing brace):

```javascript
        // Announce filter results to screen readers
        var liveRegion = document.getElementById('live-region') || document.getElementById('notification-live-region');
        if (liveRegion) {
            liveRegion.textContent = 'Showing ' + visible + ' of ' + total + ' issues';
        }
```

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/static/js/filters.js auto_a11y/web/static/js/issue-filters.js
git commit -m "fix(a11y): announce filter results via live region"
```

---

### Task 12: Dashboard template — progress bar ARIA, decorative icons

**Files:**
- Modify: `auto_a11y/web/templates/dashboard.html:154-159` (progress bar)
- Modify: `auto_a11y/web/templates/dashboard.html` (all `<i>` icons)

- [ ] **Step 1: Add ARIA to progress bar**

Change lines 154-158 from:

```html
                    <div class="progress" style="height: 30px;">
                        {% set coverage = (stats.tested_pages / stats.total_pages * 100) if stats.total_pages > 0 else 0 %}
                        <div class="progress-bar bg-success" style="width: {{ coverage }}%">
                            {{ "%.1f"|format(coverage) }}% {{ _('Tested') }}
                        </div>
```

to (note: `{% set coverage %}` moves before `<div class="progress">` so `aria-valuenow` can reference it):

```html
                    {% set coverage = (stats.tested_pages / stats.total_pages * 100) if stats.total_pages > 0 else 0 %}
                    <div class="progress" style="height: 30px;" role="progressbar" aria-valuenow="{{ "%.1f"|format(coverage) }}" aria-valuemin="0" aria-valuemax="100" aria-label="{{ _('Test coverage') }}">
                        <div class="progress-bar bg-success" style="width: {{ coverage }}%">
                            {{ "%.1f"|format(coverage) }}% {{ _('Tested') }}
                        </div>
```

- [ ] **Step 2: Add `aria-hidden="true"` to all decorative icons**

All `<i class="bi ...">` icons on this page are decorative (next to text labels). Add `aria-hidden="true"` to each one. There are approximately 12 icons.

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/templates/dashboard.html
git commit -m "fix(a11y): add progress bar ARIA, hide decorative icons"
```

---

### Task 13: Admin template sweep — icons and tables (batch 1)

**Files:**
- Modify: All templates in `auto_a11y/web/templates/auth/`
- Modify: All templates in `auto_a11y/web/templates/projects/`
- Modify: All templates in `auto_a11y/web/templates/websites/`

- [ ] **Step 1: Sweep `auth/` templates**

For each template in `auto_a11y/web/templates/auth/`:
- Add `aria-hidden="true"` to decorative `<i class="bi ...">` icons
- Verify form labels match `for`/`id` attributes
- Verify `<table>` elements have `<caption>` or `aria-label` and `<th scope="col">`

- [ ] **Step 2: Sweep `projects/` templates**

For each template in `auto_a11y/web/templates/projects/`:
- Add `aria-hidden="true"` to decorative icons
- Add `<caption>` or `aria-label` to any `<table>` elements
- Add `scope="col"` to `<th>` elements
- Verify heading hierarchy (one `<h1>`, no skipped levels)

- [ ] **Step 3: Sweep `websites/` templates**

Same pattern as projects.

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/templates/auth/ auto_a11y/web/templates/projects/ auto_a11y/web/templates/websites/
git commit -m "fix(a11y): sweep auth, projects, websites templates for icons and tables"
```

---

### Task 14: Admin template sweep — icons and tables (batch 2)

**Files:**
- Modify: All templates in `auto_a11y/web/templates/pages/`
- Modify: All templates in `auto_a11y/web/templates/testing/`
- Modify: All templates in `auto_a11y/web/templates/reports/`

- [ ] **Step 1: Sweep `pages/` templates**

Same a11y sweep pattern: decorative icons, table accessibility, heading hierarchy, form labels.

- [ ] **Step 2: Sweep `testing/` templates**

Same pattern. Additionally for `testing/configure.html`:
- Verify the Bootstrap modals have `aria-labelledby` pointing to the modal title
- Verify close buttons have `aria-label`

- [ ] **Step 3: Sweep `reports/` templates**

Same pattern.

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/templates/pages/ auto_a11y/web/templates/testing/ auto_a11y/web/templates/reports/
git commit -m "fix(a11y): sweep pages, testing, reports templates for icons and tables"
```

---

### Task 15: Admin template sweep — remaining templates (batch 3)

**Files:**
- Modify: All templates in `auto_a11y/web/templates/recordings/`
- Modify: All templates in `auto_a11y/web/templates/schedules/`
- Modify: All templates in `auto_a11y/web/templates/scripts/`
- Modify: All templates in `auto_a11y/web/templates/website_users/`
- Modify: All templates in `auto_a11y/web/templates/project_users/`
- Modify: All templates in `auto_a11y/web/templates/project_participants/`
- Modify: All templates in `auto_a11y/web/templates/discovered_pages/`
- Modify: All templates in `auto_a11y/web/templates/drupal_sync/`
- Modify: All templates in `auto_a11y/web/templates/automated_tests/`
- Modify: All templates in `auto_a11y/web/templates/share_tokens/`
- Modify: `auto_a11y/web/templates/help.html`
- Modify: `auto_a11y/web/templates/about.html`
- Modify: `auto_a11y/web/templates/403.html`
- Modify: `auto_a11y/web/templates/404.html`
- Modify: `auto_a11y/web/templates/500.html`

- [ ] **Step 1: Sweep all remaining template directories**

Apply the same a11y sweep pattern to each:
- Decorative icons: `aria-hidden="true"`
- Tables: `<caption>` or `aria-label`, `<th scope="col">`
- Forms: labels, `required` attributes
- Heading hierarchy: one `<h1>`, no skipped levels
- Bootstrap modals: `aria-labelledby` on modal, `aria-label` on close buttons

For `drupal_sync/sync_card.html` specifically:
- Verify the upload modal (`#uploadModal`) has `aria-labelledby="uploadModalLabel"` (add `id="uploadModalLabel"` to the `<h5 class="modal-title">` if needed)

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/templates/
git commit -m "fix(a11y): sweep remaining admin templates for icons, tables, forms, modals"
```

---

### Task 16: Static report base template — landmarks, skip link, dynamic lang

**Files:**
- Modify: `auto_a11y/web/templates/static_report/base.html:1-3,168-177,215`

- [ ] **Step 1: Make `lang` attribute dynamic**

Change line 2 from:

```html
<html lang="en">
```

to:

```html
<html lang="{{ language }}">
```

- [ ] **Step 2: Add skip link**

After line 168 (`<body>`), add:

```html
    <a class="skip-link" href="#main-content" style="position:absolute;top:-40px;left:0;background:#0d6efd;color:white;padding:8px;text-decoration:none;z-index:1100;">Skip to main content</a>
```

(Inline styles since this is a standalone file.)

- [ ] **Step 3: Add `id="main-content"` to `<main>`**

Change line 215 from:

```html
    <main class="container-fluid py-4">
```

to:

```html
    <main id="main-content" class="container-fluid py-4">
```

- [ ] **Step 4: Fix navbar toggler**

Change line 176 from:

```html
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
```

to:

```html
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
```

- [ ] **Step 5: Add `aria-hidden="true"` to decorative icons**

Add `aria-hidden="true"` to all `<i class="bi ...">` elements in the template.

- [ ] **Step 6: Add inline skip link focus style**

In the `<style>` block (around line 17), add:

```css
        .skip-link:focus {
            top: 0;
            z-index: 1100;
        }
```

- [ ] **Step 7: Add inline reduced motion**

In the `<style>` block, add:

```css
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
```

- [ ] **Step 8: Commit**

```bash
git add auto_a11y/web/templates/static_report/base.html
git commit -m "fix(a11y): add skip link, dynamic lang, landmarks to static report base"
```

---

### Task 17: Static report content templates — tables, charts, headings

**Files:**
- Modify: `auto_a11y/web/templates/static_report/index.html`
- Modify: `auto_a11y/web/templates/static_report/summary.html`
- Modify: `auto_a11y/web/templates/static_report/page_detail.html`
- Modify: `auto_a11y/web/templates/static_report/dedup_index.html`
- Modify: `auto_a11y/web/templates/static_report/dedup_component.html`
- Modify: `auto_a11y/web/templates/static_report/dedup_unassigned.html`
- Modify: `auto_a11y/web/templates/static_report/project_deduplicated.html`
- Modify: `auto_a11y/web/templates/static_report/recordings_report.html`

- [ ] **Step 1: Read each template and apply fixes**

For each template:
- Add `<caption>` or `aria-label` to `<table>` elements
- Add `scope="col"` to `<th>` elements
- Add `aria-hidden="true"` to decorative icons
- Add `role="img"` and `aria-label` to `<canvas>` chart elements (e.g., `<canvas role="img" aria-label="Bar chart showing issues by category">`)
- Verify heading hierarchy
- Ensure links have distinguishable names (no bare "View" or "Details")

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/templates/static_report/
git commit -m "fix(a11y): add table captions, chart labels, icons to static report templates"
```

---

### Task 18: Standalone report templates — same fixes independently

**Files:**
- Modify: `auto_a11y/web/templates/static_report/comprehensive_report_standalone.html`
- Modify: `auto_a11y/web/templates/static_report/recordings_report_standalone.html`

- [ ] **Step 1: Read both standalone templates**

These do NOT extend `static_report/base.html` — they have their own complete HTML structure. Apply all the same fixes from Task 16 independently:
- Dynamic `lang="{{ language }}"` on `<html>`
- Skip link with inline styles
- `<main id="main-content">`
- Navbar toggler ARIA
- Decorative icon `aria-hidden="true"`
- Inline focus and reduced motion styles

Also apply Task 17 fixes:
- Table `<caption>` / `<th scope>`
- Chart `<canvas>` labels
- Heading hierarchy

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/templates/static_report/comprehensive_report_standalone.html auto_a11y/web/templates/static_report/recordings_report_standalone.html
git commit -m "fix(a11y): add a11y fixes to standalone report templates"
```

---

### Task 19: Public templates sweep — icons, tables, headings

**Files:**
- Modify: `auto_a11y/web/templates/public/project.html`
- Modify: `auto_a11y/web/templates/public/project_list.html`
- Modify: `auto_a11y/web/templates/public/website.html`
- Modify: `auto_a11y/web/templates/public/page.html`
- Modify: `auto_a11y/web/templates/public/error/403.html`

- [ ] **Step 1: Sweep each public template**

These are already in good shape. Check and fix:
- Any decorative icons missing `aria-hidden="true"`
- Table accessibility (`<caption>`, `<th scope>`)
- Heading hierarchy
- Link accessible names

- [ ] **Step 2: Commit**

```bash
git add auto_a11y/web/templates/public/
git commit -m "fix(a11y): sweep public templates for remaining a11y issues"
```

---

### Task 20: Final verification

- [ ] **Step 1: Run the application and spot-check key pages**

```bash
python run.py --debug
```

Visit these pages and verify with keyboard navigation and browser devtools:
- `/` (login page)
- `/dashboard`
- `/projects/` (project list)
- A project detail page
- A page detail page with test results
- The help modal (click any `?` icon)
- A public token page (`/t/<token>/`)

- [ ] **Step 2: Check for regressions**

Verify:
- Skip link works on every admin page
- Navbar toggler works on mobile
- Help modal opens/closes correctly with focus management
- Notifications are announced
- Static reports render correctly
- Language switching still works

- [ ] **Step 3: Verify WCAG 2.2-specific criteria and remaining spec items**

Verify these items from the spec that are expected to already be satisfied:
- **5g Status Information:** Status indicators (badges, colors) convey meaning via text, not just color
- **6c Print Styles:** Print styles in static reports don't hide essential content
- **2.4.12 Focus Not Obscured:** Sticky headers/footers don't fully obscure focused elements (check mobile bottom nav)
- **3.2.6 Consistent Help:** Help mechanism is in consistent location across admin pages (settings dropdown)
- **3.3.7 Redundant Entry:** Forms don't re-ask for information already provided
- **3.3.8 Accessible Authentication:** Login uses standard fields, no CAPTCHA

- [ ] **Step 4: Commit any remaining fixes found during verification**

```bash
git add -A
git commit -m "fix(a11y): address issues found during final verification"
```
