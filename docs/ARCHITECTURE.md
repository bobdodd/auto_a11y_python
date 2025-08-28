# Auto A11y Python - System Architecture

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Technology Decisions](#technology-decisions)
6. [Integration Points](#integration-points)
7. [Security Considerations](#security-considerations)
8. [Performance Optimization](#performance-optimization)

## Overview

Auto A11y Python is a comprehensive web accessibility testing platform that combines:
- **Browser-based testing** using Pyppeteer (Python port of Puppeteer)
- **AI-powered analysis** using Anthropic's Claude API
- **Modular JavaScript test scripts** executed in browser context
- **Project-based organization** for managing multiple websites
- **Efficient web scraping** with intelligent page discovery

### Design Philosophy

1. **Separation of Concerns**: Clear boundaries between scraping, testing, analysis, and reporting
2. **Modularity**: Reusable components that can be extended or replaced
3. **Browser-Native Testing**: JavaScript tests run in actual browser context for accuracy
4. **AI Enhancement**: Claude AI provides visual and semantic analysis beyond rule-based testing
5. **Performance First**: Efficient scraping and parallel processing where possible
6. **Maintainability**: Clear documentation, type hints, and consistent patterns

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Interface                         │
│                     (Flask + Bootstrap)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      API Layer                               │
│                  (RESTful + WebSocket)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Core Engine                                │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐     │
│  │   Project   │ │   Website    │ │      Page        │     │
│  │   Manager   │ │   Manager    │ │     Manager      │     │
│  └─────────────┘ └──────────────┘ └──────────────────┘     │
│                                                              │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐     │
│  │   Scraper   │ │   Testing    │ │    Reporting     │     │
│  │   Engine    │ │   Engine     │ │     Engine       │     │
│  └─────────────┘ └──────────────┘ └──────────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        │             │             │              │
┌───────▼──────┐ ┌────▼──────┐ ┌───▼────┐ ┌──────▼──────┐
│   Pyppeteer  │ │JavaScript │ │ Claude │ │   MongoDB   │
│   Browser    │ │   Tests   │ │   AI   │ │  Database   │
└──────────────┘ └───────────┘ └────────┘ └─────────────┘
```

## Core Components

### 1. Project Manager (`auto_a11y.core.project_manager`)

**Purpose**: Manages the lifecycle of accessibility testing projects.

**Responsibilities**:
- Create, update, delete projects
- Associate websites with projects
- Track testing history
- Manage project metadata and configuration

**Key Classes**:
```python
class ProjectManager:
    def create_project(name: str, description: str) -> Project
    def add_website(project_id: str, url: str) -> Website
    def get_project_status(project_id: str) -> ProjectStatus
    def archive_project(project_id: str) -> bool
```

### 2. Scraper Engine (`auto_a11y.core.scraper`)

**Purpose**: Discovers and catalogs pages within websites.

**Responsibilities**:
- Crawl websites respecting robots.txt
- Discover pages through link analysis
- Handle dynamic content and JavaScript-rendered pages
- Maintain crawl state and resume capability

**Key Classes**:
```python
class ScraperEngine:
    def discover_pages(website: Website, config: ScrapConfig) -> List[Page]
    def validate_url(url: str) -> bool
    def respect_robots_txt(url: str) -> bool
    def extract_links(page_content: str) -> List[str]
```

**Configuration**:
```python
@dataclass
class ScrapConfig:
    max_depth: int = 3
    max_pages: int = 500
    follow_external: bool = False
    respect_robots: bool = True
    request_delay: float = 1.0
    timeout: int = 30
    user_agent: str = "Auto-A11y/1.0"
```

### 3. Testing Engine (`auto_a11y.testing.engine`)

**Purpose**: Orchestrates accessibility testing across pages.

**Responsibilities**:
- Load pages in Pyppeteer browser
- Inject JavaScript test scripts
- Execute tests and collect results
- Coordinate with Claude AI for visual analysis
- Manage test queues and parallel execution

**Key Classes**:
```python
class TestingEngine:
    async def test_page(page: Page) -> TestResult
    async def inject_scripts(browser_page: PyppeteerPage) -> None
    async def run_js_tests(browser_page: PyppeteerPage) -> Dict
    async def run_ai_analysis(screenshot: bytes, html: str) -> AIResult
```

### 4. JavaScript Test Modules (`auto_a11y.scripts/`)

**Purpose**: Browser-executed accessibility tests.

**Structure**: Each module focuses on specific WCAG criteria:
- `headings.js` - Heading hierarchy and structure
- `images.js` - Image alt text and decorative images
- `forms.js` - Form labels and ARIA
- `landmarks.js` - ARIA landmarks and regions
- `color.js` - Color contrast
- `focus.js` - Focus indicators and tab order
- `language.js` - Language declarations
- `titleAttr.js` - Title attributes
- `tabindex.js` - Tab index values

**Integration Pattern**:
```javascript
// Each script exports a scrape function
function headingsScrape() {
    return {
        errors: [...],      // Violations found
        warnings: [...],    // Potential issues
        passes: [...],      // Successful checks
        metadata: {...}     // Additional data
    };
}
```

### 5. AI Analysis Module (`auto_a11y.ai.claude_analyzer`)

**Purpose**: Provides AI-powered visual and semantic analysis.

**Responsibilities**:
- Screenshot analysis for visual issues
- Reading order verification
- Complex pattern recognition
- Semantic heading analysis
- Animation and motion detection

**Key Methods**:
```python
class ClaudeAnalyzer:
    async def analyze_headings(screenshot: bytes, html: str) -> HeadingAnalysis
    async def analyze_reading_order(screenshot: bytes, html: str) -> ReadingOrderAnalysis
    async def detect_animations(html: str) -> AnimationAnalysis
    async def analyze_modals(screenshot: bytes, html: str) -> ModalAnalysis
```

### 6. Database Layer (`auto_a11y.models/`)

**Purpose**: Data persistence and retrieval using MongoDB.

**Collections**:
- `projects` - Project metadata and configuration
- `websites` - Website information and scraping config
- `pages` - Discovered pages and their status
- `test_results` - Historical test results
- `ai_analyses` - Claude AI analysis results
- `reports` - Generated reports

**Key Models**:
```python
@dataclass
class Project:
    id: ObjectId
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    websites: List[Website]
    status: ProjectStatus

@dataclass
class TestResult:
    id: ObjectId
    page_id: ObjectId
    test_date: datetime
    violations: List[Violation]
    warnings: List[Warning]
    passes: List[Pass]
    ai_findings: List[AIFinding]
    score: AccessibilityScore
```

## Data Flow

### 1. Project Creation Flow
```
User → Web UI → API → ProjectManager → MongoDB
                ↓
         WebsiteManager → ScraperEngine → Page Discovery
                                    ↓
                              MongoDB (pages collection)
```

### 2. Testing Flow
```
Scheduler/User → TestingEngine → Pyppeteer Browser
                      ↓                ↓
                Load Page      Inject JS Scripts
                      ↓                ↓
                Take Screenshot   Execute Tests
                      ↓                ↓
                Claude API ← → Collect Results
                      ↓
                Aggregate Results → MongoDB
                      ↓
                Report Generator → Output (XLSX/HTML/JSON)
```

### 3. Real-time Updates Flow
```
Testing Engine → WebSocket → Browser Client
         ↓
   Progress Updates
   Live Results
   Error Notifications
```

## Technology Decisions

### Why Pyppeteer over Selenium?
1. **Native Puppeteer compatibility** - Direct port maintains API consistency
2. **Better JavaScript handling** - Built for modern web apps
3. **Headless-first design** - More efficient for automated testing
4. **DevTools Protocol** - Direct Chrome communication
5. **Smaller footprint** - No separate driver management

### Why Keep JavaScript Test Scripts?
1. **Browser context execution** - Direct DOM access
2. **Proven reliability** - Existing scripts are battle-tested
3. **Easy maintenance** - Web developers can contribute
4. **Performance** - No serialization overhead
5. **Compatibility** - Works with any browser automation tool

### Why MongoDB?
1. **Flexible schema** - Accessibility results vary per page
2. **Document-based** - Natural fit for web page data
3. **Scalability** - Handles large test result sets
4. **Aggregation pipeline** - Powerful reporting queries
5. **GridFS** - Store screenshots and reports

### Why Claude AI?
1. **Visual understanding** - Can "see" rendering issues
2. **Context awareness** - Understands semantic relationships
3. **Pattern recognition** - Identifies complex accessibility issues
4. **Natural language** - Provides human-readable explanations
5. **Continuous improvement** - AI models improve over time

## Integration Points

### 1. Browser Integration
```python
# Pyppeteer browser lifecycle
browser = await launch(headless=True, args=['--no-sandbox'])
page = await browser.newPage()
await page.goto(url, {'waitUntil': 'networkidle2'})
await page.addScriptTag({'path': 'scripts/headings.js'})
results = await page.evaluate('headingsScrape()')
```

### 2. Claude AI Integration
```python
# AI analysis configuration
CLAUDE_CONFIG = {
    'model': 'claude-3-opus-20240229',
    'max_tokens': 4096,
    'temperature': 1,
    'system': 'You are an accessibility expert...'
}

# Analysis request
result = await anthropic.messages.create(
    model=CLAUDE_CONFIG['model'],
    messages=[{
        'role': 'user',
        'content': [
            {'type': 'image', 'source': {'type': 'base64', 'data': screenshot}},
            {'type': 'text', 'text': prompt}
        ]
    }]
)
```

### 3. JavaScript Script Integration
```python
# Script injection pattern
SCRIPT_PATH = Path('scripts')
SCRIPTS = [
    'accessibleName.js',  # Dependencies first
    'ariaRoles.js',
    'colorContrast.js',
    'xpath.js',
    'headings.js',        # Test scripts
    'images.js',
    'forms.js'
]

for script in SCRIPTS:
    await page.addScriptTag({'path': SCRIPT_PATH / script})
```

## Security Considerations

### 1. Input Validation
- URL validation and sanitization
- XSS prevention in test results
- SQL injection prevention (parameterized queries)
- File path traversal prevention

### 2. Authentication & Authorization
- API key management for Claude AI
- User authentication for web interface
- Project-level access control
- Rate limiting for API endpoints

### 3. Data Protection
- Encryption at rest for sensitive data
- HTTPS for all communications
- Secure storage of screenshots
- PII detection and masking

### 4. Browser Security
- Sandboxed browser execution
- Disable unnecessary permissions
- Regular browser updates
- Content Security Policy (CSP)

## Performance Optimization

### 1. Parallel Processing
```python
# Concurrent page testing
async def test_pages_parallel(pages: List[Page], max_concurrent: int = 5):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def test_with_limit(page):
        async with semaphore:
            return await test_page(page)
    
    tasks = [test_with_limit(page) for page in pages]
    return await asyncio.gather(*tasks)
```

### 2. Caching Strategy
- Browser context reuse
- JavaScript compilation cache
- MongoDB query result cache
- Static resource caching

### 3. Resource Management
- Browser pool management
- Memory leak prevention
- Connection pooling
- Graceful degradation

### 4. Monitoring & Metrics
- Test execution time tracking
- Memory usage monitoring
- API call rate monitoring
- Error rate tracking

## Error Handling

### 1. Graceful Degradation
```python
class TestResult:
    def __init__(self):
        self.js_tests = None      # May fail
        self.ai_analysis = None   # May fail
        self.screenshot = None    # May fail
        
    def get_comprehensive_result(self):
        # Combine available results
        return merge_results(
            self.js_tests or {},
            self.ai_analysis or {},
            fallback=self.get_basic_analysis()
        )
```

### 2. Retry Logic
```python
@retry(max_attempts=3, backoff=exponential)
async def fetch_page(url: str):
    # Automatic retry with exponential backoff
    pass
```

### 3. Error Categories
- **Recoverable**: Network timeout, rate limits
- **Partial Failure**: Some tests pass, others fail
- **Critical**: Database connection, invalid configuration
- **User Error**: Invalid URLs, wrong credentials

## Future Extensibility

### 1. Plugin Architecture
```python
class TestPlugin(ABC):
    @abstractmethod
    async def run(self, page: Page) -> TestResult:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
```

### 2. Additional AI Providers
- OpenAI GPT-4 Vision
- Google Gemini
- Local models (LLaMA, etc.)

### 3. Export Formats
- WCAG compliance reports
- VPAT documents
- CI/CD integration
- Slack/Teams notifications

### 4. Advanced Features
- Visual regression testing
- Accessibility score trends
- Automated fix suggestions
- Browser extension