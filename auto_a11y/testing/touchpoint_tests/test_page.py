"""
Page-level touchpoint test module
Tests page-level accessibility including page titles, responsive breakpoints, etc.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Page-Level Accessibility Tests",
    "touchpoint": "page",
    "description": "Tests page-level accessibility including page titles, responsive breakpoints, and other page-wide concerns.",
    "version": "2.0.0",
    "wcagCriteria": ["2.4.2", "1.4.10"],
    "tests": [
        {
            "id": "page-title",
            "name": "Page Title",
            "description": "Checks that the page has a descriptive title element.",
            "impact": "critical",
            "wcagCriteria": ["2.4.2"],
        },
        {
            "id": "responsive-breakpoints",
            "name": "CSS Media Query Breakpoints",
            "description": "Identifies responsive breakpoints defined in CSS @media rules to guide testing at different viewport widths.",
            "impact": "info",
            "wcagCriteria": ["1.4.10"],
        }
    ]
}

async def test_page(page) -> Dict[str, Any]:
    """
    Test page-level accessibility including page title and responsive breakpoints

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results
    """
    results = {
        'applicable': True,
        'errors': [],
        'warnings': [],
        'passes': [],
        'discovery': [],
        'elements_tested': 0,
        'elements_passed': 0,
        'elements_failed': 0,
        'test_name': 'page',
        'checks': []
    }

    try:
        # Get title length limit from config (default 60)
        title_length_limit = 60
        try:
            config_limit = await page.evaluate('() => window.a11yConfig && window.a11yConfig.titleLengthLimit')
            if config_limit:
                title_length_limit = config_limit
        except:
            pass

        # Execute JavaScript to get page title info
        title_data = await page.evaluate('''
            () => {
                const titleElement = document.querySelector('title');
                const allTitles = document.querySelectorAll('head > title');
                
                return {
                    hasTitleElement: !!titleElement,
                    titleText: titleElement ? titleElement.textContent.trim() : '',
                    titleCount: allTitles.length
                };
            }
        ''')

        results['elements_tested'] += 1

        # Test 1: ErrNoPageTitle - No title element
        if not title_data['hasTitleElement']:
            results['errors'].append({
                'err': 'ErrNoPageTitle',
                'type': 'err',
                'cat': 'page',
                'element': 'head',
                'xpath': '/html/head',
                'html': '<head>',
                'description': 'Page is missing a title element'
            })
            results['elements_failed'] += 1

        # Test 2: ErrEmptyPageTitle - Empty title
        elif not title_data['titleText']:
            results['errors'].append({
                'err': 'ErrEmptyPageTitle',
                'type': 'err',
                'cat': 'page',
                'element': 'title',
                'xpath': '/html/head/title',
                'html': '<title></title>',
                'description': 'Page title element is empty'
            })
            results['elements_failed'] += 1

        # Test 3: WarnPageTitleTooShort - Title too short (< 5 chars)
        elif len(title_data['titleText']) < 5:
            results['warnings'].append({
                'err': 'WarnPageTitleTooShort',
                'type': 'warn',
                'cat': 'page',
                'element': 'title',
                'xpath': '/html/head/title',
                'html': f'<title>{title_data["titleText"]}</title>',
                'description': f'Page title is too short ({len(title_data["titleText"])} characters)',
                'found': title_data['titleText'],
                'length': len(title_data['titleText'])
            })
            results['elements_failed'] += 1

        # Test 4: WarnPageTitleTooLong - Title too long
        elif len(title_data['titleText']) > title_length_limit:
            results['warnings'].append({
                'err': 'WarnPageTitleTooLong',
                'type': 'warn',
                'cat': 'page',
                'element': 'title',
                'xpath': '/html/head/title',
                'html': f'<title>{title_data["titleText"][:50]}...</title>',
                'description': f'Page title exceeds {title_length_limit} characters ({len(title_data["titleText"])} characters)',
                'found': title_data['titleText'],
                'length': len(title_data['titleText']),
                'limit': title_length_limit
            })
            results['elements_passed'] += 1
            results['passes'].append({
                'check': 'page_title',
                'title': title_data['titleText'][:title_length_limit] + '...',
                'xpath': '/html/head/title',
                'wcag': ['2.4.2'],
                'reason': 'Page has title (but too long)'
            })

        # Title is valid
        else:
            results['elements_passed'] += 1
            results['passes'].append({
                'check': 'page_title',
                'title': title_data['titleText'],
                'xpath': '/html/head/title',
                'wcag': ['2.4.2'],
                'reason': 'Page has descriptive title'
            })

        # Test 5: ErrMultiplePageTitles - Multiple title elements
        if title_data['titleCount'] > 1:
            results['errors'].append({
                'err': 'ErrMultiplePageTitles',
                'type': 'err',
                'cat': 'page',
                'element': 'head',
                'xpath': '/html/head',
                'html': '<head>',
                'description': f'Page has {title_data["titleCount"]} title elements (should have exactly one)',
                'count': title_data['titleCount']
            })

        # Add check summary
        results['checks'].append({
            'description': 'Page title',
            'wcag': ['2.4.2'],
            'total': 1,
            'passed': results['elements_passed'],
            'failed': results['elements_failed']
        })

        # Discovery: Responsive breakpoints
        breakpoint_data = await page.evaluate('''
            () => {
                const breakpoints = new Set();

                for (const sheet of document.styleSheets) {
                    try {
                        if (sheet.cssRules) {
                            for (const rule of sheet.cssRules) {
                                if (rule instanceof CSSMediaRule) {
                                    const media = rule.media.mediaText;
                                    const widthMatches = media.match(/(?:min-width|max-width):\\s*(\\d+)px/g);

                                    if (widthMatches) {
                                        widthMatches.forEach(match => {
                                            const value = parseInt(match.match(/(\\d+)px/)[1]);
                                            breakpoints.add(value);
                                        });
                                    }
                                }
                            }
                        }
                    } catch (e) {
                        // Skip stylesheets we can't access (CORS)
                    }
                }

                return Array.from(breakpoints).sort((a, b) => a - b);
            }
        ''')

        if breakpoint_data and len(breakpoint_data) > 0:
            results['discovery'].append({
                'err': 'DiscoResponsiveBreakpoints',
                'type': 'disco',
                'cat': 'page',
                'element': 'html',
                'xpath': '/html',
                'html': '<html>',
                'description': f'Page defines {len(breakpoint_data)} responsive breakpoint(s): {", ".join(map(str, breakpoint_data))}px',
                'metadata': {
                    'breakpointCount': len(breakpoint_data),
                    'breakpoints': ', '.join(map(str, breakpoint_data)),
                    'minBreakpoint': breakpoint_data[0],
                    'maxBreakpoint': breakpoint_data[-1]
                }
            })

        return results

    except Exception as e:
        logger.error(f"Error in test_page: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'discovery': [],
            'passes': [],
            'test_name': 'page'
        }
