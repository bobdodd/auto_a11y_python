# Semantic HTML Accessibility Overhaul Design

**Date:** 2026-03-18
**Scope:** Full semantic HTML overhaul of all Flask templates (admin + public)
**Goal:** Achieve exemplary WCAG 2.1 compliance in the Auto A11y web interface through strict heading hierarchy, proper form semantics, and comprehensive semantic HTML5 element usage.

---

## 1. Heading Hierarchy (Strict Sequential)

### Rules
- Exactly one `<h1>` per page (the page title)
- `<h2>` for major sections, `<h3>` for subsections, `<h4>` for sub-subsections
- No heading levels skipped (no jumping from `<h1>` to `<h5>`)
- No Bootstrap heading sizing classes on heading elements (no `<h1 class="h2">`, `<h1 class="h4">`, etc.) — use custom CSS classes for visual sizing if needed
- Modal titles use `<h2>` — rationale: Bootstrap modals are focus-trapped and effectively isolate heading context for screen reader users. While modals are not technically separate documents per the W3C spec, the focus trap creates a practical barrier that makes `<h2>` the most usable choice for assistive technology navigation within the modal.

### Templates Affected (comprehensive list of heading class overrides)
- **dashboard.html**: `<h1 class="h2">` becomes `<h1>`, card headings `<h6>` become `<h2>`
- **about.html**: `<h1 class="h2">` becomes `<h1>`, section headings `<h5>`/`<h6>` become `<h2>`/`<h3>`
- **help.html**: Sidebar nav headings `<h5>` become `<h2>`, content headings adjusted
- **auth/login.html**: `<h1 class="h4">` becomes `<h1>` (with custom CSS sizing if needed)
- **auth/register.html**: `<h1 class="h4">` becomes `<h1>` (with custom CSS sizing if needed)
- **projects/create.html**, **projects/view.html**: Modal titles `<h5>` become `<h2>`, interior headings follow sequence
- **pages/view.html**: All `<h6>` subsections become appropriate `<h2>`/`<h3>`/`<h4>` based on nesting
- **All other templates**: Audit all `class="h[1-6]"` on heading elements and remove/replace

---

## 2. Semantic Structure

### `<section>` Usage
Wrap every distinct content group that has (or should have) a heading. Each `<section>` gets `aria-labelledby` pointing to its heading ID.

**Where to add:**
- Dashboard: statistics, quick actions, test coverage, system status
- Project view: websites list, discovered pages, recordings
- Page view: errors, warnings, info accordion groups
- Testing dashboard: test selection areas
- All similar content groupings across templates

### `<article>` Usage
Wrap self-contained, independently meaningful content items:
- Each project card in project list
- Each website card in project view
- Each recording in recording lists

For test results in accordion views, `<article>` wraps the `.accordion-item` element (the outermost container for each result), preserving the existing Bootstrap accordion markup inside:
```html
<article class="accordion-item">
    <h3 class="accordion-header">
        <button class="accordion-button" ...>...</button>
    </h3>
    <div class="accordion-collapse collapse" ...>
        <div class="accordion-body">...</div>
    </div>
</article>
```

### `<aside>` Usage
Sidebar and supplementary content:
- Help page sidebar navigation
- Quick stats cards where supplementary to main content

### Navigation Landmarks
Add `aria-label` to distinguish multiple `<nav>` elements on the same page:
- **base.html** main `<nav>` (line 23): add `aria-label="{{ _('Main navigation') }}"`
- **static_report/base.html** main `<nav>`: add `aria-label="{{ _('Report navigation') }}"`
- Mobile bottom nav in base.html already has `aria-label="{{ _('Mobile navigation') }}"` — no change needed

---

## 3. Form Semantics

### `<fieldset>` / `<legend>`
Group related form controls with `<fieldset>` and descriptive `<legend>`:
- **Login form**: email + password
- **Registration form**: account details
- **Profile page**: profile info fieldset, password change fieldset
- **Project create/edit**: project type, WCAG level, touchpoint tests (with nested sub-groups), AI testing
- Reset default browser `<fieldset>` styling via CSS (no border/padding)

### `aria-describedby`
Connect helper text to form inputs. Every `<input>` with a `.form-text` sibling gets `aria-describedby` pointing to the helper text's `id`.

