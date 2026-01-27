# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Auto A11y Python is a comprehensive web accessibility testing platform that combines automated DOM testing with AI-powered visual analysis. It tests websites for WCAG 2.1 compliance using JavaScript test scripts executed in browser context (via Playwright), enhanced with Claude AI for visual accessibility analysis.

**Key Technologies:**
- Python 3.8+ (Flask web framework)
- MongoDB (database)
- Playwright (browser automation, replaced Pyppeteer)
- Claude AI by Anthropic (visual analysis)
- JavaScript test scripts (browser-executed accessibility tests)

## Common Development Commands

### Running the Application

```bash
# Initial setup (first time only)
python run.py --setup

# Start the web interface (default: http://127.0.0.1:5001)
python run.py

# Start with custom host/port
python run.py --host 0.0.0.0 --port 8080

# Start in debug mode
python run.py --debug

# Test database connection
python run.py --test-db

# Download Chromium browser for Playwright
python run.py --download-browser
# Or manually: python -m playwright install chromium
```

### Fixture Testing (Critical)

**Only accessibility tests that pass ALL their fixtures are enabled in production.** The fixture system validates test accuracy against ~900 known HTML test cases.

```bash
# Quick validation (~5 minutes) - USE THIS DURING DEVELOPMENT
python test_fixtures.py --type Disco

# Test specific category
python test_fixtures.py --category Forms
python test_fixtures.py --category Images

# Test specific error code
python test_fixtures.py --code ErrNoAlt

# Full test suite (~1 hour - only run before major releases)
python test_fixtures.py

# View results
# Web interface: http://localhost:5001/testing/fixture-status
# Results saved to: fixture_test_results.json and MongoDB
```

### Development Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Start MongoDB (if not running)
mongod

# 3. Start Flask app (with auto-reload)
python run.py --debug

# 4. After making changes to test code, validate with fixtures
python test_fixtures.py --category <YourCategory>
```

### Git Workflow

**CRITICAL: NEVER rewrite git history.**

- **NEVER use:** `git commit --amend`, `git rebase -i`, `git reset --hard`, `git push --force`, or any other commands that modify existing commits
- **Always create new commits** for changes, even if fixing mistakes from previous commits
- **Reason:** This project may have multiple collaborators and shared branches. Rewriting history breaks collaboration and can cause data loss
- If you need to undo changes, use `git revert` to create new commits that reverse previous changes
- If commits need to be reorganized, consult with the repository owner first

## High-Level Architecture

### Testing Flow

```
User → Flask Web UI → Testing Engine → Playwright Browser
                            ↓
                    1. Load target page
                    2. Inject JavaScript dependencies
                    3. Inject test scripts
                    4. Execute tests in browser context
                    5. Capture screenshot
                    6. Run Claude AI analysis (optional)
                    7. Aggregate results → MongoDB
                    8. Generate reports (HTML/XLSX/JSON/PDF)
