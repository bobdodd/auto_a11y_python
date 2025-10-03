"""
Animations touchpoint test module
Evaluates CSS animations on the page for accessibility considerations, focusing on prefers-reduced-motion media query support.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "CSS Animations Analysis",
    "touchpoint": "animations",
    "description": "Evaluates CSS animations on the page for accessibility considerations, focusing on prefers-reduced-motion media query support, infinite animations, and animation duration. This test helps ensure content is accessible to users who may experience motion sickness, vestibular disorders, or other conditions affected by movement on screen.",
    "version": "1.0.0",
    "wcagCriteria": ["2.2.2", "2.3.3"],
    "tests": [
        {
            "id": "animations-reduced-motion",
            "name": "Reduced Motion Support",
            "description": "Checks if the page provides prefers-reduced-motion media query support for users who have indicated they prefer reduced motion in their system settings.",
            "impact": "high",
            "wcagCriteria": ["2.3.3"],
        },
        {
            "id": "animations-infinite",
            "name": "Infinite Animations",
            "description": "Identifies animations set to run indefinitely (animation-iteration-count: infinite). These can cause significant accessibility issues for users with vestibular disorders or attention-related disabilities.",
            "impact": "high",
            "wcagCriteria": ["2.2.2", "2.3.3"],
        },
        {
            "id": "animations-duration",
            "name": "Long Duration Animations",
            "description": "Identifies animations that run for an extended period (over 5 seconds), which can be distracting or disorienting for some users.",
            "impact": "medium",
            "wcagCriteria": ["2.2.2"],
        }
    ]
}

async def test_animations(page) -> Dict[str, Any]:
    """
    Test CSS animations for accessibility requirements
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze animations
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
                    test_name: 'animations',
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
                
                // Find all elements with animations
                function findAnimatedElements() {
                    const elements = [];
                    const all = document.body.querySelectorAll('*');
                    
                    all.forEach(element => {
                        const style = window.getComputedStyle(element);
                        if (style.animation && style.animationName !== 'none') {
                            // Get full animation CSS properties
                            const animationCSS = {
                                'animation-name': style.animationName,
                                'animation-duration': style.animationDuration,
                                'animation-timing-function': style.animationTimingFunction,
                                'animation-delay': style.animationDelay,
                                'animation-iteration-count': style.animationIterationCount,
                                'animation-direction': style.animationDirection,
                                'animation-fill-mode': style.animationFillMode,
                                'animation-play-state': style.animationPlayState
                            };

                            elements.push({
                                element: element,
                                tag: element.tagName.toLowerCase(),
                                xpath: getFullXPath(element),
                                animation: {
                                    name: style.animationName,
                                    duration: style.animationDuration,
                                    iterationCount: style.animationIterationCount,
                                    playState: style.animationPlayState
                                },
                                css: animationCSS
                            });
                        }
                    });
                    
                    return elements;
                }
                
                // Check for reduced motion support in stylesheets
                function hasReducedMotionSupport() {
                    try {
                        for (let sheet of document.styleSheets) {
                            try {
                                for (let rule of sheet.cssRules) {
                                    if (rule instanceof CSSMediaRule) {
                                        const condition = rule.conditionText.toLowerCase();
                                        if (condition.includes('prefers-reduced-motion')) {
                                            return true;
                                        }
                                    }
                                }
                            } catch (e) {
                                // Skip inaccessible stylesheets
                            }
                        }
                    } catch (e) {
                        // Error accessing stylesheets
                    }
                    return false;
                }
                
                const animatedElements = findAnimatedElements();
                const hasReducedMotion = hasReducedMotionSupport();
                
                if (animatedElements.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No animations found on the page';
                    return results;
                }
                
                results.elements_tested = animatedElements.length;
                
                // Check for reduced motion support
                if (!hasReducedMotion) {
                    results.errors.push({
                        err: 'ErrNoReducedMotionSupport',
                        type: 'err',
                        cat: 'animations',
                        element: 'page',
                        xpath: '/html',
                        html: 'page-wide',
                        description: `Page has ${animatedElements.length} animations but lacks prefers-reduced-motion media query support`
                    });
                    results.elements_failed++;
                } else {
                    results.elements_passed++;
                }
                
                // Check each animated element
                animatedElements.forEach(item => {
                    const { element, animation } = item;
                    
                    // Check for infinite animations
                    if (animation.iterationCount === 'infinite') {
                        // Format CSS for display
                        const cssLines = Object.entries(item.css)
                            .map(([prop, value]) => `  ${prop}: ${value};`)
                            .join('\\n');

                        results.errors.push({
                            err: 'ErrInfiniteAnimation',
                            type: 'err',
                            cat: 'animations',
                            element: item.tag,
                            xpath: item.xpath,
                            html: element.outerHTML.substring(0, 200),
                            description: 'Element has infinite animation which can cause accessibility issues',
                            animationName: animation.name,
                            animationCSS: cssLines,
                            cssProperties: item.css
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                    
                    // Check for long duration animations
                    const duration = parseFloat(animation.duration);
                    const durationMs = animation.duration.includes('ms') ? duration : duration * 1000;

                    if (durationMs > 5000) {
                        // Format CSS for display
                        const cssLines = Object.entries(item.css)
                            .map(([prop, value]) => `  ${prop}: ${value};`)
                            .join('\\n');

                        results.warnings.push({
                            err: 'WarnLongAnimation',
                            type: 'warn',
                            cat: 'animations',
                            element: item.tag,
                            xpath: item.xpath,
                            html: element.outerHTML.substring(0, 200),
                            description: `Animation duration (${animation.duration}) exceeds 5 seconds`,
                            duration: animation.duration,
                            animationCSS: cssLines,
                            cssProperties: item.css
                        });
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Reduced motion support',
                    wcag: ['2.3.3'],
                    total: 1,
                    passed: hasReducedMotion ? 1 : 0,
                    failed: hasReducedMotion ? 0 : 1
                });
                
                results.checks.push({
                    description: 'Animation accessibility',
                    wcag: ['2.2.2', '2.3.3'],
                    total: animatedElements.length,
                    passed: results.elements_passed - (hasReducedMotion ? 0 : 1), // Exclude the page-level check
                    failed: results.elements_failed - (hasReducedMotion ? 0 : 1)
                });
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_animations: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }