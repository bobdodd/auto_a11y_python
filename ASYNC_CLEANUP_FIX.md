# Async Event Loop Cleanup Fix

## Problem
Runtime error occurring when running tests with AI analysis enabled:
```
RuntimeError: Event loop is closed
```

The error was happening in the httpx client (used internally by the Anthropic SDK) when trying to close connections after the main event loop had already been closed.

## Root Cause
The Claude AI client (AsyncAnthropic) was not being properly closed after use, leaving async connections open. When Python's event loop closed at the end of execution, these connections tried to close themselves but the event loop was already gone.

## Solution

### 1. Added Cleanup Method to Claude Client
**File:** `/auto_a11y/ai/claude_client.py`

Added an `aclose()` method to properly close the async client:
```python
async def aclose(self):
    """Close the async client properly"""
    try:
        if hasattr(self.async_client, '_client'):
            await self.async_client._client.aclose()
    except Exception as e:
        logger.debug(f"Error closing Claude client: {e}")
```

### 2. Updated Test Runner to Call Cleanup
**File:** `/auto_a11y/testing/test_runner.py`

Added proper cleanup in a finally block:
```python
finally:
    # Clean up Claude client to avoid event loop errors
    if analyzer and hasattr(analyzer, 'client'):
        try:
            await analyzer.client.aclose()
        except Exception as cleanup_error:
            logger.debug(f"Error cleaning up AI analyzer: {cleanup_error}")
```

## Other Changes

### Contrast Ratio Rounding
**File:** `/auto_a11y/scripts/tests/colorContrast.js`

Also fixed the contrast ratio display to round to 2 decimal places:
```javascript
// Round ratio to 2 decimal places for cleaner display
ratio = Math.round(ratio * 100) / 100;
```

This makes contrast ratios display as clean numbers like 4.69:1 instead of 4.68949989000882:1

## Impact
- Eliminates the "Event loop is closed" runtime error
- Ensures proper cleanup of async resources
- Prevents resource leaks from unclosed connections
- Makes error messages cleaner with rounded contrast ratios

## Testing
The fix ensures that:
1. AI analysis can run without causing event loop errors
2. The analyzer properly cleans up after itself
3. If cleanup fails, it's logged as debug (not an error) since it's not critical
4. Tests continue to work whether AI analysis is enabled or not