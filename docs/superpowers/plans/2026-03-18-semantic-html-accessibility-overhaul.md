# Semantic HTML Accessibility Overhaul Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Achieve exemplary WCAG 2.1 compliance across all Flask templates through strict heading hierarchy, semantic HTML5 structure, and proper form semantics.

**Architecture:** Fix all 81 Jinja2 templates across admin, public, and static report interfaces. Changes are CSS-first (add semantic element resets to style.css), then template-by-template fixes grouped by functional area. Each task produces a self-contained commit.

**Tech Stack:** Jinja2 templates, Bootstrap 5, CSS

**Spec:** `docs/superpowers/specs/2026-03-18-semantic-html-accessibility-overhaul-design.md`

---

## File Structure

### Files to Modify

**CSS (1 file):**
- `auto_a11y/web/static/css/style.css` — Add semantic element resets (fieldset, legend, dl, dt, dd, figure, figcaption, caption)

**Base templates (2 files):**
- `auto_a11y/web/templates/base.html` — Nav aria-label, dropdown toggles `<a>` → `<button>`
- `auto_a11y/web/templates/static_report/base.html` — Nav aria-label, dropdown toggle fix

**Auth templates (6 files):**
- `auto_a11y/web/templates/auth/login.html` — h1 class, fieldset
- `auto_a11y/web/templates/auth/register.html` — h1 class, fieldset, aria-describedby
- `auto_a11y/web/templates/auth/profile.html` — h2 class, fieldsets, aria-describedby
- `auto_a11y/web/templates/auth/user_list.html` — table caption, mobile card headings
- `auto_a11y/web/templates/auth/user_edit.html` — heading classes, fieldsets, aria-describedby
- `auto_a11y/web/templates/auth/user_create.html` — h1 class, fieldset, aria-describedby

**Dashboard & informational (4 files):**
- `auto_a11y/web/templates/dashboard.html` — h1 class, heading hierarchy, sections
- `auto_a11y/web/templates/index.html` — sections, heading hierarchy
- `auto_a11y/web/templates/about.html` — heading hierarchy, sections, aside
- `auto_a11y/web/templates/help.html` — heading hierarchy, sidebar aria-label

**Project templates (4 files):**
- `auto_a11y/web/templates/projects/list.html` — articles, heading hierarchy
- `auto_a11y/web/templates/projects/view.html` — h1 class, sections, articles, heading hierarchy
- `auto_a11y/web/templates/projects/create.html` — h1 class, fieldsets, aria-describedby
- `auto_a11y/web/templates/projects/edit.html` — h1 class, fieldsets, aria-describedby

**Website templates (5 files):**
- `auto_a11y/web/templates/websites/view.html` — h1 class, sections, heading hierarchy
- `auto_a11y/web/templates/websites/edit.html` — h1 class, fieldsets, aria-describedby
- `auto_a11y/web/templates/websites/discovery_run.html` — heading hierarchy, fieldset
- `auto_a11y/web/templates/websites/discovery_history.html` — heading hierarchy, table caption
- `auto_a11y/web/templates/websites/documents.html` — table caption

**Page templates (5 files):**
- `auto_a11y/web/templates/pages/view.html` — h1 class, accordion articles, heading hierarchy
- `auto_a11y/web/templates/pages/view_enhanced.html` — same patterns as view.html
- `auto_a11y/web/templates/pages/edit.html` — h1 class, fieldset, aria-describedby
- `auto_a11y/web/templates/pages/test_matrix.html` — heading hierarchy, table caption
- `auto_a11y/web/templates/pages/test_matrix_v2.html` — heading hierarchy, table caption

**Testing templates (5 files):**
- `auto_a11y/web/templates/testing/dashboard.html` — h1 class, sections, heading hierarchy
- `auto_a11y/web/templates/testing/configure.html` — heading hierarchy, fieldsets
- `auto_a11y/web/templates/testing/fixture_status.html` — heading hierarchy, sections, table caption
- `auto_a11y/web/templates/testing/trends.html` — heading hierarchy, figure/figcaption
- `auto_a11y/web/templates/testing/result.html` — heading hierarchy, sections

**Recording templates (4 files):**
- `auto_a11y/web/templates/recordings/list.html` — h1 class, articles, heading hierarchy
- `auto_a11y/web/templates/recordings/detail.html` — h1 class, dl for metadata, sections, figure
- `auto_a11y/web/templates/recordings/combined.html` — articles, heading hierarchy
- `auto_a11y/web/templates/recordings/upload.html` — fieldset, aria-describedby

**Schedule templates (4 files):**
- `auto_a11y/web/templates/schedules/list.html` — table caption, heading hierarchy
- `auto_a11y/web/templates/schedules/view.html` — heading hierarchy, dl for metadata, table captions
- `auto_a11y/web/templates/schedules/dashboard.html` — heading hierarchy, sections
- `auto_a11y/web/templates/schedules/form.html` — fieldset, aria-describedby

**Script templates (4 files):**
- `auto_a11y/web/templates/scripts/list.html` — table caption, heading hierarchy
- `auto_a11y/web/templates/scripts/view.html` — heading hierarchy, dl for metadata, table captions
- `auto_a11y/web/templates/scripts/create.html` — fieldsets, aria-describedby
- `auto_a11y/web/templates/scripts/edit.html` — fieldsets, aria-describedby

**User management templates (13 files):**
- `auto_a11y/web/templates/project_users/list.html` — table caption
- `auto_a11y/web/templates/project_users/view.html` — heading hierarchy
- `auto_a11y/web/templates/project_users/create.html` — fieldset, aria-describedby
- `auto_a11y/web/templates/project_users/edit.html` — fieldset, aria-describedby
- `auto_a11y/web/templates/website_users/list.html` — table caption
- `auto_a11y/web/templates/website_users/view.html` — heading hierarchy
- `auto_a11y/web/templates/website_users/create.html` — fieldset, aria-describedby
- `auto_a11y/web/templates/website_users/edit.html` — fieldset, aria-describedby
- `auto_a11y/web/templates/project_participants/list.html` — table caption
- `auto_a11y/web/templates/project_participants/create_supervisor.html` — fieldset
- `auto_a11y/web/templates/project_participants/create_tester.html` — fieldset
- `auto_a11y/web/templates/project_participants/edit_supervisor.html` — fieldset
- `auto_a11y/web/templates/project_participants/edit_tester.html` — fieldset

**Other admin templates (4 files):**
- `auto_a11y/web/templates/share_tokens/token_list_partial.html` — table caption
- `auto_a11y/web/templates/discovered_pages/view.html` — dl for metadata, heading hierarchy
- `auto_a11y/web/templates/reports/dashboard.html` — heading hierarchy, sections
- `auto_a11y/web/templates/automated_tests/list.html` — heading hierarchy

**Public templates (4 files):**
- `auto_a11y/web/templates/public/project_list.html` — articles
- `auto_a11y/web/templates/public/project.html` — dl fix, heading hierarchy
- `auto_a11y/web/templates/public/website.html` — heading hierarchy, sections
- `auto_a11y/web/templates/public/page.html` — dl fix, heading hierarchy

**Public templates note:** `public/public_base.html` was audited and requires no changes — it already uses proper `<header>`, `<footer>`, labeled `<nav>`, and `<main>` elements.

**Static report templates (10 files):**
- `auto_a11y/web/templates/static_report/comprehensive_report_standalone.html` — table captions, heading hierarchy
- `auto_a11y/web/templates/static_report/recordings_report_standalone.html` — dropdown toggle, heading hierarchy
- `auto_a11y/web/templates/static_report/recordings_report.html` — heading hierarchy
- `auto_a11y/web/templates/static_report/page_detail.html` — figure/figcaption, heading hierarchy
- `auto_a11y/web/templates/static_report/summary.html` — heading hierarchy, sections
- `auto_a11y/web/templates/static_report/project_deduplicated.html` — table captions
- `auto_a11y/web/templates/static_report/dedup_index.html` — heading hierarchy
- `auto_a11y/web/templates/static_report/dedup_component.html` — heading hierarchy
- `auto_a11y/web/templates/static_report/dedup_unassigned.html` — heading hierarchy
- `auto_a11y/web/templates/static_report/index.html` — heading hierarchy

**Drupal templates (2 files):**
- `auto_a11y/web/templates/drupal_sync/project_sync.html` — heading hierarchy
- `auto_a11y/web/templates/drupal_sync/sync_card.html` — heading hierarchy

---

## Implementation Tasks

### Task 1: CSS Semantic Element Resets

**Files:**
- Modify: `auto_a11y/web/static/css/style.css`

- [ ] **Step 1: Read the current CSS file**

Read `auto_a11y/web/static/css/style.css` to find the end of the file and understand existing patterns.

- [ ] **Step 2: Add semantic element reset styles**

Append to `auto_a11y/web/static/css/style.css`:

```css
/* ===== Semantic HTML Element Resets ===== */

/* Fieldset - remove browser defaults.
   min-inline-size: auto prevents Firefox/Chrome fieldset min-width quirk.
   float: none and width: auto fix legend rendering quirks. */
fieldset {
    border: none;
    padding: 0;
    margin: 0 0 1.5rem 0;
    min-inline-size: auto;
}

legend {
    padding: 0;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    float: none;
    width: auto;
}

/* Definition list styling */
dl {
    margin-bottom: 1rem;
}

dt {
    font-weight: 600;
    color: #495057;
}

dd {
    margin-left: 0;
    margin-bottom: 0.5rem;
}

/* Figure and figcaption */
figure {
    margin: 1rem 0;
}

figcaption {
    font-size: 0.95rem;
    color: #6c757d;
    margin-top: 0.5rem;
}

/* Table captions */
table caption {
    padding: 0.5rem 0;
    caption-side: top;
}
```

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/static/css/style.css
git commit -m "style: add CSS resets for semantic HTML elements (fieldset, legend, dl, figure, caption)"
```

---

### Task 2: Base Template — Navigation and Dropdown Fixes

**Files:**
- Modify: `auto_a11y/web/templates/base.html`

- [ ] **Step 1: Read base.html**

Read `auto_a11y/web/templates/base.html` in full.

- [ ] **Step 2: Add aria-label to main nav**

Find the main `<nav>` element (around line 23) and add `aria-label="{{ _('Main navigation') }}"`.

- [ ] **Step 3: Convert all dropdown toggles from `<a>` to `<button>`**

For each dropdown toggle (Testing, Reports, Language, Settings, User — around lines 47, 64, 80, 90, 108):

Replace pattern:
```html
<a class="nav-link dropdown-toggle" href="#" id="testingDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
```

With:
```html
<button type="button" class="nav-link dropdown-toggle" id="testingDropdown" data-bs-toggle="dropdown" aria-expanded="false">
```

And change the closing `</a>` to `</button>`.

Remove `href="#"` and `role="button"` — they are no longer needed on a `<button>`.

- [ ] **Step 4: Verify the page loads and dropdowns work**

Start the app and verify all nav dropdowns open/close correctly in a browser.

- [ ] **Step 5: Commit**

```bash
git add auto_a11y/web/templates/base.html
git commit -m "fix(a11y): add nav aria-label, convert dropdown toggles from <a> to <button>"
```

---

### Task 3: Static Report Base Template — Navigation Fix

**Files:**
- Modify: `auto_a11y/web/templates/static_report/base.html`

- [ ] **Step 1: Read static_report/base.html**

Read the file in full.

- [ ] **Step 2: Add aria-label to nav and fix dropdown toggles**

Same pattern as Task 2: add `aria-label` to the main `<nav>`, convert any `<a role="button">` dropdown toggles to `<button type="button">`.

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/templates/static_report/base.html
git commit -m "fix(a11y): add nav aria-label, fix dropdown toggle in static report base"
```

---

### Task 4: Auth Templates — Headings, Fieldsets, aria-describedby, aria-invalid

**Note on `aria-invalid` (applies to ALL form tasks):** Wherever Jinja conditionally renders error classes on form inputs (e.g., `class="form-control {% if error %}is-invalid{% endif %}"`), also add `aria-invalid="true"` conditionally. Pattern: `aria-invalid="{{ 'true' if error else 'false' }}"`. Check each form template for error state rendering and add `aria-invalid` alongside the visual error class.

**Files:**
- Modify: `auto_a11y/web/templates/auth/login.html`
- Modify: `auto_a11y/web/templates/auth/register.html`
- Modify: `auto_a11y/web/templates/auth/profile.html`
- Modify: `auto_a11y/web/templates/auth/user_list.html`
- Modify: `auto_a11y/web/templates/auth/user_edit.html`
- Modify: `auto_a11y/web/templates/auth/user_create.html`

- [ ] **Step 1: Read all auth templates**

Read all 6 files.

- [ ] **Step 2: Fix login.html**

1. Remove Bootstrap heading size class from h1: `<h1 class="h4 mb-0">` → `<h1 class="mb-0">`
2. Wrap email + password form fields in `<fieldset><legend class="visually-hidden">{{ _('Login Credentials') }}</legend>...</fieldset>`

- [ ] **Step 3: Fix register.html**

1. Remove heading size class: `<h1 class="h4 mb-0">` → `<h1 class="mb-0">`
2. Wrap form fields in `<fieldset><legend class="visually-hidden">{{ _('Account Details') }}</legend>...</fieldset>`
3. For each `.form-text` helper div, add an `id` attribute (e.g., `id="display_name-help"`, `id="password-help"`) and add `aria-describedby` to the corresponding input.

- [ ] **Step 4: Fix profile.html**

1. Remove heading size classes from both h2 elements
2. Wrap profile form fields in `<fieldset><legend class="visually-hidden">{{ _('Profile Information') }}</legend>...</fieldset>`
3. Wrap password change form fields in `<fieldset><legend class="visually-hidden">{{ _('Change Password') }}</legend>...</fieldset>`
4. Add `aria-describedby` for any `.form-text` helper divs

- [ ] **Step 5: Fix user_list.html**

1. Add `<caption class="visually-hidden">{{ _('List of users with roles and status') }}</caption>` as first child of the `<table>`
2. Fix any `<h6>` mobile card headings to `<h2>` (to follow page h1)

- [ ] **Step 6: Fix user_edit.html**

1. Remove heading size classes (h2 with h4/h5 classes)
2. Fix subsection headings: `<h2 class="h5">` → `<h3>` for "User Statistics", "Reset Password", "Account Locked"
3. Wrap form groups in `<fieldset>` with appropriate `<legend>`
4. Add `aria-describedby` for `.form-text` helper divs

- [ ] **Step 7: Fix user_create.html**

1. Remove heading size class from h1
2. Wrap form in `<fieldset><legend class="visually-hidden">{{ _('New User Account') }}</legend>...</fieldset>`
3. Add `aria-describedby` for `.form-text` helper divs

- [ ] **Step 8: Commit**

```bash
git add auto_a11y/web/templates/auth/
git commit -m "fix(a11y): fix heading hierarchy, add fieldsets and aria-describedby in auth templates"
```

---

### Task 5: Dashboard & Informational Pages — Headings, Sections, Aside

**Files:**
- Modify: `auto_a11y/web/templates/dashboard.html`
- Modify: `auto_a11y/web/templates/index.html`
- Modify: `auto_a11y/web/templates/about.html`
- Modify: `auto_a11y/web/templates/help.html`

- [ ] **Step 1: Read all 4 files**

Read dashboard.html, index.html, about.html, help.html in full.

- [ ] **Step 2: Fix dashboard.html**

1. Remove `h2` class from h1: `<h1 class="h2 mb-4">` → `<h1 class="mb-4">`
2. Change all stat card `<h6>` headings to `<h2>` (lines ~17, 30, 43, 56, 73, 86, 99, 112)
3. Change `<h5>` section headings (Quick Actions, Test Coverage, System Status) to `<h2>`
4. Wrap stat card rows in `<section aria-labelledby="stats-heading">` with an `<h2 id="stats-heading">` (can be visually-hidden if no visible heading exists)
5. Wrap Quick Actions in `<section aria-labelledby="actions-heading">`
6. Wrap Test Coverage in `<section aria-labelledby="coverage-heading">`
7. Wrap System Status in `<section aria-labelledby="status-heading">`

- [ ] **Step 3: Fix index.html**

1. Wrap feature cards section in `<section aria-labelledby="features-heading">`
2. Add `<h2 id="features-heading">` (visually-hidden if needed) before the feature cards row
3. Change feature card `<h5>` titles to `<h2>`

- [ ] **Step 4: Fix about.html**

1. Remove `h2` class from h1
2. Change all `<h5>` card headers to `<h2>` ("About Auto A11y", "WCAG Data Attribution", "Additional Resources", "Quick Info")
3. Change all `<h6>` subsections to `<h3>` ("Features", "Source", "Copyright", etc.)
4. Wrap each main card in `<section>` with `aria-labelledby`
5. Wrap the sidebar column (Quick Info card) in `<aside>`

- [ ] **Step 5: Fix help.html**

1. Change sidebar `<h5>` to `<h2>` ("Documentation")
2. Add `aria-label="{{ _('Documentation navigation') }}"` to sidebar `<nav>`
3. Fix heading hierarchy throughout:
   - `<h5>` alert headings → `<h3>` (under h2 section headings)
   - `<h5>` card headers → `<h3>` (under h2 section headings)
   - `<h4>` cards under h2 sections → `<h3>`
   - `<h5>` conformance levels → `<h4>` (under h3 card heading)
   - `<h6>` subsections → `<h4>` (under h3 headings in about section)
4. Wrap sidebar column in `<aside>`

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/templates/dashboard.html auto_a11y/web/templates/index.html auto_a11y/web/templates/about.html auto_a11y/web/templates/help.html
git commit -m "fix(a11y): fix heading hierarchy, add sections and aside in dashboard, index, about, help"
```

---

### Task 6: Project Templates — Headings, Sections, Articles, Fieldsets

**Files:**
- Modify: `auto_a11y/web/templates/projects/list.html`
- Modify: `auto_a11y/web/templates/projects/view.html`
- Modify: `auto_a11y/web/templates/projects/create.html`
- Modify: `auto_a11y/web/templates/projects/edit.html`

- [ ] **Step 1: Read all 4 files**

Read all project templates in full.

- [ ] **Step 2: Fix projects/list.html**

1. Wrap the project cards grid in `<section aria-labelledby="projects-heading">` (use the existing h1 or add an h2)
2. Change each project card `<div class="card h-100">` to `<article class="card h-100">`
3. Change card title `<h5>` to `<h2>`

- [ ] **Step 3: Fix projects/view.html**

1. Remove `h2` class from h1
2. Change all stat card `<h6>` headings to `<h2>`
3. Wrap Websites section in `<section aria-labelledby="websites-heading">`; change `<h5>` heading to `<h2 id="websites-heading">`
4. Wrap each website card in `<article>`; change `<h6>` card titles to `<h3>`
5. Wrap Discovered Pages section in `<section>`; fix heading hierarchy
6. Wrap Recordings section in `<section>`; fix heading hierarchy
7. Fix modal titles from `<h5>` to `<h2>`
8. Add `<caption>` to any tables missing them

- [ ] **Step 4: Fix projects/create.html**

1. Remove `h2` class from h1
2. Wrap project details form fields (name, description, type) in `<fieldset><legend>{{ _('Project Details') }}</legend>...</fieldset>`
3. Wrap compliance settings (WCAG level, page load strategy, browser mode) in `<fieldset><legend>{{ _('Compliance Settings') }}</legend>...</fieldset>`
4. Wrap touchpoint tests section in `<fieldset><legend>{{ _('Touchpoint Tests') }}</legend>...</fieldset>`
5. Wrap AI testing section in `<fieldset><legend>{{ _('AI-Assisted Testing') }}</legend>...</fieldset>`
6. For each `.form-text` helper, add `id` and connect via `aria-describedby` on the input
7. Fix any heading hierarchy issues (h5/h6 → h2/h3)
8. Fix modal titles from `<h5>` to `<h2>`

- [ ] **Step 5: Fix projects/edit.html**

Apply same patterns as create.html. Read the file first to confirm structure matches.

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/templates/projects/
git commit -m "fix(a11y): fix headings, add sections/articles/fieldsets in project templates"
```

