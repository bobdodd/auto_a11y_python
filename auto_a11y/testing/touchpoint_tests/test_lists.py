"""
Lists touchpoint test module
Evaluates the implementation and styling of HTML lists to ensure proper semantic structure.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "List Structure Analysis",
    "touchpoint": "lists",
    "description": "Evaluates the implementation and styling of HTML lists to ensure proper semantic structure for screen reader users. This test identifies improper list implementations, excessive nesting, empty lists, and custom bullet styling that may impact accessibility.",
    "version": "1.0.0",
    "wcagCriteria": ["1.3.1", "4.1.1", "2.4.10"],
    "tests": [
        {
            "id": "fake-lists",
            "name": "Fake List Detection",
            "description": "Identifies elements that visually appear as lists but don't use proper list markup (ul/ol and li elements).",
            "impact": "high",
            "wcagCriteria": ["1.3.1"],
        },
        {
            "id": "empty-lists",
            "name": "Empty List Detection",
            "description": "Identifies list elements (ul/ol) that contain no list items.",
            "impact": "medium",
            "wcagCriteria": ["4.1.1"],
        },
        {
            "id": "deep-nesting",
            "name": "Excessive List Nesting",
            "description": "Identifies lists with excessive nesting depth that may cause navigation difficulties.",
            "impact": "medium",
            "wcagCriteria": ["2.4.10"],
        },
        {
            "id": "custom-bullets",
            "name": "Custom Bullet Styling",
            "description": "Identifies lists with custom bullet styling that may impact screen reader announcements.",
            "impact": "low",
            "wcagCriteria": ["1.3.1"],
        }
    ]
}

async def test_lists(page) -> Dict[str, Any]:
    """
    Test proper implementation of lists and their styling
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze lists
        results = await page.evaluate(r'''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'lists',
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
                
                // Calculate list nesting depth
                function calculateListDepth(element) {
                    let depth = 0;
                    let current = element;
                    
                    while (current.parentElement) {
                        if (current.parentElement.tagName.match(/^(UL|OL)$/)) {
                            depth++;
                        }
                        current = current.parentElement;
                    }
                    
                    return depth;
                }
                
                // Check for fake lists (elements styled as lists but not using ul/ol)
                const potentialFakeLists = Array.from(document.querySelectorAll('div, span, p'))
                    .filter(el => {
                        const style = window.getComputedStyle(el);
                        const text = el.textContent;
                        const html = el.innerHTML;

                        // Skip if element contains a proper list structure
                        if (el.querySelector('ul, ol')) {
                            return false;
                        }

                        // Check for explicit list styling or bullet characters
                        if (style.display === 'list-item' ||
                            html.includes('•') || html.includes('·') || html.includes('‣') ||
                            html.includes('◦') || html.includes('▪') || html.includes('▫')) {
                            return true;
                        }

                        // Check for icon fonts used as bullets (Font Awesome, Material Icons, etc.)
                        const iconElements = el.querySelectorAll('i, span[class*="icon"], span[class*="fa-"], span[class*="material-"]');
                        if (iconElements.length >= 3) {
                            // Check if they appear to be used as bullets (siblings with text following)
                            let bulletCount = 0;
                            iconElements.forEach(icon => {
                                const parent = icon.parentElement;
                                // Skip if the icon is inside a proper list item - that's OK (just bad CSS practice)
                                if (parent && parent.closest('li')) {
                                    return; // Icon is in a list item, don't count it
                                }
                                // Check if icon is at start of parent and parent has text after it
                                if (parent && parent.firstElementChild === icon && parent.textContent.trim().length > icon.textContent.trim().length) {
                                    bulletCount++;
                                }
                            });
                            if (bulletCount >= 3) {
                                return true;
                            }
                        }

                        // Check for text starting with dash/hyphen/asterisk bullets
                        const lines = text.split('\n').filter(line => line.trim().length > 0);
                        if (lines.length >= 3) {
                            const bulletLines = lines.filter(line => line.match(/^\s*[-–—*•]\s/));
                            // If at least 50% of lines start with bullets, it's likely a list
                            if (bulletLines.length >= lines.length * 0.5) {
                                return true;
                            }
                        }

                        // Check for numbered lists (1. 2. 3. or 1) 2) 3))
                        if (lines.length >= 3) {
                            const numberedLines = lines.filter(line => line.match(/^\s*\d+[\.\)]\s/));
                            if (numberedLines.length >= lines.length * 0.5) {
                                return true;
                            }
                        }

                        // For <br> tags, be more conservative
                        const brCount = (html.match(/<br\s*\/?>/gi) || []).length;
                        if (brCount >= 3) {
                            // Only flag as fake list if:
                            // 1. Has intro text ending with colon
                            // 2. Items are relatively short (avg < 100 chars)
                            // 3. Multiple items start with similar patterns
                            const parts = html.split(/<br\s*\/?>/gi)
                                .map(part => part.replace(/<[^>]*>/g, '').trim())
                                .filter(part => part.length > 0);

                            if (parts.length >= 3) {
                                // Check for intro ending with colon
                                const hasIntro = parts[0].match(/:\s*$/);

                                // Check average length of items (excluding first if it's intro)
                                const items = hasIntro ? parts.slice(1) : parts;
                                const avgLength = items.reduce((sum, item) => sum + item.length, 0) / items.length;

                                // Check if items start with similar patterns (bullets, numbers, dashes)
                                const patterned = items.filter(item =>
                                    item.match(/^[-–—*•◦▪▫·‣]\s/) ||
                                    item.match(/^\d+[\.\)]\s/)
                                );

                                // Only flag if has intro with colon AND items are short OR items have bullet patterns
                                if ((hasIntro && avgLength < 150) || patterned.length >= items.length * 0.5) {
                                    return true;
                                }
                            }
                        }

                        return false;
                    });

                // Filter out nested elements - only keep the outermost fake list containers
                const filteredFakeLists = potentialFakeLists.filter(element => {
                    // Check if any of the other potential fake lists is an ancestor of this element
                    return !potentialFakeLists.some(other =>
                        other !== element && other.contains(element)
                    );
                });

                filteredFakeLists.forEach(element => {
                    const style = window.getComputedStyle(element);
                    const html = element.innerHTML;
                    const text = element.textContent;

                    // Determine what pattern makes this look like a fake list
                    let pattern = 'unknown';
                    let detectedBullets = [];

                    // Check for icon fonts first
                    const iconElements = element.querySelectorAll('i, span[class*="icon"], span[class*="fa-"], span[class*="material-"]');
                    const iconBullets = [];
                    iconElements.forEach(icon => {
                        const parent = icon.parentElement;
                        if (parent && parent.firstElementChild === icon) {
                            // Get text after the icon in the same parent
                            const textContent = Array.from(parent.childNodes)
                                .filter(node => node !== icon && (node.nodeType === 3 || !node.matches('i, span[class*="icon"], span[class*="fa-"], span[class*="material-"]')))
                                .map(node => node.textContent)
                                .join('')
                                .trim();
                            if (textContent.length > 0) {
                                iconBullets.push(textContent);
                            }
                        }
                    });

                    if (iconBullets.length >= 3) {
                        pattern = 'icon font bullets (Font Awesome, Material Icons, etc.)';
                        detectedBullets = iconBullets;
                    } else if (style.display === 'list-item') {
                        pattern = 'CSS list-item display';
                    } else if (html.includes('•')) {
                        pattern = 'bullet character (•)';
                        detectedBullets = text.split('•').map(item => item.trim()).filter(item => item.length > 0);
                    } else if (html.includes('·')) {
                        pattern = 'middot character (·)';
                        detectedBullets = text.split('·').map(item => item.trim()).filter(item => item.length > 0);
                    } else if (html.includes('‣')) {
                        pattern = 'triangular bullet (‣)';
                        detectedBullets = text.split('‣').map(item => item.trim()).filter(item => item.length > 0);
                    } else if (html.includes('◦') || html.includes('▪') || html.includes('▫')) {
                        pattern = 'geometric bullet characters';
                        const bullets = ['◦', '▪', '▫'];
                        for (const bullet of bullets) {
                            if (html.includes(bullet)) {
                                detectedBullets = text.split(bullet).map(item => item.trim()).filter(item => item.length > 0);
                                break;
                            }
                        }
                    } else {
                        // Check for line-based patterns
                        const lines = text.split('\n').filter(line => line.trim().length > 0);
                        const bulletLines = lines.filter(line => line.match(/^\s*[-–—*•]\s/));
                        const numberedLines = lines.filter(line => line.match(/^\s*\d+[\.\)]\s/));

                        if (bulletLines.length >= lines.length * 0.5) {
                            pattern = 'dash or asterisk bullets';
                            detectedBullets = bulletLines.map(line => line.replace(/^\s*[-–—*•]\s*/, '').trim());
                        } else if (numberedLines.length >= lines.length * 0.5) {
                            pattern = 'numbered list (1. 2. 3.)';
                            detectedBullets = numberedLines.map(line => line.replace(/^\s*\d+[\.\)]\s*/, '').trim());
                        } else if ((html.match(/<br\s*\/?>/gi) || []).length >= 3) {
                            pattern = 'line breaks with list patterns';
                            detectedBullets = html.split(/<br\s*\/?>/gi).map(item => item.replace(/<[^>]*>/g, '').trim()).filter(item => item.length > 0);
                        }
                    }

                    // Get sample items (max 5)
                    const sampleItems = detectedBullets.slice(0, 5).map((item, idx) => ({
                        index: idx + 1,
                        text: item.substring(0, 100)
                    }));

                    results.errors.push({
                        err: 'ErrFakeListImplementation',
                        type: 'err',
                        cat: 'list',
                        element: element.tagName.toLowerCase(),
                        xpath: getFullXPath(element),
                        html: element.outerHTML.substring(0, 200),
                        description: `Element appears to be a list using ${pattern} but does not use proper list markup`,
                        pattern: pattern,
                        itemCount: detectedBullets.length,
                        sampleItems: sampleItems,
                        innerHTML: element.innerHTML.substring(0, 100)
                    });
                    results.elements_failed++;
                });
                
                // Find all proper lists
                const allLists = Array.from(document.querySelectorAll('ul, ol, dl'));
                
                if (allLists.length === 0 && filteredFakeLists.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No lists found on the page';
                    return results;
                }

                results.elements_tested = allLists.length + filteredFakeLists.length;
                
                allLists.forEach(list => {
                    const listTag = list.tagName.toLowerCase();

                    // Get items based on list type
                    const items = listTag === 'dl'
                        ? list.querySelectorAll('dt, dd')
                        : list.querySelectorAll('li');

                    const depth = calculateListDepth(list);

                    // Check for redundant role="list" on native list elements
                    const roleAttr = list.getAttribute('role');
                    if (roleAttr === 'list') {
                        let reason = '';
                        if (listTag === 'ul' || listTag === 'ol') {
                            reason = `${listTag.toUpperCase()} element has redundant role="list" - native HTML list semantics should be used`;
                        } else if (listTag === 'dl') {
                            reason = 'DL element has inappropriate role="list" - this obscures the term-definition relationship';
                        }

                        if (reason) {
                            results.warnings.push({
                                err: 'WarnListRoleOnList',
                                type: 'warn',
                                cat: 'list',
                                element: listTag,
                                xpath: getFullXPath(list),
                                html: list.outerHTML.substring(0, 200),
                                description: reason,
                                listType: listTag
                            });
                        }
                    }

                    // Check for empty lists (only for ul/ol, not dl)
                    if (listTag !== 'dl' && items.length === 0) {
                        results.errors.push({
                            err: 'ErrEmptyList',
                            type: 'err',
                            cat: 'list',
                            element: listTag,
                            xpath: getFullXPath(list),
                            html: list.outerHTML.substring(0, 200),
                            description: 'List element contains no list items',
                            listType: listTag
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }

                    // Check for excessive nesting (more than 3 levels)
                    if (depth > 3) {
                        results.warnings.push({
                            err: 'WarnDeepListNesting',
                            type: 'warn',
                            cat: 'list',
                            element: list.tagName.toLowerCase(),
                            xpath: getFullXPath(list),
                            html: list.outerHTML.substring(0, 200),
                            description: `List is nested ${depth} levels deep (recommended max: 3)`,
                            depth: depth
                        });
                    }
                    
                    // Check styling of list items for custom bullets and icon fonts
                    items.forEach(item => {
                        const style = window.getComputedStyle(item);
                        const beforePseudo = window.getComputedStyle(item, '::before');

                        const beforeContent = beforePseudo.getPropertyValue('content');
                        const hasCustomBullet = beforeContent &&
                                              beforeContent !== 'none' &&
                                              beforeContent !== 'normal' &&
                                              beforeContent !== '""' &&
                                              beforeContent !== '"\\0022\\0022"';

                        const beforeFontFamily = beforePseudo.getPropertyValue('font-family') || '';
                        const hasIconFont = beforeFontFamily.includes('icon') ||
                                          beforeFontFamily.includes('awesome') ||
                                          beforeFontFamily.includes('material') ||
                                          (beforeContent && beforeContent.match(/[^\u0000-\u007F]/));

                        const beforeBackgroundImage = beforePseudo.getPropertyValue('background-image');

                        // Check for image/svg bullets (must be first child and small)
                        let hasImage = beforeBackgroundImage && beforeBackgroundImage !== 'none';
                        if (!hasImage) {
                            const firstChild = item.firstElementChild;
                            if (firstChild) {
                                const tagName = firstChild.tagName.toUpperCase();
                                if (tagName === 'IMG' || tagName === 'SVG') {
                                    // Check if it's small (likely a bullet icon)
                                    const rect = firstChild.getBoundingClientRect();
                                    if (rect.width < 50 && rect.height < 50) {
                                        hasImage = true;
                                    }
                                }
                            }
                        }

                        // Check for icon font elements used as bullets (Font Awesome, Material Icons, etc.)
                        const listStyleType = style.getPropertyValue('list-style-type');
                        let hasIconFontElement = false;

                        // Only check if list-style-type is none (indicating custom styling)
                        if (listStyleType === 'none') {
                            // Look for icon elements within the list item (not just first child)
                            // Common patterns: <i> tags or <span> with icon classes
                            const iconCandidates = item.querySelectorAll('i, span[class*="icon"], span[class*="fa"], span[class*="material"], span[class*="glyph"]');

                            if (iconCandidates.length > 0) {
                                // Check if any of these icon candidates appear early in the content
                                // (likely being used as a bullet rather than inline icon)
                                for (const icon of iconCandidates) {
                                    const iconClasses = icon.className || '';
                                    const iconTag = icon.tagName.toUpperCase();

                                    // Confirm it looks like an icon (has icon-related classes or is <i> tag)
                                    if (iconTag === 'I' ||
                                        iconClasses.toLowerCase().includes('icon') ||
                                        iconClasses.toLowerCase().includes('fa') ||
                                        iconClasses.toLowerCase().includes('material') ||
                                        iconClasses.toLowerCase().includes('glyph')) {
                                        hasIconFontElement = true;
                                        break;
                                    }
                                }
                            }
                        }

                        // If icon font element is found with list-style: none, create a warning
                        if (hasIconFontElement) {
                            // Find the first icon element to get its classes for the warning message
                            const iconElement = item.querySelector('i, span[class*="icon"], span[class*="fa"], span[class*="material"], span[class*="glyph"]');
                            const iconClasses = iconElement ? (iconElement.className || 'icon element') : 'icon element';

                            results.warnings.push({
                                err: 'WarnIconFontBulletsInList',
                                type: 'warn',
                                cat: 'list',
                                element: item.tagName.toLowerCase(),
                                xpath: getFullXPath(item),
                                html: item.outerHTML.substring(0, 200),
                                description: `List item uses icon font elements (${iconClasses.substring(0, 50)}) with list-style: none instead of CSS list-style-type property`,
                                iconClasses: iconClasses.substring(0, 100),
                                listStyleType: listStyleType,
                                parentList: list.tagName.toLowerCase()
                            });
                        } else if (hasCustomBullet || hasIconFont || hasImage) {
                            // Determine what type of custom styling was detected
                            let customType = '';
                            let customDetails = '';

                            if (hasImage) {
                                if (beforeBackgroundImage && beforeBackgroundImage !== 'none') {
                                    customType = '::before background-image';
                                    customDetails = beforeBackgroundImage.substring(0, 100);
                                } else if (item.querySelector('img')) {
                                    customType = '<img> element as bullet';
                                    const img = item.querySelector('img');
                                    customDetails = img ? img.src.split('/').pop().substring(0, 50) : '';
                                } else if (item.querySelector('svg')) {
                                    customType = '<svg> element as bullet';
                                }
                            } else if (hasIconFont) {
                                customType = '::before with icon font';
                                const fontFam = beforeFontFamily ? beforeFontFamily.substring(0, 50) : 'unknown';
                                const content = beforeContent ? beforeContent.substring(0, 30) : '';
                                customDetails = `font-family: ${fontFam}, content: ${content}`;
                            } else if (hasCustomBullet) {
                                customType = '::before with custom content';
                                customDetails = beforeContent ? `content: ${beforeContent.substring(0, 50)}` : '';
                            }

                            results.warnings.push({
                                err: 'WarnCustomBulletStyling',
                                type: 'warn',
                                cat: 'list',
                                element: item.tagName.toLowerCase(),
                                xpath: getFullXPath(item),
                                html: item.outerHTML.substring(0, 200),
                                description: `List item uses custom bullet styling (${customType}) that may affect screen reader announcements`,
                                customType: customType,
                                customDetails: customDetails,
                                listStyleType: listStyleType
                            });
                        }
                    });
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'List structure integrity',
                    wcag: ['1.3.1', '4.1.1'],
                    total: allLists.length + filteredFakeLists.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed + filteredFakeLists.length
                });
                
                const deepNestingCount = allLists.filter(list => calculateListDepth(list) > 3).length;
                if (deepNestingCount > 0) {
                    results.checks.push({
                        description: 'List nesting depth',
                        wcag: ['2.4.10'],
                        total: allLists.length,
                        passed: allLists.length - deepNestingCount,
                        failed: deepNestingCount
                    });
                }
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_lists: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }