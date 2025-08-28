# JavaScript Test Script Integration

## Overview

Auto A11y Python maintains the battle-tested JavaScript accessibility testing scripts from the original a11yAuto project. These scripts run directly in the browser context via Pyppeteer, providing accurate DOM-based testing.

## Architecture

```
Python Testing Engine
        │
        ├── Pyppeteer Browser Instance
        │            │
        │            ├── Page Context
        │            │       │
        │            │       ├── Inject Dependencies
        │            │       ├── Inject Test Scripts  
        │            │       └── Execute Tests
        │            │
        │            └── Collect Results
        │
        └── Process & Store Results
```

## Script Organization

### Directory Structure
```
auto_a11y/scripts/
├── dependencies/           # Required libraries
│   ├── accessibleName.js  # W3C accessible name calculation
│   ├── ariaRoles.js       # ARIA role definitions
│   ├── colorContrast.js   # Color contrast calculations
│   └── xpath.js           # XPath utilities
│
├── tests/                 # Test modules
│   ├── headings.js       # Heading hierarchy tests
│   ├── images.js         # Image accessibility tests
│   ├── forms.js          # Form accessibility tests
│   ├── landmarks.js      # ARIA landmark tests
│   ├── color.js          # Color contrast tests
│   ├── focus.js          # Focus indicator tests
│   ├── language.js       # Language declaration tests
│   ├── titleAttr.js      # Title attribute tests
│   └── tabindex.js       # Tab index tests
│
└── utilities/            # Helper functions
    ├── a11yCodes.js     # Error code definitions
    └── jsScrape.js      # JavaScript extraction

```

## Script Interface

### Standard Test Script Pattern

Each test script follows this pattern:

```javascript
/**
 * Test script for [WCAG criterion]
 * @returns {Object} Test results
 */
function [name]Scrape() {
    // Initialize results
    let errorList = [];
    let warningList = [];
    let passList = [];
    
    // Query DOM elements
    const elements = document.querySelectorAll(selector);
    
    // Test each element
    elements.forEach(element => {
        // Perform tests
        if (violationCondition) {
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'category',
                err: 'ErrorCode',
                xpath: getXPath(element),
                element: element.tagName,
                details: additionalInfo,
                fpTempId: element.getAttribute('a11y-fpId')
            });
        }
    });
    
    return {
        errors: errorList,
        warnings: warningList,
        passes: passList,
        metadata: {
            testedElements: elements.length,
            testTime: Date.now()
        }
    };
}
```

### Result Object Structure

```javascript
{
    errors: [
        {
            url: "https://example.com/page",
            type: "err",              // "err" or "warn"
            cat: "heading",           // Category of test
            err: "ErrEmptyHeading",   // Error code
            xpath: "/html/body/h2[1]", // Element location
            element: "H2",            // Tag name
            headingText: "",          // Context-specific data
            parentLandmark: "main",   // Parent landmark if applicable
            fpTempId: "fp_123"        // Temporary failure point ID
        }
    ],
    warnings: [...],
    passes: [...],
    metadata: {
        testedElements: 42,
        testTime: 1642428000000
    }
}
```

## Python Integration

### 1. Script Loading

```python
from pathlib import Path
import asyncio
from pyppeteer import launch

class ScriptInjector:
    """Manages JavaScript test script injection"""
    
    SCRIPT_DIR = Path(__file__).parent / 'scripts'
    
    # Load order matters - dependencies first
    SCRIPT_LOAD_ORDER = [
        'dependencies/accessibleName.js',
        'dependencies/ariaRoles.js',
        'dependencies/colorContrast.js',
        'dependencies/xpath.js',
        'tests/headings.js',
        'tests/images.js',
        'tests/forms.js',
        'tests/landmarks.js',
        'tests/color.js',
        'tests/focus.js',
        'tests/language.js',
        'tests/titleAttr.js',
        'tests/tabindex.js'
    ]
    
    async def inject_scripts(self, page):
        """Inject all test scripts into page"""
        for script_path in self.SCRIPT_LOAD_ORDER:
            full_path = self.SCRIPT_DIR / script_path
            await page.addScriptTag({'path': str(full_path)})
```

### 2. Test Execution

```python
class JavaScriptTestRunner:
    """Executes JavaScript tests in browser context"""
    
    async def run_test(self, page, test_name: str) -> dict:
        """
        Run a specific test script
        
        Args:
            page: Pyppeteer page object
            test_name: Name of test function (e.g., 'headingsScrape')
            
        Returns:
            Test results dictionary
        """
        try:
            # Execute test function
            result = await page.evaluate(f'{test_name}()')
            
            # Add execution metadata
            result['execution'] = {
                'test_name': test_name,
                'timestamp': datetime.now().isoformat(),
                'page_url': page.url
            }
            
            return result
            
        except Exception as e:
            return {
                'errors': [],
                'warnings': [],
                'passes': [],
                'execution_error': str(e)
            }
    
    async def run_all_tests(self, page) -> dict:
        """Run all available tests"""
        test_functions = [
            'headingsScrape',
            'imagesScrape',
            'formScrape',
            'landmarksScrape',
            'colorScrape',
            'focusScrape',
            'languageScrape',
            'titleAttrScrape',
            'tabindexScrape'
        ]
        
        results = {}
        for test_func in test_functions:
            results[test_func] = await self.run_test(page, test_func)
        
        return results
```

### 3. Result Processing

```python
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class TestViolation:
    """Represents a single test violation"""
    url: str
    type: str  # 'err' or 'warn'
    category: str
    error_code: str
    xpath: str
    element: str
    details: Dict[str, Any]
    
class ResultProcessor:
    """Processes JavaScript test results"""
    
    def process_results(self, raw_results: dict) -> dict:
        """
        Process raw JavaScript test results
        
        Args:
            raw_results: Raw results from JavaScript tests
            
        Returns:
            Processed and categorized results
        """
        processed = {
            'violations': [],
            'warnings': [],
            'passes': [],
            'summary': {}
        }
        
        # Aggregate all test results
        for test_name, test_result in raw_results.items():
            if 'execution_error' in test_result:
                continue
                
            # Process errors as violations
            for error in test_result.get('errors', []):
                processed['violations'].append(
                    self._process_violation(error, test_name)
                )
            
            # Process warnings
            for warning in test_result.get('warnings', []):
                processed['warnings'].append(
                    self._process_violation(warning, test_name)
                )
            
            # Track passes
            processed['passes'].extend(
                test_result.get('passes', [])
            )
        
        # Generate summary
        processed['summary'] = {
            'total_violations': len(processed['violations']),
            'total_warnings': len(processed['warnings']),
            'total_passes': len(processed['passes']),
            'violation_categories': self._categorize_violations(
                processed['violations']
            )
        }
        
        return processed
    
    def _process_violation(self, violation: dict, source: str) -> dict:
        """Process individual violation"""
        return {
            'id': f"{source}_{violation['err']}",
            'source': source,
            'impact': self._determine_impact(violation),
            'category': violation['cat'],
            'error_code': violation['err'],
            'xpath': violation.get('xpath'),
            'element': violation.get('element'),
            'details': violation,
            'wcag_criteria': self._map_to_wcag(violation['err'])
        }
    
    def _determine_impact(self, violation: dict) -> str:
        """Determine violation impact level"""
        error_code = violation['err']
        
        # Critical violations
        if error_code.startswith('Err'):
            if 'NoAlt' in error_code or 'NoLabel' in error_code:
                return 'critical'
            elif 'Empty' in error_code:
                return 'serious'
            else:
                return 'moderate'
        
        # Warnings are typically minor or moderate
        elif error_code.startswith('Warn'):
            return 'minor'
        
        return 'moderate'
    
    def _map_to_wcag(self, error_code: str) -> List[str]:
        """Map error codes to WCAG criteria"""
        wcag_mapping = {
            'ErrNoAlt': ['1.1.1'],
            'ErrEmptyHeading': ['1.3.1', '2.4.6'],
            'ErrNoLabel': ['1.3.1', '3.3.2', '4.1.2'],
            'ErrInsufficientContrast': ['1.4.3'],
            'ErrNoPageTitle': ['2.4.2'],
            'ErrMissingLang': ['3.1.1'],
            # Add more mappings
        }
        
        return wcag_mapping.get(error_code, [])
```

## Test Script Details

### 1. Headings Test (`headings.js`)

**Tests For:**
- Empty headings
- Skipped heading levels
- Headings longer than 60 characters
- Multiple H1 elements
- Headings with mismatched visible/accessible text

**WCAG Criteria:**
- 1.3.1 Info and Relationships (Level A)
- 2.4.6 Headings and Labels (Level AA)

### 2. Images Test (`images.js`)

**Tests For:**
- Missing alt attributes
- Empty alt text on informative images
- Redundant alt text (e.g., "image of")
- Missing figure captions
- Decorative images not properly marked

**WCAG Criteria:**
- 1.1.1 Non-text Content (Level A)

### 3. Forms Test (`forms.js`)

**Tests For:**
- Input elements without labels
- Labels not properly associated
- Missing fieldset/legend for radio groups
- Required fields not indicated
- Missing error messages
- Placeholder text used as labels

**WCAG Criteria:**
- 1.3.1 Info and Relationships (Level A)
- 3.3.2 Labels or Instructions (Level A)
- 4.1.2 Name, Role, Value (Level A)

### 4. Landmarks Test (`landmarks.js`)

**Tests For:**
- Missing main landmark
- Multiple banner/contentinfo landmarks
- Improper nesting of landmarks
- Missing navigation landmarks
- Unnamed regions

**WCAG Criteria:**
- 1.3.1 Info and Relationships (Level A)
- 2.4.1 Bypass Blocks (Level A)

### 5. Color Test (`color.js`)

**Tests For:**
- Insufficient text contrast
- Link text contrast
- Focus indicator contrast
- Color as sole information conveyor

**WCAG Criteria:**
- 1.4.3 Contrast Minimum (Level AA)
- 1.4.6 Contrast Enhanced (Level AAA)
- 1.4.1 Use of Color (Level A)

## Advanced Integration

### Custom Script Injection

```python
class CustomScriptManager:
    """Manages custom accessibility test scripts"""
    
    async def add_custom_script(self, page, script_content: str):
        """Add custom test script to page"""
        await page.evaluateOnNewDocument(script_content)
    
    async def run_custom_test(self, page, function_name: str):
        """Run custom test function"""
        return await page.evaluate(f'{function_name}()')
```

### Script Caching

```python
class ScriptCache:
    """Caches compiled scripts for performance"""
    
    def __init__(self):
        self._cache = {}
    
    async def get_compiled_script(self, script_path: Path) -> str:
        """Get cached or compile script"""
        if script_path not in self._cache:
            with open(script_path, 'r') as f:
                self._cache[script_path] = f.read()
        return self._cache[script_path]
```

### Error Recovery

```python
class TestErrorHandler:
    """Handles JavaScript test execution errors"""
    
    async def safe_run_test(self, page, test_name: str) -> dict:
        """Run test with error recovery"""
        try:
            # Set timeout for test execution
            result = await asyncio.wait_for(
                page.evaluate(f'{test_name}()'),
                timeout=30.0
            )
            return result
            
        except asyncio.TimeoutError:
            return {
                'errors': [],
                'warnings': [],
                'passes': [],
                'timeout_error': f'Test {test_name} timed out'
            }
            
        except Exception as e:
            # Try to get partial results
            try:
                partial = await page.evaluate('''
                    () => {
                        return {
                            errors: window.a11y_errors || [],
                            warnings: window.a11y_warnings || [],
                            passes: window.a11y_passes || []
                        };
                    }
                ''')
                partial['partial_error'] = str(e)
                return partial
                
            except:
                return {
                    'errors': [],
                    'warnings': [],
                    'passes': [],
                    'fatal_error': str(e)
                }
```

## Performance Optimization

### 1. Script Bundling

```python
class ScriptBundler:
    """Bundles scripts for efficient injection"""
    
    def create_bundle(self, scripts: List[Path]) -> str:
        """Create single bundle from multiple scripts"""
        bundle = []
        for script_path in scripts:
            with open(script_path, 'r') as f:
                bundle.append(f'// Source: {script_path.name}\n')
                bundle.append(f.read())
                bundle.append('\n\n')
        
        return ''.join(bundle)
```

### 2. Parallel Test Execution

```python
class ParallelTestRunner:
    """Runs tests in parallel when possible"""
    
    async def run_independent_tests(self, page) -> dict:
        """Run non-conflicting tests in parallel"""
        # Tests that don't modify DOM can run in parallel
        independent_tests = [
            'headingsScrape',
            'imagesScrape',
            'languageScrape'
        ]
        
        tasks = [
            self.run_test(page, test)
            for test in independent_tests
        ]
        
        results = await asyncio.gather(*tasks)
        return dict(zip(independent_tests, results))
```

## Debugging

### Enable Debug Mode

```python
class DebugTestRunner:
    """Test runner with debug capabilities"""
    
    async def run_with_debug(self, page, test_name: str):
        """Run test with debug information"""
        
        # Inject debug helpers
        await page.evaluate('''
            window.a11y_debug = {
                logs: [],
                errors: [],
                log: function(msg) {
                    this.logs.push({
                        time: Date.now(),
                        message: msg
                    });
                    console.log('[A11Y]', msg);
                }
            };
        ''')
        
        # Run test
        result = await page.evaluate(f'{test_name}()')
        
        # Collect debug info
        debug_info = await page.evaluate('window.a11y_debug')
        
        return {
            'result': result,
            'debug': debug_info
        }
```

## Testing the Tests

### Unit Tests for JavaScript

```javascript
// test_headings.test.js
describe('Headings Test', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
    });
    
    test('detects empty heading', () => {
        document.body.innerHTML = '<h1></h1>';
        const result = headingsScrape();
        
        expect(result.errors).toHaveLength(1);
        expect(result.errors[0].err).toBe('ErrEmptyHeading');
    });
    
    test('detects skipped level', () => {
        document.body.innerHTML = '<h1>Title</h1><h3>Subtitle</h3>';
        const result = headingsScrape();
        
        expect(result.errors).toHaveLength(1);
        expect(result.errors[0].err).toBe('ErrSkippedHeadingLevel');
    });
});
```

### Integration Tests

```python
import pytest
from pyppeteer import launch

@pytest.mark.asyncio
async def test_headings_integration():
    """Test headings script integration"""
    browser = await launch(headless=True)
    page = await browser.newPage()
    
    # Load test HTML
    await page.setContent('''
        <html>
            <body>
                <h1>Main Title</h1>
                <h3>Skipped Level</h3>
                <h2></h2>
            </body>
        </html>
    ''')
    
    # Inject and run test
    injector = ScriptInjector()
    await injector.inject_scripts(page)
    
    result = await page.evaluate('headingsScrape()')
    
    assert len(result['errors']) == 2
    assert any(e['err'] == 'ErrEmptyHeading' for e in result['errors'])
    assert any(e['err'] == 'ErrSkippedLevel' for e in result['errors'])
    
    await browser.close()
```