---

### Task 7: Website Templates — Headings, Sections, Fieldsets

**Files:**
- Modify: `auto_a11y/web/templates/websites/view.html`
- Modify: `auto_a11y/web/templates/websites/edit.html`
- Modify: `auto_a11y/web/templates/websites/discovery_run.html`
- Modify: `auto_a11y/web/templates/websites/discovery_history.html`
- Modify: `auto_a11y/web/templates/websites/documents.html`

- [ ] **Step 1: Read all website templates**

Read all 5 files.

- [ ] **Step 2: Fix websites/view.html**

1. Remove `h2` class from h1
2. Change stat card `<h6>` headings to `<h2>`
3. Wrap major content groups (pages table, discovered pages, documents) in `<section>` with `aria-labelledby`
4. Fix heading hierarchy for section headings
5. Add `<caption>` to tables missing them

- [ ] **Step 3: Fix websites/edit.html**

1. Remove `h2` class from h1
2. Change `<h5>` section headings to `<h2>` ("Basic Information", "Scraping Configuration")
3. Wrap each form section in `<fieldset>` with appropriate `<legend>`
4. Add `aria-describedby` for `.form-text` helpers

- [ ] **Step 4: Fix websites/discovery_run.html**

1. Fix heading hierarchy
2. Wrap form in `<fieldset>` if applicable

- [ ] **Step 5: Fix websites/discovery_history.html and documents.html**

1. Fix heading hierarchy
2. Add `<caption>` to tables

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/templates/websites/
git commit -m "fix(a11y): fix headings, add sections/fieldsets in website templates"
```

---

### Task 8: Page Templates — Headings, Accordion Articles, Fieldsets

**Files:**
- Modify: `auto_a11y/web/templates/pages/view.html`
- Modify: `auto_a11y/web/templates/pages/view_enhanced.html`
- Modify: `auto_a11y/web/templates/pages/edit.html`
- Modify: `auto_a11y/web/templates/pages/test_matrix.html`
- Modify: `auto_a11y/web/templates/pages/test_matrix_v2.html`

- [ ] **Step 1: Read all page templates**

Read all 5 files. pages/view.html is large — read in sections.

- [ ] **Step 2: Fix pages/view.html**

1. Remove `h2` class from h1
2. Wrap error/warning/info accordion sections in `<section>` with `aria-labelledby`
3. Change `<div class="accordion-item">` to `<article class="accordion-item">` for each test result
4. Fix heading hierarchy throughout (h5/h6 → appropriate levels)
5. Add `<figure>` wrapping for screenshot modals
6. Add `<caption>` to any tables

- [ ] **Step 3: Fix pages/view_enhanced.html**

Apply same patterns as view.html.

- [ ] **Step 4: Fix pages/edit.html**

1. Remove `h2` class from h1
2. Wrap form in `<fieldset><legend class="visually-hidden">{{ _('Page Details') }}</legend>...</fieldset>`
3. Fix `<h5>` info section to `<h2>`
4. Add `aria-describedby` for `.form-text` helpers

- [ ] **Step 5: Fix test_matrix.html and test_matrix_v2.html**

1. Fix heading hierarchy
2. Add `<caption>` to test matrix tables

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/templates/pages/
git commit -m "fix(a11y): fix headings, add accordion articles and fieldsets in page templates"
```

---

### Task 9: Testing Templates — Headings, Sections, Fieldsets, Figure

**Files:**
- Modify: `auto_a11y/web/templates/testing/dashboard.html`
- Modify: `auto_a11y/web/templates/testing/configure.html`
- Modify: `auto_a11y/web/templates/testing/fixture_status.html`
- Modify: `auto_a11y/web/templates/testing/trends.html`
- Modify: `auto_a11y/web/templates/testing/result.html`

