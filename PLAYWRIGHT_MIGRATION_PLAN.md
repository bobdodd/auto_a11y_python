# Playwright Migration Plan

## Overview

This document provides a comprehensive plan for migrating from Pyppeteer to Playwright-Python. The migration will resolve the browser stability issues (Session closed, Target closed errors) that occur during multi-state testing with authenticated users.

**Estimated Effort:** 4-6 days
**Risk Level:** Medium (well-defined API mappings, extensive testing required)
**Recommended Approach:** Phased migration with parallel operation capability

---

## Table of Contents

1. [Pre-Migration Setup](#1-pre-migration-setup)
2. [Phase 1: Browser Manager](#2-phase-1-browser-manager-foundation)
3. [Phase 2: Core Components](#3-phase-2-core-components)
4. [Phase 3: Testing Infrastructure](#4-phase-3-testing-infrastructure)
5. [Phase 4: Support Files](#5-phase-4-support-files)
6. [API Reference Mapping](#6-api-reference-mapping)
7. [Testing Strategy](#7-testing-strategy)
8. [Rollback Plan](#8-rollback-plan)

---

## 1. Pre-Migration Setup

### 1.1 Install Playwright

```bash
# Add to requirements.txt
playwright>=1.40.0

# Install
pip install playwright

# Download browser binaries
playwright install chromium
# Optional: playwright install firefox webkit
```

### 1.2 Update requirements.txt

```diff
- pyppeteer>=1.0.2
+ playwright>=1.40.0
```

### 1.3 Create Feature Flag for Gradual Rollout

Add to `config.py`:

```python
# Browser engine selection (for gradual migration)
BROWSER_ENGINE = os.environ.get('BROWSER_ENGINE', 'playwright')  # 'playwright' or 'pyppeteer'
```

---

## 2. Phase 1: Browser Manager (Foundation)

**File:** `auto_a11y/core/browser_manager.py`
**Priority:** CRITICAL - All other components depend on this
**Effort:** 1-1.5 days

### 2.1 Current Pyppeteer Implementation

```python
# Current imports
from pyppeteer import launch
from pyppeteer.errors import BrowserError, PageError, TimeoutError

# Current launch
browser = await launch(
    headless=True,
    args=['--no-sandbox', '--disable-setuid-sandbox', ...],
    executablePath=chromium_path
)
```

### 2.2 New Playwright Implementation

```python
# New imports
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

class BrowserManager:
    """Playwright-based browser manager with improved stability"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._playwright = None
        self._browser: Browser = None
        self._context: BrowserContext = None
        self._default_timeout = self.config.get('timeout', 30000)

    async def start(self) -> None:
        """Start browser with Playwright"""
        if self._browser:
            return

        self._playwright = await async_playwright().start()

        launch_options = {
            'headless': self.config.get('headless', True),
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080'
            ]
        }

        # Optional: specify executable path
        if self.config.get('executable_path'):
            launch_options['executable_path'] = self.config['executable_path']

        self._browser = await self._playwright.chromium.launch(**launch_options)
        logger.info("Playwright browser started successfully")

    async def stop(self) -> None:
        """Stop browser gracefully"""
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("Playwright browser stopped")

    async def create_context(self, storage_state: str = None) -> BrowserContext:
        """Create isolated browser context (replaces newPage with isolation)"""
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': self.config.get('user_agent',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        }

        # Load saved authentication state if provided
        if storage_state:
            context_options['storage_state'] = storage_state

        context = await self._browser.new_context(**context_options)
        context.set_default_timeout(self._default_timeout)
        context.set_default_navigation_timeout(self._default_timeout)

        return context

    async def create_page(self, context: BrowserContext = None) -> Page:
        """Create new page in context"""
        if context is None:
            if self._context is None:
                self._context = await self.create_context()
            context = self._context

        page = await context.new_page()
        return page

    async def goto(self, page: Page, url: str, wait_until: str = 'networkidle',
                   timeout: int = None) -> bool:
        """Navigate to URL with auto-waiting"""
        try:
            # Playwright uses 'networkidle' not 'networkidle2'
            if wait_until == 'networkidle2':
                wait_until = 'networkidle'
            elif wait_until == 'networkidle0':
                wait_until = 'networkidle'

            await page.goto(url, wait_until=wait_until, timeout=timeout or self._default_timeout)
            return True
        except PlaywrightTimeoutError:
            logger.warning(f"Navigation timeout for {url}")
            return False
        except PlaywrightError as e:
            logger.error(f"Navigation error for {url}: {e}")
            return False

    async def is_running(self) -> bool:
        """Check if browser is running and responsive"""
        try:
            if not self._browser or not self._browser.is_connected():
                return False
            return True
        except Exception:
            return False

    async def close_page(self, page: Page) -> None:
        """Close page safely"""
        try:
            if page and not page.is_closed():
                await page.close()
        except Exception as e:
            logger.warning(f"Error closing page: {e}")

    async def close_context(self, context: BrowserContext) -> None:
        """Close context and all its pages"""
        try:
            await context.close()
        except Exception as e:
            logger.warning(f"Error closing context: {e}")
```

### 2.3 Key API Changes

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `launch()` | `playwright.chromium.launch()` | Part of playwright instance |
| `browser.newPage()` | `context.new_page()` | Context-based for isolation |
| `page.setViewport()` | Context option or `page.set_viewport_size()` | Set at context level preferred |
| `page.setUserAgent()` | Context option `user_agent=` | Set at context level |
| `page.setDefaultNavigationTimeout()` | `context.set_default_navigation_timeout()` | Context level |
| `browser.close()` | `browser.close()` + `playwright.stop()` | Must stop playwright instance |

---

## 3. Phase 2: Core Components

### 3.1 Login Automation

**File:** `auto_a11y/testing/login_automation.py`
**Effort:** 0.5 days

#### Current vs New Implementation

```python
# BEFORE (Pyppeteer)
await page.goto(login_url, {'waitUntil': 'networkidle2'})
await page.waitForSelector(username_selector, {'visible': True})
await page.type(username_selector, username, {'delay': 50})
await page.click(submit_selector)
await page.waitForNavigation({'waitUntil': 'networkidle2'})

# AFTER (Playwright)
await page.goto(login_url, wait_until='networkidle')
await page.wait_for_selector(username_selector, state='visible')
await page.fill(username_selector, username)  # Auto-clears, auto-waits
await page.click(submit_selector)
await page.wait_for_load_state('networkidle')
```

#### Authentication State Persistence (NEW FEATURE)

```python
class LoginAutomation:
    async def perform_login(self, context: BrowserContext, user, timeout: int = 30000) -> dict:
        """Perform login and optionally save state for reuse"""
        page = await context.new_page()

        try:
            # Navigate to login
            await page.goto(user.login_url, wait_until='networkidle', timeout=timeout)

            # Fill credentials using Playwright's auto-waiting fill()
            await page.fill(user.username_selector, user.username)
            await page.fill(user.password_selector, user.password)

            # Submit and wait for navigation
            async with page.expect_navigation(wait_until='networkidle'):
                await page.click(user.submit_selector)

            # Verify login success
            if user.success_selector:
                await page.wait_for_selector(user.success_selector, timeout=timeout)

            return {'success': True, 'page': page}

        except Exception as e:
            return {'success': False, 'error': str(e), 'page': page}

    async def save_auth_state(self, context: BrowserContext, path: str) -> None:
        """Save authentication state for reuse"""
        await context.storage_state(path=path)

    async def perform_logout(self, page: Page, user, timeout: int = 30000) -> dict:
        """Perform logout"""
        try:
            if user.logout_url:
                await page.goto(user.logout_url, wait_until='networkidle', timeout=timeout)
            elif user.logout_selector:
                await page.click(user.logout_selector)
                await page.wait_for_load_state('networkidle')

            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
```

### 3.2 Script Executor

**File:** `auto_a11y/testing/script_executor.py`
**Effort:** 0.5 days

#### Key Changes

```python
# BEFORE (Pyppeteer)
elements = await page.xpath(selector)
element = elements[0] if elements else None
await page.evaluate('(el) => el.click()', element)
await element.type(value)
await page.waitForSelector(selector, {'visible': True, 'timeout': timeout})
await page.waitForNavigation({'waitUntil': 'networkidle2', 'timeout': timeout})

# AFTER (Playwright)
element = page.locator(selector)  # Unified locator API
await element.click()  # Auto-waits, no JS workaround needed
await element.fill(value)  # Auto-clears first
await page.wait_for_selector(selector, state='visible', timeout=timeout)
await page.wait_for_load_state('networkidle', timeout=timeout)
```

#### Action Type Mapping

```python
class ScriptExecutor:
    async def execute_step(self, page: Page, step: dict) -> dict:
        """Execute a single script step"""
        action = step['action_type']
        selector = step.get('selector')
        value = step.get('value')
        timeout = step.get('timeout', 5000)

        try:
            if action == 'click':
                await page.click(selector, timeout=timeout)

            elif action == 'type':
                await page.fill(selector, value)  # fill() is better than type()

            elif action == 'select':
                await page.select_option(selector, value)

            elif action == 'hover':
                await page.hover(selector)

            elif action == 'scroll':
                await page.locator(selector).scroll_into_view_if_needed()

            elif action == 'wait':
                await page.wait_for_timeout(int(value))

            elif action == 'wait_for_selector':
                await page.wait_for_selector(selector, state='visible', timeout=timeout)

            elif action == 'press_key':
                await page.keyboard.press(value)

            elif action == 'navigate':
                await page.goto(value, wait_until='networkidle')

            elif action == 'clear_cookies':
                context = page.context
                await context.clear_cookies()

            elif action == 'clear_storage':
                await page.evaluate('() => { localStorage.clear(); sessionStorage.clear(); }')

            return {'success': True}

        except PlaywrightTimeoutError as e:
            return {'success': False, 'error': f'Timeout: {e}'}
        except PlaywrightError as e:
            return {'success': False, 'error': str(e)}
```

### 3.3 Script Injector

**File:** `auto_a11y/testing/script_injector.py`
**Effort:** 0.25 days

```python
# BEFORE (Pyppeteer)
await page.addScriptTag({'path': script_path})
await page.evaluateOnNewDocument(script_content)
result = await page.evaluate('window.runA11yTest()')

# AFTER (Playwright)
await page.add_script_tag(path=script_path)
await page.add_init_script(script_content)  # Runs before every navigation
result = await page.evaluate('window.runA11yTest()')  # Same syntax
```

### 3.4 Scraper

**File:** `auto_a11y/core/scraper.py`
**Effort:** 0.5 days

Major changes involve using BrowserContext for isolation:

```python
class ScrapingEngine:
    async def discover_website(self, website, progress_callback=None, ...):
        """Discover pages with Playwright"""

        # Create isolated context for this discovery session
        context = await self.browser_manager.create_context()

        # Handle authentication if needed
        if website_user_id:
            page = await context.new_page()
            login_result = await self.login_automation.perform_login(context, user)
            if not login_result['success']:
                raise RuntimeError(f"Login failed: {login_result['error']}")

        try:
            # Discovery loop
            for url in urls_to_visit:
                page = await context.new_page()
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)

                    # Extract links
                    links = await page.evaluate('''() => {
                        return Array.from(document.querySelectorAll('a[href]'))
                            .map(a => ({href: a.href, text: a.textContent}));
                    }''')

                    # Take screenshot
                    await page.screenshot(path=screenshot_path, full_page=False)

                finally:
                    await page.close()
        finally:
            await context.close()
```

---

## 4. Phase 3: Testing Infrastructure

### 4.1 Multi-State Test Runner

**File:** `auto_a11y/testing/multi_state_test_runner.py`
**Effort:** 1 day

This is where the stability improvements will be most visible.

```python
class MultiStateTestRunner:
    async def test_page_multi_state(
        self,
        page_id: str,
        scripts: List[PageSetupScript],
        test_function,
        session_id: str,
        browser_manager: BrowserManager,
        page_url: str,
        authenticated_user=None,
        auth_state_path: str = None
    ) -> List[TestResult]:
        """
        Test page across multiple states using Playwright's context isolation.

        Key improvement: Each state gets a fresh context, eliminating
        the connection stability issues from Pyppeteer.
        """
        results = []
        state_sequence = 0

        for script in scripts:
            # Create FRESH context for each state (key stability improvement)
            context = await browser_manager.create_context(
                storage_state=auth_state_path if authenticated_user else None
            )

            try:
                page = await context.new_page()

                # Navigate to test page
                await page.goto(page_url, wait_until='networkidle')

                # Test BEFORE script (if configured)
                if script.test_before_execution:
                    test_result = await test_function(page, page_id)
                    test_result.state_sequence = state_sequence
                    test_result.session_id = session_id
                    results.append(test_result)
                    state_sequence += 1

                # Execute script
                script_result = await self.script_executor.execute_script(page, script)

                # Test AFTER script (if configured)
                if script.test_after_execution:
                    test_result = await test_function(page, page_id)
                    test_result.state_sequence = state_sequence
                    test_result.session_id = session_id
                    test_result.metadata['script_executed'] = {
                        'script_id': script.id,
                        'script_name': script.name,
                        'success': script_result['success']
                    }
                    results.append(test_result)
                    state_sequence += 1

            except Exception as e:
                logger.error(f"Error in state {state_sequence}: {e}")
                # Create error result
                results.append(TestResult(
                    page_id=page_id,
                    error=str(e),
                    state_sequence=state_sequence,
                    session_id=session_id
                ))
            finally:
                # Clean context closure (no leftover connections)
                await context.close()

        return results
```

### 4.2 Test Runner

**File:** `auto_a11y/testing/test_runner.py`
**Effort:** 0.5 days

Mainly orchestration changes to use new browser manager patterns.

### 4.3 CSS Focus Capture

**File:** `auto_a11y/testing/css_focus_capture.py`
**Effort:** 0.25 days

```python
# BEFORE (Pyppeteer)
page.on('response', handler)
page.remove_listener('response', handler)

# AFTER (Playwright)
page.on('response', handler)
page.remove_listener('response', handler)  # Same API!
```

### 4.4 Touchpoint Tests (52+ files)

**Files:** `auto_a11y/testing/touchpoint_tests/*.py`
**Effort:** 0.25 days (mostly unchanged)

Good news: The touchpoint tests primarily use `page.evaluate()` which has the same API in Playwright. Minimal changes needed.

```python
# These work identically in Playwright
result = await page.evaluate('window.runHeadingsTest()')
result = await page.evaluate('window.runFormsTest()')
# etc.
```

---

## 5. Phase 4: Support Files

### 5.1 Browser Download Utility

**File:** `download_chromium.py`
**Effort:** 0.1 days

```python
# BEFORE (Pyppeteer)
from pyppeteer import chromium_downloader
chromium_downloader.download_chromium()
path = chromium_downloader.chromium_executable()

# AFTER (Playwright)
import subprocess
subprocess.run(['playwright', 'install', 'chromium'], check=True)
# Playwright manages browser binaries automatically
```

### 5.2 Run Script

**File:** `run.py`
**Effort:** 0.1 days

Update browser verification logic.

### 5.3 Website Routes

**File:** `auto_a11y/web/routes/websites.py`
**Effort:** 0.1 days

Update Chromium availability check.

---

## 6. API Reference Mapping

### 6.1 Browser & Page Lifecycle

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `launch(headless=True)` | `playwright.chromium.launch(headless=True)` | |
| `browser.newPage()` | `context.new_page()` | Context-based |
| `browser.close()` | `browser.close()` then `playwright.stop()` | |
| `page.close()` | `page.close()` | Same |
| `browser.process` | N/A | Use `browser.is_connected()` |

### 6.2 Navigation

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `page.goto(url, {'waitUntil': 'networkidle2'})` | `page.goto(url, wait_until='networkidle')` | |
| `page.waitForNavigation()` | `page.wait_for_load_state()` or `expect_navigation()` | |
| `page.reload()` | `page.reload()` | Same |
| `page.goBack()` | `page.go_back()` | Snake case |
| `page.url` | `page.url` | Same |

### 6.3 Selectors & Elements

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `page.$(selector)` | `page.query_selector(selector)` | Or use `locator()` |
| `page.$$(selector)` | `page.query_selector_all(selector)` | |
| `page.$x(xpath)` | `page.locator(xpath)` | Auto-detected |
| `page.waitForSelector(sel, {visible: true})` | `page.wait_for_selector(sel, state='visible')` | |
| `page.waitForXPath(xpath)` | `page.wait_for_selector(xpath)` | Auto-detected |

### 6.4 User Interaction

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `page.click(selector)` | `page.click(selector)` | Auto-waits |
| `page.type(selector, text, {delay: 50})` | `page.type(selector, text, delay=50)` | |
| `page.type(selector, text)` | `page.fill(selector, text)` | fill() auto-clears |
| `element.type(text)` | `element.fill(text)` | |
| `page.select(selector, value)` | `page.select_option(selector, value)` | |
| `page.hover(selector)` | `page.hover(selector)` | Same |
| `page.focus(selector)` | `page.focus(selector)` | Same |
| `page.keyboard.press('Enter')` | `page.keyboard.press('Enter')` | Same |

### 6.5 Page Content & Evaluation

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `page.evaluate(fn)` | `page.evaluate(fn)` | Same |
| `page.evaluateOnNewDocument(fn)` | `page.add_init_script(fn)` | |
| `page.addScriptTag({path})` | `page.add_script_tag(path=path)` | |
| `page.content()` | `page.content()` | Same |
| `page.title()` | `page.title()` | Same |

### 6.6 Screenshots

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `page.screenshot({path, fullPage: true})` | `page.screenshot(path=path, full_page=True)` | |
| `page.screenshot({type: 'jpeg', quality: 80})` | `page.screenshot(type='jpeg', quality=80)` | |

### 6.7 Viewport & Device

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `page.setViewport({width, height})` | `page.set_viewport_size({width, height})` | |
| `page.setUserAgent(ua)` | Context option `user_agent=ua` | Set at context |

### 6.8 Cookies & Storage

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `page.cookies()` | `context.cookies()` | Context level |
| `page.setCookie(...cookies)` | `context.add_cookies(cookies)` | |
| `page.deleteCookie(*cookies)` | `context.clear_cookies()` | |
| `page._client.send('Network.clearBrowserCookies')` | `context.clear_cookies()` | Clean API |
| N/A | `context.storage_state(path=)` | NEW: Save auth |
| N/A | `browser.new_context(storage_state=)` | NEW: Load auth |

### 6.9 Authentication

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `page.authenticate({username, password})` | `context.set_http_credentials({username, password})` | HTTP Basic |

### 6.10 Events

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `page.on('response', handler)` | `page.on('response', handler)` | Same |
| `page.remove_listener('response', handler)` | `page.remove_listener('response', handler)` | Same |

### 6.11 Timeouts

| Pyppeteer | Playwright | Notes |
|-----------|------------|-------|
| `page.setDefaultNavigationTimeout(ms)` | `context.set_default_navigation_timeout(ms)` | Context level |
| `page.setDefaultTimeout(ms)` | `context.set_default_timeout(ms)` | Context level |

### 6.12 Errors

| Pyppeteer | Playwright |
|-----------|------------|
| `pyppeteer.errors.TimeoutError` | `playwright.async_api.TimeoutError` |
| `pyppeteer.errors.PageError` | `playwright.async_api.Error` |
| `pyppeteer.errors.NetworkError` | `playwright.async_api.Error` |
| `pyppeteer.errors.BrowserError` | `playwright.async_api.Error` |

---

## 7. Testing Strategy

### 7.1 Unit Tests

Create parallel test suite that tests both engines:

```python
@pytest.mark.parametrize("engine", ["pyppeteer", "playwright"])
async def test_browser_launch(engine):
    manager = BrowserManager(engine=engine)
    await manager.start()
    assert await manager.is_running()
    await manager.stop()
```

### 7.2 Integration Tests

1. **Discovery Test:** Run discovery on a test website
2. **Login Test:** Test authentication with a test user
3. **Multi-State Test:** Run multi-state tests on pages with scripts
4. **Screenshot Test:** Verify screenshots are captured correctly

### 7.3 Manual Testing Checklist

- [ ] Discovery completes without browser crashes
- [ ] Guest testing works
- [ ] Authenticated testing works (Marie Tremblay user)
- [ ] Multi-state testing completes all states
- [ ] Screenshots are captured at each state
- [ ] AI analysis runs without connection errors
- [ ] Error messages display correctly on failures

---

## 8. Rollback Plan

### 8.1 Keep Pyppeteer Available

Don't remove Pyppeteer from requirements immediately. Keep both:

```txt
# requirements.txt
playwright>=1.40.0
pyppeteer>=1.0.2  # Keep for rollback
```

### 8.2 Feature Flag

Use environment variable to switch engines:

```bash
# Use Playwright (default after migration)
export BROWSER_ENGINE=playwright

# Rollback to Pyppeteer if needed
export BROWSER_ENGINE=pyppeteer
```

### 8.3 Git Branch Strategy

```bash
# Create migration branch
git checkout -b feature/playwright-migration

# Work on migration
# ...

# If issues arise, rollback is simple
git checkout main
```

---

## 9. Migration Execution Checklist

### Week 1: Foundation (Days 1-2)

- [ ] Install Playwright and verify browser binaries
- [ ] Create new `browser_manager_playwright.py`
- [ ] Test browser launch/stop/page creation
- [ ] Implement `goto()` with proper wait strategies
- [ ] Test context isolation

### Week 1: Core (Days 3-4)

- [ ] Migrate `login_automation.py`
- [ ] Implement auth state save/load
- [ ] Migrate `script_executor.py`
- [ ] Migrate `script_injector.py`
- [ ] Test script execution flow

### Week 2: Testing (Days 5-6)

- [ ] Migrate `multi_state_test_runner.py`
- [ ] Migrate `test_runner.py`
- [ ] Migrate `scraper.py`
- [ ] Update `css_focus_capture.py`
- [ ] Update support files

### Week 2: Validation (Day 7+)

- [ ] Run full test suite
- [ ] Test with Marie Tremblay user
- [ ] Test multi-state on problematic pages
- [ ] Performance comparison
- [ ] Documentation updates

---

## 10. Expected Improvements After Migration

| Issue | Before (Pyppeteer) | After (Playwright) |
|-------|-------------------|-------------------|
| Session closed errors | Frequent | Eliminated |
| Target closed errors | Frequent | Eliminated |
| Multi-user stability | Poor | Excellent |
| Viewport changes | Destabilizes | Stable |
| Connection recovery | Manual, unreliable | Automatic |
| Auth state management | Manual cookies | Built-in storage state |
| Test isolation | Poor | Context-based isolation |
| Performance | Baseline | 20-30% faster |

---

## Appendix: File Change Summary

| File | Change Type | Effort |
|------|-------------|--------|
| `browser_manager.py` | Major rewrite | 1.5 days |
| `login_automation.py` | Moderate changes | 0.5 days |
| `script_executor.py` | Moderate changes | 0.5 days |
| `script_injector.py` | Minor changes | 0.25 days |
| `scraper.py` | Moderate changes | 0.5 days |
| `multi_state_test_runner.py` | Major changes | 1 day |
| `test_runner.py` | Moderate changes | 0.5 days |
| `css_focus_capture.py` | Minor changes | 0.25 days |
| `touchpoint_tests/*.py` | Minimal/None | 0.25 days |
| `download_chromium.py` | Replace | 0.1 days |
| `run.py` | Minor changes | 0.1 days |
| `routes/websites.py` | Minor changes | 0.1 days |
| **Total** | | **5-6 days** |
