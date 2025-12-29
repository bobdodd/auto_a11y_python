# Demo Site Setup - Quebec Insurance Company Presentation

## Overview

I've created a complete bilingual demo website with intentional accessibility issues for your Quebec insurance company presentation. The demo showcases autoA11y's ability to detect both standard and AI-powered accessibility issues.

## Setup Complete ✓

### Files Created

**Demo Site Structure:**
```
demo_site/
├── README.md                   # Complete documentation
├── index.html                  # French homepage (with issues)
├── index-en.html               # English homepage
├── services.html               # French services page
├── css/
│   └── styles.css             # Responsive CSS with contrast issues
├── js/
│   ├── carousel.js            # Auto-playing carousel (no controls)
│   └── spinner.js             # Infinite spinner (no SR announcement)
├── images/                    # Placeholder for images
└── pdfs/                      # Placeholder for PDF links
```

**Backend Integration:**
- `auto_a11y/web/routes/demo.py` - Flask blueprint to serve demo
- `auto_a11y/web/app.py` - Updated to register demo blueprint

## Next Steps

### 1. Restart the autoA11y Server

The server needs to be restarted to load the new demo blueprint:

```bash
# Stop the current server (Ctrl+C in the terminal where it's running)
# Then restart:
cd /Users/bob3/Desktop/auto_a11y_python
source venv/bin/activate
python run.py
```

### 2. Access the Demo

Once restarted, access:
- **Demo info**: http://127.0.0.1:5001/demo/info
- **French homepage**: http://127.0.0.1:5001/demo/
- **English homepage**: http://127.0.0.1:5001/demo/index-en.html
- **Services page**: http://127.0.0.1:5001/demo/services.html

### 3. Test with autoA11y

1. **Create a new project** in autoA11y (or use existing)
2. **Add website**: `http://127.0.0.1:5001/demo/`
3. **Add pages to scan**:
   - `http://127.0.0.1:5001/demo/` (French homepage)
   - `http://127.0.0.1:5001/demo/index-en.html` (English)
   - `http://127.0.0.1:5001/demo/services.html` (Services)
4. **Run automated tests** on all pages
5. **Test at multiple breakpoints** (mobile and desktop) to catch responsive issues

## Intentional Issues Included

### Standard Automated Tests

1. **ErrMissingAccessibleName** - Icon button without label (toolbar)
2. **ErrTimersWithoutControls** - Auto-playing carousel without pause button
3. **ErrDocumentLinkWrongLanguage** - English PDF linked from French page
4. **WarnInfiniteAnimationSpinner** - Loading spinner with aria-hidden
5. **ErrInappropriateMenuRole** - Navigation using wrong ARIA role
6. **Interactive map with aria-hidden** - Focusable elements hidden from screen readers
7. **Language switcher buried** - tabindex="99" makes it hard to reach
8. **Color contrast issues** - Desktop sidebar (#999 on #ddd, #aaa on #e5e5e5)

### AI Detection Tests

9. **Fake headings** - Styled divs instead of semantic h2, h3 elements
10. **Mixed language content** - English phrases on French pages without lang attributes

### Examples of Mixed Language (for AI detection):
- "We're committed to digital excellence" (on French page)
- "online and manage your account" (mixed in French text)
- "government programs designed to serve" (no lang attribute)

## Presentation Points

### For Quebec Government:

1. **Bilingual Support** ✓
   - Proper French/English dual-language site
   - Language switcher (though poorly implemented for demo)
   - Detects missing lang attributes on mixed content

2. **AI-Powered Detection** ✓
   - Detects non-dominant language text without proper markup
   - Identifies fake headings (styled text that looks like headings)
   - Critical for Quebec: catches poorly translated pages

3. **Responsive Testing** ✓
   - Desktop-only content with accessibility issues
   - Demonstrates importance of multi-breakpoint testing
   - Contrast issues hidden on mobile

4. **Comprehensive Coverage** ✓
   - 10+ distinct issue types
   - Standard WCAG violations
   - Quebec-specific concerns (language switching, bilingual content)

## Demo Workflow for Presentation

1. **Show the demo site** in browser
   - Point out it looks modern and professional
   - Show the language switcher, carousel, services

2. **Add to autoA11y**
   - Create project: "Quebec Government Demo"
   - Add website: http://127.0.0.1:5001/demo/
   - Scan all 3 pages

3. **Review results**
   - Show standard violations detected
   - Highlight AI detection of mixed languages
   - Demonstrate fake headings caught by AI
   - Show desktop-only contrast issues

4. **Generate reports**
   - Use the PowerPoint generation (already created)
   - Show comprehensive WCAG analysis
   - Export to recording report format

## PowerPoint Already Created

You already have the BC Assessment analysis PowerPoint with charts and graphs. You can:
- Use it as a template for the demo results
- Generate a new one after scanning the demo site
- Show the comparison between real site (BC Assessment) and demo

## Optional Enhancements

If you want to add actual images:
- Quebec insurance company logo → `demo_site/images/quebec-logo.svg`
- Hero images → `demo_site/images/hero1.jpg`, `hero2.jpg`, `hero3.jpg`
- Service icons → `demo_site/images/service1.svg`, etc.

If you want actual PDFs:
- Create placeholder PDFs → `demo_site/pdfs/guide-services-en.pdf`
- The links are already set up in the HTML

## Summary

✅ Complete bilingual demo site created
✅ 10+ intentional accessibility issues included
✅ AI tests for language mixing and fake headings
✅ Responsive design with breakpoint-specific issues
✅ Flask route integrated (needs server restart)
✅ Full documentation provided

**Next Action**: Restart the autoA11y server to activate the demo site!