- [ ] **Step 1: Read all testing templates**

Read all 5 files.

- [ ] **Step 2: Fix testing/dashboard.html**

1. Remove `h2` class from h1
2. Change all stat card `<h6>` headings to `<h2>`
3. Wrap stat cards section in `<section>` with `aria-labelledby`
4. Fix all heading hierarchy issues

- [ ] **Step 3: Fix testing/configure.html**

1. Change `<h5>` section heading to `<h2>`
2. Change `<h6>` subsection headings to `<h3>`
3. Wrap form sections in `<fieldset>` with `<legend>`

- [ ] **Step 4: Fix testing/fixture_status.html**

1. Change `<h5>` card headings to `<h2>`
2. Wrap summary section in `<section>` with `aria-labelledby`
3. Add `<caption>` to tables

- [ ] **Step 5: Fix testing/trends.html**

1. Fix heading hierarchy
2. Wrap charts in `<figure>` with `<figcaption>`

- [ ] **Step 6: Fix testing/result.html**

1. Fix heading hierarchy
2. Wrap result sections in `<section>`

- [ ] **Step 7: Commit**

```bash
git add auto_a11y/web/templates/testing/
git commit -m "fix(a11y): fix headings, add sections/fieldsets/figures in testing templates"
```

---

### Task 10: Recording Templates — Headings, Articles, DL, Figure

**Files:**
- Modify: `auto_a11y/web/templates/recordings/list.html`
- Modify: `auto_a11y/web/templates/recordings/detail.html`
- Modify: `auto_a11y/web/templates/recordings/combined.html`
- Modify: `auto_a11y/web/templates/recordings/upload.html`

- [ ] **Step 1: Read all recording templates**

Read all 4 files.

- [ ] **Step 2: Fix recordings/list.html**

1. Remove `h2` class from h1
2. Change each recording card `<div class="card h-100">` to `<article class="card h-100">`
3. Change `<h5>` card titles to `<h2>`; `<h6>` to `<h3>`

- [ ] **Step 3: Fix recordings/detail.html**

1. Remove `h2` class from h1
2. Convert metadata section from custom div layout to `<dl>`/`<dt>`/`<dd>`
3. Wrap metadata in `<section>` with `aria-labelledby`
4. Wrap screenshots in `<figure>` with `<figcaption>`
5. Add `<caption>` to tables

- [ ] **Step 4: Fix recordings/combined.html**

1. Wrap each recording card in `<article>`
2. Fix heading hierarchy

- [ ] **Step 5: Fix recordings/upload.html**

1. Wrap form in `<fieldset>` with `<legend>`
2. Add `aria-describedby` for all `.form-text` helper divs (this file has many)

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/templates/recordings/
git commit -m "fix(a11y): fix headings, add articles/dl/figures in recording templates"
```

---

### Task 11: Schedule & Script Templates — Headings, Table Captions, Fieldsets

**Files:**
- Modify: `auto_a11y/web/templates/schedules/list.html`
- Modify: `auto_a11y/web/templates/schedules/view.html`
- Modify: `auto_a11y/web/templates/schedules/dashboard.html`
- Modify: `auto_a11y/web/templates/schedules/form.html`
- Modify: `auto_a11y/web/templates/scripts/list.html`
- Modify: `auto_a11y/web/templates/scripts/view.html`
- Modify: `auto_a11y/web/templates/scripts/create.html`
- Modify: `auto_a11y/web/templates/scripts/edit.html`

- [ ] **Step 1: Read all schedule and script templates**

Read all 8 files.

- [ ] **Step 2: Fix schedule templates**

1. Fix heading hierarchy in all schedule templates
2. Add `<caption>` to tables in list.html and view.html
3. Convert key-value metadata in view.html to `<dl>`/`<dt>`/`<dd>`
4. Wrap sections in view.html and dashboard.html with `<section>` and `aria-labelledby`
5. Wrap form.html form fields in `<fieldset>` with `<legend>`
6. Add `aria-describedby` for `.form-text` helper divs in form.html

- [ ] **Step 3: Fix script templates**

1. Fix heading hierarchy in all script templates
2. Add `<caption>` to tables in list.html and view.html
3. Convert key-value metadata in view.html to `<dl>`/`<dt>`/`<dd>`
4. Wrap form fields in create.html and edit.html in `<fieldset>` with `<legend>`
5. Add `aria-describedby` for `.form-text` helper divs in create.html and edit.html

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/templates/schedules/ auto_a11y/web/templates/scripts/
git commit -m "fix(a11y): fix headings, add table captions and fieldsets in schedule/script templates"
```

---

### Task 12: User Management Templates — Table Captions, Fieldsets, aria-describedby

