# WCAG 2.2 AA Remediation Design

**Date:** 2026-03-17
**Scope:** Both admin and public interfaces, plus static report templates
**Target:** WCAG 2.2 Level AA conformance
**Framework:** Keep Bootstrap 5.1.3 for admin; fix a11y issues within it
**Focus:** Blind and visually impaired users; APG (ARIA Authoring Practices Guide) patterns

## Context

Auto A11y is a web accessibility testing platform built by CNIB. It has two interfaces:

- **Admin interface** (~65 templates extending `base.html`): Used by auditors/admins. Built on Bootstrap 5.1.3. Has significant accessibility gaps.
- **Public interface** (5 templates extending `public_base.html`): Client-facing read-only views. Already has decent accessibility (skip links, landmarks, ARIA, progressive enhancement).
- **Static reports** (~10 templates in `static_report/`): Standalone HTML files generated and downloaded by clients.

## Approach

**Template-by-template sweep in layers:**

1. Base templates first (cascading fixes to all child pages)
2. Shared JavaScript files
3. Shared CSS
4. Individual templates
5. Static report templates

## Section 1: Admin Base Template (`base.html`)

All changes here cascade to every admin page (~65 templates).

### 1a. Skip Link

Add before `<nav>`:

```html
<a class="skip-link" href="#main-content">{{ _('Skip to main content') }}</a>
```

CSS for `.skip-link` already exists in `style.css` (lines 127-140). Increase z-index to 1100 (above Bootstrap navbar at 1030).

### 1b. Main Content ID

Change:
```html
<main class="container-fluid mt-4">
```
To:
```html
<main id="main-content" class="container-fluid mt-4">
```

### 1c. Navbar Toggler

Add `aria-controls`, `aria-expanded`, and `aria-label`:

```html
<button class="navbar-toggler" type="button" data-bs-toggle="collapse"
        data-bs-target="#navbarNav" aria-controls="navbarNav"
        aria-expanded="false" aria-label="{{ _('Toggle navigation') }}">
```

### 1d. Settings Dropdown

Add missing `aria-expanded="false"` to the settings dropdown toggle.

### 1e. Active Nav Items

Add `aria-current="page"` to active nav links using Jinja2 conditionals, matching the pattern already used in the mobile bottom nav:

```html
<a class="nav-link" href="..." {% if request.endpoint == 'dashboard' %}aria-current="page"{% endif %}>
```

Apply to: Dashboard, Projects, Testing dropdown items, Reports dropdown items, user dropdown items.

### 1f. Decorative Icons

Add `aria-hidden="true"` to all `<i class="bi ...">` elements in the base template that are decorative (have adjacent text labels).

### 1g. Alert Dismiss Buttons

Add `aria-label="{{ _('Dismiss') }}"` to `btn-close` buttons that lack accessible labels.

### 1h. Spinner Label

Add visually-hidden label to the spinner:

```html
<div class="spinner-border spinner-border-sm me-2" role="status">
    <span class="visually-hidden">{{ _('Loading...') }}</span>
</div>
```

### 1i. Live Region for Notifications

Add a persistent live region container for dynamic notifications:

```html
<div id="notification-live-region" class="visually-hidden" aria-live="polite" aria-atomic="true"></div>
```

Update `showNotification()` to also set the text content of this region when creating alerts.

## Section 2: Public Base Template (`public_base.html`)

### 2a. Flash Messages

Change from `role="alert"` on the `<ul>` to wrapping in a proper alert container:

```html
<div role="alert">
    <ul class="flash-messages">
        {% for category, message in messages %}
        <li class="flash-{{ category }}">{{ message }}</li>
        {% endfor %}
    </ul>
</div>
```

No other changes needed. The public base template already has skip links, semantic landmarks, ARIA labels on navs, a live region, and proper language attributes.

## Section 3: Shared JavaScript Fixes

### 3a. Help System Modal (`help-system.js`)

