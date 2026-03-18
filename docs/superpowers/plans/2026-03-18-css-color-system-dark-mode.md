# CSS Color System & Dark Mode Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor all CSS colors to semantic custom properties and add a WCAG 2.2 AA dark mode with OS detection + manual toggle.

**Architecture:** Single semantic token layer in `tokens.css` with `:root` (light), `@media (prefers-color-scheme: dark)`, and `[data-theme="dark"]` overrides. Zero raw color values anywhere. Zero inline color styles.

**Tech Stack:** CSS custom properties, vanilla JavaScript (toggle + localStorage), Jinja2 templates, Bootstrap 5 variable re-pointing.

**Spec:** `docs/superpowers/specs/2026-03-18-css-color-system-dark-mode-design.md`

---

## File Structure

### Files to Create
- `auto_a11y/web/static/css/theme-toggle.css` — Toggle button styles (both modes)
- `auto_a11y/web/static/js/theme-toggle.js` — Toggle logic, localStorage, aria-live
- `auto_a11y/web/templates/components/theme_toggle.html` — Jinja2 partial for toggle button

### Files to Modify (in order)
1. `auto_a11y/web/static/public/css/tokens.css` — Expand to full token set with light/dark/print
2. `auto_a11y/web/static/css/style.css` — Replace hardcoded colors with `var()`, add Bootstrap re-pointing
3. `auto_a11y/web/static/css/mobile.css` — Replace hardcoded colors with `var()`
4. `auto_a11y/web/static/css/help-system.css` — Replace hardcoded colors with `var()`
5. `auto_a11y/web/static/public/css/main.css` — Update old token names to new names
6. `auto_a11y/web/static/public/css/print.css` — Force light mode tokens in print
7. `demo_site/css/styles.css` — Replace structural UI colors with `var()`
8. `auto_a11y/web/templates/base.html` — Anti-FOUC script, tokens.css import, toggle
9. `auto_a11y/web/templates/public/public_base.html` — Anti-FOUC script, toggle
10. `auto_a11y/web/templates/static_report/base.html` — Token import for linked reports
11. `auto_a11y/reporting/static_html_generator.py` — Inline tokens in standalone reports
12. ~26 admin templates — Extract inline color styles to CSS classes
13. ~6 demo site templates — Extract inline color styles to CSS classes

---

## Task 1: Expand tokens.css with Full Token Set

**Files:**
- Modify: `auto_a11y/web/static/public/css/tokens.css`

This is the foundation. Every other task depends on this.

- [ ] **Step 1: Read the current tokens.css**

Current file at `auto_a11y/web/static/public/css/tokens.css` has 13 color tokens plus typography/spacing. We keep all non-color tokens unchanged.

- [ ] **Step 2: Replace the file with the full token set**

Write the complete `tokens.css` with all tokens from the spec. Structure:

```css
/*
 * Design tokens for the Auto A11y application.
 * All colour tokens have both light and dark mode values.
 * All text colours meet WCAG 2.2 AA (4.5:1+).
 * All non-text UI components meet 3:1+ per SC 1.4.11.
 */

/* ===== LIGHT MODE (default) ===== */
:root {
    /* Brand */
    --color-brand: #1a5276;
    --color-brand-hover: #0e2f44;
    --color-brand-subtle: #f4f6f7;

    /* Text */
    --color-text: #1c1c1c;
    --color-text-muted: #4a4a4a;
    --color-text-inverse: #ffffff;
    --color-text-heading: #1c1c1c;
    --color-text-code: #dd1144;

    /* Links */
    --color-link: #0a58ca;
    --color-link-hover: #084298;
    --color-link-visited: #1a5276;

    /* Backgrounds */
    --color-bg: #ffffff;
    --color-bg-subtle: #f4f6f7;
    --color-bg-elevated: #ffffff;
    --color-bg-header: #1a5276;
    --color-bg-footer: #f8f9fa;
    --color-bg-code: #f4f4f4;
    --color-bg-input: #ffffff;
    --color-bg-scrollbar: #f1f1f1;
    --color-bg-overlay: rgba(0, 0, 0, 0.5);

    /* Borders */
    --color-border: #d5d8dc;
    --color-border-strong: #85929e;
    --color-border-input: #86868b;
    --color-border-input-focus: #0a58ca;
    --color-border-table: #dee2e6;

    /* Focus & Interaction */
    --color-focus-ring: #0a58ca;
    --color-button-primary-bg: #1a5276;
    --color-button-primary-text: #ffffff;
    --color-button-primary-hover: #0e2f44;
    --color-scrollbar-thumb: #888888;

    /* Severity */
    --color-severity-high: #922b21;
    --color-severity-high-bg: #fdedec;
    --color-severity-high-border: #922b21;
    --color-severity-medium: #7d6608;
    --color-severity-medium-bg: #fff3cd;
    --color-severity-medium-border: #b38600;
    --color-severity-low: #2c3e50;
    --color-severity-pass: #1e8449;
    --color-severity-pass-bg: #eafaf1;
    --color-severity-pass-border: #1e8449;
    --color-info: #0e7490;
    --color-info-bg: #d1ecf1;
    --color-info-border: #0e7490;

    /* Discovery */
    --color-discovery: #6f42c1;
    --color-discovery-bg: #f3eefa;
    --color-discovery-border: #6f42c1;
    --color-discovery-hover: #5a32a3;

    /* Severity gradient endpoints (for report section headers) */
    --color-severity-high-gradient-end: #c82333;
    --color-severity-medium-gradient-end: #e0a800;
    --color-severity-pass-gradient-end: #148040;
    --color-info-gradient-end: #0aa2c0;
    --color-discovery-gradient-end: #5a32a3;

    /* Shadows */
    --color-shadow-subtle: rgba(0, 0, 0, 0.08);
    --color-shadow-medium: rgba(0, 0, 0, 0.1);
    --color-shadow-strong: rgba(0, 0, 0, 0.15);

    /* Progress & Animation */
    --color-progress-track: #e9ecef;
    --color-progress-fill: #198754;
    --color-spinner-overlay: rgba(255, 255, 255, 0.8);
    --color-pulse-ring: rgba(25, 135, 84, 0.4);

    /* Help System */
    --color-help-icon: #3498db;
    --color-help-icon-hover: #2980b9;
    --color-help-heading: #2c3e50;

    /* SSO Buttons (brand-mandated, same in both modes) */
    --color-sso-microsoft-bg: #2f2f2f;
    --color-sso-microsoft-hover: #1a1a1a;
    --color-sso-google-bg: #ffffff;
    --color-sso-google-text: #3c4043;
    --color-sso-google-border: #dadce0;
    --color-sso-google-hover: #f7f8f8;

    /* Demo Site */
    --color-demo-brand: #004d99;
    --color-demo-brand-hover: #003d7a;
    --color-demo-cookie-link: #aaddff;

    /* Typography (unchanged from existing) */
    --font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --font-mono: ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Consolas, monospace;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.5rem;
    --font-size-2xl: 2rem;
    --line-height: 1.6;
    --line-height-tight: 1.3;

    /* Spacing (unchanged from existing) */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    --space-2xl: 3rem;

    /* Layout (unchanged from existing) */
    --container-max: 72rem;
    --border-radius: 4px;
}

/* ===== DARK MODE (OS preference) ===== */
@media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
        --color-brand: #5da9e9;
        --color-brand-hover: #6db3f2;
        --color-brand-subtle: #252542;

        --color-text: #e0e0e6;
        --color-text-muted: #8a8a9a;
        --color-text-inverse: #ffffff;
        --color-text-heading: #ffffff;
        --color-text-code: #f28b82;

        --color-link: #6db3f2;
        --color-link-hover: #7ebcfa;
        --color-link-visited: #5da9e9;

        --color-bg: #1a1a2e;
        --color-bg-subtle: #252542;
        --color-bg-elevated: #2d2d4a;
        --color-bg-header: #12122a;
        --color-bg-footer: #151530;
        --color-bg-code: #252542;
        --color-bg-input: #252542;
        --color-bg-scrollbar: #1a1a2e;
        --color-bg-overlay: rgba(0, 0, 0, 0.7);

        --color-border: #6a6a8c;
        --color-border-strong: #7a7a9a;
        --color-border-input: #7a7a9a;
        --color-border-input-focus: #5da9e9;
        --color-border-table: #6a6a8c;

        --color-focus-ring: #6db3f2;
        --color-button-primary-bg: #5da9e9;
        --color-button-primary-text: #0e1525;
        --color-button-primary-hover: #6db3f2;
        --color-scrollbar-thumb: #6a6a8a;

        --color-severity-high: #f28b82;
        --color-severity-high-bg: #3d1f1f;
        --color-severity-high-border: #f28b82;
        --color-severity-medium: #f9a825;
        --color-severity-medium-bg: #3d3520;
        --color-severity-medium-border: #f9a825;
        --color-severity-low: #b0b0bc;
        --color-severity-pass: #81c784;
        --color-severity-pass-bg: #1f3d2a;
        --color-severity-pass-border: #81c784;
        --color-info: #64b5f6;
        --color-info-bg: #1f2d3d;
        --color-info-border: #64b5f6;

        --color-discovery: #b39ddb;
        --color-discovery-bg: #2d1f4a;
        --color-discovery-border: #b39ddb;
        --color-discovery-hover: #c4b0e0;

        --color-severity-high-gradient-end: #d95050;
        --color-severity-medium-gradient-end: #d4a020;
        --color-severity-pass-gradient-end: #6aab6d;
        --color-info-gradient-end: #509dbf;
        --color-discovery-gradient-end: #9070c0;

        --color-shadow-subtle: rgba(0, 0, 0, 0.3);
        --color-shadow-medium: rgba(0, 0, 0, 0.4);
        --color-shadow-strong: rgba(0, 0, 0, 0.5);

        --color-progress-track: #3a3a5c;
        --color-progress-fill: #81c784;
        --color-spinner-overlay: rgba(0, 0, 0, 0.6);
        --color-pulse-ring: rgba(129, 199, 132, 0.4);

        --color-help-icon: #64b5f6;
        --color-help-icon-hover: #6db3f2;
        --color-help-heading: #e0e0e6;

        --color-demo-brand: #5da9e9;
        --color-demo-brand-hover: #6db3f2;
        --color-demo-cookie-link: #6db3f2;
    }
}

/* ===== DARK MODE (manual override — always wins) ===== */
/* IMPORTANT: This block must contain ALL dark values, identical to the
   @media (prefers-color-scheme: dark) block above. Copy every token. */
[data-theme="dark"] {
    --color-brand: #5da9e9;
    --color-brand-hover: #6db3f2;
    --color-brand-subtle: #252542;

    --color-text: #e0e0e6;
    --color-text-muted: #8a8a9a;
    --color-text-inverse: #ffffff;
    --color-text-heading: #ffffff;
    --color-text-code: #f28b82;

    --color-link: #6db3f2;
    --color-link-hover: #7ebcfa;
    --color-link-visited: #5da9e9;

    --color-bg: #1a1a2e;
    --color-bg-subtle: #252542;
    --color-bg-elevated: #2d2d4a;
    --color-bg-header: #12122a;
    --color-bg-footer: #151530;
    --color-bg-code: #252542;
    --color-bg-input: #252542;
    --color-bg-scrollbar: #1a1a2e;
    --color-bg-overlay: rgba(0, 0, 0, 0.7);

    --color-border: #6a6a8c;
    --color-border-strong: #7a7a9a;
    --color-border-input: #7a7a9a;
    --color-border-input-focus: #5da9e9;
    --color-border-table: #6a6a8c;

    --color-focus-ring: #6db3f2;
    --color-button-primary-bg: #5da9e9;
    --color-button-primary-text: #0e1525;
    --color-button-primary-hover: #6db3f2;
    --color-scrollbar-thumb: #6a6a8a;

    --color-severity-high: #f28b82;
    --color-severity-high-bg: #3d1f1f;
    --color-severity-high-border: #f28b82;
    --color-severity-medium: #f9a825;
    --color-severity-medium-bg: #3d3520;
    --color-severity-medium-border: #f9a825;
    --color-severity-low: #b0b0bc;
    --color-severity-pass: #81c784;
    --color-severity-pass-bg: #1f3d2a;
    --color-severity-pass-border: #81c784;
    --color-info: #64b5f6;
    --color-info-bg: #1f2d3d;
    --color-info-border: #64b5f6;

    --color-discovery: #b39ddb;
    --color-discovery-bg: #2d1f4a;
    --color-discovery-border: #b39ddb;
    --color-discovery-hover: #c4b0e0;

    --color-severity-high-gradient-end: #d95050;
    --color-severity-medium-gradient-end: #d4a020;
    --color-severity-pass-gradient-end: #6aab6d;
    --color-info-gradient-end: #509dbf;
    --color-discovery-gradient-end: #9070c0;

    --color-shadow-subtle: rgba(0, 0, 0, 0.3);
    --color-shadow-medium: rgba(0, 0, 0, 0.4);
    --color-shadow-strong: rgba(0, 0, 0, 0.5);

    --color-progress-track: #3a3a5c;
    --color-progress-fill: #81c784;
    --color-spinner-overlay: rgba(0, 0, 0, 0.6);
    --color-pulse-ring: rgba(129, 199, 132, 0.4);

    --color-help-icon: #64b5f6;
    --color-help-icon-hover: #6db3f2;
    --color-help-heading: #e0e0e6;

    --color-demo-brand: #5da9e9;
    --color-demo-brand-hover: #6db3f2;
    --color-demo-cookie-link: #6db3f2;
}

/* ===== PRINT (force light mode regardless of theme) ===== */
/* IMPORTANT: This block must contain ALL light values to override
   any dark mode that may be active. Copy every token from :root. */
@media print {
    :root,
    :root[data-theme="dark"] {
        --color-brand: #1a5276;
        --color-brand-hover: #0e2f44;
        --color-brand-subtle: #f4f6f7;

        --color-text: #1c1c1c;
        --color-text-muted: #4a4a4a;
        --color-text-inverse: #ffffff;
        --color-text-heading: #1c1c1c;
        --color-text-code: #dd1144;

        --color-link: #0a58ca;
        --color-link-hover: #084298;
        --color-link-visited: #1a5276;

        --color-bg: #ffffff;
        --color-bg-subtle: #f4f6f7;
        --color-bg-elevated: #ffffff;
        --color-bg-header: #1a5276;
        --color-bg-footer: #f8f9fa;
        --color-bg-code: #f4f4f4;
        --color-bg-input: #ffffff;
        --color-bg-scrollbar: #f1f1f1;
        --color-bg-overlay: rgba(0, 0, 0, 0.5);

        --color-border: #d5d8dc;
        --color-border-strong: #85929e;
        --color-border-input: #86868b;
        --color-border-input-focus: #0a58ca;
        --color-border-table: #dee2e6;

        --color-focus-ring: #0a58ca;
        --color-button-primary-bg: #1a5276;
        --color-button-primary-text: #ffffff;
        --color-button-primary-hover: #0e2f44;
        --color-scrollbar-thumb: #888888;

        --color-severity-high: #922b21;
        --color-severity-high-bg: #fdedec;
        --color-severity-high-border: #922b21;
        --color-severity-medium: #7d6608;
        --color-severity-medium-bg: #fff3cd;
        --color-severity-medium-border: #b38600;
        --color-severity-low: #2c3e50;
        --color-severity-pass: #1e8449;
        --color-severity-pass-bg: #eafaf1;
        --color-severity-pass-border: #1e8449;
        --color-info: #0e7490;
        --color-info-bg: #d1ecf1;
        --color-info-border: #0e7490;

        --color-discovery: #6f42c1;
        --color-discovery-bg: #f3eefa;
        --color-discovery-border: #6f42c1;
        --color-discovery-hover: #5a32a3;

        --color-severity-high-gradient-end: #c82333;
        --color-severity-medium-gradient-end: #e0a800;
        --color-severity-pass-gradient-end: #148040;
        --color-info-gradient-end: #0aa2c0;
        --color-discovery-gradient-end: #5a32a3;

        --color-shadow-subtle: rgba(0, 0, 0, 0.08);
        --color-shadow-medium: rgba(0, 0, 0, 0.1);
        --color-shadow-strong: rgba(0, 0, 0, 0.15);

        --color-progress-track: #e9ecef;
        --color-progress-fill: #198754;
        --color-spinner-overlay: rgba(255, 255, 255, 0.8);
        --color-pulse-ring: rgba(25, 135, 84, 0.4);

        --color-help-icon: #3498db;
        --color-help-icon-hover: #2980b9;
        --color-help-heading: #2c3e50;

        --color-demo-brand: #004d99;
        --color-demo-brand-hover: #003d7a;
        --color-demo-cookie-link: #aaddff;
    }
}
```

