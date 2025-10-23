# Static HTML Report Design

## Overview

A downloadable, multi-page static website that replicates the online page testing experience. The report can be viewed offline, shared with stakeholders, and archived for compliance documentation.

## Requirements

### Must Have
1. **Multi-page structure** - Separate HTML files to handle large reports
2. **Navigation** - Index page with links to all test result pages
3. **Filters** - Client-side filtering by touchpoint, impact, issue type
4. **Scores & Summaries** - Accessibility scores, issue counts, WCAG compliance
5. **Full issue details** - Same accordion structure as online view
6. **Responsive design** - Works on mobile, tablet, desktop
7. **Self-contained** - All CSS, JS, images embedded or included
8. **ZIP packaging** - Single downloadable archive
9. **No server required** - Pure static HTML/CSS/JS

### Nice to Have
1. **Search functionality** - Find specific issues or pages
2. **Export options** - Print-friendly CSS, PDF generation
3. **Comparison view** - Compare multiple test runs
4. **Dark mode** - User preference toggle

---

## Architecture

### Directory Structure

```
static_report_YYYYMMDD_HHMMSS/
├── index.html                    # Main landing page with overview
├── summary.html                  # Executive summary with scores
├── pages/
│   ├── page_001.html            # Individual page results
│   ├── page_002.html
│   └── ...
├── assets/
│   ├── css/
│   │   ├── bootstrap.min.css    # Bootstrap 5
│   │   ├── bootstrap-icons.css  # Icons
│   │   └── custom.css           # Custom styles
│   ├── js/
│   │   ├── bootstrap.bundle.js  # Bootstrap with Popper
│   │   ├── filters.js           # Client-side filtering
│   │   ├── navigation.js        # Navigation helpers
│   │   └── search.js            # Search functionality
│   └── images/
│       └── screenshots/         # Page screenshots
└── data/
    └── manifest.json            # Metadata about the report
```

### Page Types

#### 1. Index Page (`index.html`)
**Purpose:** Entry point, navigation hub

**Features:**
- Project/website information
- Test run metadata (date, WCAG level, touchpoints tested)
- Summary statistics (total issues, pages tested, compliance %)
- List of all tested pages with:
  - Page title and URL
  - Issue counts by type (errors, warnings, info)
  - Accessibility score
  - Link to detailed results
- Filters: Search by URL, filter by status
- Quick stats cards

**Layout:**
```
┌──────────────────────────────────────────┐
│  Project: Example Website                │
│  Test Date: 2024-10-22  WCAG: AA        │
├──────────────────────────────────────────┤
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐    │
│  │ 45  │  │ 12  │  │ 150 │  │ 85% │    │
│  │Pages│  │Errs │  │Warns│  │Score│    │
│  └─────┘  └─────┘  └─────┘  └─────┘    │
├──────────────────────────────────────────┤
│  [Search box] [Filter dropdown]         │
├──────────────────────────────────────────┤
│  Page List:                              │
│  ┌────────────────────────────────────┐ │
│  │ Homepage (/)            [View] →   │ │
│  │ 3 errors, 8 warnings    Score: 82% │ │
│  ├────────────────────────────────────┤ │
│  │ About (/about)          [View] →   │ │
│  │ 1 error, 5 warnings     Score: 91% │ │
│  └────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

#### 2. Summary Page (`summary.html`)
**Purpose:** Executive overview for stakeholders

**Features:**
- Overall accessibility score
- WCAG compliance status (A, AA, AAA)
- Issue distribution by:
  - Type (errors, warnings, info)
  - Touchpoint
  - Impact level
  - WCAG criterion
- Top issues across all pages
- Recommendations prioritized by impact
- Charts/visualizations (HTML canvas or SVG)
- Printable format

#### 3. Page Detail (`pages/page_NNN.html`)
**Purpose:** Detailed test results for a single page

**Features:**
- **Exact replica of online view** from `templates/pages/view.html`
- Page information (URL, title, test date)
- Screenshot thumbnail
- Summary cards (errors, warnings, info, discovery counts)
- Latest Test Results section:
  - Grouped by issue type (errors → warnings → info → discovery)
  - Grouped by touchpoint (alphabetical)
  - Grouped by error code (outer accordion)
  - Individual instances (inner accordion)
  - Full issue details with:
    - What/Why/Who/How to remediate
    - WCAG criteria with links
    - Code snippets
    - XPath with copy button
- Client-side filters:
  - By touchpoint
  - By impact level
  - By WCAG criterion
- Navigation:
  - Back to index
  - Previous/Next page
  - Jump to specific page

---

## Data Flow

### Generation Process

1. **User initiates report**
   - From UI: Project view, Website view, or Pages list
   - Selects pages to include (all, filtered, or specific)
   - Chooses report options (WCAG level, touchpoints)

2. **Generator collects data**
   - Fetch test results for selected pages
   - Fetch screenshots
   - Calculate summary statistics
   - Aggregate issue data

3. **Generate HTML files**
   - Create index.html with page list
   - Create summary.html with statistics
   - Create page detail files (pages/page_NNN.html)
   - Copy/embed assets (CSS, JS, images)
   - Generate manifest.json

4. **Package as ZIP**
   - Create ZIP archive
   - Store in reports directory
   - Return download URL

5. **User downloads**
   - Download ZIP file
   - Extract locally
   - Open index.html in browser

### Template Rendering

Use Jinja2 templates, similar to online views:
- Base template with common header/footer
- Page-specific content blocks
- Reuse existing template structure where possible

---

## Technical Implementation

### Backend (Python)

#### New Module: `auto_a11y/reporting/static_html_generator.py`

```python
class StaticHTMLReportGenerator:
    """Generates multi-page static HTML reports"""

    def __init__(self, database, config):
        self.db = database
        self.config = config
        self.template_env = self._setup_templates()

    def generate_report(self, page_ids, options) -> Path:
        """
        Generate complete static HTML report

        Returns:
            Path to generated ZIP file
        """
        # 1. Create temporary directory
        # 2. Generate all HTML files
        # 3. Copy assets
        # 4. Create manifest
        # 5. ZIP everything
        # 6. Clean up temp directory
        # 7. Return ZIP path

    def _generate_index(self, pages, stats):
        """Generate index.html"""

    def _generate_summary(self, pages, stats):
        """Generate summary.html"""

    def _generate_page_detail(self, page, test_result):
        """Generate individual page detail HTML"""

    def _copy_assets(self, dest_dir):
        """Copy CSS, JS, fonts, images"""

    def _create_manifest(self, pages, options):
        """Create manifest.json with metadata"""

    def _package_as_zip(self, source_dir) -> Path:
        """ZIP the report directory"""
```

#### Integration Points

1. **Report Generator** (`auto_a11y/reporting/report_generator.py`)
   - Add `generate_static_html_report()` method
   - Add format='static_html' option

2. **Web Routes** (`auto_a11y/web/routes/reports.py`)
   - Add endpoint: `/api/v1/reports/static-html`
   - Accept POST with page_ids and options
   - Return download URL

3. **UI** (add to project/website views)
   - "Generate Offline Report" button
   - Modal for options selection
   - Progress indicator
   - Download link when ready

### Frontend (JavaScript)

#### Client-Side Filtering (`assets/js/filters.js`)

```javascript
class IssueFilter {
    constructor() {
        this.filters = {
            touchpoint: 'all',
            impact: 'all',
            type: 'all',
            wcag: 'all'
        };
    }

    applyFilters() {
        // Show/hide issues based on current filters
        // Update counts
        // Persist to localStorage
    }

    resetFilters() {
        // Reset to defaults
    }
}
```

#### Search (`assets/js/search.js`)

```javascript
class ReportSearch {
    search(query) {
        // Search across:
        // - Issue descriptions
        // - XPaths
        // - Code snippets
        // - WCAG criteria
    }

    highlightResults() {
        // Highlight matching text
    }
}
```

#### Navigation (`assets/js/navigation.js`)

```javascript
class ReportNav {
    goToPage(pageNum) {
        // Navigate to specific page
    }

    nextPage() {
        // Go to next page in sequence
    }

    prevPage() {
        // Go to previous page
    }
}
```

### Templates

#### Base Template (`templates/static_report/base.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Accessibility Report{% endblock %}</title>

    <!-- Embedded CSS -->
    <link rel="stylesheet" href="../assets/css/bootstrap.min.css">
    <link rel="stylesheet" href="../assets/css/bootstrap-icons.css">
    <link rel="stylesheet" href="../assets/css/custom.css">

    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="../index.html">
                Accessibility Report
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="../index.html">Index</a>
                <a class="nav-link" href="../summary.html">Summary</a>
            </div>
        </div>
    </nav>

    <main class="container-fluid py-4">
        {% block content %}{% endblock %}
    </main>

    <footer class="footer mt-auto py-3 bg-light">
        <div class="container text-center">
            <span class="text-muted">
                Generated by Auto A11y on {{ generation_date }}
            </span>
        </div>
    </footer>

    <!-- Embedded JS -->
    <script src="../assets/js/bootstrap.bundle.js"></script>
    <script src="../assets/js/filters.js"></script>
    <script src="../assets/js/navigation.js"></script>
    <script src="../assets/js/search.js"></script>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### Index Template (`templates/static_report/index.html`)

Extends base, shows page list with filtering/search.

#### Summary Template (`templates/static_report/summary.html`)

Extends base, shows statistics and charts.

#### Page Detail Template (`templates/static_report/page_detail.html`)

Extends base, reuses structure from `templates/pages/view.html` but:
- Removes server-side links (no Flask url_for)
- Uses relative paths for navigation
- Embeds all data (no AJAX calls)
- Includes inline filtering JS

---

## Asset Management

### CSS

**Option 1: Embed Inline**
- Pros: Single file, no external dependencies
- Cons: Larger file size, not cacheable

**Option 2: Include as Files**
- Pros: Cacheable, cleaner HTML
- Cons: Multiple files, relative paths

**Recommendation:** Include as files in `assets/css/`

### JavaScript

**Same considerations as CSS**

**Recommendation:** Include as files, use vanilla JS or minimal dependencies

### Images/Screenshots

- Store in `assets/images/screenshots/`
- Use relative paths: `../assets/images/screenshots/page_001.png`
- Optimize size (compress, resize to max width)
- Lazy load for performance

### Fonts

- Embed Bootstrap Icons as font files
- Include in `assets/fonts/`

---

## Manifest File (`data/manifest.json`)

```json
{
    "report_id": "unique-id",
    "generated_at": "2024-10-22T10:30:00Z",
    "generator_version": "1.0.0",
    "project": {
        "id": "project-id",
        "name": "Example Website",
        "url": "https://example.com"
    },
    "test_config": {
        "wcag_level": "AA",
        "touchpoints_tested": ["headings", "images", "forms", "..."],
        "ai_tests_enabled": true
    },
    "statistics": {
        "total_pages": 45,
        "pages_tested": 45,
        "total_issues": 234,
        "errors": 12,
        "warnings": 150,
        "info": 72,
        "discovery": 45,
        "average_score": 85.3
    },
    "pages": [
        {
            "id": "page-id",
            "title": "Homepage",
            "url": "https://example.com/",
            "file": "pages/page_001.html",
            "score": 82,
            "issues": {
                "errors": 3,
                "warnings": 8,
                "info": 5,
                "discovery": 2
            }
        }
    ]
}
```

---

## User Interface Flow