Rewrite `createHelpModal()` and related methods to follow the APG Dialog (Modal) pattern:

**Modal container attributes:**
```html
<div role="dialog" aria-modal="true" aria-labelledby="help-modal-title">
```

**Focus management:**
- On open: save reference to the trigger element, move focus to the first focusable element inside the modal (the close button or the modal content)
- On close: return focus to the saved trigger element
- Focus trap: intercept Tab and Shift+Tab to cycle focus within the modal

**Keyboard:**
- Escape key closes the modal

**Implementation:** Add a `showHelp(topicPath)` modification that:
1. Stores `document.activeElement` as `this.previousFocus`
2. After showing modal, focuses the close button
3. Adds keydown handler for Escape and Tab trapping
4. `hideHelp()` removes handlers and calls `this.previousFocus.focus()`

### 3b. Navigation Shortcuts (`navigation.js`)

**Remove bare letter key shortcuts** (`i`, `s`, `g`) that conflict with screen reader navigation. NVDA and JAWS use single letter keys for quick navigation (e.g., `h` for headings, `f` for forms). Custom single-key shortcuts break this.

**Remove bare arrow key shortcuts** — Screen readers use arrow keys to read content line by line. Hijacking them prevents basic reading.

**Keep:** The "Back to Top" button (it's a proper `<button>` with a click handler). Optionally keep Ctrl+key combinations if useful, but remove all bare key bindings.

### 3c. Dynamic Notifications (`showNotification()` in `base.html`)

Update to also populate the `#notification-live-region` element:

```javascript
window.showNotification = function(title, message, type) {
    // Existing visual alert creation...

    // Also announce to screen readers via live region
    var liveRegion = document.getElementById('notification-live-region');
    if (liveRegion) {
        liveRegion.textContent = title + ': ' + message;
    }
};
```

### 3d. Search Results Announcement (`search.js`)

Make the `#search-results-count` element a live region:

```html
<span id="search-results-count" aria-live="polite" aria-atomic="true"></span>
```

Or add the attribute dynamically in the constructor. This ensures screen readers announce result counts as they change.

## Section 4: CSS / Focus / Motion Fixes

### 4a. Focus Indicators (`style.css`)

Upgrade to `:focus-visible` with `:focus` fallback:

```css
a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* Fallback for browsers that don't support :focus-visible */
a:focus,
button:focus,
input:focus,
select:focus,
textarea:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* Remove outline on mouse click for browsers supporting :focus-visible */
a:focus:not(:focus-visible),
button:focus:not(:focus-visible) {
    outline: none;
}
```

WCAG 2.2 SC 2.4.11 requires 2px minimum perimeter thickness. Current 2px solid outline meets this.

### 4b. Reduced Motion (`style.css`)

Add at the end of the stylesheet:

```css
@media (prefers-reduced-motion: reduce) {
    .card {
        transition: none;
    }

    .alert {
        animation: none;
    }

    .help-modal,
    .help-modal-content {
        animation: none;
    }

    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

### 4c. Skip Link Z-Index

Update `.skip-link:focus` z-index from 100 to 1100:

```css
.skip-link:focus {
    top: 0;
    z-index: 1100;
}
```

## Section 5: Individual Template Sweep

### 5a. Heading Hierarchy

Every page must have exactly one `<h1>`. Verify across all templates. No heading level skipping (e.g., `<h2>` to `<h4>`).

### 5b. Data Tables

For every `<table>` across all templates, ensure:

- `<caption>` element or `aria-label` describing the table's purpose
- `<th scope="col">` for column headers
- `<th scope="row">` for row headers where applicable
- Sortable columns use `aria-sort="ascending|descending|none"`

### 5c. Forms

For every form across all templates:

- Every `<input>`, `<select>`, `<textarea>` has a `<label>` with matching `for`/`id`
- Required fields use `required` attribute (HTML5) or `aria-required="true"`
- Error messages associated via `aria-describedby`
- Related fields grouped with `<fieldset>`/`<legend>` where appropriate

### 5d. Bootstrap Modals

For modals in `drupal_sync/sync_card.html` and `testing/configure.html`:

- Verify `aria-labelledby` points to the modal title `<h5>`
- Verify close buttons have accessible labels
- Bootstrap 5 handles `role="dialog"`, `aria-modal`, focus trap, and Escape automatically

### 5e. Decorative Icons (All Templates)

Systematic sweep: add `aria-hidden="true"` to all `<i class="bi ...">` icons that are decorative. For icon-only interactive elements (if any), add `aria-label` instead.

### 5f. Progress Bars

Dashboard progress bar — add ARIA attributes:

```html
<div class="progress" style="height: 30px;"
     role="progressbar" aria-valuenow="{{ coverage }}"
     aria-valuemin="0" aria-valuemax="100"
     aria-label="{{ _('Test coverage') }}">
```

### 5g. Status Information

Verify that all status indicators (badges, colors) convey information through text, not just color. From audit: current implementation already uses text labels alongside colors.

## Section 6: Static Report Templates

### 6a. Base Template (`static_report/base.html`)

- Ensure `lang` attribute on `<html>`
- Add skip link
- Add `<main id="main-content">` landmark
- Add `<header>` and `<nav>` landmarks
- Include inline focus styles (standalone file, no external CSS dependency)

### 6b. Content Templates

For each report template (`summary.html`, `page_detail.html`, `index.html`, dedup templates):

- Data tables: `<caption>`, `<th scope>` attributes
- Charts (`<canvas>`): `aria-label` describing the chart, consider `role="img"`
- Issue lists: proper semantic structure (headings, lists)
- Collapsible sections: APG accordion pattern if interactive
- Links: distinguishable accessible names (no bare "View" or "Details")

### 6c. Print Styles

Ensure print styles don't hide essential content. The public frontend's `print.css` can serve as a reference pattern.

## WCAG 2.2-Specific Criteria

Beyond the above fixes, verify conformance with these 2.2-specific success criteria:

- **2.4.11 Focus Appearance (AA):** Focus indicator has minimum 2px perimeter, 3:1 contrast. Addressed in Section 4a.
- **2.4.12 Focus Not Obscured (AA):** Ensure sticky headers/footers don't fully obscure focused elements. Bootstrap's navbar is `position: static` on desktop, shouldn't be an issue. Verify on mobile where bottom nav is fixed.
- **3.2.6 Consistent Help (A):** Help mechanism (settings dropdown with Help link) is in consistent location across all admin pages via `base.html`. Satisfied.
- **3.3.7 Redundant Entry (A):** Forms should not re-ask for information already provided in the same session. Verify in multi-step forms (if any). Most forms in this app are single-page.
- **3.3.8 Accessible Authentication (AA):** Login form uses standard email/password fields. SSO buttons are accessible. No CAPTCHA. Satisfied.

## Out of Scope

- Already-exported static report HTML files (only fix templates for future generation)
- Replacing Bootstrap with custom CSS
- Third-party library internals (Chart.js, Bootstrap JS)
- WCAG AAA conformance
- Automated testing of the app against itself (meta-testing)

## Files Affected

**High-impact (cascade to many pages):**
- `auto_a11y/web/templates/base.html`
- `auto_a11y/web/templates/public/public_base.html`
- `auto_a11y/web/static/css/style.css`
- `auto_a11y/web/static/js/help-system.js`
- `auto_a11y/web/static/js/navigation.js`
- `auto_a11y/web/static/js/search.js`

**Medium-impact (individual templates):**
- All ~65 admin templates (icon `aria-hidden`, heading hierarchy, table/form fixes)
- All ~10 static report templates
- All ~5 public templates

**Low-impact (minor tweaks):**
- `auto_a11y/web/static/css/help-system.css` (motion reduction)
- `auto_a11y/web/static/css/mobile.css` (verify focus styles)