**All templates with `.form-text` elements** (23 files) need this connection. Key examples:
- projects/create.html, projects/edit.html
- scripts/create.html, scripts/edit.html
- websites/edit.html
- auth/register.html, auth/profile.html, auth/user_edit.html, auth/user_create.html
- pages/edit.html
- website_users/edit.html, website_users/create.html
- project_users/edit.html, project_users/create.html
- share_tokens/ templates
- schedules/ templates
- recordings/upload.html
- All other templates containing `.form-text` helper text

### `aria-invalid`
Add `aria-invalid="true"` to form fields rendered in error state (where Jinja adds error classes).

### `<a role="button">` to `<button>`
Replace dropdown toggle anchors with `<button type="button">` elements. Must keep `data-bs-toggle="dropdown"` attribute and the `id` used by `aria-labelledby` on the sibling `<ul>`.

**All instances to convert:**
- **base.html**: lines 47, 64, 80, 90, 108 (affects all pages extending base.html)
- **static_report/base.html**: line 203 (standalone report navigation)
- **static_report/page_detail.html**: standalone navbar dropdown (if present)
- **static_report/recordings_report_standalone.html**: standalone navbar dropdown (if present)

---

## 4. Tables, Definition Lists, Figures

### Table `<caption>`
Add `<caption>` (visually hidden where appropriate) to all tables lacking one. Tables needing captions include those in:
- recordings/detail.html (2 tables)
- projects/view.html (2 tables)
- schedules/view.html (5 tables)
- schedules/dashboard.html (1 table)
- scripts/view.html (2 tables)
- auth/user_list.html (1 table)
- websites/view.html (1 table)
- static_report/comprehensive_report_standalone.html (5 tables — 3 currently use `aria-label`, 2 have no accessible name; convert all to `<caption>` for consistency)
- All other tables without captions found during implementation

### `<dl>` / `<dt>` / `<dd>`
Replace key-value metadata displays with definition lists:
- Project metadata (created/updated dates)
- Page metadata (URL, status, last tested)
- User details (role, email, access level)
- Test result metadata (error code, category, WCAG criterion)
- Schedule metadata in schedules/view.html (key-value tables)
- Script metadata in scripts/view.html (key-value tables)
- Style with CSS to match current visual appearance

### `<figure>` / `<figcaption>`
Wrap visual content with semantic elements:
- Screenshot modals in page/website views
- Charts in testing/trends and static reports

---

## 5. CSS for Visual Consistency

Add to existing stylesheets (no new files):

```css
/* Reset fieldset browser defaults */
fieldset { border: none; padding: 0; margin: 0 0 1.5rem 0; }
legend { padding: 0; font-size: 1rem; font-weight: 600; }

/* Definition list styling */
dl { margin-bottom: 1rem; }
dt { font-weight: 600; color: #495057; }
dd { margin-left: 0; margin-bottom: 0.5rem; }

/* Figure styling */
figure { margin: 1rem 0; }
figcaption { font-size: 0.95rem; color: #6c757d; margin-top: 0.5rem; }
```

---

## 6. Scope and Boundaries

### In Scope
- All templates in `auto_a11y/web/templates/` (admin)
- All templates in `auto_a11y/web/templates/public/` (public-facing)
- Static report templates (`auto_a11y/web/templates/static_report/`)
- CSS changes for visual consistency

### Public Templates Note
`public_base.html` uses a different layout and CSS from the admin `base.html`. The public templates already have good semantic structure (`<header>`, `<footer>`, labeled `<nav>`, `<main>`). The heading hierarchy, `<section>`, `<dl>`, and `aria-describedby` rules still apply. The `<a role="button">` to `<button>` and fieldset changes primarily affect admin templates.

### Out of Scope
- JavaScript behavior changes (focus management, ARIA state toggling already handled by Bootstrap)
- Color contrast changes (already compliant)
- Skip links (already implemented correctly)
- Icon accessibility — all icon-only interactive elements have accessible text via `aria-label`. Non-interactive decorative icons next to visible text may not all have `aria-hidden="true"` — adding this attribute to remaining decorative icons is included in scope as a low-impact cleanup task
- Live regions (already implemented correctly)

---

## 7. Risk Mitigation

- **Visual regression**: CSS resets for `<fieldset>`, `<dl>`, `<figure>` prevent layout changes
- **Bootstrap JS**: `<button>` replacements for dropdown toggles must keep `data-bs-toggle="dropdown"` attribute and the `id` referenced by `aria-labelledby` on the sibling `<ul>` — Bootstrap 5 fully supports `<button>` dropdowns
- **Template inheritance**: Changes to `base.html` affect all child templates — test thoroughly
- **Incremental approach**: Templates updated one at a time, each verified before moving on
