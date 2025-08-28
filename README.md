# Auto A11y Python

A comprehensive web accessibility testing tool that combines automated DOM testing with AI-powered visual analysis. This is a Python port of the original autoA11y.js Node.js application, maintaining the core JavaScript test scripts while adding enhanced features.

## Overview

Auto A11y Python is a comprehensive web accessibility testing platform that:
- Crawls websites to discover pages automatically using Pyppeteer
- Executes battle-tested JavaScript accessibility tests in browser context
- Integrates Claude AI for visual accessibility analysis beyond DOM testing
- Provides project-based organization for managing multiple websites
- Generates detailed WCAG 2.1 compliance reports in multiple formats

## Features

- **Automated Accessibility Testing**: Comprehensive WCAG 2.1 compliance testing using JavaScript test scripts from the original autoA11y.js
- **AI-Powered Visual Analysis**: Optional Claude AI integration detects visual issues that DOM testing might miss
- **Smart Web Scraping**: Automatic page discovery with robots.txt compliance
- **Browser-Based Testing**: Real DOM testing using Pyppeteer (Python port of Puppeteer)
- **Project Management**: Organize testing across multiple projects and websites
- **Comprehensive Reporting**: Generate HTML, JSON, CSV, and PDF reports
- **Asynchronous Processing**: Background task runner for non-blocking operations
- **Web Interface**: Modern Flask application with Bootstrap 5 UI

## Technology Stack

- **Backend**: Python 3.8+
- **Browser Automation**: Pyppeteer (Puppeteer for Python)
- **Database**: MongoDB 4.0+
- **AI Integration**: Claude AI by Anthropic
- **Web Framework**: Flask with Blueprints
- **Testing Scripts**: JavaScript (preserved from original autoA11y.js)
- **Task Queue**: Async task runner for background jobs

## Prerequisites

- Python 3.8 or higher
- MongoDB 4.0 or higher
- Google Chrome or Chromium browser

## Installation

```bash
# Clone the repository
git clone https://github.com/[your-username]/auto_a11y_python.git
cd auto_a11y_python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up MongoDB (if not already running)
# Install MongoDB and start the service
# Default connection: mongodb://localhost:27017/

# Configure the application
cp config.example.py config.py
# Edit config.py with your settings

# Run initial setup
python run.py --setup
```

The setup process will:
- Create necessary directories
- Set up database indexes  
- Download Chromium browser for Pyppeteer
- Create a sample project to get started

## Configuration

Edit `config.py` to customize your settings:

```python
# MongoDB settings
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "auto_a11y"

# Server settings
HOST = "127.0.0.1"
PORT = 5000
DEBUG = False

# AI settings (optional)
RUN_AI_ANALYSIS = False  # Set to True to enable Claude AI
CLAUDE_API_KEY = "your-anthropic-api-key"

# Directories
SCREENSHOTS_DIR = "screenshots"
REPORTS_DIR = "reports"

# Scraping settings
MAX_DEPTH = 3
MAX_PAGES_PER_WEBSITE = 100
```

## Usage

### Starting the Application

```bash
# Run with default settings
python run.py

# Run with options
python run.py --host 0.0.0.0 --port 8080 --debug

# Other commands
python run.py --test-db          # Test database connection
python run.py --download-browser  # Download Chromium
python run.py --setup            # Run initial setup
```

### Web Interface

Open your browser to `http://localhost:5000`

#### Workflow:

1. **Create a Project**: Organize your testing efforts
2. **Add Websites**: Add websites to test within projects
3. **Discover Pages**: Automatically crawl and discover pages
4. **Run Tests**: Execute accessibility tests on pages
5. **Generate Reports**: Export detailed compliance reports

## JavaScript Test Scripts

The core accessibility tests are JavaScript modules executed in the browser context:

- **headings.js**: Heading hierarchy and structure
- **images.js**: Alt text and decorative images
- **forms.js & forms2.js**: Form labels and accessibility
- **landmarks.js**: ARIA landmarks and regions
- **colorContrast.js**: WCAG color contrast ratios
- **focus.js**: Keyboard navigation and focus
- **language.js**: Language declarations
- **pageTitle.js**: Page title requirements
- **tabindex.js**: Tab order and keyboard access
- **ariaRoles.js**: ARIA attribute validation
- **svg.js**: SVG accessibility
- **pdf.js**: PDF link detection

## AI Analysis Features

When Claude AI is enabled, the system detects:

- **Visual Headings**: Text that looks like headings but lacks semantic markup
- **Reading Order**: Mismatches between visual and DOM order
- **Modal Accessibility**: Issues with dialogs and overlays
- **Language Changes**: Unmarked foreign language content
- **Motion & Animation**: Problematic animations
- **Interactive Elements**: Custom controls lacking ARIA

## Project Structure

```
auto_a11y_python/
├── auto_a11y/
│   ├── core/            # Core functionality
│   │   ├── browser_manager.py
│   │   ├── database.py
│   │   └── scraper.py
│   ├── models/          # Data models
│   ├── scripts/         # JavaScript test files
│   │   └── tests/       # Individual test modules
│   ├── testing/         # Test runner
│   │   ├── test_runner.py
│   │   ├── script_injector.py
│   │   └── result_processor.py
│   ├── ai/              # Claude AI integration
│   │   ├── claude_analyzer.py
│   │   └── analysis_modules.py
│   ├── reporting/       # Report generation
│   │   ├── report_generator.py
│   │   └── formatters.py
│   └── web/            # Flask application
│       ├── app.py
│       └── routes/
├── templates/          # HTML templates
├── static/            # CSS, JS, images
├── docs/              # Documentation
├── config.py          # Configuration
└── run.py            # Entry point
```

## API Usage

The application provides REST API endpoints for automation:

```python
# Example: Test a page
POST /api/pages/{page_id}/test
{
    "include_ai": true,
    "take_screenshot": true
}

# Example: Generate report
POST /api/reports/generate
{
    "type": "website",
    "id": "website_id",
    "format": "html",
    "include_ai": true
}

# Example: Discover pages
POST /api/websites/{website_id}/discover
{
    "max_depth": 3,
    "max_pages": 50
}
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   ```bash
   # Ensure MongoDB is running
   mongod
   # Test connection
   python run.py --test-db
   ```

2. **Browser Download Failed**
   ```bash
   # Manual download
   python run.py --download-browser
   # Or install Chrome/Chromium system-wide
   ```

3. **JavaScript Tests Not Loading**
   - Check that all files exist in `/auto_a11y/scripts/tests/`
   - Review browser console for errors
   - Ensure Pyppeteer is properly installed

4. **AI Analysis Not Working**
   - Verify Claude API key in config.py
   - Check API rate limits
   - Ensure `RUN_AI_ANALYSIS = True` in config

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

GNU General Public License v3.0

## Author

Bob Dodd

## Acknowledgments

- Original autoA11y.js Node.js application for the JavaScript test suite
- Pyppeteer team for the Python port of Puppeteer
- Claude AI by Anthropic for visual accessibility analysis
- Flask and MongoDB communities

## Support

For issues, questions, or contributions, please use the GitHub issue tracker.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.