**Files:**
- Modify: `auto_a11y/web/templates/project_users/list.html`
- Modify: `auto_a11y/web/templates/project_users/view.html`
- Modify: `auto_a11y/web/templates/project_users/create.html`
- Modify: `auto_a11y/web/templates/project_users/edit.html`
- Modify: `auto_a11y/web/templates/website_users/list.html`
- Modify: `auto_a11y/web/templates/website_users/view.html`
- Modify: `auto_a11y/web/templates/website_users/create.html`
- Modify: `auto_a11y/web/templates/website_users/edit.html`
- Modify: `auto_a11y/web/templates/project_participants/list.html`
- Modify: `auto_a11y/web/templates/project_participants/create_supervisor.html`
- Modify: `auto_a11y/web/templates/project_participants/create_tester.html`
- Modify: `auto_a11y/web/templates/project_participants/edit_supervisor.html`
- Modify: `auto_a11y/web/templates/project_participants/edit_tester.html`

- [ ] **Step 1: Read all user management templates**

Read all 12 files.

- [ ] **Step 2: Fix list templates**

For project_users/list.html, website_users/list.html, project_participants/list.html:
1. Add `<caption class="visually-hidden">` to each table
2. Fix any heading hierarchy issues

- [ ] **Step 3: Fix view templates**

For project_users/view.html, website_users/view.html (if exists):
1. Fix heading hierarchy
2. Verify `<dl>` usage is correct for metadata

- [ ] **Step 4: Fix create/edit templates**

For all create and edit templates:
1. Wrap form fields in `<fieldset>` with `<legend>`
2. Add `aria-describedby` for `.form-text` helper divs
3. Fix heading hierarchy

- [ ] **Step 5: Commit**

```bash
git add auto_a11y/web/templates/project_users/ auto_a11y/web/templates/website_users/ auto_a11y/web/templates/project_participants/
git commit -m "fix(a11y): add table captions, fieldsets, aria-describedby in user management templates"
```

---

### Task 13: Other Admin Templates — Discovered Pages, Share Tokens, Reports, etc.

**Files:**
- Modify: `auto_a11y/web/templates/share_tokens/token_list_partial.html`
- Modify: `auto_a11y/web/templates/discovered_pages/view.html`
- Modify: `auto_a11y/web/templates/reports/dashboard.html`
- Modify: `auto_a11y/web/templates/automated_tests/list.html`
- Modify: `auto_a11y/web/templates/drupal_sync/project_sync.html`
- Modify: `auto_a11y/web/templates/drupal_sync/sync_card.html`

- [ ] **Step 1: Read all remaining admin templates**

Read all 6 files.

- [ ] **Step 2: Fix share_tokens/token_list_partial.html**

Add `<caption class="visually-hidden">` to the tokens table.

- [ ] **Step 3: Fix discovered_pages/view.html**

1. Convert metadata display from `<h6>` labels to `<dl>`/`<dt>`/`<dd>` structure
2. Fix heading hierarchy

- [ ] **Step 4: Fix reports/dashboard.html**

1. Fix heading hierarchy
2. Wrap sections with `<section>` and `aria-labelledby`

- [ ] **Step 6: Fix automated_tests/list.html**

Fix heading hierarchy.

- [ ] **Step 7: Fix drupal_sync templates**

Fix heading hierarchy in project_sync.html and sync_card.html.

- [ ] **Step 8: Commit**

```bash
git add auto_a11y/web/templates/share_tokens/ auto_a11y/web/templates/discovered_pages/ auto_a11y/web/templates/reports/ auto_a11y/web/templates/automated_tests/ auto_a11y/web/templates/drupal_sync/
git commit -m "fix(a11y): fix headings, table captions, dl structure in remaining admin templates"
```

---

### Task 14: Public Templates — DL Fix, Headings, Articles

**Files:**
- Modify: `auto_a11y/web/templates/public/project_list.html`
- Modify: `auto_a11y/web/templates/public/project.html`
- Modify: `auto_a11y/web/templates/public/website.html`
- Modify: `auto_a11y/web/templates/public/page.html`

- [ ] **Step 1: Read all public templates**

Read all 4 files.

- [ ] **Step 2: Fix public/project_list.html**

Wrap each project item in `<article>` if the structure supports it.

- [ ] **Step 3: Fix public/project.html**

1. Fix `<dl class="stats">` — currently has `<div class="stat-card">` children instead of `<dt>`/`<dd>`. Replace with proper `<dl><dt><dd>` structure.
2. Fix heading hierarchy
3. Wrap content sections in `<section>` with `aria-labelledby`

- [ ] **Step 4: Fix public/website.html**

1. Fix heading hierarchy
2. Wrap sections with `<section>` and `aria-labelledby`

- [ ] **Step 5: Fix public/page.html**

