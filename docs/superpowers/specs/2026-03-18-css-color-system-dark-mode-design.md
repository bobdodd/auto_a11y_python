# CSS Color System Refactoring & Dark Mode Design

**Date:** 2026-03-18
**Status:** Draft

## Overview

Refactor all CSS color usage across the entire codebase (admin interface, public frontend, help system, mobile styles, demo site) to use semantic CSS custom properties (variables) named by use case. Add a WCAG 2.2 AA-compliant dark color scheme activated by OS preference with a manual override toggle.

## Key Constraints

1. **Zero inline color styles** — all color values in CSS files only, never in HTML `style` attributes
2. **Zero raw color values in CSS rules** — every color property uses `var(--token-name)`
3. **Every token has both light and dark values** — no token exists without both modes defined
4. **All text/foreground colors meet WCAG 2.2 AA** (4.5:1 for normal text, 3:1 for large text and UI components)
5. **All non-text UI components (borders, inputs, scrollbars, focus rings) meet 3:1** per SC 1.4.11
6. **Focus indicators: 2px solid, 2px offset** — satisfies SC 2.4.7 and SC 2.4.11
7. **All tokens named by use case** — no color-descriptive or numbered names
8. **Screen reader compatible** — toggle announces state changes via `aria-live`
9. **Print styles force light mode** — `@media print` overrides dark tokens to light values
10. **Minimum browser requirement:** CSS custom properties support (all modern browsers, IE11 excluded)

## Architecture

### Single Semantic Token Layer

One set of CSS custom property names, defined at `:root` for light mode and overridden for dark mode. No primitive/abstract color layer.

### CSS Cascade Order

```css
/* 1. tokens.css loaded BEFORE Bootstrap */
:root { /* light mode defaults — all tokens defined here */ }

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { /* dark when OS prefers, unless manually set to light */ }
}

[data-theme="dark"] { /* manual dark override, always wins */ }

@media print {
  :root { /* force light mode for print regardless of data-theme */ }
}

/* 2. Bootstrap CSS loaded second */
/* 3. Post-Bootstrap overrides: re-point Bootstrap --bs-* variables to our tokens */
/* 4. Component stylesheets (style.css, mobile.css, help-system.css, etc.) */
```

### Bootstrap Integration Strategy

The admin interface uses Bootstrap 5 which defines its own `--bs-*` custom properties. To integrate:

1. `tokens.css` is loaded BEFORE Bootstrap, defining all semantic tokens
2. A post-Bootstrap override section (in `style.css`) re-points Bootstrap variables to our tokens:
   ```css
   :root {
     --bs-primary: var(--color-brand);
     --bs-primary-rgb: 26, 82, 118;  /* light mode: RGB of #1a5276 */
     --bs-info: var(--color-info);
     --bs-info-rgb: 14, 116, 144;    /* light mode: RGB of #0e7490 */
     --bs-success: var(--color-severity-pass);
     --bs-danger: var(--color-severity-high);
     --bs-warning: var(--color-severity-medium);
     --bs-body-color: var(--color-text);
     --bs-body-bg: var(--color-bg);
     --bs-border-color: var(--color-border);
   }
   /* Dark mode overrides for RGB triplets: */
   @media (prefers-color-scheme: dark) {
     :root:not([data-theme="light"]) {
       --bs-primary-rgb: 93, 169, 233;  /* RGB of #5da9e9 */
       --bs-info-rgb: 100, 181, 246;    /* RGB of #64b5f6 */
     }
   }
   [data-theme="dark"] {
     --bs-primary-rgb: 93, 169, 233;
     --bs-info-rgb: 100, 181, 246;
   }
   ```
   Note: Bootstrap uses `--bs-*-rgb` triplets for alpha channel operations like `rgba(var(--bs-primary-rgb), 0.5)`. These must be kept in sync with the corresponding token values.
3. The existing `--primary-color`, `--secondary-color`, `--success-color`, `--danger-color`, `--warning-color`, `--info-color` variables in `style.css` are **removed** and replaced by the new token names.

### Migration from Existing Token Names

The public frontend's existing `tokens.css` variables are renamed:

| Old Name | New Name |
|---|---|
| `--color-primary` | `--color-brand` |
| `--color-primary-light` | `--color-link` (was used for links) |
| `--color-primary-dark` | `--color-brand-hover` |
| `--focus-outline` | Decomposed into `--color-focus-ring` + hardcoded `2px solid` + `outline-offset: 2px` |
| `--focus-offset` | Removed (hardcoded as `2px` per user requirement) |

All references to the old names in `main.css` and any other file are updated to the new names. No backward-compatibility aliases — the old names are fully replaced.

**Focus indicator change:** The existing public frontend uses `3px solid` focus outlines. This changes to `2px solid` with `2px offset` per user requirement. This is a deliberate design change, not a bug.

### Dark Mode Toggle

- **OS detection:** `@media (prefers-color-scheme: dark)` — automatic
- **Manual override:** `data-theme` attribute on `<html>` — `"light"`, `"dark"`, or absent (auto)
- **Persistence:** `localStorage` key `theme-preference` — values `"light"`, `"dark"`, `"auto"`
- **Anti-FOUC script** (inline in `<head>`, before any stylesheet):
  ```javascript
  (function() {
    try {
      var pref = localStorage.getItem('theme-preference');
      if (pref === 'dark' || pref === 'light') {
        document.documentElement.setAttribute('data-theme', pref);
      }
      // If 'auto' or null, no attribute set — CSS media query handles it
    } catch(e) {
      // localStorage unavailable (private browsing, CSP, etc.) — fall back to OS preference
    }
  })();
  ```
- **Toggle UI:** Button in site header, cycles auto -> light -> dark -> auto
  - `aria-label` at each state:
    - Auto: `"Color theme: automatic. Switch to light."`
    - Light: `"Color theme: light. Switch to dark."`
    - Dark: `"Color theme: dark. Switch to automatic."`
  - `aria-live="polite"` region announces: `"Color theme changed to light."` / `"Color theme changed to dark."` / `"Color theme changed to automatic."`
  - Icons are `aria-hidden="true"`:
    - Light state: sun icon (Unicode U+2600 or SVG)
    - Dark state: moon icon (Unicode U+263D or SVG)
    - Auto state: circle half-filled icon (Unicode U+25D0 or SVG) — represents "half light, half dark"

## Token Definitions

### Brand / Primary

| Token | Light Value | Dark Value | Light contrast on #fff | Dark contrast on #1a1a2e |
|---|---|---|---|---|
| `--color-brand` | `#1a5276` | `#5da9e9` | 8.36:1 AAA | 6.76:1 AA |
| `--color-brand-hover` | `#0e2f44` | `#6db3f2` | 13.92:1 AAA | 7.62:1 AAA |
| `--color-brand-subtle` | `#f4f6f7` | `#252542` | N/A (bg) | N/A (bg) |

Note: `--color-brand-subtle` and `--color-bg-subtle` share the same values intentionally. `--color-brand-subtle` is for brand-tinted areas (e.g., highlighted rows), while `--color-bg-subtle` is for general layout offset (sidebars, alternating rows). They may diverge in future themes.

### Text

| Token | Light Value | Dark Value | Light contrast on #fff | Dark contrast on #1a1a2e |
|---|---|---|---|---|
| `--color-text` | `#1c1c1c` | `#e0e0e6` | 17.04:1 AAA | 12.98:1 AAA |
| `--color-text-muted` | `#4a4a4a` | `#8a8a9a` | 8.86:1 AAA | 5.02:1 AA |
| `--color-text-inverse` | `#ffffff` | `#ffffff` | N/A | N/A |