The `[data-theme="dark"]` block and `@media print` block both repeat their full value sets. This is intentional — CSS custom properties require explicit values in each scope.

- [ ] **Step 3: Verify the file loads without errors**

Open the app in a browser and check the browser console for CSS parse errors. Run:
```bash
.venv/bin/python run.py --debug
```
Visit `http://127.0.0.1:5001` and check browser devtools console for errors.

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/static/public/css/tokens.css
git commit -m "feat: expand tokens.css with full semantic color token set and dark mode"
```

---

## Task 2: Create Theme Toggle Component

**Files:**
- Create: `auto_a11y/web/static/js/theme-toggle.js`
- Create: `auto_a11y/web/static/css/theme-toggle.css`
- Create: `auto_a11y/web/templates/components/theme_toggle.html`

- [ ] **Step 1: Create theme-toggle.js**

Write to `auto_a11y/web/static/js/theme-toggle.js`:

```javascript
/**
 * Theme toggle: cycles auto -> light -> dark -> auto.
 * Persists preference in localStorage under 'theme-preference'.
 * Announces changes via aria-live region.
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'theme-preference';
    var STATES = ['auto', 'light', 'dark'];
    var LABELS = {
        auto: 'Color theme: automatic. Switch to light.',
        light: 'Color theme: light. Switch to dark.',
        dark: 'Color theme: dark. Switch to automatic.'
    };
    var ANNOUNCEMENTS = {
        auto: 'Color theme changed to automatic.',
        light: 'Color theme changed to light.',
        dark: 'Color theme changed to dark.'
    };

    function getPreference() {
        try {
            return localStorage.getItem(STORAGE_KEY) || 'auto';
        } catch (e) {
            return 'auto';
        }
    }

    function setPreference(pref) {
        try {
            localStorage.setItem(STORAGE_KEY, pref);
        } catch (e) {
            // localStorage unavailable — preference won't persist
        }
    }

    function applyTheme(pref) {
        if (pref === 'light' || pref === 'dark') {
            document.documentElement.setAttribute('data-theme', pref);
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    }

    function updateButton(btn, pref) {
        btn.setAttribute('aria-label', LABELS[pref]);
        // Update icon visibility
        var icons = btn.querySelectorAll('[data-theme-icon]');
        for (var i = 0; i < icons.length; i++) {
            icons[i].hidden = icons[i].getAttribute('data-theme-icon') !== pref;
        }
    }

    function announce(pref) {
        var region = document.getElementById('theme-announce');
        if (region) {
            region.textContent = ANNOUNCEMENTS[pref];
        }
    }

    function init() {
        var btn = document.getElementById('theme-toggle');
        if (!btn) return;

        var currentPref = getPreference();
        updateButton(btn, currentPref);

        btn.addEventListener('click', function () {
            var current = getPreference();
            var nextIndex = (STATES.indexOf(current) + 1) % STATES.length;
            var next = STATES[nextIndex];

            setPreference(next);
            applyTheme(next);
            updateButton(btn, next);
            announce(next);
        });
    }

    // Run on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
```

- [ ] **Step 2: Create theme-toggle.css**

Write to `auto_a11y/web/static/css/theme-toggle.css`:

```css
/* Theme toggle button */
.theme-toggle {
    background: none;
    border: 2px solid var(--color-text-inverse);
    border-radius: var(--border-radius, 4px);
    color: var(--color-text-inverse);
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    font-size: 1.1rem;
    line-height: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
.theme-toggle:hover {
    background: var(--color-shadow-subtle);
}
.theme-toggle:focus-visible {
    outline: 2px solid var(--color-focus-ring);
    outline-offset: 2px;
}

/* Screen reader only announcement region */
#theme-announce {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
```

- [ ] **Step 3: Create theme_toggle.html partial**

Write to `auto_a11y/web/templates/components/theme_toggle.html`:

```html
<button type="button" id="theme-toggle" class="theme-toggle" aria-label="Color theme: automatic. Switch to light.">
    <span data-theme-icon="auto" aria-hidden="true">&#x25D0;</span>
    <span data-theme-icon="light" aria-hidden="true" hidden>&#x2600;</span>
    <span data-theme-icon="dark" aria-hidden="true" hidden>&#x263D;</span>
</button>
<div id="theme-announce" aria-live="polite" aria-atomic="true"></div>
```

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/static/js/theme-toggle.js auto_a11y/web/static/css/theme-toggle.css auto_a11y/web/templates/components/theme_toggle.html
git commit -m "feat: add theme toggle component with aria-live announcements"
```

---

## Task 3: Update base.html (Admin Template)

**Files:**
- Modify: `auto_a11y/web/templates/base.html`

- [ ] **Step 1: Add anti-FOUC script and tokens.css import**

In `base.html`, BEFORE the Bootstrap CSS link (line 9), add:

```html
    <!-- Anti-FOUC: apply saved theme before render -->
    <script>
    (function(){try{var p=localStorage.getItem('theme-preference');if(p==='dark'||p==='light'){document.documentElement.setAttribute('data-theme',p);}}catch(e){}})();
    </script>
    <!-- Design Tokens (must load before Bootstrap) -->
    <link rel="stylesheet" href="{{ url_for('public.static', filename='css/tokens.css') }}">
```

After the mobile.css link (line 15), add:

```html
    <!-- Theme Toggle -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/theme-toggle.css') }}">
```

- [ ] **Step 2: Add toggle button to the navbar**

In the navbar's right-side `<ul>` (around line 77, before the language selector `<li>`), add:

```html
                    <!-- Theme Toggle -->
                    <li class="nav-item d-flex align-items-center px-2">
                        {% include 'components/theme_toggle.html' %}
                    </li>
```

- [ ] **Step 3: Add theme-toggle.js before the closing body tag**

Before `{% block extra_js %}` (line 615), add:

```html
    <script src="{{ url_for('static', filename='js/theme-toggle.js') }}"></script>
```

- [ ] **Step 4: Verify the toggle appears and cycles through states**

Run the app and confirm:
- The toggle button appears in the nav bar
- Clicking cycles: auto (half-circle) -> light (sun) -> dark (moon) -> auto
- Screen reader announces each state change
- Preference persists across page reloads
- OS preference is respected when set to "auto"

- [ ] **Step 5: Commit**

```bash
git add auto_a11y/web/templates/base.html
git commit -m "feat: add anti-FOUC script, tokens import, and theme toggle to admin base"
```

---

## Task 4: Update public_base.html (Public Frontend Template)

**Files:**
- Modify: `auto_a11y/web/templates/public/public_base.html`

- [ ] **Step 1: Add anti-FOUC script before first stylesheet**

Before the `reset.css` link (line 7), add the same anti-FOUC script:

```html
    <script>
    (function(){try{var p=localStorage.getItem('theme-preference');if(p==='dark'||p==='light'){document.documentElement.setAttribute('data-theme',p);}}catch(e){}})();
    </script>
```

- [ ] **Step 2: Add theme toggle CSS link**

`tokens.css` is already linked on line 8 — no change needed there. After the `print.css` link (line 10), add the theme-toggle CSS:

```html
    <link rel="stylesheet" href="{{ url_for('static', filename='css/theme-toggle.css') }}">
```

- [ ] **Step 3: Add toggle to the public header**

In the `<header>` section, after the language nav and before the closing `</div>`, add the toggle include:

```html
            {% include 'components/theme_toggle.html' %}
```

- [ ] **Step 4: Add theme-toggle.js before closing body tag**

Add before `</body>`:

```html
    <script src="{{ url_for('static', filename='js/theme-toggle.js') }}"></script>
```

- [ ] **Step 5: Commit**

```bash
git add auto_a11y/web/templates/public/public_base.html
git commit -m "feat: add anti-FOUC script and theme toggle to public frontend base"
```

---

## Task 5: Refactor style.css (Admin Stylesheet)

**Files:**
- Modify: `auto_a11y/web/static/css/style.css`

This is the largest single file change. Read the full file first.

- [ ] **Step 1: Read style.css completely**

Read `auto_a11y/web/static/css/style.css` to understand all color usages.

- [ ] **Step 2: Remove old variable definitions and add Bootstrap re-pointing**

Replace the existing `:root` block (lines 3-10) with Bootstrap re-pointing:

```css
/* Re-point Bootstrap variables to our design tokens */
:root {
    --bs-primary: var(--color-brand);
    --bs-primary-rgb: 26, 82, 118;
    --bs-info: var(--color-info);
    --bs-info-rgb: 14, 116, 144;
    --bs-success: var(--color-severity-pass);
    --bs-danger: var(--color-severity-high);
    --bs-warning: var(--color-severity-medium);
    --bs-body-color: var(--color-text);
    --bs-body-bg: var(--color-bg);
    --bs-border-color: var(--color-border);
}

@media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
        --bs-primary-rgb: 93, 169, 233;
        --bs-info-rgb: 100, 181, 246;
    }
}
[data-theme="dark"] {
    --bs-primary-rgb: 93, 169, 233;
    --bs-info-rgb: 100, 181, 246;
}
```

Also remove the later `:root` blocks that override `--bs-primary` and `--bs-info` (around lines 324-356 in current file).

- [ ] **Step 3: Replace all hardcoded colors throughout the file**

For every CSS rule containing a hardcoded color, replace with the appropriate `var()`. Use the mapping from the spec's "Additional Utility Tokens" table. Key replacements:

- `#0d6efd` / `var(--primary-color)` → `var(--color-brand)`
- `#0a58ca` → `var(--color-link)` or `var(--color-focus-ring)` depending on context
- `#084298` → `var(--color-link-hover)`
- `#0e7490` / `var(--bs-info)` → `var(--color-info)`
- `#198754` / `var(--success-color)` → `var(--color-severity-pass)`
- `#dc3545` / `var(--danger-color)` → `var(--color-severity-high)`
- `#ffc107` / `var(--warning-color)` → `var(--color-severity-medium)`
- `white` / `#fff` → `var(--color-text-inverse)` (on colored bg) or `var(--color-bg)` (as background)
- `#212529` / `#333` / `#495057` → `var(--color-text)`
- `#555` / `#666` / `#6c757d` → `var(--color-text-muted)`
- `#dee2e6` → `var(--color-border-table)`
- `#e0e0e0` / `#d5d8dc` → `var(--color-border)`
- `#86868b` → `var(--color-border-input)`
- `#f8f9fa` / `#f0f0f0` / `#f4f6f7` → `var(--color-bg-subtle)`
- `#e9ecef` → `var(--color-progress-track)`
- `#f1f1f1` → `var(--color-bg-scrollbar)`
- `#888` / `#888888` → `var(--color-scrollbar-thumb)`
- `rgba(0,0,0,0.02)` / `rgba(0,0,0,0.08)` → `var(--color-shadow-subtle)`
- `rgba(0,0,0,0.1)` → `var(--color-shadow-medium)`
- `rgba(0,0,0,0.15)` → `var(--color-shadow-strong)`
- `rgba(255,255,255,0.8)` → `var(--color-spinner-overlay)`
- `rgba(25,135,84,0.4)` → `var(--color-pulse-ring)`
- Focus outlines: change `2px solid var(--primary-color)` → `2px solid var(--color-focus-ring)` with `outline-offset: 2px`

- [ ] **Step 4: Update the high contrast media query**

Replace hardcoded colors in `@media (prefers-contrast: more)` with token references where appropriate (e.g., `#000` becomes stronger versions of existing tokens).

- [ ] **Step 5: Verify no raw color values remain**

Search the file for any remaining hex codes, rgb/rgba values, or named colors. The ONLY exceptions allowed are:
- Inside the `:root` Bootstrap re-pointing block (RGB triplet values)
- `transparent` and `inherit` (CSS keywords, not colors)

Run: Search for `#[0-9a-fA-F]` and `rgb` in the file.

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/web/static/css/style.css
git commit -m "refactor: replace all hardcoded colors in style.css with design tokens"
```

---

## Task 6: Refactor mobile.css

**Files:**
- Modify: `auto_a11y/web/static/css/mobile.css`

- [ ] **Step 1: Read mobile.css completely**

- [ ] **Step 2: Replace all hardcoded colors**

Key replacements:
- `#dee2e6` → `var(--color-border-table)`
- `#f0f0f0` → `var(--color-bg-subtle)`
- `#f8f9fa` → `var(--color-bg-subtle)`
- `var(--bs-primary)` → `var(--color-brand)` (or leave as `--bs-primary` since it's now re-pointed)
- `var(--bs-secondary)` → keep as-is (Bootstrap handles it)
- `rgba(0,0,0,0.08)` → `var(--color-shadow-subtle)`
- `rgba(0,0,0,0.1)` → `var(--color-shadow-medium)`
- `rgba(255,255,255,*)` values → appropriate tokens
- `white` → `var(--color-bg)` or `var(--color-text-inverse)` by context

- [ ] **Step 3: Verify no raw color values remain**

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/static/css/mobile.css
git commit -m "refactor: replace all hardcoded colors in mobile.css with design tokens"
```

---

## Task 7: Refactor help-system.css

**Files:**
- Modify: `auto_a11y/web/static/css/help-system.css`

- [ ] **Step 1: Read help-system.css completely**

- [ ] **Step 2: Replace all hardcoded colors**

Key replacements:
- `#fff` → `var(--color-bg)` (modal bg) or `var(--color-text-inverse)` (text on colored bg)
- `#f9f9f9` / `#f4f4f4` → `var(--color-bg-subtle)`
- `#f0f0f0` → `var(--color-bg-subtle)`
- `#e0e0e0` → `var(--color-border)`
- `#d14` → `var(--color-text-code)`
- `#333` / `#34495e` → `var(--color-text-heading)`
- `#2c3e50` → `var(--color-help-heading)`
- `#555` / `#666` → `var(--color-text-muted)`
- `#495057` / `#6c757d` → `var(--color-text-muted)`
- `#3498db` → `var(--color-help-icon)`
- `#2980b9` → `var(--color-help-icon-hover)`
- `rgba(0,0,0,0.5)` → `var(--color-bg-overlay)`
- `rgba(0,0,0,0.15)` → `var(--color-shadow-strong)`

- [ ] **Step 3: Verify no raw color values remain**

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/static/css/help-system.css
git commit -m "refactor: replace all hardcoded colors in help-system.css with design tokens"
```

---

## Task 8: Update public frontend main.css

**Files:**
- Modify: `auto_a11y/web/static/public/css/main.css`

- [ ] **Step 1: Read main.css completely**

- [ ] **Step 2: Update old token names to new names**

Replace all references per migration table:
- `var(--color-primary)` → `var(--color-brand)`
- `var(--color-primary-light)` → `var(--color-link)`
- `var(--color-primary-dark)` → `var(--color-brand-hover)`
- `var(--focus-outline)` → `2px solid var(--color-focus-ring)` (decomposed)
- `var(--focus-offset)` → `2px` (hardcoded)

Also replace any remaining hardcoded colors (SSO button colors, flash message colors, etc.) with token references.

- [ ] **Step 3: Verify no raw color values remain**

- [ ] **Step 4: Commit**

```bash
git add auto_a11y/web/static/public/css/main.css
git commit -m "refactor: migrate public frontend CSS to new token names"
```

---

## Task 9: Update print.css

**Files:**
- Modify: `auto_a11y/web/static/public/css/print.css`

- [ ] **Step 1: Read print.css**

- [ ] **Step 2: Add print-mode token overrides**

`tokens.css` (Task 1) already has a `@media print` block that forces all tokens to light mode values. The role of `print.css` is print-specific layout (hiding nav, expanding accordions, etc.), NOT token overrides. In this step, only replace any hardcoded colors in the existing print layout rules with token references. Do NOT duplicate the token override block from `tokens.css`.

- [ ] **Step 3: Commit**

```bash
git add auto_a11y/web/static/public/css/print.css
git commit -m "refactor: force light mode tokens in print stylesheet"
```

---

## Task 10: Refactor demo_site/css/styles.css

**Files:**
- Modify: `demo_site/css/styles.css`

- [ ] **Step 1: Read demo_site/css/styles.css completely**

- [ ] **Step 2: Inline token definitions at the top of the file**

The demo site is served as a standalone test target, not necessarily through the Flask app. Therefore, inline the full `:root`, `@media (prefers-color-scheme: dark)`, `[data-theme="dark"]`, and `@media print` token blocks directly at the top of `demo_site/css/styles.css`. Copy them from `tokens.css` (the output of Task 1). This ensures the demo site works independently regardless of how it is served.

Note: Demo site SVGs (`demo_site/images/*.svg`) contain hardcoded colors for gradients. These are left as-is since they are image assets, not UI chrome.

- [ ] **Step 3: Replace structural UI colors with tokens**

Replace colors in the demo site's chrome (nav, footer, cookie banner, buttons) with `var()` references. Use `--color-demo-brand`, `--color-demo-brand-hover`, `--color-demo-cookie-link` for brand-specific elements.

**Leave intentionally inaccessible elements as hardcoded** with comments:

```css
/* INTENTIONAL: low contrast for accessibility testing */
.fake-heading { color: #999; }
```

- [ ] **Step 4: Commit**

```bash
git add demo_site/css/styles.css
git commit -m "refactor: tokenize demo site structural UI colors, preserve intentional test issues"
```

---

## Task 11: Extract Inline Styles from Admin Templates

**Files:**
- Modify: ~26 template files (see complete list in spec)
- Modify: `auto_a11y/web/static/css/style.css` (add new utility classes)

This task covers ALL admin templates with inline color styles. Work through them in batches.

- [ ] **Step 1: Create CSS utility classes for common inline patterns**

Add to `style.css` a section of utility classes that replace the inline styles. Common patterns:

```css
/* Severity badge/text colors (replacing inline styles) */
.text-severity-high { color: var(--color-severity-high); }
.text-severity-medium { color: var(--color-severity-medium); }
.text-severity-pass { color: var(--color-severity-pass); }
.text-info-custom { color: var(--color-info); }
.text-discovery { color: var(--color-discovery); }

.bg-severity-high-subtle { background-color: var(--color-severity-high-bg); }
.bg-severity-medium-subtle { background-color: var(--color-severity-medium-bg); }
.bg-severity-pass-subtle { background-color: var(--color-severity-pass-bg); }
.bg-info-subtle { background-color: var(--color-info-bg); }
.bg-discovery-subtle { background-color: var(--color-discovery-bg); }

.border-subtle { border-color: var(--color-border); }
.border-table { border-color: var(--color-border-table); }
```

- [ ] **Step 2: Process simple template fixes (border-only inline styles)**

These templates only have `border-color` inline styles — straightforward replacements:

- `templates/website_users/list.html` — `#ddd` → class `border-subtle`
- `templates/schedules/list.html` — `#ddd` → class `border-subtle`
- `templates/schedules/dashboard.html` — `#ddd` → class `border-subtle`
- `templates/recordings/detail.html` — `#dee2e6` → class `border-table`
- `templates/recordings/upload.html` — `#dee2e6` → class `border-table`
- `templates/project_users/list.html` — `#ddd` → class `border-subtle`
- `templates/project_participants/list.html` — `#ddd` → class `border-subtle`
- `templates/discovered_pages/view.html` — `#dee2e6` → class `border-table`
- `templates/scripts/list.html` — `#ddd` → class `border-subtle`

For each: find the `style="..."` attribute, extract the color portion, replace with the appropriate CSS class, remove the `style` attribute if no other styles remain.

- [ ] **Step 3: Commit simple template fixes**

```bash
git add auto_a11y/web/templates/website_users/ auto_a11y/web/templates/schedules/ auto_a11y/web/templates/recordings/ auto_a11y/web/templates/project_users/ auto_a11y/web/templates/project_participants/ auto_a11y/web/templates/discovered_pages/ auto_a11y/web/templates/scripts/ auto_a11y/web/static/css/style.css
git commit -m "refactor: extract inline border colors from simple templates to CSS classes"
```

- [ ] **Step 4: Process dashboard and testing templates**

- `templates/dashboard.html` — `#6f42c1` → class `text-discovery`
- `templates/testing/trends.html` — `#e7f3ff` → class `bg-info-subtle`, `#6f42c1` → class `text-discovery`
- `templates/testing/dashboard.html` — `#fff` → class with `var(--color-bg)`, `#6f42c1` → class `text-discovery`
- `templates/pages/view.html` — Multiple severity colors → use severity utility classes
- `templates/pages/view_enhanced.html` — `#6f42c1` → class `text-discovery`
- `templates/projects/edit.html` — `#0d6efd` → class using `var(--color-brand)`
- `templates/websites/view.html` — `var(--bs-link-color)` → `var(--color-link)`

- [ ] **Step 5: Commit dashboard and testing template fixes**

```bash
git add auto_a11y/web/templates/dashboard.html auto_a11y/web/templates/testing/ auto_a11y/web/templates/pages/ auto_a11y/web/templates/projects/edit.html auto_a11y/web/templates/websites/view.html
git commit -m "refactor: extract inline colors from dashboard/testing/page templates"
```

- [ ] **Step 6: Process static report templates**

These are the most complex — they have many inline severity/gradient colors. For each template:

- `templates/static_report/base.html`
- `templates/static_report/page_detail.html`
- `templates/static_report/dedup_component.html`
- `templates/static_report/dedup_unassigned.html`
- `templates/static_report/dedup_index.html`
- `templates/static_report/comprehensive_report_standalone.html`
- `templates/static_report/recordings_report_standalone.html`
- `templates/static_report/summary.html` — Note: `#996404` maps to `var(--color-severity-medium)` (slight hue change from original, acceptable)
- `templates/static_report/index.html`

Replace inline `background`, `color`, `background: linear-gradient(...)` with CSS classes that use tokens. For gradients:

```css
.severity-header-high {
    background: linear-gradient(135deg, var(--color-severity-high), var(--color-severity-high-gradient-end));
    color: var(--color-text-inverse);
}
```

- [ ] **Step 7: Commit static report template fixes**

```bash
git add auto_a11y/web/templates/static_report/ auto_a11y/web/static/css/style.css
git commit -m "refactor: extract inline colors from static report templates to CSS classes"
```

---

## Task 12: Extract Inline Styles from Demo Site Templates

**Files:**
- Modify: `demo_site/services.html`, `demo_site/services-en.html`
- Modify: `demo_site/login.html`, `demo_site/login-en.html`
- Modify: `demo_site/index.html`, `demo_site/index-en.html`

- [ ] **Step 1: Read each demo site template**

- [ ] **Step 2: Replace structural UI inline colors with CSS classes**

For demo site chrome (nav, footer, forms), replace inline colors with classes that reference tokens. For intentional test issues, leave hardcoded with comments.

- [ ] **Step 3: Commit**

```bash
git add demo_site/
git commit -m "refactor: extract inline colors from demo site templates"
```

---

## Task 13: Update Static Report Generator for Token Inlining

**Files:**
- Modify: `auto_a11y/reporting/static_html_generator.py`
- Modify: `auto_a11y/web/templates/static_report/base.html`

- [ ] **Step 1: Read static_html_generator.py**

Focus on `_read_embedded_assets()` (around line 704) and `_copy_assets()` methods.

- [ ] **Step 2: Add tokens.css to embedded assets for standalone reports**

In `_read_embedded_assets()`, add reading of `tokens.css`:

```python
tokens_css_path = static_dir / 'public' / 'css' / 'tokens.css'
tokens_css = tokens_css_path.read_text(encoding='utf-8')
```

Pass `tokens_css` to the template context so standalone templates can include it in their `<style>` block.

- [ ] **Step 3: Add tokens.css to copied assets for linked reports**

In `_copy_assets()`, add copying of `tokens.css` to the assets directory:

```python
tokens_src = static_dir / 'public' / 'css' / 'tokens.css'
shutil.copy2(tokens_src, css_dir / 'tokens.css')
```

- [ ] **Step 4: Update static_report/base.html to link tokens.css**

Add before the `custom.css` link:

```html
<link rel="stylesheet" href="{{ asset_path }}css/tokens.css">
```

- [ ] **Step 5: Update standalone report templates to inline tokens**

In each standalone template that uses `{{ bootstrap_css|safe }}`, add `{{ tokens_css|safe }}` in the same `<style>` block.

- [ ] **Step 6: Commit**

```bash
git add auto_a11y/reporting/static_html_generator.py auto_a11y/web/templates/static_report/
git commit -m "feat: include design tokens in static report generation"
```

---

## Task 14: Final Verification

- [ ] **Step 1: Search entire codebase for remaining hardcoded colors**

Run a search across all CSS files for hex codes, rgb values, and named colors:

```bash
grep -rn '#[0-9a-fA-F]\{3,8\}' auto_a11y/web/static/css/ auto_a11y/web/static/public/css/ demo_site/css/
grep -rn 'rgb\|rgba' auto_a11y/web/static/css/ auto_a11y/web/static/public/css/ demo_site/css/
```

The ONLY allowed exceptions:
- RGB triplets inside `:root` Bootstrap re-pointing blocks
- `transparent`, `inherit`, `currentColor` (CSS keywords)
- Demo site intentional test issues (must have comment)
- The `:root` token definitions themselves in tokens.css

- [ ] **Step 2: Search all templates for remaining inline color styles**

```bash
grep -rn 'style=.*\(color\|background\|border.*#\|border.*rgb\)' auto_a11y/web/templates/ demo_site/
```

Must return zero results (except demo site intentional issues).

- [ ] **Step 3: Test light mode**

- Run the app: `.venv/bin/python run.py --debug`
- Visit each major page: dashboard, projects, pages, testing, reports, help
- Verify all colors render correctly
- Check browser console for errors

- [ ] **Step 4: Test dark mode via OS preference**

- Set OS to dark mode
- Reload the app
- Verify all pages render with dark colors
- Check contrast of all text is readable
- Verify severity colors are distinguishable

- [ ] **Step 5: Test dark mode via manual toggle**

- Set OS back to light mode
- Use the toggle to switch to dark
- Verify dark mode applies
- Refresh — verify dark mode persists
- Toggle to light — verify light mode
- Toggle to auto — verify follows OS

- [ ] **Step 6: Test print output**

- In dark mode, open print preview (Ctrl+P)
- Verify print uses light mode colors (black text on white)

- [ ] **Step 7: Test static report generation**

- Generate a static report via the web UI
- Open the HTML file directly (not through the server)
- Verify tokens load correctly
- Verify dark mode works if OS is set to dark

- [ ] **Step 8: Test public frontend**

- Navigate to a public share token URL
- Verify tokens apply correctly
- Verify toggle works
- Test dark mode

- [ ] **Step 9: Test focus indicators**

- Tab through all major interactive elements (links, buttons, form inputs, nav items, dropdowns) in both light and dark mode
- Verify focus ring is `2px solid`, `2px offset`, and clearly visible against both backgrounds
- Check that no elements still use the old `3px solid` focus style

- [ ] **Step 10: Test high contrast mode**

- Enable `prefers-contrast: more` in browser devtools (or OS settings)
- Verify all borders and text remain visible
- Verify no raw color values override tokens in high contrast

- [ ] **Step 11: Test demo site**

- Visit the demo site
- Verify structural UI (nav, footer, cookie banner) responds to dark mode toggle/OS preference
- Verify intentional test issues (fake headings, low-contrast text) remain unchanged as hardcoded values

- [ ] **Step 12: Delete backup files**

Remove any `.backup` files found during the process (e.g., `templates/pages/view.html.backup`) if they are no longer needed.

- [ ] **Step 13: Commit any final fixes**

```bash
git add -A
git commit -m "fix: address remaining issues from final verification"
```
