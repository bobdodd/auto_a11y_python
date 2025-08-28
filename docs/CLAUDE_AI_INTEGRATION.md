# Claude AI Integration Documentation

## Overview

Auto A11y Python integrates Anthropic's Claude AI to provide advanced accessibility analysis beyond traditional rule-based testing. Claude analyzes screenshots and HTML to detect complex accessibility issues that require visual understanding and semantic context.

## Architecture

```
Testing Engine
     │
     ├── Capture Screenshot (Base64)
     ├── Extract HTML (Cleaned)
     │
     └── Claude Analysis Pipeline
             │
             ├── Visual Analysis
             │   ├── Heading Detection
             │   ├── Reading Order
             │   └── Layout Issues
             │
             ├── Semantic Analysis
             │   ├── Content Relationships
             │   ├── Modal Dialogs
             │   └── Interactive Elements
             │
             └── Motion Analysis
                 ├── Animation Detection
                 └── Auto-playing Media
```

## Claude Configuration

### API Setup

```python
from anthropic import Anthropic
from dataclasses import dataclass
from typing import Optional

@dataclass
class ClaudeConfig:
    """Claude AI configuration"""
    api_key: str
    model: str = "claude-3-opus-20240229"  # Most capable model
    max_tokens: int = 4096
    temperature: float = 1.0
    timeout: int = 60
    
    # Model options
    MODELS = {
        'opus': 'claude-3-opus-20240229',      # Best quality
        'sonnet': 'claude-3-sonnet-20240229',  # Balanced
        'haiku': 'claude-3-haiku-20240307'     # Fastest
    }
    
class ClaudeClient:
    """Claude AI client wrapper"""
    
    def __init__(self, config: ClaudeConfig):
        self.config = config
        self.client = Anthropic(api_key=config.api_key)
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        return """You are a pedantic and thoughtful assistant focused on 
        digital accessibility concerns. You check results in as many ways 
        as possible for accuracy. You are an expert in WCAG 2.1 guidelines 
        and modern web accessibility best practices."""
```

## Analysis Modules

### 1. Visual Heading Analysis

**Purpose**: Detect visual headings not properly marked up in HTML.

```python
class HeadingAnalyzer:
    """Analyzes heading structure visually and semantically"""
    
    async def analyze_headings(
        self, 
        screenshot: bytes, 
        html: str
    ) -> dict:
        """
        Detect heading mismatches between visual and semantic structure
        
        Args:
            screenshot: Page screenshot as base64
            html: Cleaned HTML without scripts
            
        Returns:
            Analysis results with heading issues
        """
        prompt = """The image is a web screenshot. The following content is 
        the HTML source code for the image. 
        
        Using only the image, identify each probable heading based on:
        - Font size, weight, and prominence
        - Visual hierarchy and spacing
        - Exclude menu items and tab headers
        
        Using only the HTML, identify all headings declared as:
        - <h1> through <h6> tags
        - Elements with role="heading" and aria-level
        
        Match visual headings with HTML headings and identify:
        1. Visual headings not marked up in HTML (with XPath)
        2. HTML headings not visible in the image
        3. Heading level mismatches
        
        Reply ONLY with stringified JSON:
        {
            "imageHeadings": [...],
            "htmlHeadings": [...],
            "unmatchedImageHeadings": [...],
            "unmatchedHtmlHeadings": [...],
            "levelMismatches": [...]
        }
        
        The HTML: """ + html
        
        response = await self._send_request(screenshot, prompt)
        return json.loads(response)
    
    async def _send_request(
        self, 
        image: bytes, 
        prompt: str
    ) -> str:
        """Send request to Claude API"""
        message = await self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=self.system_prompt,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        )
        
        return message.content[0].text
```

### 2. Reading Order Analysis

**Purpose**: Verify that visual reading order matches DOM order.

```python
class ReadingOrderAnalyzer:
    """Analyzes reading order consistency"""
    
    async def analyze_reading_order(
        self, 
        screenshot: bytes, 
        html: str
    ) -> dict:
        """Check if DOM order matches visual reading order"""
        
        prompt = """Analyze the reading order of this web page.
        
        1. Identify the natural visual reading order from the screenshot
        2. Compare with the DOM order in the HTML
        3. Find any mismatches where DOM order differs from visual order
        
        Consider:
        - Left-to-right, top-to-bottom reading patterns
        - Multi-column layouts
        - Floating elements
        - Absolutely positioned content
        
        Return JSON with:
        {
            "visualOrder": ["element1", "element2", ...],
            "domOrder": ["element1", "element2", ...],
            "mismatches": [
                {
                    "element": "...",
                    "xpath": "...",
                    "visualPosition": 3,
                    "domPosition": 7,
                    "issue": "Element appears earlier visually than in DOM"
                }
            ],
            "readingOrderCorrect": true/false
        }"""
        
        return await self._analyze(screenshot, html, prompt)
```

### 3. Modal Dialog Analysis

**Purpose**: Detect modal dialogs and analyze their accessibility.

```python
class ModalAnalyzer:
    """Analyzes modal dialog accessibility"""
    
    async def analyze_modals(
        self, 
        screenshot: bytes, 
        html: str
    ) -> dict:
        """Detect and analyze modal dialogs"""
        
        prompt = """Identify any modal dialogs or overlays in this page.
        
        For each modal found, check:
        1. Does it have role="dialog" or role="alertdialog"?
        2. Does it have an accessible name (aria-label/aria-labelledby)?
        3. Does it start with a heading (h1 or h2)?
        4. Is there a visible close button?
        5. Does it trap focus (check for focus management code)?
        6. Is the background content marked as inert or aria-hidden?
        7. Can it be closed with Escape key?
        
        Return JSON:
        {
            "modalsFound": [...],
            "accessibilityIssues": [...],
            "recommendations": [...]
        }"""
        
        return await self._analyze(screenshot, html, prompt)
```

### 4. Language Analysis

**Purpose**: Detect language changes and verify proper markup.

```python
class LanguageAnalyzer:
    """Analyzes language declarations"""
    
    async def analyze_language(
        self, 
        screenshot: bytes, 
        html: str
    ) -> dict:
        """Detect language usage and verify markup"""
        
        prompt = """Analyze the language usage in this web page.
        
        1. What is the dominant language of the page?
        2. Does the HTML lang attribute match?
        3. Are there any content sections in different languages?
        4. Are language changes properly marked with lang attributes?
        
        Return JSON:
        {
            "dominantLanguage": "en",
            "htmlLangAttribute": "en",
            "languageMatches": true,
            "foreignLanguageContent": [
                {
                    "xpath": "...",
                    "detectedLanguage": "es",
                    "hasLangAttribute": false,
                    "content": "..."
                }
            ]
        }"""
        
        return await self._analyze(screenshot, html, prompt)
```

### 5. Animation Detection

**Purpose**: Detect animations and motion that may cause issues.

```python
class AnimationAnalyzer:
    """Analyzes animations and motion"""
    
    async def analyze_animations(self, html: str) -> dict:
        """Detect animations in HTML/CSS"""
        
        prompt = """Analyze this HTML for animations and motion.
        
        Find:
        1. CSS animations and transitions
        2. Auto-playing videos or animated GIFs
        3. Infinite animations
        4. Parallax scrolling effects
        
        Check:
        - Is prefers-reduced-motion media query respected?
        - Can animations be paused?
        - Do they last longer than 5 seconds?
        
        Return JSON:
        {
            "animationsFound": [...],
            "infiniteAnimations": [...],
            "prefersReducedMotion": true/false,
            "accessibilityIssues": [...]
        }"""
        
        return await self._analyze_html_only(html, prompt)
```

### 6. Interactive Element Analysis

**Purpose**: Analyze interactive elements for keyboard accessibility.

```python
class InteractiveAnalyzer:
    """Analyzes interactive element accessibility"""
    
    async def analyze_interactivity(
        self, 
        screenshot: bytes, 
        html: str
    ) -> dict:
        """Analyze interactive elements"""
        
        prompt = """Identify all interactive elements in this page.
        
        For each interactive element:
        1. Is it keyboard accessible (button, a, input, or tabindex)?
        2. Does it have a visible focus indicator?
        3. Is the purpose clear from its accessible name?
        4. Are click handlers on non-semantic elements?
        
        Special checks:
        - Dropdown menus using aria-expanded
        - Toggle buttons using aria-pressed
        - Tab panels with proper ARIA
        
        Return JSON:
        {
            "interactiveElements": [...],
            "keyboardInaccessible": [...],
            "missingAriaStates": [...],
            "recommendations": [...]
        }"""
        
        return await self._analyze(screenshot, html, prompt)
```

## Integration with Testing Engine

### 1. Main Integration Class

```python
from typing import List, Optional
import asyncio
import base64

class ClaudeIntegration:
    """Main Claude AI integration for accessibility testing"""
    
    def __init__(self, config: ClaudeConfig):
        self.config = config
        self.client = ClaudeClient(config)
        
        # Initialize analyzers
        self.heading_analyzer = HeadingAnalyzer(self.client)
        self.reading_order_analyzer = ReadingOrderAnalyzer(self.client)
        self.modal_analyzer = ModalAnalyzer(self.client)
        self.language_analyzer = LanguageAnalyzer(self.client)
        self.animation_analyzer = AnimationAnalyzer(self.client)
        self.interactive_analyzer = InteractiveAnalyzer(self.client)
    
    async def analyze_page(
        self, 
        screenshot: bytes,
        html: str,
        analyses: List[str] = None
    ) -> dict:
        """
        Run requested AI analyses on page
        
        Args:
            screenshot: Page screenshot
            html: Cleaned HTML
            analyses: List of analyses to run
            
        Returns:
            Combined analysis results
        """
        if analyses is None:
            analyses = ['headings', 'reading_order', 'language']
        
        results = {}
        tasks = []
        
        # Create analysis tasks
        if 'headings' in analyses:
            tasks.append(self._run_analysis(
                'headings',
                self.heading_analyzer.analyze_headings,
                screenshot, html
            ))
        
        if 'reading_order' in analyses:
            tasks.append(self._run_analysis(
                'reading_order',
                self.reading_order_analyzer.analyze_reading_order,
                screenshot, html
            ))
        
        if 'modals' in analyses:
            tasks.append(self._run_analysis(
                'modals',
                self.modal_analyzer.analyze_modals,
                screenshot, html
            ))
        
        # Run analyses in parallel
        analysis_results = await asyncio.gather(*tasks)
        
        # Combine results
        for result in analysis_results:
            results.update(result)
        
        return results
    
    async def _run_analysis(
        self, 
        name: str, 
        analyzer_func, 
        *args
    ) -> dict:
        """Run single analysis with error handling"""
        try:
            result = await analyzer_func(*args)
            return {name: result}
        except Exception as e:
            return {name: {'error': str(e)}}
```

### 2. HTML Preprocessing

```python
from bs4 import BeautifulSoup

class HTMLPreprocessor:
    """Preprocesses HTML for Claude analysis"""
    
    @staticmethod
    def clean_html(html: str) -> str:
        """
        Remove scripts and simplify HTML for token efficiency
        
        Args:
            html: Raw HTML
            
        Returns:
            Cleaned HTML optimized for AI analysis
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script tags
        for script in soup.find_all('script'):
            script.decompose()
        
        # Remove style tags (keep inline styles)
        for style in soup.find_all('style'):
            style.decompose()
        
        # Remove comments
        for comment in soup.find_all(text=lambda t: isinstance(t, Comment)):
            comment.extract()
        
        # Remove data attributes (keep aria attributes)
        for tag in soup.find_all():
            attrs_to_remove = [
                attr for attr in tag.attrs 
                if attr.startswith('data-') and not attr.startswith('data-aria')
            ]
            for attr in attrs_to_remove:
                del tag[attr]
        
        # Pretty print with minimal formatting
        return soup.prettify(formatter='minimal')
```

### 3. Screenshot Optimization

```python
from PIL import Image
import io

class ScreenshotOptimizer:
    """Optimizes screenshots for Claude analysis"""
    
    @staticmethod
    def optimize_screenshot(
        screenshot: bytes, 
        max_width: int = 1920,
        quality: int = 85
    ) -> bytes:
        """
        Optimize screenshot for API transmission
        
        Args:
            screenshot: Raw screenshot bytes
            max_width: Maximum width in pixels
            quality: JPEG quality (1-100)
            
        Returns:
            Optimized screenshot bytes
        """
        # Open image
        img = Image.open(io.BytesIO(screenshot))
        
        # Resize if needed
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save optimized image
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        
        return output.getvalue()
```

## Prompt Engineering

### Best Practices

1. **Be Specific**: Clearly define what to analyze
2. **Request JSON**: Always request JSON output for parsing
3. **Provide Context**: Include relevant WCAG criteria
4. **Set Boundaries**: Specify what to exclude (e.g., menu items)

### Prompt Templates

```python
class PromptTemplates:
    """Reusable prompt templates for Claude"""
    
    HEADING_ANALYSIS = """
    Analyze heading structure for WCAG 2.1 compliance.
    
    Requirements:
    - 1.3.1 Info and Relationships (Level A)
    - 2.4.6 Headings and Labels (Level AA)
    
    Check for:
    {checks}
    
    Return JSON with:
    {output_format}
    
    HTML: {html}
    """
    
    @classmethod
    def get_heading_prompt(cls, html: str, checks: List[str]) -> str:
        """Generate heading analysis prompt"""
        return cls.HEADING_ANALYSIS.format(
            checks='\n'.join(f'- {check}' for check in checks),
            output_format='{\n  "issues": [...],\n  "summary": {...}\n}',
            html=html
        )
```

## Error Handling

### Rate Limiting

```python
import time
from typing import Optional

class RateLimiter:
    """Handles Claude API rate limiting"""
    
    def __init__(self, requests_per_minute: int = 50):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Clean old requests
        self.request_times = [
            t for t in self.request_times 
            if now - t < 60
        ]
        
        # Check if limit reached
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (now - self.request_times[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.request_times.append(time.time())
```

### Retry Logic

```python
class ClaudeRetry:
    """Retry logic for Claude API calls"""
    
    @staticmethod
    async def with_retry(
        func, 
        max_retries: int = 3,
        backoff: float = 1.0
    ):
        """Execute function with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                wait_time = backoff * (2 ** attempt)
                await asyncio.sleep(wait_time)
```

### Fallback Strategies

```python
class ClaudeFallback:
    """Fallback strategies when Claude is unavailable"""
    
    @staticmethod
    def get_basic_analysis(html: str) -> dict:
        """Provide basic analysis without AI"""
        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            'fallback': True,
            'basic_analysis': {
                'heading_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                'image_count': len(soup.find_all('img')),
                'form_count': len(soup.find_all('form')),
                'has_main': soup.find('main') is not None,
                'has_nav': soup.find('nav') is not None
            }
        }
```

## Cost Optimization

### Token Usage Tracking

```python
@dataclass
class TokenUsage:
    """Track token usage for cost monitoring"""
    input_tokens: int
    output_tokens: int
    model: str
    
    @property
    def estimated_cost(self) -> float:
        """Estimate cost in USD"""
        # Claude pricing (as of 2024)
        pricing = {
            'claude-3-opus-20240229': {
                'input': 15.00 / 1_000_000,   # $15 per 1M tokens
                'output': 75.00 / 1_000_000   # $75 per 1M tokens
            },
            'claude-3-sonnet-20240229': {
                'input': 3.00 / 1_000_000,
                'output': 15.00 / 1_000_000
            }
        }
        
        if self.model in pricing:
            input_cost = self.input_tokens * pricing[self.model]['input']
            output_cost = self.output_tokens * pricing[self.model]['output']
            return input_cost + output_cost
        
        return 0.0

class TokenTracker:
    """Track token usage across requests"""
    
    def __init__(self):
        self.usage_history = []
    
    def add_usage(self, usage: TokenUsage):
        """Add usage record"""
        self.usage_history.append(usage)
    
    def get_total_cost(self) -> float:
        """Get total estimated cost"""
        return sum(u.estimated_cost for u in self.usage_history)
```

### Selective Analysis

```python
class SelectiveAnalyzer:
    """Selectively run expensive analyses"""
    
    def should_run_ai_analysis(self, page_complexity: dict) -> bool:
        """Determine if AI analysis is needed"""
        
        # Skip AI for simple pages
        if page_complexity['element_count'] < 50:
            return False
        
        # Always run for complex layouts
        if page_complexity['has_modals'] or page_complexity['has_tabs']:
            return True
        
        # Run periodically for samples
        return random.random() < 0.1  # 10% sample
```

## Testing Claude Integration

### Mock Claude Client

```python
class MockClaudeClient:
    """Mock Claude client for testing"""
    
    async def analyze(self, screenshot: bytes, html: str, prompt: str) -> str:
        """Return mock responses"""
        
        if 'heading' in prompt.lower():
            return json.dumps({
                'imageHeadings': ['Visual Heading 1'],
                'htmlHeadings': ['<h1>Heading 1</h1>'],
                'unmatchedImageHeadings': [],
                'unmatchedHtmlHeadings': []
            })
        
        return json.dumps({'mock': True})
```

### Integration Tests

```python
import pytest

@pytest.mark.asyncio
async def test_claude_heading_analysis():
    """Test Claude heading analysis integration"""
    
    # Setup
    config = ClaudeConfig(api_key='test_key')
    integration = ClaudeIntegration(config)
    
    # Mock client
    integration.client = MockClaudeClient()
    
    # Test data
    screenshot = b'fake_screenshot_data'
    html = '<h1>Test Heading</h1>'
    
    # Run analysis
    result = await integration.analyze_page(
        screenshot, 
        html, 
        analyses=['headings']
    )
    
    # Assertions
    assert 'headings' in result
    assert 'imageHeadings' in result['headings']
```