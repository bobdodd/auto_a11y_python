"""
Timers touchpoint test module
Evaluates JavaScript timers for proper user control mechanisms.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "JavaScript Timer Control Analysis",
    "touchpoint": "timers",
    "description": "Evaluates JavaScript timers (setTimeout and setInterval) for proper user control mechanisms. This test identifies automatically starting timers and content that changes without user initiation, which may cause issues for users with cognitive disabilities.",
    "version": "1.0.0",
    "wcagCriteria": ["2.2.1", "2.2.2"],
    "tests": [
        {
            "id": "auto-start-timers",
            "name": "Auto-Starting Timers",
            "description": "Identifies timers that start automatically on page load without user interaction.",
            "impact": "high",
            "wcagCriteria": ["2.2.1", "2.2.2"],
        },
        {
            "id": "timer-controls",
            "name": "Timer Control Mechanisms",
            "description": "Checks if timers have associated user interface controls (play, pause, stop).",
            "impact": "high",
            "wcagCriteria": ["2.2.1", "2.2.2"],
        },
        {
            "id": "timer-detection",
            "name": "JavaScript Timer Detection",
            "description": "Identifies JavaScript timers used on the page for informational purposes.",
            "impact": "informational",
            "wcagCriteria": [],
        }
    ]
}

async def test_timers(page) -> Dict[str, Any]:
    """
    Test for presence and control of timers in JavaScript
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # First inject the timer tracking code
        await page.evaluate('''
            () => {
                // Create global tracking object
                window._timerTracking = {
                    timers: new Map(),
                    intervals: new Map(),
                    autoStartTimers: new Set()
                };

                // Track setTimeout calls
                const originalSetTimeout = window.setTimeout;
                window.setTimeout = function (callback, delay, ...args) {
                    const stack = new Error().stack;
                    const timerId = originalSetTimeout.call(this, callback, delay, ...args);
                    window._timerTracking.timers.set(timerId, {
                        type: 'timeout',
                        delay: delay,
                        stack: stack,
                        startTime: Date.now(),
                        autoStart: true
                    });
                    return timerId;
                };

                // Track setInterval calls
                const originalSetInterval = window.setInterval;
                window.setInterval = function (callback, delay, ...args) {
                    const stack = new Error().stack;
                    const timerId = originalSetInterval.call(this, callback, delay, ...args);
                    window._timerTracking.intervals.set(timerId, {
                        type: 'interval',
                        delay: delay,
                        stack: stack,
                        startTime: Date.now(),
                        autoStart: true
                    });
                    return timerId;
                };

                // Track clearTimeout calls
                const originalClearTimeout = window.clearTimeout;
                window.clearTimeout = function (timerId) {
                    window._timerTracking.timers.delete(timerId);
                    return originalClearTimeout.call(this, timerId);
                };

                // Track clearInterval calls
                const originalClearInterval = window.clearInterval;
                window.clearInterval = function (timerId) {
                    window._timerTracking.intervals.delete(timerId);
                    return originalClearInterval.call(this, timerId);
                };
            }
        ''')
        
        # Wait for any initial timers to be set
        await asyncio.sleep(1)
        
        # Execute JavaScript to analyze timers
        results = await page.evaluate('''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'timers',
                    checks: []
                };
                
                // Function to generate XPath for elements
                function getFullXPath(element) {
                    if (!element) return '';
                    
                    function getElementIdx(el) {
                        let count = 1;
                        for (let sib = el.previousSibling; sib; sib = sib.previousSibling) {
                            if (sib.nodeType === 1 && sib.tagName === el.tagName) {
                                count++;
                            }
                        }
                        return count;
                    }
                    
                    let path = '';
                    while (element && element.nodeType === 1) {
                        const idx = getElementIdx(element);
                        const tagName = element.tagName.toLowerCase();
                        path = `/${tagName}[${idx}]${path}`;
                        element = element.parentNode;
                    }
                    return path;
                }
                
                // Verify tracking object exists
                if (!window._timerTracking) {
                    results.applicable = false;
                    results.not_applicable_reason = 'Timer tracking not available';
                    return results;
                }
                
                // Find timer controls
                function findTimerControls() {
                    const controls = [];
                    const interactiveElements = document.querySelectorAll(
                        'button, input[type="button"], input[type="submit"], [role="button"], ' +
                        'a[href], [onclick], [onkeydown], [onkeyup], [onmousedown], [onmouseup]'
                    );

                    interactiveElements.forEach(element => {
                        const inlineHandlers = [
                            element.getAttribute('onclick'),
                            element.getAttribute('onkeydown'),
                            element.getAttribute('onkeyup'),
                            element.getAttribute('onmousedown'),
                            element.getAttribute('onmouseup')
                        ].filter(Boolean);

                        const hasTimerControl = inlineHandlers.some(handler => 
                            handler.includes('setTimeout') || 
                            handler.includes('setInterval') ||
                            handler.includes('clearTimeout') ||
                            handler.includes('clearInterval')
                        );

                        if (hasTimerControl) {
                            controls.push({
                                element: element.tagName.toLowerCase(),
                                id: element.id || null,
                                text: element.textContent.trim(),
                                xpath: getFullXPath(element)
                            });
                        }
                    });

                    return controls;
                }
                
                const timerList = [];
                const controls = findTimerControls();
                
                // Process timeouts
                window._timerTracking.timers.forEach((timer, id) => {
                    timerList.push({
                        id: id,
                        type: 'timeout',
                        delay: timer.delay,
                        autoStart: timer.autoStart,
                        startTime: timer.startTime
                    });
                });

                // Process intervals
                window._timerTracking.intervals.forEach((interval, id) => {
                    timerList.push({
                        id: id,
                        type: 'interval',
                        delay: interval.delay,
                        autoStart: interval.autoStart,
                        startTime: interval.startTime
                    });
                });
                
                if (timerList.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No timers detected on the page';
                    return results;
                }
                
                results.elements_tested = timerList.length;
                
                const autoStartTimers = timerList.filter(t => t.autoStart);
                let timersWithoutControls = 0;
                
                // Check for auto-start timers
                if (autoStartTimers.length > 0) {
                    results.errors.push({
                        err: 'ErrAutoStartTimers',
                        type: 'err',
                        cat: 'timers',
                        element: 'page',
                        xpath: '/html',
                        html: '<page>',
                        description: `Found ${autoStartTimers.length} auto-starting timer(s)`,
                        count: autoStartTimers.length,
                        timerTypes: autoStartTimers.map(t => t.type)
                    });
                    results.elements_failed++;
                }
                
                // Check for timers without controls
                if (timerList.length > controls.length) {
                    timersWithoutControls = timerList.length - controls.length;
                    results.errors.push({
                        err: 'ErrTimersWithoutControls',
                        type: 'err',
                        cat: 'timers',
                        element: 'page',
                        xpath: '/html',
                        html: '<page>',
                        description: `Found ${timersWithoutControls} timer(s) without user controls`,
                        count: timersWithoutControls,
                        totalTimers: timerList.length,
                        totalControls: controls.length
                    });
                    results.elements_failed++;
                }
                
                if (results.elements_failed === 0) {
                    results.elements_passed = 1; // Page-level pass
                }
                
                // Check for long-running intervals (potential accessibility issue)
                timerList.forEach(timer => {
                    if (timer.type === 'interval' && timer.delay < 1000) {
                        results.warnings.push({
                            err: 'WarnFastInterval',
                            type: 'warn',
                            cat: 'timers',
                            element: 'timer',
                            xpath: '/html',
                            html: '<timer>',
                            description: `Fast interval detected (${timer.delay}ms) - may cause performance or accessibility issues`,
                            timerId: timer.id,
                            delay: timer.delay
                        });
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Auto-starting timers',
                    wcag: ['2.2.1', '2.2.2'],
                    total: timerList.length,
                    passed: timerList.length - autoStartTimers.length,
                    failed: autoStartTimers.length
                });
                
                if (timersWithoutControls > 0) {
                    results.checks.push({
                        description: 'Timer user controls',
                        wcag: ['2.2.1', '2.2.2'],
                        total: timerList.length,
                        passed: controls.length,
                        failed: timersWithoutControls
                    });
                }
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_timers: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }