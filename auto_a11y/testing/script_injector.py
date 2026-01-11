"""
JavaScript test script injection for browser context

Uses Playwright for browser automation.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from playwright.async_api import Page

logger = logging.getLogger(__name__)


class ScriptInjector:
    """Manages JavaScript test script injection into browser pages"""
    
    # Script directory
    SCRIPT_DIR = Path(__file__).parent.parent / 'scripts'
    
    # Utility scripts needed by Python tests that use page.evaluate()
    SCRIPT_LOAD_ORDER = [
        'tests/accessibleName.js',  # Required by many tests
        'tests/ariaRoles.js',       # ARIA role definitions
        'tests/colorContrast.js',   # Color contrast calculations
        'tests/xpath.js',           # XPath utilities
    ]
    
    # No JavaScript tests remain - all replaced by Python touchpoint tests
    TEST_FUNCTIONS = {}
    
    def __init__(self, test_config=None):
        """Initialize script injector
        
        Args:
            test_config: TestConfiguration instance for enabling/disabling tests
        """
        self.test_config = test_config
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
                    # Script loaded successfully - no need to log each one
            except Exception as e:
                logger.error(f"Failed to load script {script_path}: {e}")
        
        return scripts
    
    async def inject_all_scripts(self, page: Page) -> bool:
        """
        Inject all test scripts into a browser page

        Args:
            page: Playwright Page object

        Returns:
            True if all scripts injected successfully
        """
        try:
            # Inject scripts in order using Playwright's add_init_script
            for script_path in self.SCRIPT_LOAD_ORDER:
                if script_path in self.loaded_scripts:
                    await page.add_init_script(self.loaded_scripts[script_path])
                    # Script injected - silent unless error

            # Inject configuration for tests to use
            # Use project_config if available, otherwise use defaults
            title_limit = 60
            heading_limit = 60
            if hasattr(self, 'project_config') and self.project_config:
                title_limit = self.project_config.get('titleLengthLimit', 60)
                heading_limit = self.project_config.get('headingLengthLimit', 60)

            config_js = f'''
                window.a11yConfig = {{
                    titleLengthLimit: {title_limit},
                    headingLengthLimit: {heading_limit}
                }};
            '''
            await page.add_init_script(config_js)

            # Add helper function to check if scripts are loaded
            await page.add_init_script('''
                window.a11yTestsLoaded = true;
                window.a11yTestFunctions = {};
                // All legacy JS tests removed - replaced by Python touchpoint tests
            ''')

            return True

        except Exception as e:
            logger.error(f"Failed to inject scripts: {e}")
            return False
    
    async def inject_script_files(self, page: Page) -> bool:
        """
        Inject scripts using file paths (alternative method)

        Args:
            page: Playwright Page object

        Returns:
            True if successful
        """
        try:
            already_injected = await page.evaluate('() => window.__a11y_scripts_injected === true')
            if already_injected:
                logger.debug("Scripts already injected, skipping re-injection")
                return True

            import asyncio
            for script_path in self.SCRIPT_LOAD_ORDER:
                full_path = self.SCRIPT_DIR / script_path
                if full_path.exists():
                    logger.debug(f"Injecting script: {script_path}")
                    await page.add_script_tag(path=str(full_path))
                    # Verify connection after each script injection
                    await asyncio.sleep(0.05)

            logger.debug("DEBUG inject_script_files: All scripts injected, setting flag")
            await page.evaluate('() => { window.__a11y_scripts_injected = true; }')

            # Brief pause to let injected scripts initialize
            await asyncio.sleep(0.2)

            # Verify page is still responsive
            try:
                await asyncio.wait_for(page.evaluate('() => true'), timeout=2.0)
                logger.debug("DEBUG inject_script_files: Page connection verified after injection")
            except Exception as verify_err:
                logger.error(f"Page connection lost after script injection: {verify_err}")
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to inject script files: {e}")
            return False
    
    async def run_test(self, page: Page, test_name: str) -> Dict[str, Any]:
        """
        Run a specific test function on the page

        Args:
            page: Playwright Page object
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
    
    async def run_all_tests(self, page: Page) -> Dict[str, Dict[str, Any]]:
        """
        Run all available tests on the page (JavaScript and Python-based)

        Args:
            page: Playwright Page object

        Returns:
            Dictionary mapping test names to results
        """
        results = {}
        
        # Import test config if not provided
        if self.test_config is None:
            from auto_a11y.config.test_config import get_test_config
            self.test_config = get_test_config()

        # Check global enable
        if not self.test_config.config.get("global", {}).get("enabled", True):
            logger.info("All tests are disabled globally")
            return results

        # Run JavaScript-based tests if enabled
        if self.test_config.config.get("global", {}).get("run_javascript_tests", True):
            for test_name in self.TEST_FUNCTIONS.keys():
                # Map test to touchpoint
                touchpoint = self._get_touchpoint_for_js_test(test_name)

                # Check if test is enabled
                if self.test_config.is_test_enabled(test_name, touchpoint):
                    try:
                        result = await self.run_test(page, test_name)
                        results[test_name] = result
                        # Test completed
                    except Exception as e:
                        logger.error(f"Test {test_name} failed: {e}")
                        results[test_name] = {
                            'test_name': test_name,
                            'error': str(e),
                            'errors': [],
                            'warnings': [],
                            'passes': []
                        }
                else:
                    logger.debug(f"Skipping disabled JavaScript test: {test_name}")
        else:
            logger.info("JavaScript tests are disabled globally")

        # Run Python-based touchpoint tests if enabled
        if self.test_config.config.get("global", {}).get("run_python_tests", True):
            try:
                from auto_a11y.testing.touchpoint_tests import TOUCHPOINT_TESTS
                from auto_a11y.config.touchpoint_tests import get_touchpoint_for_test
                
                logger.debug(f"DEBUG run_all_tests: Starting Python touchpoint tests, {len(TOUCHPOINT_TESTS)} tests available")
                test_count = 0
                import asyncio
                for touchpoint_id, test_func in TOUCHPOINT_TESTS.items():
                    # Check if touchpoint is enabled
                    if self.test_config.is_touchpoint_enabled(touchpoint_id):
                        try:
                            # Verify connection before each test
                            try:
                                await asyncio.wait_for(page.evaluate('() => true'), timeout=2.0)
                            except Exception as conn_err:
                                logger.error(f"DEBUG: Connection DEAD before test {touchpoint_id}: {conn_err}")
                                break
                            
                            # Run the Python-based test
                            test_count += 1
                            logger.debug(f"DEBUG run_all_tests: Running test #{test_count}: {touchpoint_id}")
                            result = await test_func(page)
                            
                            # Filter results based on individual test settings AND fixture validation
                            if 'errors' in result:
                                filtered_errors = []
                                for error in result['errors']:
                                    error_code = error.get('err', '')
                                    # Check both: is test enabled in config AND did it pass fixture validation?
                                    if (self.test_config.is_test_enabled(error_code, touchpoint_id) and
                                        self.test_config.is_test_available_by_fixture(error_code)):
                                        filtered_errors.append(error)
                                    else:
                                        logger.debug(f"Filtering out {error_code}: enabled={self.test_config.is_test_enabled(error_code, touchpoint_id)}, passed_fixtures={self.test_config.is_test_available_by_fixture(error_code)}")
                                result['errors'] = filtered_errors

                            if 'warnings' in result:
                                filtered_warnings = []
                                for warning in result['warnings']:
                                    error_code = warning.get('err', '')
                                    # Check both: is test enabled in config AND did it pass fixture validation?
                                    if (self.test_config.is_test_enabled(error_code, touchpoint_id) and
                                        self.test_config.is_test_available_by_fixture(error_code)):
                                        filtered_warnings.append(warning)
                                    else:
                                        logger.debug(f"Filtering out {error_code}: enabled={self.test_config.is_test_enabled(error_code, touchpoint_id)}, passed_fixtures={self.test_config.is_test_available_by_fixture(error_code)}")
                                result['warnings'] = filtered_warnings

                            if 'info' in result:
                                filtered_info = []
                                for info_item in result['info']:
                                    error_code = info_item.get('err', '')
                                    # Check both: is test enabled in config AND did it pass fixture validation?
                                    if (self.test_config.is_test_enabled(error_code, touchpoint_id) and
                                        self.test_config.is_test_available_by_fixture(error_code)):
                                        filtered_info.append(info_item)
                                    else:
                                        logger.debug(f"Filtering out {error_code}: enabled={self.test_config.is_test_enabled(error_code, touchpoint_id)}, passed_fixtures={self.test_config.is_test_available_by_fixture(error_code)}")
                                result['info'] = filtered_info

                            if 'discovery' in result:
                                filtered_discovery = []
                                for discovery_item in result['discovery']:
                                    error_code = discovery_item.get('err', '')
                                    # Check both: is test enabled in config AND did it pass fixture validation?
                                    if (self.test_config.is_test_enabled(error_code, touchpoint_id) and
                                        self.test_config.is_test_available_by_fixture(error_code)):
                                        filtered_discovery.append(discovery_item)
                                    else:
                                        logger.debug(f"Filtering out {error_code}: enabled={self.test_config.is_test_enabled(error_code, touchpoint_id)}, passed_fixtures={self.test_config.is_test_available_by_fixture(error_code)}")
                                result['discovery'] = filtered_discovery

                            # Override JavaScript test results if the Python version exists
                            # This allows gradual migration from JS to Python tests
                            if touchpoint_id in results:
                                logger.debug(f"Replacing JS test {touchpoint_id} with Python version")
                            
                            results[touchpoint_id] = result
                            
                        except Exception as e:
                            error_msg = str(e)
                            is_connection_error = any(x in error_msg for x in [
                                'Session closed', 'Protocol Error', 'Target closed',
                                'Connection closed', 'Page crashed'
                            ])
                            
                            if is_connection_error:
                                logger.error(f"Browser connection lost during {touchpoint_id}: {error_msg}")
                                results[touchpoint_id] = {
                                    'test_name': touchpoint_id,
                                    'error': str(e),
                                    'errors': [],
                                    'warnings': [],
                                    'passes': []
                                }
                                logger.warning("Stopping test execution due to browser connection loss")
                                break  # Stop testing - browser is gone
                            else:
                                logger.error(f"Python touchpoint test {touchpoint_id} failed: {e}", exc_info=True)
                                results[touchpoint_id] = {
                                    'test_name': touchpoint_id,
                                    'error': str(e),
                                    'errors': [],
                                    'warnings': [],
                                    'passes': []
                                }
                    else:
                        logger.debug(f"Skipping disabled touchpoint: {touchpoint_id}")
                    
            except ImportError as e:
                logger.warning(f"Could not import touchpoint tests: {e}")
        else:
            logger.info("Python tests are disabled globally")
        
        return results
    
    def _get_touchpoint_for_js_test(self, test_name: str) -> str:
        """
        Map JavaScript test name to touchpoint
        
        Args:
            test_name: JavaScript test name
            
        Returns:
            Touchpoint ID
        """
        # Map JavaScript test names to touchpoints
        js_test_to_touchpoint = {
            'headings': 'headings',
            'images': 'images',
            'forms2': 'forms',
            'landmarks': 'landmarks',
            'color': 'colors_contrast',
            'focus': 'focus_management',
            'language': 'language',
            'pageTitle': 'semantic_structure',
            'tabindex': 'keyboard_navigation',
            'titleAttr': 'semantic_structure',
            'fonts': 'fonts',
            'svg': 'images',
            'pdf': 'documents'
        }
        
        return js_test_to_touchpoint.get(test_name, 'general')
    
    def get_available_tests(self) -> List[str]:
        """
        Get list of available tests
        
        Returns:
            List of test names
        """
        return list(self.TEST_FUNCTIONS.keys())