### Generating Report

1. User navigates to Project or Website view
2. Clicks "Generate Offline Report" button
3. Modal opens with options:
   - Select pages (all, filtered, specific)
   - WCAG level
   - Include screenshots (yes/no)
   - Include discovery items (yes/no)
4. User clicks "Generate"
5. Progress bar shows generation status
6. When complete, "Download Report" button appears
7. User downloads ZIP file
8. User extracts and opens `index.html`

### Viewing Report

1. Open `index.html` in any modern browser
2. Browse pages from index
3. Click page to view details
4. Use filters to focus on specific issues
5. Search for specific problems
6. Navigate between pages
7. Print or share as needed

---

## Performance Considerations

### File Size

- Limit pages per report (e.g., max 500 pages)
- Compress images (80% quality JPG)
- Minify CSS/JS
- Consider pagination for very large reports

### Generation Time

- Async/background job for large reports
- Progress updates via WebSocket
- Queue system for multiple concurrent requests
- Cache templates

### Browser Performance

- Lazy load screenshots
- Virtual scrolling for long issue lists
- Debounce search/filter inputs
- Use CSS containment for accordion items

---

## Security Considerations

1. **Sanitize all user input** - URLs, page titles, descriptions
2. **Escape HTML** in code snippets
3. **No inline event handlers** - Use addEventListener
4. **Content Security Policy** - Add CSP meta tag
5. **No external dependencies** - Everything self-contained

---

## Testing Strategy

### Unit Tests

- Test report generation with mock data
- Test ZIP packaging
- Test template rendering

### Integration Tests

- Generate report for sample project
- Verify all files created
- Check ZIP structure
- Validate HTML syntax

### Manual Tests

- Open in different browsers (Chrome, Firefox, Safari, Edge)
- Test on mobile devices
- Verify filters work
- Test search functionality
- Check print stylesheet
- Verify accessibility of report itself!

---

## Future Enhancements

1. **Comparison Reports** - Compare two test runs
2. **Trend Charts** - Show issue trends over time
3. **Custom Branding** - Logo, colors, company name
4. **Multiple Languages** - i18n support
5. **Accessibility Statement Generator** - Auto-generate compliance statement
6. **Issue Export** - Export issues to CSV, JIRA, GitHub Issues
7. **Interactive Charts** - Use Chart.js for visualizations
8. **PDF Generation** - Convert HTML to PDF with working links

---

## Implementation Plan

### Phase 1: Core Functionality
- [ ] Create static HTML generator class
- [ ] Design base template
- [ ] Implement index page generation
- [ ] Implement page detail generation
- [ ] Basic filtering (client-side)
- [ ] ZIP packaging
- [ ] Web API endpoint

### Phase 2: Enhanced Features
- [ ] Summary page with statistics
- [ ] Search functionality
- [ ] Navigation helpers
- [ ] Screenshot optimization
- [ ] Progress tracking

### Phase 3: Polish
- [ ] Print stylesheet
- [ ] Mobile optimization
- [ ] Performance optimization
- [ ] Documentation
- [ ] User guide (included in report)

---

## Success Criteria

1. ✅ Report opens in any browser without server
2. ✅ All issue details visible and formatted correctly
3. ✅ Filters and search work client-side
4. ✅ Navigation between pages is smooth
5. ✅ File size reasonable (< 50MB for 100 pages)
6. ✅ Generation completes in < 30 seconds for 50 pages
7. ✅ Report itself passes accessibility tests
8. ✅ Shareable and archivable for compliance

---

## Related Documentation

- [LATEST_TEST_RESULTS_UI.md](./LATEST_TEST_RESULTS_UI.md) - Online view structure
- [GENERIC_DESCRIPTIONS_GUIDE.md](./GENERIC_DESCRIPTIONS_GUIDE.md) - Issue descriptions
- [API_DESIGN.md](./API_DESIGN.md) - API integration
