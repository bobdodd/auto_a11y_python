# Discovery Report Feature

## Overview

A new report type has been added to Auto A11y Python that focuses specifically on identifying pages requiring manual accessibility inspection. This report highlights content that needs human review beyond automated testing.

## What It Does

The Discovery Report identifies and lists pages with:

1. **Discovery (Disco) Issues** - Content that requires manual review and human judgment
2. **Informational (Info) Issues** - Important notices about page content
3. **Accessible Names Touchpoint Issues** - Problems with forms, links, buttons, and other interactive elements that may have poor or missing accessible names

## Key Features

### Report Content

- **Executive Summary**: Overall statistics showing how many pages need inspection
- **Statistics Dashboard**:
  - Total pages needing inspection
  - Total Discovery issues
  - Total Info items
  - Total Accessible Name issues
- **Issue Breakdown by Type**: Top issues organized by category
- **Page-by-Page Listing**: Detailed view of each page requiring inspection, including:
  - Page title and URL
  - Issue summary
  - Detailed issue descriptions
  - "Why it matters" explanations
  - "How to fix" guidance

### Report Formats

- **HTML** (Recommended): Interactive, styled report with easy navigation
- **PDF**: Print-ready format for distribution

### Report Scope

- **Website Level**: Generate report for a single website
- **Project Level**: Generate report covering all websites in a project

## Files Created/Modified

### New Files

1. **`auto_a11y/reporting/discovery_report.py`**
   - Core report generation class: `DiscoveryReportGenerator`
   - Data collection and aggregation logic
   - HTML and PDF formatters
   - Professional styling with clear visual hierarchy

### Modified Files

1. **`auto_a11y/web/routes/reports.py`**
   - Added import for `DiscoveryReportGenerator`
   - Added route: `/reports/generate/discovery/website/<website_id>`
   - Added route: `/reports/generate/discovery/project/<project_id>`

2. **`auto_a11y/web/templates/reports/dashboard.html`**
   - Added "Discovery Report" card to dashboard
   - Changed layout from 2 columns to 3 columns
   - Added modal dialog for report generation
   - Added JavaScript functions for modal interaction

## How to Use

### From the Web Interface

1. Navigate to the **Reports Dashboard** (`/reports/dashboard`)
2. Click the **"Generate Inspection Report"** button on the Manual Inspection card
3. In the modal dialog:
   - Select scope (Single Website or Entire Project)
   - Choose a project
   - If "Single Website" is selected, choose a specific website
   - Select format (HTML or PDF)
4. Click **"Generate Inspection Report"**
5. The report will be generated and saved to the server
6. You'll be redirected back to the Reports Dashboard
7. Find your report in the **"Recent Reports"** list (sorted by newest first)
8. Click the download icon to download the report

### Programmatically

```python
from auto_a11y.reporting.discovery_report import DiscoveryReportGenerator

# Initialize generator
generator = DiscoveryReportGenerator(database, config)

# Generate website report
report_path = generator.generate_website_discovery_report(
    website_id='your-website-id',
    format='html'  # or 'pdf'
)

# Generate project report
report_path = generator.generate_project_discovery_report(
    project_id='your-project-id',
    format='html'  # or 'pdf'
)
```

## Report Structure

### HTML Report Sections

1. **Header**
   - Report title
   - Scope information (website or project)
   - Generation timestamp

2. **Executive Summary**
   - Description of report purpose
   - Statistics dashboard with 4 key metrics

3. **Issue Breakdown by Type**
   - Discovery issues (top 10)
   - Informational items (top 10)
   - Accessible Name issues (top 10)
   - Each with count and description

4. **Pages Requiring Manual Inspection**
   - Sorted by total issue count (highest priority first)
   - Each page shows:
     - Page title and clickable URL
     - Issue count summary
     - Discovery issues section
     - Info issues section
     - Accessible Names issues section
   - Each issue includes:
     - Issue ID
     - Description
     - Why it matters
     - How to fix

5. **Footer**
   - Tool information
   - Generation timestamp

## Styling

The report uses a modern, professional design:

- **Color Coding**:
  - Discovery issues: Purple accent
  - Info issues: Blue accent
  - Accessible Names: Orange accent
- **Responsive Layout**: Works on all screen sizes
- **Print-Friendly**: PDF generation supported
- **Accessible**: WCAG-compliant contrast ratios and semantic HTML

## Use Cases

1. **Manual Testing Prioritization**: Identify which pages testers should focus on
2. **Content Review**: Find pages with forms, videos, or complex interactions
3. **Quality Assurance**: Track pages with informational notices
4. **Sprint Planning**: Estimate manual testing effort based on issue counts
5. **Compliance Documentation**: Generate evidence of thorough review process

## Technical Details

### Data Collection

The report generator:
1. Queries all pages in scope (website or project)
2. Retrieves latest test results for each page
3. Filters for Discovery, Info, and Accessible Names touchpoint issues
4. Aggregates statistics by issue type
5. Sorts pages by total issue count (priority order)
6. Enriches issues with catalog information

### Performance Considerations

- Efficiently processes multiple pages in a single pass
- Uses database queries with proper indexing
- Generates reports in-memory before writing to disk
- Suitable for websites with hundreds of pages

### Dependencies

- Python 3.8+
- Existing Auto A11y Python infrastructure
- WeasyPrint (for PDF generation)
  - Install: `pip install weasyprint`
  - Optional: HTML reports work without it

## Future Enhancements

Potential improvements:

1. **Filtering Options**: Allow filtering by specific issue types
2. **Export to CSV**: Add spreadsheet export for issue tracking
3. **Email Distribution**: Automatically send reports to stakeholders
4. **Scheduling**: Generate reports on a regular schedule
5. **Comparison View**: Compare inspection needs across time periods
6. **Priority Scoring**: Add automated priority scoring based on issue severity

## Testing

To test the discovery report:

```bash
# Ensure you have test data
# 1. Create a project
# 2. Add a website
# 3. Discover pages
# 4. Run tests on pages

# Then access the web interface and generate a report
python run.py
# Navigate to http://localhost:5000/reports/dashboard
# Click "Generate Discovery Report"
```

## Support

For questions or issues with the Discovery Report feature, please refer to:
- Main documentation: [README.md](README.md)
- Architecture overview: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Issue tracking: GitHub Issues
