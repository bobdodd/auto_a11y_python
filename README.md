# Auto A11y Python

A modern Python-based automated accessibility testing tool that combines powerful browser-based testing with an efficient project management interface.

## Overview

Auto A11y Python is a comprehensive web accessibility testing platform that:
- Crawls websites to discover pages automatically
- Performs deep accessibility testing using browser automation
- Integrates AI-powered analysis using Claude for advanced pattern detection
- Provides project-based organization for managing multiple websites
- Generates detailed reports in multiple formats

## Features

- **Smart Web Scraping**: Efficient page discovery with configurable depth and scope
- **Browser-Based Testing**: Real DOM testing using Pyppeteer (Python port of Puppeteer)
- **AI-Enhanced Analysis**: Claude AI integration for visual and semantic accessibility testing
- **Modular Test Scripts**: Reusable JavaScript modules for specific accessibility checks
- **Project Management**: Organize testing by projects and websites
- **Comprehensive Reporting**: Export results in XLSX, JSON, and HTML formats

## Technology Stack

- **Backend**: Python 3.9+
- **Browser Automation**: Pyppeteer
- **Database**: MongoDB
- **AI Integration**: Anthropic Claude API
- **Web Framework**: Flask
- **Testing Scripts**: JavaScript (browser-executed)

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
```

## Quick Start

```bash
# Run the web interface
python run.py

# Or run command-line interface
python -m auto_a11y --url https://example.com --output report.xlsx
```

## Project Structure

```
auto_a11y_python/
├── auto_a11y/           # Main application package
│   ├── core/            # Core functionality
│   ├── testing/         # Testing engines and rules
│   ├── scripts/         # JavaScript test modules
│   ├── web/             # Web interface
│   └── utils/           # Utilities
├── tests/               # Test suite
├── docs/                # Documentation
└── requirements.txt     # Python dependencies
```

## License

GNU General Public License v3.0

## Author

Bob Dodd

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.