```

### Core Components

**1. Test Runner (`auto_a11y/testing/test_runner.py`)**
- Orchestrates the entire testing process
- Manages Playwright browser instances
- Injects and executes JavaScript test scripts
- Coordinates with Claude AI analyzer
- Main entry point: `TestRunner.test_page(page_id)`

**2. Script Executor (`auto_a11y/testing/script_executor.py`)**
- Executes JavaScript accessibility tests in browser context
- Scripts located in `auto_a11y/scripts/tests/`
- Dependencies in `auto_a11y/scripts/dependencies/`
- Each test returns: `{errors: [...], warnings: [...], passes: [...], disco: [...]}`

**3. Result Processor (`auto_a11y/testing/result_processor.py`)**
- Processes raw test results from JavaScript
- Applies touchpoint mapping (categories)
- Deduplicates issues
- Formats for database storage

**4. Browser Manager (`auto_a11y/core/browser_manager.py`)**
- Manages Playwright browser lifecycle
- Handles browser context and page creation
- Takes screenshots with element highlighting

**5. Database (`auto_a11y/core/database.py`)**
- MongoDB operations for all collections
- Collections: `projects`, `websites`, `pages`, `test_results`, `fixture_tests`
- Handles large documents (16MB MongoDB limit considerations)

**6. Claude AI Integration (`auto_a11y/ai/`)**
- Visual accessibility analysis beyond DOM testing
- Detects: visual headings, reading order, modal issues, animations
- Uses Claude Opus 4 model with vision capabilities
- Controlled by `RUN_AI_ANALYSIS` config flag

### JavaScript Test Scripts Architecture

**Location:** `auto_a11y/scripts/tests/`

**Dependencies (loaded first):**
- `accessibleName.js` - W3C accessible name calculation
- `ariaRoles.js` - ARIA role definitions
- `colorContrast.js` - Color contrast calculations
- `xpath.js` - XPath utilities

**Test Execution Pattern:**
Each test script exports a function that returns results:
```javascript
function testScrape() {
    return {
        errors: [{url, code, cat, msg, html, xpath, ...}],
        warnings: [{...}],
        passes: [{...}],
        disco: [{...}]  // Discovery results
    };
}
```

**Python-Side Mapping:**
Python touchpoint tests (`auto_a11y/testing/touchpoint_tests/`) process JavaScript results:
- Extract specific error codes
- Apply business logic and filtering
- Map to WCAG criteria and touchpoints
- Return structured `TestResult` objects

### Fixture Testing System

**Purpose:** Validates that accessibility tests work correctly before production use.

**Architecture:**
- Fixtures: `Fixtures/` directory (~900 HTML files)
- Structure: `Fixtures/{Category}/{TestType}_{ErrorCode}/{fixture}.html`
- Test runner: `test_fixtures.py`
- Each fixture file contains metadata in HTML comment:
  ```html
  <!--
  Category: Forms
  Code: ErrNoAlt
  Type: Err
  ExpectedResult: This field has no label
  -->
  ```

**Fixture Types:**
- `Err` - High severity violations (must detect)
- `Warn` - Medium severity issues (must detect)
- `Info` - Informational notices (must detect)
- `Disco` - Element discovery (must find elements)
- `AI` - AI-powered detection (requires Claude API)

**Production Gates:**
- A test is ONLY enabled in production if ALL its fixtures pass
- Partial pass = disabled (prevents false positives)
- Check status: Web UI at `/testing/fixture-status`

### Touchpoint System

**Touchpoints** are accessibility categories/themes that group related issues.

**Implementation:**
- Defined in: `auto_a11y/core/touchpoints.py`
- Mapping: Error codes → Touchpoints → WCAG criteria
- Examples: Forms, Images, ColorAndContrast, Headings, Focus, etc.
- Used for: Report organization, filtering, analytics

**Key Functions:**
- `get_touchpoint_for_code(error_code)` - Map error code to touchpoint
- `get_all_touchpoints()` - List all touchpoints with metadata
- `get_wcag_criteria_for_touchpoint(touchpoint)` - Get related WCAG rules

### Database Schema

**Key Collections:**
- `projects` - Top-level project organization
- `websites` - Websites within projects
- `pages` - Individual pages to test (discovered or manual)
- `test_results` - Test results per page (timestamped)
- `fixture_tests` - Fixture validation results
- `scheduled_tests` - APScheduler test schedules
- `drupal_config` - Drupal integration settings (if enabled)

**Important:** MongoDB has 16MB document size limit. Large test results use reference pattern or GridFS.

## Key Development Patterns

### Adding a New Accessibility Test

1. **Create/Update JavaScript test** in `auto_a11y/scripts/tests/`
2. **Create Python touchpoint test** in `auto_a11y/testing/touchpoint_tests/`
3. **Create fixture HTML files** in `Fixtures/{Category}/{Type}_{Code}/`
4. **Run fixture tests** to validate: `python test_fixtures.py --code YourCode`
5. **Only enable in production** after all fixtures pass

### Modifying Existing Tests

1. **Update JavaScript** if DOM logic changes
2. **Update Python touchpoint test** if processing logic changes
3. **Validate with fixtures:** `python test_fixtures.py --code ExistingCode`
4. **If fixtures fail:** Fix code OR update fixture expectations
5. **Never enable tests with failing fixtures**

### Working with Browser Automation

- Playwright replaced Pyppeteer (note: some old docs mention Pyppeteer)
- Browser manager handles context/page lifecycle
- Always use `async/await` for browser operations
- Screenshots are base64 encoded for Claude AI
- Browser is headless by default (`BROWSER_HEADLESS` config)

### Claude AI Integration

- Located in: `auto_a11y/ai/`
- Requires: `CLAUDE_API_KEY` in config/env
- Enable: `RUN_AI_ANALYSIS = True` in config
- Model: Claude Opus 4 (configurable via `CLAUDE_MODEL`)
- Uses: Extended thinking mode for complex analysis
- Budget: Configurable token budget per analysis

### Report Generation

- Located in: `auto_a11y/reporting/`
- Formats: HTML, Excel (XLSX), JSON, CSV, PDF (via WeasyPrint)
- Static HTML reports: Self-contained, no database dependency
- Report types: Project, Website, Page, Comparison
- Custom styling: Templates in `auto_a11y/web/templates/reports/`

## Important Configuration

**Location:** `config.py` (loads from `.env`)

**Critical Settings:**
- `MONGODB_URI` - Database connection
- `CLAUDE_API_KEY` - AI features (optional but recommended)
- `RUN_AI_ANALYSIS` - Enable/disable Claude AI
- `PORT` - Default 5001 (avoid macOS AirPlay Receiver on 5000)
- `BROWSER_HEADLESS` - Headless browser mode
- `SHOW_ERROR_CODES` - Developer mode for debugging

## Testing Philosophy

**Two-Layer Testing:**
1. **JavaScript tests in browser** - Fast, accurate DOM testing
2. **Claude AI visual analysis** - Catches what DOM testing misses

**Fixture-Driven Development:**
- Write fixtures FIRST (TDD approach)
- Test against fixtures CONTINUOUSLY
- Only enable tests that pass ALL fixtures
- This prevents false positives in production

**Why JavaScript + Python:**
- JavaScript: Direct DOM access, W3C spec compliance, browser APIs
- Python: Orchestration, AI integration, data processing, web framework

## Common Gotchas

1. **Port Conflict:** macOS AirPlay Receiver uses 5000 → We use 5001
2. **MongoDB Document Size:** 16MB limit → Large results use references
3. **Playwright vs Pyppeteer:** Codebase uses Playwright (some docs outdated)
4. **Fixture Failures:** NEVER enable tests with partial fixture pass
5. **Browser Download:** First run requires: `python -m playwright install chromium`
6. **AI Analysis:** Costs money per request → Test with `RUN_AI_ANALYSIS=False` first
7. **Async Operations:** Most browser/AI operations use async/await

## File Organization

```
auto_a11y/
├── ai/                      # Claude AI integration
├── core/                    # Core functionality (browser, database, scraper)
├── testing/                 # Test runners and processors
│   ├── touchpoint_tests/   # Python test implementations
│   └── test_runner.py      # Main test orchestrator
├── scripts/                # JavaScript test scripts
│   ├── dependencies/       # Required JS libraries
│   ├── tests/              # JS test modules (BROWSER-EXECUTED)
│   └── utilities/          # JS helper functions
├── reporting/              # Report generation
├── web/                    # Flask application
│   ├── routes/            # API endpoints
│   └── templates/         # Jinja2 templates
└── models/                # Data models

Fixtures/                   # Test fixtures (~900 HTML files)
├── {Category}/            # E.g., Forms, Images, Headings
│   └── {Type}_{Code}/     # E.g., Err_NoAlt, Disco_FormOnPage
│       └── *.html         # Individual test cases

docs/                      # Architecture documentation
config.py                  # Configuration management
run.py                     # Application entry point
test_fixtures.py           # Fixture test runner
```

## Useful Resources

- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Fixture Testing:** [docs/FIXTURE_TESTING.md](docs/FIXTURE_TESTING.md)
- **Quick Reference:** [FIXTURE_TESTING_QUICKREF.md](FIXTURE_TESTING_QUICKREF.md)
- **JavaScript Integration:** [docs/JAVASCRIPT_INTEGRATION.md](docs/JAVASCRIPT_INTEGRATION.md)
- **Claude AI:** [docs/CLAUDE_AI_INTEGRATION.md](docs/CLAUDE_AI_INTEGRATION.md)
- **Issue Catalog:** [ISSUE_CATALOG.md](ISSUE_CATALOG.md)
- **Fixture Web UI:** http://localhost:5001/testing/fixture-status
