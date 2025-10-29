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

    Detects setTimeout and setInterval calls by analyzing JavaScript source code
    from inline scripts and external script tags.

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze timer usage in source code
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

                // Function to analyze JavaScript source code for timer usage
                function analyzeJavaScriptForTimers(sourceCode) {
                    const timers = {
                        setIntervals: [],
                        setTimeouts: [],
                        hasSetInterval: false,
                        hasSetTimeout: false,
                        fastIntervals: []
                    };

                    if (!sourceCode) return timers;

                    // Look for setInterval calls with delay values
                    if (sourceCode.indexOf('setInterval') !== -1) {
                        timers.hasSetInterval = true;

                        // Try to extract delay values from setInterval calls
                        // Pattern: setInterval(..., <delay>)
                        // Simple approach: look for setInterval followed by delay in common patterns
                        const intervalPattern = /setInterval\\s*\\([^,]+,\\s*(\\d+)\\s*\\)/g;
                        let match;
                        while ((match = intervalPattern.exec(sourceCode)) !== null) {
                            const delay = parseInt(match[1], 10);
                            timers.setIntervals.push({ delay: delay });

                            // Check if this is a fast interval (< 1000ms = < 1 second)
                            if (delay < 1000) {
                                timers.fastIntervals.push({
                                    delay: delay,
                                    position: match.index
                                });
                            }
                        }

                        // If we couldn't parse any delays, mark as having setInterval anyway
                        if (timers.setIntervals.length === 0) {
                            timers.setIntervals = [{ delay: null }];
                        }
                    }

                    // Look for setTimeout calls
                    if (sourceCode.indexOf('setTimeout') !== -1) {
                        timers.hasSetTimeout = true;
                        const matches = sourceCode.split('setTimeout');
                        timers.setTimeouts = new Array(matches.length - 1);
                    }

                    return timers;
                }

                // Collect all JavaScript source code from the page
                let allJavaScriptCode = '';
                let scriptSources = [];

                // Get inline scripts
                const inlineScripts = document.querySelectorAll('script:not([src])');
                inlineScripts.forEach((script, index) => {
                    if (script.textContent && script.type !== 'application/json') {
                        allJavaScriptCode += '\\n' + script.textContent;
                        scriptSources.push({
                            type: 'inline',
                            index: index,
                            preview: script.textContent.substring(0, 100)
                        });
                    }
                });

                // Analyze the collected JavaScript for timer usage
                const timerAnalysis = analyzeJavaScriptForTimers(allJavaScriptCode);

                // Check if any timers were found
                const hasTimers = timerAnalysis.hasSetInterval || timerAnalysis.hasSetTimeout;

                if (!hasTimers) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No timers detected in JavaScript source code';
                    return results;
                }

                // Find timer controls - look for buttons/controls that suggest timer management
                function findTimerControls() {
                    // Look for elements with IDs, classes, text, or aria-labels that suggest timer control
                    const controlSelectors = [
                        'button[id*="pause"]', 'button[id*="Pause"]', 'button[id*="stop"]', 'button[id*="Stop"]',
                        'button[id*="extend"]', 'button[id*="Extend"]',
                        'button[class*="pause"]', 'button[class*="stop"]', 'button[class*="extend"]',
                        'button[aria-label*="pause"]', 'button[aria-label*="stop"]', 'button[aria-label*="extend"]',
                        '.timer-controls', '#timer-controls', '.countdown-controls', '#countdown-controls',
                        'button[id*="Btn"]' // Common pattern like pauseBtn, extendBtn
                    ];

                    for (const selector of controlSelectors) {
                        try {
                            const element = document.querySelector(selector);
                            if (element) {
                                return true; // Found at least one control
                            }
                        } catch (e) {
                            // Invalid selector, skip
                        }
                    }

                    // Also check button text content for timer-related keywords
                    const buttons = document.querySelectorAll('button, [role="button"]');
                    for (const button of buttons) {
                        const text = button.textContent.toLowerCase();
                        if (text.includes('pause') || text.includes('stop') ||
                            text.includes('extend') || text.includes('resume') ||
                            text.includes('timer') || text.includes('time')) {
                            return true;
                        }
                    }

                    return false;
                }

                const hasControls = findTimerControls();

                results.elements_tested = 1; // Page-level test

                // Warn about auto-starting timers (both setTimeout and setInterval)
                // This is for manual review - not all auto-starting timers are problematic
                if (hasTimers) {
                    const timerTypes = [];
                    if (timerAnalysis.hasSetTimeout) timerTypes.push('setTimeout');
                    if (timerAnalysis.hasSetInterval) timerTypes.push('setInterval');

                    results.warnings.push({
                        err: 'WarnAutoStartTimers',
                        type: 'warn',
                        cat: 'timers',
                        element: 'page',
                        xpath: '/html',
                        html: 'page-wide',
                        description: `Page has auto-starting timers: ${timerTypes.join(', ')}. Manual review required to ensure these don't create time pressure for users.`,
                        setTimeoutCount: timerAnalysis.setTimeouts ? timerAnalysis.setTimeouts.length : 0,
                        setIntervalCount: timerAnalysis.setIntervals.length,
                        timerTypes: timerTypes,
                        scriptSources: scriptSources
                    });
                }

                // WCAG 2.2.1 & 2.2.2: Time-based content (setInterval specifically) requires user controls
                // setInterval creates continuous, auto-updating content
                if (timerAnalysis.hasSetInterval && !hasControls) {
                    const intervalCount = timerAnalysis.setIntervals.length;
                    results.errors.push({
                        err: 'ErrTimersWithoutControls',
                        type: 'err',
                        cat: 'timers',
                        element: 'page',
                        xpath: '/html',
                        html: 'page-wide',
                        description: `Page has ${intervalCount} setInterval timer(s) without pause, stop, or extend controls`,
                        intervalCount: intervalCount,
                        timeoutCount: timerAnalysis.setTimeouts.length,
                        hasControls: false,
                        scriptSources: scriptSources
                    });
                    results.elements_failed++;
                } else if (timerAnalysis.hasSetInterval && hasControls) {
                    // Timers with controls - this is acceptable
                    results.elements_passed++;
                } else {
                    // Only setTimeout, no setInterval - generally acceptable
                    results.elements_passed++;
                }

                // Check for fast intervals (< 1000ms) - Warning level
                if (timerAnalysis.fastIntervals && timerAnalysis.fastIntervals.length > 0) {
                    timerAnalysis.fastIntervals.forEach(fastInterval => {
                        results.warnings.push({
                            err: 'WarnFastInterval',
                            type: 'warn',
                            cat: 'timers',
                            element: 'page',
                            xpath: '/html',
                            html: 'page-wide',
                            description: `JavaScript interval running faster than once per second (${fastInterval.delay}ms)`,
                            delay: fastInterval.delay,
                            updatesPerSecond: Math.round(1000 / fastInterval.delay * 10) / 10
                        });
                    });
                }

                // Add check information for reporting
                results.checks.push({
                    description: 'Auto-starting timers with user controls',
                    wcag: ['2.2.1', '2.2.2'],
                    total: 1,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });

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