# Quebec Insurance Company Demo Site

A demonstration website for the Quebec insurance company presentation, containing **intentional accessibility issues** to showcase autoA11y's detection capabilities.

## Access the Demo

The demo is served by the autoA11y Flask application:

- **French homepage**: http://127.0.0.1:5001/demo/
- **English homepage**: http://127.0.0.1:5001/demo/index-en.html
- **Services page (FR)**: http://127.0.0.1:5001/demo/services.html
- **Demo information**: http://127.0.0.1:5001/demo/info

## Intentional Accessibility Issues

### 1. **ErrMissingAccessibleName**
- **Location**: Toolbar icon buttons (first button in toolbar)
- **Issue**: Icon-only button without aria-label or accessible text
- **WCAG**: 4.1.2 Name, Role, Value (Level A)

### 2. **ErrTimersWithoutControls**
- **Location**: Hero carousel at top of page
- **Issue**: Auto-playing carousel with no pause/stop/hide controls
- **WCAG**: 2.2.2 Pause, Stop, Hide (Level A)

### 3. **ErrDocumentLinkWrongLanguage**
- **Location**: French page linking to `guide-services-en.pdf`
- **Issue**: French page links to English PDF without language warning
- **WCAG**: 3.1.2 Language of Parts (Level AA)

### 4. **WarnInfiniteAnimationSpinner**
- **Location**: Loading section with spinner
- **Issue**: Spinner with `aria-hidden="true"`, no screen reader announcement
- **WCAG**: 4.1.3 Status Messages (Level AA)

### 5. **Interactive Map with aria-hidden**

- **Location**: Google Maps iframe section
- **Issue**: Interactive elements hidden with `aria-hidden="true"` but still keyboard focusable
- **WCAG**: 4.1.2 Name, Role, Value (Level A)

### 6. **Language Switcher Accessibility**

- **Location**: End of navigation menu
- **Issue**: Language switcher is at the end of a long navigation menu, requiring many tabs to reach
- **WCAG**: 2.4.3 Focus Order (Level A)
- **Note**: Users must tab through all menu items before reaching language options

### 7. **Fake Headings (AI Detection)**
- **Location**: Throughout pages (`.fake-heading` class)
- **Issue**: Visual headings styled with divs instead of proper `<h2>`, `<h3>` elements
- **Detection**: AI test for semantic structure

### 8. **Mixed Language Content (AI Detection)**
- **Location**: French pages with unmarked English phrases
- **Examples**:
  - "We're committed to digital excellence"
  - "online and manage your account"
  - "government programs designed to serve"
- **Issue**: English text on French pages without `lang="en"` attributes
- **WCAG**: 3.1.2 Language of Parts (Level AA)
- **Detection**: AI test for dominant language

### 9. **Color Contrast Issues (Desktop Only)**
- **Location**: Desktop sidebar (`.desktop-only-sidebar`)
- **Issue**: Links with insufficient contrast (#999 on #ddd, #aaa on #e5e5e5)
- **WCAG**: 1.4.3 Contrast (Minimum) (Level AA)
- **Note**: Only visible at desktop breakpoint (>769px)

## Responsive Design

The site includes:
- **Mobile breakpoint**: < 768px (sidebar hidden)
- **Desktop breakpoint**: > 769px (sidebar visible with contrast issues)

This demonstrates the importance of testing at multiple breakpoints.

## Pages

### index.html (French)

- Visually hidden H1: "Bienvenue à Assurance Québec Plus"
- Hero carousel with auto-play (h2 headings in captions)
- Service cards with mixed language content
- Interactive map with aria-hidden
- Loading spinner
- Toolbar with missing accessible names
- Desktop sidebar with contrast issues

### index-en.html (English)

- English version of homepage
- Same accessibility issues as French version
- Visually hidden H1: "Welcome to Quebec Insurance Plus"

### services.html (French)

- Proper H1: "Catalogue de Produits d'Assurance"
- Services catalog page
- Additional examples of:
  - Fake headings (using divs, not semantic h2/h3)
  - Mixed language content
  - Icon buttons without labels
  - Link to English PDF without warning

### services-en.html (English)

- Proper H1: "Insurance Products Catalog"
- English version of services page
- Same accessibility issues as French version

## Testing with autoA11y

1. **Add as Website**: Create a new project and add `http://127.0.0.1:5001/demo/` as a website
2. **Scan Pages**: Add and scan all three pages (index.html, index-en.html, services.html)
3. **Run AI Tests**: Ensure AI tests are enabled for:
   - Dominant language detection
   - Semantic structure analysis (fake headings)
4. **Test Multiple Breakpoints**: Scan at both mobile and desktop widths to catch the contrast issues

## Expected Results

AutoA11y should detect:
- 10+ distinct accessibility issue types
- Mixed language content on French pages
- Fake headings that look like h2/h3 but aren't
- Desktop-only contrast violations
- All standard WCAG violations

## Files Structure

```
demo_site/
├── index.html          # French homepage
├── index-en.html       # English homepage
├── services.html       # Services page (French)
├── css/
│   └── styles.css      # Responsive styles with issues
├── js/
│   ├── carousel.js     # Auto-playing carousel
│   └── spinner.js      # Infinite spinner
├── images/
│   └── (placeholder images)
└── pdfs/
    └── (placeholder PDFs)
```

## Notes for Presentation

This demo is designed to showcase:
1. **Standard automated testing** (contrast, missing labels, semantic issues)
2. **AI-powered detection** (mixed languages, fake headings)
3. **Responsive design testing** (desktop-only issues)
4. **Quebec-specific concerns** (bilingual content, language switching)

The issues are realistic and represent common problems in insurance company websites.

## Accessibility Features (Good Practices)

While the demo site contains intentional accessibility issues, it also demonstrates proper accessibility features:

### Skip to Main Content Link

- **Location**: First element after `<body>` tag on all pages
- **Behavior**: Hidden off-screen until focused (keyboard users press Tab)
- **Target**: Jumps directly to the H1 heading (`#main-content`)
- **tabindex="-1"**: Allows H1 to receive programmatic focus (prevents screen reader from staying on link)
- **Text**: 
  - French: "Aller au contenu principal"
  - English: "Skip to main content"
- **WCAG**: 2.4.1 Bypass Blocks (Level A)

### Proper Heading Hierarchy

- **H1**: Visually hidden on homepages, visible on services pages
- **ID**: All H1 elements have `id="main-content"` for skip link target
- **Structure**: H1 → H2 → H3 (with intentional fake headings for demo)

### Visually Hidden Content

- `.visually-hidden` class used for screen-reader-only content
- Positioned absolutely, clipped to 1px × 1px
- Accessible to assistive technology but invisible visually