1. Fix `<dl class="stats">` — same issue as project.html, replace `<div>` children with `<dt>`/`<dd>`
2. Fix heading hierarchy

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/templates/public/
git commit -m "fix(a11y): fix dl structure, headings, add articles in public templates"
```

---

### Task 15: Static Report Templates — Table Captions, Headings, Dropdown, Figure

**Files:**
- Modify: `auto_a11y/web/templates/static_report/comprehensive_report_standalone.html`
- Modify: `auto_a11y/web/templates/static_report/recordings_report_standalone.html`
- Modify: `auto_a11y/web/templates/static_report/recordings_report.html`
- Modify: `auto_a11y/web/templates/static_report/page_detail.html`
- Modify: `auto_a11y/web/templates/static_report/summary.html`
- Modify: `auto_a11y/web/templates/static_report/project_deduplicated.html`
- Modify: `auto_a11y/web/templates/static_report/dedup_index.html`
- Modify: `auto_a11y/web/templates/static_report/dedup_component.html`
- Modify: `auto_a11y/web/templates/static_report/dedup_unassigned.html`
- Modify: `auto_a11y/web/templates/static_report/index.html`

- [ ] **Step 1: Read all static report templates**

Read all 10 files (some are large — read in sections as needed).

- [ ] **Step 2: Fix comprehensive_report_standalone.html**

1. Add `<caption>` to all 5 tables (replace `aria-label` where present with `<caption>` for consistency)
2. Fix heading hierarchy
3. Wrap screenshots in `<figure>` with `<figcaption>`

- [ ] **Step 3: Fix recordings_report_standalone.html**

1. Convert any `<a role="button">` dropdown toggles to `<button type="button">`
2. Fix heading hierarchy

- [ ] **Step 4: Fix page_detail.html and summary.html**

1. Fix heading hierarchy
2. Add `<caption>` to tables
3. Wrap screenshots in `<figure>` with `<figcaption>`
4. Wrap sections with `<section>` and `aria-labelledby`
5. Check page_detail.html for any `<a role="button">` dropdown toggles and convert to `<button>` if present

- [ ] **Step 5: Fix dedup templates and remaining report templates**

For recordings_report.html, project_deduplicated.html, dedup_index.html, dedup_component.html, dedup_unassigned.html, index.html:
1. Fix heading hierarchy
2. Add `<caption>` to tables
3. Wrap sections with `<section>` and `aria-labelledby`

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/templates/static_report/
git commit -m "fix(a11y): fix headings, add table captions and figures in static report templates"
```

---

### Task 16: Add aria-hidden to Remaining Decorative Icons

**Files:**
- Modify: Multiple template files where `<i class="bi bi-...">` lacks `aria-hidden="true"`

- [ ] **Step 1: Search for icons missing aria-hidden**

Search all templates for `<i class="bi` that do NOT have `aria-hidden="true"`.

- [ ] **Step 2: Add aria-hidden="true" to decorative icons**

For each decorative icon (next to visible text) missing `aria-hidden="true"`, add the attribute.

- [ ] **Step 3: Commit**

Run `git status` first to verify only the expected template files are modified, then stage and commit:

```bash
git add auto_a11y/web/templates/
git commit -m "fix(a11y): add aria-hidden to remaining decorative icons"
```

---

### Task 17: Error Page Templates

**Files:**
- Modify: `auto_a11y/web/templates/403.html`
- Modify: `auto_a11y/web/templates/404.html`
- Modify: `auto_a11y/web/templates/500.html`
- Modify: `auto_a11y/web/templates/public/error/403.html`

- [ ] **Step 1: Read error templates**

Read all 4 error templates.

- [ ] **Step 2: Fix heading hierarchy**

Ensure each error page has exactly one `<h1>` with no Bootstrap heading size classes.

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/templates/403.html auto_a11y/web/templates/404.html auto_a11y/web/templates/500.html auto_a11y/web/templates/public/error/
git commit -m "fix(a11y): fix heading hierarchy in error templates"
```

---

### Task 18: Final Verification

- [ ] **Step 1: Search for remaining Bootstrap heading size classes**

Search all templates for `class="h[1-6]` to find any remaining heading size overrides that were missed.

- [ ] **Step 2: Search for remaining `<a role="button">`**

Search all templates for `role="button"` on anchor tags.

- [ ] **Step 3: Search for tables missing captions**

Search for `<table` and verify each has a `<caption>` child.

- [ ] **Step 4: Search for .form-text without aria-describedby**

Search for `form-text` class usage and verify corresponding inputs have `aria-describedby`.

- [ ] **Step 5: Search for remaining heading hierarchy issues**

Grep for `<h[3-6]` in templates and verify they follow proper hierarchy under h1/h2.

- [ ] **Step 6: Fix any remaining issues found**

Address any issues discovered in steps 1-5.

- [ ] **Step 7: Commit any remaining fixes**

```bash
git add auto_a11y/web/templates/ auto_a11y/web/static/css/
git commit -m "fix(a11y): final sweep for remaining semantic HTML issues"
```
