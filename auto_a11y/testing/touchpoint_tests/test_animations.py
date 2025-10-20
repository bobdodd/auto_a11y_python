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

                // Analyze keyframes to detect problematic animation patterns
                function analyzeKeyframes(animationName) {
                    const problems = [];

                    try {
                        for (let sheet of document.styleSheets) {
                            try {
                                for (let rule of sheet.cssRules) {
                                    if (rule instanceof CSSKeyframesRule && rule.name === animationName) {
                                        // Analyze keyframe rules
                                        const keyframes = Array.from(rule.cssRules);

                                        // Check for rapid opacity changes (flashing)
                                        let hasOpacityChanges = false;
                                        let opacityValues = [];

                                        keyframes.forEach(kf => {
                                            const opacity = kf.style.opacity;
                                            if (opacity !== '' && opacity !== undefined) {
                                                hasOpacityChanges = true;
                                                opacityValues.push(parseFloat(opacity));
                                            }
                                        });

                                        // If opacity toggles between very different values (e.g., 0 and 1)
                                        if (hasOpacityChanges && opacityValues.length >= 2) {
                                            const max = Math.max(...opacityValues);
                                            const min = Math.min(...opacityValues);
                                            if (max - min > 0.5) {
                                                problems.push({
                                                    type: 'flashing',
                                                    severity: 'high',
                                                    description: 'Rapid opacity changes can trigger seizures'
                                                });
                                            }
                                        }

                                        // Check for rotation animations
                                        keyframes.forEach(kf => {
                                            const transform = kf.style.transform;
                                            if (transform && transform.includes('rotate')) {
                                                problems.push({
                                                    type: 'rotation',
                                                    severity: 'medium',
                                                    description: 'Rotation can cause dizziness'
                                                });
                                            }
                                        });

                                        // Check for aggressive translations (shaking)
                                        let hasLargeTranslations = false;
                                        keyframes.forEach(kf => {
                                            const transform = kf.style.transform;
                                            if (transform && (transform.includes('translateX') || transform.includes('translateY'))) {
                                                // Try to extract pixel values
                                                const matches = transform.match(/translate[XY]\\((-?\\d+)px\\)/g);
                                                if (matches) {
                                                    matches.forEach(match => {
                                                        const value = Math.abs(parseInt(match.match(/-?\\d+/)[0]));
                                                        if (value >= 15) {
                                                            hasLargeTranslations = true;
                                                        }
                                                    });
                                                }
                                            }
                                        });

                                        if (hasLargeTranslations) {
                                            problems.push({
                                                type: 'shaking',
                                                severity: 'medium',
                                                description: 'Aggressive movement can be distracting and cause discomfort'
                                            });
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

                    return problems;
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

                // Function to detect if element appears to be a loading/busy spinner
                function isLikelySpinner(element) {
                    // Check class and id for spinner/loader/loading keywords
                    const classStr = (element.className || '').toLowerCase();
                    const idStr = (element.id || '').toLowerCase();
                    const spinnerKeywords = ['spinner', 'loader', 'loading', 'busy', 'progress', 'spin'];

                    const hasSpinnerClass = spinnerKeywords.some(keyword =>
                        classStr.includes(keyword) || idStr.includes(keyword)
                    );

                    // Check aria attributes
                    const role = element.getAttribute('role');
                    const ariaLabel = (element.getAttribute('aria-label') || '').toLowerCase();
                    const ariaLive = element.getAttribute('aria-live');

                    const hasSpinnerAria = role === 'progressbar' ||
                                          role === 'status' ||
                                          ariaLabel.includes('loading') ||
                                          ariaLabel.includes('spinner') ||
                                          ariaLive === 'polite' ||
                                          ariaLive === 'assertive';

                    // Check if element is small (likely a spinner icon)
                    const rect = element.getBoundingClientRect();
                    const isSmall = rect.width <= 100 && rect.height <= 100;

                    // Check if element is currently hidden (display: none or visibility: hidden)
                    const style = window.getComputedStyle(element);
                    const isHidden = style.display === 'none' ||
                                    style.visibility === 'hidden' ||
                                    style.opacity === '0';

                    return (hasSpinnerClass || hasSpinnerAria || isSmall) && !isHidden;
                }

                // Check for infinite animations - report one error per element
                const infiniteAnimations = animatedElements.filter(item => item.animation.iterationCount === 'infinite');

                if (infiniteAnimations.length > 0) {
                    // Check if page has animation controls (pause/stop/hide buttons)
                    const hasControls = document.querySelector('button[id*="pause"], button[id*="stop"], button[id*="hide"], button[class*="pause"], button[class*="stop"], button[class*="hide"], button[aria-label*="pause"], button[aria-label*="stop"], button[aria-label*="hide"], .animation-controls, #animation-controls') !== null;

                    if (!hasControls) {
                        // Report one error or warning per infinite animation element
                        infiniteAnimations.forEach(item => {
                            const cssLines = Object.entries(item.css)
                                .map(([prop, value]) => `  ${prop}: ${value};`)
                                .join('\\n');

                            const isSpinner = isLikelySpinner(item.element);

                            if (isSpinner) {
                                // Warn for likely spinners - they're often acceptable but should still be reviewed
                                results.warnings.push({
                                    err: 'WarnInfiniteAnimationSpinner',
                                    type: 'warn',
                                    cat: 'animations',
                                    element: item.tag,
                                    xpath: item.xpath,
                                    html: item.element.outerHTML.substring(0, 200),
                                    description: `Animation appears to be a loading/busy spinner but runs infinitely without controls`,
                                    animationCSS: cssLines,
                                    animationName: item.animation.name
                                });
                            } else {
                                // Error for other infinite animations
                                results.errors.push({
                                    err: 'ErrInfiniteAnimation',
                                    type: 'err',
                                    cat: 'animations',
                                    element: item.tag,
                                    xpath: item.xpath,
                                    html: item.element.outerHTML.substring(0, 200),
                                    description: `Animation runs infinitely without pause, stop, or hide controls`,
                                    animationCSS: cssLines,
                                    animationName: item.animation.name
                                });
                                results.elements_failed++;
                            }
                        });
                    } else {
                        infiniteAnimations.forEach(() => results.elements_passed++);
                    }
                } else {
                    // No infinite animations found
                    results.elements_passed++;
                }

                // Check for long duration animations (separate loop)
                animatedElements.forEach(item => {
                    const { element, animation } = item;
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

                // Check for problematic animation patterns
                // Only warn if: fast duration (<1s) + infinite + problematic pattern + no reduced motion support
                animatedElements.forEach(item => {
                    const { element, animation } = item;
                    const duration = parseFloat(animation.duration);
                    const durationMs = animation.duration.includes('ms') ? duration : duration * 1000;

                    // Only check fast, infinite animations
                    if (durationMs < 1000 && animation.iterationCount === 'infinite') {
                        const keyframeProblems = analyzeKeyframes(animation.name);

                        if (keyframeProblems.length > 0) {
                            // Problematic pattern detected
                            const problemTypes = keyframeProblems.map(p => p.type).join(', ');
                            const problemDescriptions = keyframeProblems.map(p => p.description).join('; ');

                            const cssLines = Object.entries(item.css)
                                .map(([prop, value]) => `  ${prop}: ${value};`)
                                .join('\\n');

                            results.warnings.push({
                                err: 'WarnProblematicAnimation',
                                type: 'warn',
                                cat: 'animation',
                                element: item.tag,
                                xpath: item.xpath,
                                html: element.outerHTML.substring(0, 200),
                                description: `Problematic animation detected: ${problemDescriptions}`,
                                animationName: animation.name,
                                duration: animation.duration,
                                durationMs: durationMs,
                                problemTypes: problemTypes,
                                problems: keyframeProblems,
                                hasReducedMotion: hasReducedMotion,
                                animationCSS: cssLines
                            });
                        }
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