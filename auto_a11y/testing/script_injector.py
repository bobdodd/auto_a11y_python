"""
JavaScript test script injection for browser context
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class ScriptInjector:
    """Manages JavaScript test script injection into browser pages"""
    
    # Script directory
    SCRIPT_DIR = Path(__file__).parent.parent / 'scripts'
    
    # Load order is important - dependencies first
    SCRIPT_LOAD_ORDER = [
        # Dependencies must be loaded first
        'tests/accessibleName.js',  # Required by many tests
        'tests/ariaRoles.js',       # ARIA role definitions
        'tests/colorContrast.js',   # Color contrast calculations
        'tests/xpath.js',           # XPath utilities
        'tests/a11yCodes.js',       # Error code definitions
        'tests/passTracking.js',    # Pass tracking helpers
        
        # Test scripts
        'tests/headings.js',
        'tests/images.js',
        'tests/forms2.js',
        'tests/landmarks.js',
        'tests/color.js',
        'tests/focus.js',
        'tests/language.js',
        'tests/pageTitle.js',
        'tests/tabindex.js',
        'tests/titleAttr.js',
        'tests/fonts.js',
        'tests/svg.js',
        'tests/pdf.js'
    ]
    
    # Map test names to their function names
    TEST_FUNCTIONS = {
        'headings': 'headingsScrape',
        'images': 'imagesScrape',
        'forms2': 'forms2Scrape',
        'landmarks': 'landmarksScrape',
        'color': 'colorScrape',
        'focus': 'focusScrape',
        'language': 'languageScrape',
        'pageTitle': 'pageTitleScrape',
        'tabindex': 'tabindexScrape',
        'titleAttr': 'titleAttrScrape',
        'fonts': 'fontsScrape',
        'svg': 'svgScrape',
        'pdf': 'pdfScrape'
    }
    
    def __init__(self):
        """Initialize script injector"""
        self.loaded_scripts = self._load_scripts()
        
    def _load_scripts(self) -> Dict[str, str]:
        """
        Load all JavaScript files into memory
        
        Returns:
            Dictionary mapping script paths to content
        """
        scripts = {}
        
        for script_path in self.SCRIPT_LOAD_ORDER:
            full_path = self.SCRIPT_DIR / script_path
            
            if not full_path.exists():
                logger.warning(f"Script not found: {full_path}")
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    scripts[script_path] = f.read()
                    logger.debug(f"Loaded script: {script_path}")
            except Exception as e:
                logger.error(f"Failed to load script {script_path}: {e}")
        
        return scripts
    
    async def inject_all_scripts(self, page) -> bool:
        """
        Inject all test scripts into a browser page
        
        Args:
            page: Pyppeteer page object
            
        Returns:
            True if all scripts injected successfully
        """
        try:
            # Inject scripts in order
            for script_path in self.SCRIPT_LOAD_ORDER:
                if script_path in self.loaded_scripts:
                    await page.evaluateOnNewDocument(self.loaded_scripts[script_path])
                    logger.debug(f"Injected script: {script_path}")
            
            # Add helper function to check if scripts are loaded
            await page.evaluateOnNewDocument('''
                window.a11yTestsLoaded = true;
                window.a11yTestFunctions = {
                    headings: typeof headingsScrape !== 'undefined',
                    images: typeof imagesScrape !== 'undefined',
                    forms2: typeof forms2Scrape !== 'undefined',
                    landmarks: typeof landmarksScrape !== 'undefined',
                    color: typeof colorScrape !== 'undefined',
                    focus: typeof focusScrape !== 'undefined',
                    language: typeof languageScrape !== 'undefined',
                    pageTitle: typeof pageTitleScrape !== 'undefined',
                    tabindex: typeof tabindexScrape !== 'undefined',
                    titleAttr: typeof titleAttrScrape !== 'undefined'
                };
            ''')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to inject scripts: {e}")
            return False
    
    async def inject_script_files(self, page) -> bool:
        """
        Inject scripts using file paths (alternative method)
        
        Args:
            page: Pyppeteer page object
            
        Returns:
            True if successful
        """
        try:
            for script_path in self.SCRIPT_LOAD_ORDER:
                full_path = self.SCRIPT_DIR / script_path
                if full_path.exists():
                    await page.addScriptTag({'path': str(full_path)})
                    logger.debug(f"Injected script file: {script_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to inject script files: {e}")
            return False
    
    async def run_test(self, page, test_name: str) -> Dict[str, Any]:
        """
        Run a specific test function on the page
        
        Args:
            page: Pyppeteer page object
            test_name: Name of test to run
            
        Returns:
            Test results dictionary
        """
        function_name = self.TEST_FUNCTIONS.get(test_name)
        if not function_name:
            raise ValueError(f"Unknown test: {test_name}")
        
        try:
            # Check if function exists
            exists = await page.evaluate(f'typeof {function_name} !== "undefined"')
            if not exists:
                raise RuntimeError(f"Test function {function_name} not found in page context")
            
            # Run the test
            result = await page.evaluate(f'{function_name}()')
            
            # Add metadata
            if isinstance(result, dict):
                result['test_name'] = test_name
                result['function_name'] = function_name
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to run test {test_name}: {e}")
            return {
                'test_name': test_name,
                'error': str(e),
                'errors': [],
                'warnings': [],
                'passes': []
            }
    
    async def run_all_tests(self, page) -> Dict[str, Dict[str, Any]]:
        """
        Run all available tests on the page
        
        Args:
            page: Pyppeteer page object
            
        Returns:
            Dictionary mapping test names to results
        """
        results = {}
        
        for test_name in self.TEST_FUNCTIONS.keys():
            try:
                result = await self.run_test(page, test_name)
                results[test_name] = result
                logger.debug(f"Completed test: {test_name}")
            except Exception as e:
                logger.error(f"Test {test_name} failed: {e}")
                results[test_name] = {
                    'test_name': test_name,
                    'error': str(e),
                    'errors': [],
                    'warnings': [],
                    'passes': []
                }
        
        return results
    
    def get_available_tests(self) -> List[str]:
        """
        Get list of available tests
        
        Returns:
            List of test names
        """
        return list(self.TEST_FUNCTIONS.keys())