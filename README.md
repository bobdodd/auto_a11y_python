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

### Microsoft 365 SSO (Optional)

The login page supports "Sign in with Microsoft" for client users. This is optional -- if the environment variables are left blank, the SSO button is hidden and only email/password login is available.

#### 1. Register an app in Azure AD

1. Go to the [Azure Portal](https://portal.azure.com/) and navigate to **Microsoft Entra ID** (formerly Azure Active Directory) > **App registrations** > **New registration**.
2. Set the following fields:
   - **Name**: whatever you like (e.g. "Auto A11y Public").
   - **Supported account types**: choose **Accounts in any organizational directory (Any Microsoft Entra ID tenant - Multitenant)** to allow users from any Microsoft 365 organization, or choose **Single tenant** if you only want users from your own organization.
   - **Redirect URI**: select **Web** and enter your callback URL. For local development this is `http://localhost:5001/auth/microsoft/callback`. For production, use your real domain (e.g. `https://reports.example.com/auth/microsoft/callback`).
3. Click **Register**.

#### 2. Collect the values you need

After registration, on the app's **Overview** page:

| Value | Where to find it | `.env` variable |
|---|---|---|
| Application (client) ID | Overview page, top | `MICROSOFT_CLIENT_ID` |
| Directory (tenant) ID | Overview page, top (only needed for single-tenant; use `common` for multi-tenant) | `MICROSOFT_TENANT_ID` |

#### 3. Create a client secret

1. Go to **Certificates & secrets** > **Client secrets** > **New client secret**.
2. Give it a description and expiry period, then click **Add**.
3. Copy the **Value** immediately (it is only shown once).

| Value | `.env` variable |
|---|---|
| Client secret value | `MICROSOFT_CLIENT_SECRET` |

#### 4. API permissions

The default registration already grants the `User.Read` delegated permission under Microsoft Graph, which is all that is needed. Verify this under **API permissions** -- you should see `Microsoft Graph > User.Read` listed. No admin consent is required for this permission.

#### 5. Add to your `.env`

```bash
MICROSOFT_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MICROSOFT_CLIENT_SECRET=your-secret-value
MICROSOFT_TENANT_ID=common
```

Set `MICROSOFT_TENANT_ID` to `common` (the default) for multi-tenant, or to your specific tenant ID for single-tenant.

#### 6. Verify

Start the app and visit `/auth/login`. The "Sign in with Microsoft" button should appear above the email/password form.

### Google SSO (Optional)

The login page also supports "Sign in with Google". Like Microsoft SSO, this is optional -- if the environment variables are left blank, the Google button is hidden.

#### 1. Create a project in Google Cloud Console

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project (or select an existing one).
2. Navigate to **APIs & Services** > **OAuth consent screen**.
3. Choose **External** user type (allows any Google account) or **Internal** (restricts to your Google Workspace organization only). Click **Create**.
4. Fill in the required fields:
   - **App name**: whatever you like (e.g. "Auto A11y Public").
   - **User support email**: your email address.
   - **Developer contact information**: your email address.
5. Click **Save and Continue**.
6. On the **Scopes** screen, click **Add or Remove Scopes** and add:
   - `openid`
   - `email`
   - `profile`
7. Click **Save and Continue** through the remaining screens.

#### 2. Create OAuth credentials

1. Navigate to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** > **OAuth client ID**.
3. Set **Application type** to **Web application**.
4. Give it a name (e.g. "Auto A11y Public").
5. Under **Authorized redirect URIs**, add your callback URL. For local development this is `http://localhost:5001/auth/google/callback`. For production, use your real domain (e.g. `https://reports.example.com/auth/google/callback`).
6. Click **Create**.

#### 3. Collect the values you need

After creation, a dialog shows your credentials:

| Value | `.env` variable |
|---|---|
| Client ID | `GOOGLE_CLIENT_ID` |
| Client secret | `GOOGLE_CLIENT_SECRET` |

You can also find these later under **APIs & Services** > **Credentials** by clicking on the OAuth client you created.

#### 4. Add to your `.env`

```bash
GOOGLE_CLIENT_ID=xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxx
```

#### 5. Verify

Start the app and visit `/auth/login`. The "Sign in with Google" button should appear above the email/password form.

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
├── Fixtures/          # Test fixtures for validation
├── config.py          # Configuration
├── test_fixtures.py   # Fixture testing script
└── run.py            # Entry point
```

## Testing

### Fixture Testing

Auto A11y includes a comprehensive fixture testing system to validate that accessibility tests work correctly before deploying them in production. For complete documentation:

- **[Fixture Testing Guide](docs/FIXTURE_TESTING.md)** - Comprehensive guide with workflows and examples
- **[Quick Reference](FIXTURE_TESTING_QUICKREF.md)** - Command cheat sheet for daily use

**Quick start:**
```bash
# Test all fixtures (takes ~1 hour for ~900 fixtures)
python test_fixtures.py

# Test only Discovery fixtures (~5 minutes)
python test_fixtures.py --type Disco

# Test specific category
python test_fixtures.py --category Images

# Test specific error code
python test_fixtures.py --code ErrNoAlt

# Combine filters
python test_fixtures.py --type Err --category Headings --limit 10
```

Only tests that pass ALL their fixtures are enabled in production. View fixture status at `http://localhost:5001/testing/fixture-status`

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