`--color-text-inverse` stays `#ffffff` in both modes. It is used exclusively on colored backgrounds (brand headers, primary buttons, severity badges) where white text is needed regardless of theme. It is NOT the "opposite of body text" — it is "text on colored surfaces." Using it on `--color-bg` would be invisible in light mode.
| `--color-text-heading` | `#1c1c1c` | `#ffffff` | 17.04:1 AAA | 17.06:1 AAA |
| `--color-text-code` | `#dd1144` | `#f28b82` | 4.96:1 AA (also 4.51:1 on #f4f4f4 code bg) | 7.14:1 AAA |

### Links

| Token | Light Value | Dark Value | Light contrast on #fff | Dark contrast on #1a1a2e |
|---|---|---|---|---|
| `--color-link` | `#0a58ca` | `#6db3f2` | 6.44:1 AA | 7.62:1 AAA |
| `--color-link-hover` | `#084298` | `#7ebcfa` | 9.72:1 AAA | 8.50:1 AAA |
| `--color-link-visited` | `#1a5276` | `#5da9e9` | 8.36:1 AAA | 6.76:1 AA |

Note: `--color-link-visited` matches `--color-brand` intentionally — visited links adopt the brand color to avoid cluttered link states while remaining distinct from unvisited links.

### Backgrounds

| Token | Light Value | Dark Value |
|---|---|---|
| `--color-bg` | `#ffffff` | `#1a1a2e` |
| `--color-bg-subtle` | `#f4f6f7` | `#252542` |
| `--color-bg-elevated` | `#ffffff` | `#2d2d4a` |
| `--color-bg-header` | `#1a5276` | `#12122a` |
| `--color-bg-footer` | `#f8f9fa` | `#151530` |

Footer uses `--color-text` for body text and `--color-text-muted` for secondary text. Contrast: `--color-text` (`#e0e0e6`) on `--color-bg-footer` (`#151530`) = 13.72:1 AAA. `--color-text-muted` (`#8a8a9a`) on `#151530` = 5.30:1 AA.
| `--color-bg-code` | `#f4f4f4` | `#252542` |
| `--color-bg-input` | `#ffffff` | `#252542` |
| `--color-bg-scrollbar` | `#f1f1f1` | `#1a1a2e` |
| `--color-bg-overlay` | `rgba(0,0,0,0.5)` | `rgba(0,0,0,0.7)` |

### Borders

All border tokens meet 3:1 against their adjacent backgrounds per SC 1.4.11.

| Token | Light Value | Dark Value | Dark contrast on adjacent bg |
|---|---|---|---|
| `--color-border` | `#d5d8dc` | `#6a6a8c` | 3.14:1 on #1a1a2e (page bg) |
| `--color-border-strong` | `#85929e` | `#7a7a9a` | 4.12:1 on #1a1a2e |
| `--color-border-input` | `#86868b` | `#7a7a9a` | 3.57:1 on #252542 (input bg) |
| `--color-border-input-focus` | `#0a58ca` | `#5da9e9` | — (focus ring, high contrast) |
| `--color-border-table` | `#dee2e6` | `#6a6a8c` | 3.14:1 on #1a1a2e |

### Focus & Interaction

| Token | Light Value | Dark Value |
|---|---|---|
| `--color-focus-ring` | `#0a58ca` | `#6db3f2` |
| `--color-button-primary-bg` | `#1a5276` | `#5da9e9` |
| `--color-button-primary-text` | `#ffffff` | `#0e1525` |
| `--color-button-primary-hover` | `#0e2f44` | `#6db3f2` |
| `--color-scrollbar-thumb` | `#888888` | `#6a6a8a` |

Focus indicators use `outline: 2px solid var(--color-focus-ring); outline-offset: 2px;`

Scrollbar thumb: `#6a6a8a` achieves 3.28:1 on `#1a1a2e` (scrollbar track bg), meeting SC 1.4.11.

### Severity / Status

| Token | Light Value | Dark Value | Light on #fff | Dark on #1a1a2e |
|---|---|---|---|---|
| `--color-severity-high` | `#922b21` | `#f28b82` | 8.11:1 AAA | 7.14:1 AAA |
| `--color-severity-high-bg` | `#fdedec` | `#3d1f1f` | N/A (bg) | N/A (bg) |
| `--color-severity-high-border` | `#922b21` | `#f28b82` | — | 6.22:1 on #3d1f1f bg |
| `--color-severity-medium` | `#7d6608` | `#f9a825` | 5.56:1 AA | 8.66:1 AAA |
| `--color-severity-medium-bg` | `#fff3cd` | `#3d3520` | N/A | N/A |
| `--color-severity-medium-border` | `#b38600` | `#f9a825` | — | 6.16:1 on #3d3520 bg |
| `--color-severity-low` | `#2c3e50` | `#b0b0bc` | 10.98:1 AAA | 7.95:1 AAA |
| `--color-severity-pass` | `#1e8449` | `#81c784` | 4.72:1 AA | 8.48:1 AAA |
| `--color-severity-pass-bg` | `#eafaf1` | `#1f3d2a` | N/A | N/A |
| `--color-severity-pass-border` | `#1e8449` | `#81c784` | — | 5.93:1 on #1f3d2a bg |
| `--color-info` | `#0e7490` | `#64b5f6` | 5.36:1 AA | 7.70:1 AAA |
| `--color-info-bg` | `#d1ecf1` | `#1f2d3d` | N/A | N/A |
| `--color-info-border` | `#0e7490` | `#64b5f6` | — | 6.32:1 on #1f2d3d bg |

Severity tinted backgrounds use a `2px solid` border in the corresponding border token color to ensure alert regions are distinguishable.

### Discovery (new — heavily used in templates)

| Token | Light Value | Dark Value | Light on #fff | Dark on #1a1a2e |
|---|---|---|---|---|
| `--color-discovery` | `#6f42c1` | `#b39ddb` | 6.51:1 AA | 7.12:1 AAA |
| `--color-discovery-bg` | `#f3eefa` | `#2d1f4a` | N/A (bg) | N/A (bg) |
| `--color-discovery-border` | `#6f42c1` | `#b39ddb` | — | 6.23:1 on #2d1f4a bg |
| `--color-discovery-hover` | `#5a32a3` | `#c4b0e0` | — | — |

### Severity Gradient Pairs (for section headers in static reports)

| Token | Light Value | Dark Value |
|---|---|---|
| `--color-severity-high-gradient-end` | `#c82333` | `#d95050` |
| `--color-severity-medium-gradient-end` | `#e0a800` | `#d4a020` |
| `--color-severity-pass-gradient-end` | `#148040` | `#6aab6d` |
| `--color-info-gradient-end` | `#0aa2c0` | `#509dbf` |
| `--color-discovery-gradient-end` | `#5a32a3` | `#9070c0` |

### Shadows

| Token | Light Value | Dark Value |
|---|---|---|
| `--color-shadow-subtle` | `rgba(0,0,0,0.08)` | `rgba(0,0,0,0.3)` |
| `--color-shadow-medium` | `rgba(0,0,0,0.1)` | `rgba(0,0,0,0.4)` |
| `--color-shadow-strong` | `rgba(0,0,0,0.15)` | `rgba(0,0,0,0.5)` |

### Progress / Animation

| Token | Light Value | Dark Value |
|---|---|---|
| `--color-progress-track` | `#e9ecef` | `#3a3a5c` |
| `--color-progress-fill` | `#198754` | `#81c784` |
| `--color-spinner-overlay` | `rgba(255,255,255,0.8)` | `rgba(0,0,0,0.6)` |
| `--color-pulse-ring` | `rgba(25,135,84,0.4)` | `rgba(129,199,132,0.4)` |

### Help System

| Token | Light Value | Dark Value |
|---|---|---|
| `--color-help-icon` | `#3498db` | `#64b5f6` |
| `--color-help-icon-hover` | `#2980b9` | `#6db3f2` |
| `--color-help-heading` | `#2c3e50` | `#e0e0e6` |

### SSO Buttons (brand-mandated)

SSO buttons use brand-mandated colors that do not change between modes. In dark mode, the Google button (white bg) will appear as a bright element against the dark page. This is expected per brand guidelines. The buttons should be placed within a card or container using `--color-bg-elevated` to provide visual integration.

| Token | Value (both modes) |
|---|---|
| `--color-sso-microsoft-bg` | `#2f2f2f` |
| `--color-sso-microsoft-hover` | `#1a1a1a` |
| `--color-sso-google-bg` | `#ffffff` |
| `--color-sso-google-text` | `#3c4043` |
| `--color-sso-google-border` | `#dadce0` |
| `--color-sso-google-hover` | `#f7f8f8` |

### Demo Site

The demo site includes intentional accessibility issues for testing purposes. Token conversion applies to the demo site's structural/chrome UI (navigation, footer, cookie banner) but intentionally inaccessible test elements (fake headings, low-contrast text, missing alt text, etc.) are **left as hardcoded values with comments explaining they are deliberate test cases**. Only the site's surrounding UI gets tokenized.

| Token | Light Value | Dark Value |
|---|---|---|
| `--color-demo-brand` | `#004d99` | `#5da9e9` |
| `--color-demo-brand-hover` | `#003d7a` | `#6db3f2` |
| `--color-demo-cookie-link` | `#aaddff` | `#6db3f2` |

### Additional Utility Tokens

Colors found across CSS files that map to existing tokens or need new ones:

| Hardcoded Value | Where Used | Maps To Token |
|---|---|---|
| `#333` | help-system headings, demo body text | `--color-text` |
| `#555` | help-system body text, scrollbar | `--color-text-muted` |
| `#666` | help-system close btn, secondary text | `--color-text-muted` |
| `#495057` | style.css dt, help-system score heading | `--color-text` |
| `#6c757d` | style.css figcaption, help-system score | `--color-text-muted` |
| `#e0e0e0` | help-system modal borders | `--color-border` |
| `#f0f0f0` | help-system close hover bg, mobile bg | `--color-bg-subtle` |
| `#f9f9f9` | help-system example box bg | `--color-bg-subtle` |
| `#34495e` | help-system h4 | `--color-text-heading` |
| `#dee2e6` | many borders, footer, mobile | `--color-border-table` |
| `#ddd` | template inline borders | `--color-border` |
| `#0d6efd` | Bootstrap blue in templates | `--color-brand` |
| `#e7f3ff` | testing trends bg | `--color-info-bg` |
| `white` / `#fff` | many places | `--color-text-inverse` or `--color-bg` (context-dependent) |
| `#000` | high contrast mode | `--color-text` (in high-contrast context) |

### High Contrast Mode

The existing `@media (prefers-contrast: more)` styles in `style.css` are preserved and updated to reference tokens. High contrast mode is handled as a separate concern from dark mode — it simply forces stronger border values. A full high-contrast theme is out of scope for this phase but the architecture supports adding one later via an additional `[data-theme="high-contrast"]` selector.

## File Changes

### Files to Modify

1. **`auto_a11y/web/static/public/css/tokens.css`** — expand from 13 tokens to full token set with light/dark/print values
2. **`auto_a11y/web/static/css/style.css`** — remove `--primary-color` etc., replace all hardcoded colors with `var()`, add Bootstrap `--bs-*` re-pointing
3. **`auto_a11y/web/static/css/mobile.css`** — replace all hardcoded colors with `var()`
4. **`auto_a11y/web/static/css/help-system.css`** — replace all hardcoded colors with `var()`
5. **`auto_a11y/web/static/public/css/main.css`** — update old token names to new names
6. **`auto_a11y/web/static/public/css/print.css`** — ensure print forces light mode tokens
7. **`demo_site/css/styles.css`** — replace structural UI colors with `var()`, leave intentional test issues as hardcoded
8. **`auto_a11y/web/templates/base.html`** — add anti-FOUC script in `<head>`, include `tokens.css` before Bootstrap, add toggle component in nav

### Templates Requiring Inline Style Removal

All inline `style` attributes containing color values must be extracted to CSS classes. Complete list:

| Template | Colors to Extract |
|---|---|
| `templates/dashboard.html` | `#6f42c1` |
| `templates/pages/view.html` | `#6f42c1`, `#dc3545`, `#ffc107`, `#0e7490`, `#6e6e6e`, `#0dcaf0`, `#f8f9fa`, `#0066cc`, `#17a2b8`, `#fff5f5`, `#fffef5`, `#f0fcff` |
| `templates/pages/view_enhanced.html` | `#6f42c1` |
| `templates/projects/edit.html` | `#0d6efd` |
| `templates/websites/view.html` | `var(--bs-link-color)` |
| `templates/website_users/list.html` | `#ddd` |
| `templates/static_report/base.html` | `#0d6efd`, `white` |
| `templates/static_report/recordings_report_standalone.html` | `#0d6efd`, `white` |
| `templates/static_report/page_detail.html` | `#dc3545`, `#c82333`, `#fff5f5`, `#f8f9fa`, `#ffc107`, `#e0a800`, `#212529`, `#fffbeb`, `#0e7490`, `#0aa2c0`, `#e8f9fd`, `#6f42c1`, `#5a32a3`, `#f3eefa`, `#0dcaf0`, `#6e6e6e`, `#17a2b8`, `#f0fcff` |
| `templates/static_report/scripts/list.html` | `#ddd` |
| `templates/static_report/dedup_component.html` | `#0066cc`, `#f8f9fa`, `#dc3545`, `#c82333`, `#fff5f5`, `#ffc107`, `#e0a800`, `#fffdf5`, `#0e7490`, `#0aa2c0`, `#f5fdff`, `#6f42c1`, `#5a32a3`, `#f8f5ff` |
| `templates/static_report/dedup_unassigned.html` | `#0066cc`, `#6f42c1`, `#dc3545`, `#ffc107`, `#0e7490` |
| `templates/static_report/dedup_index.html` | `#6f42c1` |
| `templates/static_report/comprehensive_report_standalone.html` | `#f8f9fa`, `#28a745`, `#198754`, `#ffc107`, `#dc3545`, `#17a2b8`, `#6f42c1`, `#000`, `#fff`, `#212529`, `#e0a800` |
| `templates/static_report/summary.html` | `#996404` |
| `templates/static_report/index.html` | `#fee`, `#fff3cd`, `#e7f5ff`, `#f0f0f0`, `#d1ecf1` |
| `templates/schedules/list.html` | `#ddd` |
| `templates/schedules/dashboard.html` | `#ddd` |
| `templates/recordings/detail.html` | `#dee2e6` |
| `templates/recordings/upload.html` | `#dee2e6` |
| `templates/project_users/list.html` | `#ddd` |
| `templates/project_participants/list.html` | `#ddd` |
| `templates/discovered_pages/view.html` | `#dee2e6` |
| `templates/testing/trends.html` | `#e7f3ff`, `#6f42c1` |
| `templates/testing/dashboard.html` | `#fff`, `#6f42c1` |

**Demo site templates:**
| Template | Colors to Extract |
|---|---|
| `demo_site/services.html` + `services-en.html` | `#aaa`, `#e5e5e5`, `#999`, `#ddd` |
| `demo_site/login.html` + `login-en.html` | `#999` |
| `demo_site/index.html` + `index-en.html` | `#999`, `#ddd` |

Note: Demo site SVGs (`images/*.svg`) contain hardcoded colors for gradients. These are left as-is since they are image assets, not UI chrome.

### Files to Create

9. **`auto_a11y/web/static/css/theme-toggle.css`** — toggle button styles
10. **`auto_a11y/web/static/js/theme-toggle.js`** — toggle logic, localStorage, aria-live announcements
11. **`auto_a11y/web/templates/components/theme_toggle.html`** — Jinja2 partial for toggle button

### Import Order (every page)

1. `tokens.css` (defines all variables — must be first)
2. Bootstrap CSS
3. Component stylesheets (which include Bootstrap `--bs-*` re-pointing)

### What Will NOT Change

- Python backend logic
- JavaScript test scripts (accessibility tests)
- Fixture HTML files
- Database schema
- SSO button brand colors (mandated by Microsoft/Google)
- Demo site SVG image assets
- Demo site intentionally inaccessible test elements

### Static Report Token Strategy

Static HTML reports are self-contained files that inline all CSS. The report generation code (in `auto_a11y/reporting/`) must inline the token definitions from `tokens.css` into the `<style>` block of each generated report. This ensures static reports support both light and dark modes independently of the web application. The report generator should include the full `:root` (light), `@media (prefers-color-scheme: dark)`, and `@media print` blocks. Static reports do not include the manual toggle (they follow OS preference only).

### CSS Custom Property Fallback Strategy

No fallback values are used in `var()` calls (i.e., we do NOT use `var(--color-text, #1c1c1c)`). Rationale:
- `tokens.css` is loaded first in the cascade and is a hard dependency for all pages
- If `tokens.css` fails to load, the entire UI is broken (not just colors) — adding color fallbacks would mask a loading failure that needs to be caught
- Fallback values create a maintenance burden (two places to update every color)
- Minimum browser requirement (CSS custom properties) is documented and enforced

## WCAG 2.2 Compliance Summary

| Criterion | How Met |
|---|---|
| **1.4.3 Contrast (Minimum) AA** | All text colors verified at 4.5:1+ against their backgrounds in both modes |
| **1.4.6 Contrast (Enhanced) AAA** | Most dark mode text achieves 7:1+ (exception: muted text at 5.02:1) |
| **1.4.11 Non-text Contrast** | All UI component borders/inputs/scrollbar meet 3:1+ (dark borders use #6a6a8c+ for 3.14:1+) |
| **2.4.7 Focus Visible** | 2px solid focus ring, 2px offset, high contrast color |
| **2.4.11 Focus Not Obscured (Minimum)** | 2px offset prevents overlap with element borders |
| **1.4.1 Use of Color** | Severity levels use text labels + icons, not color alone |
| **1.3.1 Info and Relationships** | Theme toggle uses proper ARIA labeling |
