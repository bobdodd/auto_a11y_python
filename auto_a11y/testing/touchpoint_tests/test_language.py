"""
Language touchpoint test module
Tests language declarations and attributes for accessibility compliance.
"""

from typing import Dict, Any, List, Set
import logging
import re

logger = logging.getLogger(__name__)

# ISO 639-1 two-letter language codes (most widely supported)
VALID_LANGUAGE_CODES: Set[str] = {
    'aa', 'ab', 'ae', 'af', 'ak', 'am', 'an', 'ar', 'as', 'av', 'ay', 'az',
    'ba', 'be', 'bg', 'bh', 'bi', 'bm', 'bn', 'bo', 'br', 'bs',
    'ca', 'ce', 'ch', 'co', 'cr', 'cs', 'cu', 'cv', 'cy',
    'da', 'de', 'dv', 'dz',
    'ee', 'el', 'en', 'eo', 'es', 'et', 'eu',
    'fa', 'ff', 'fi', 'fj', 'fo', 'fr', 'fy',
    'ga', 'gd', 'gl', 'gn', 'gu', 'gv',
    'ha', 'he', 'hi', 'ho', 'hr', 'ht', 'hu', 'hy', 'hz',
    'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'io', 'is', 'it', 'iu',
    'ja', 'jv',
    'ka', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'ku', 'kv', 'kw', 'ky',
    'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv',
    'mg', 'mh', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my',
    'na', 'nb', 'nd', 'ne', 'ng', 'nl', 'nn', 'no', 'nr', 'nv', 'ny',
    'oc', 'oj', 'om', 'or', 'os',
    'pa', 'pi', 'pl', 'ps', 'pt',
    'qu',
    'rm', 'rn', 'ro', 'ru', 'rw',
    'sa', 'sc', 'sd', 'se', 'sg', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'ss', 'st', 'su', 'sv', 'sw',
    'ta', 'te', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty',
    'ug', 'uk', 'ur', 'uz',
    've', 'vi', 'vo',
    'wa', 'wo',
    'xh',
    'yi', 'yo',
    'za', 'zh', 'zu'
}

# Regex pattern for valid language code format: 2-3 letters optionally followed by region code
LANG_FORMAT_PATTERN = re.compile(r'^[a-z]{2,3}(-[A-Z]{2})?$', re.IGNORECASE)

TEST_DOCUMENTATION = {
    "testName": "Language Declaration Tests",
    "touchpoint": "language",
    "description": "Tests proper language declarations on HTML element and language changes throughout the document.",
    "version": "1.0.0",
    "wcagCriteria": ["3.1.1", "3.1.2"],
    "tests": [
        {
            "id": "page-language",
            "name": "Page Language Declaration",
            "description": "Checks that the HTML element has a valid lang attribute.",
            "impact": "critical",
            "wcagCriteria": ["3.1.1"],
        },
        {
            "id": "language-changes",
            "name": "Language Changes",
            "description": "Checks that elements with lang attributes use valid language codes.",
            "impact": "serious",
            "wcagCriteria": ["3.1.2"],
        }
    ]
}


def validate_language_code(lang_code: str) -> tuple[bool, bool, str]:
    """
    Validate a language code.

    Args:
        lang_code: The language code to validate

    Returns:
        Tuple of (is_valid_format, is_recognized_code, primary_language)
    """
    if not lang_code or not lang_code.strip():
        return (False, False, '')

    # Check format
    if not LANG_FORMAT_PATTERN.match(lang_code):
        return (False, False, '')

    # Extract primary language code (before dash if present)
    primary_lang = lang_code.split('-')[0].lower()

    # Check if recognized
    is_recognized = primary_lang in VALID_LANGUAGE_CODES

    return (True, is_recognized, primary_lang)


async def test_language(page) -> Dict[str, Any]:
    """
    Test language declarations and attributes.

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results
    """
    try:
        # Get HTML element lang attribute and all elements with lang attributes
        lang_data = await page.evaluate('''
            () => {
                const htmlElement = document.querySelector('html');
                const htmlLang = htmlElement ? htmlElement.getAttribute('lang') : null;
                const htmlHasLang = htmlElement ? htmlElement.hasAttribute('lang') : false;

                // Get all elements with lang attribute (excluding html element)
                const elementsWithLang = Array.from(document.querySelectorAll('[lang]'))
                    .filter(el => el !== htmlElement)
                    .map(el => ({
                        tagName: el.tagName,
                        lang: el.getAttribute('lang'),
                        xpath: getXPath(el),
                        html: el.outerHTML.substring(0, 200)
                    }));

                // Simple XPath generator
                function getXPath(element) {
                    if (element.id) {
                        return `//*[@id="${element.id}"]`;
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    let ix = 0;
                    const siblings = element.parentNode ? element.parentNode.childNodes : [];
                    for (let i = 0; i < siblings.length; i++) {
                        const sibling = siblings[i];
                        if (sibling === element) {
                            return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }

                return {
                    htmlHasLang: htmlHasLang,
                    htmlLang: htmlLang,
                    elementsWithLang: elementsWithLang
                };
            }
        ''')

        results = {
            'applicable': True,
            'errors': [],
            'warnings': [],
            'discovery': [],
            'passes': [],
            'elements_tested': 0,
            'elements_passed': 0,
            'elements_failed': 0,
            'test_name': 'language',
            'checks': []
        }

        # Test 1: HTML element language declaration
        lang_check = {
            'description': 'Page has language declaration',
            'wcag': ['3.1.1'],
            'total': 1,
            'passed': 0,
            'failed': 0
        }

        if not lang_data['htmlHasLang']:
            # Missing lang attribute
            results['errors'].append({
                'err': 'ErrNoPageLanguage',
                'type': 'err',
                'cat': 'language',
                'xpath': '/html',
                'html': '<html>',
                'fpTempId': '0'
            })
            lang_check['failed'] = 1
            results['elements_failed'] += 1
        elif not lang_data['htmlLang'] or not lang_data['htmlLang'].strip():
            # Empty lang attribute
            results['errors'].append({
                'err': 'ErrHtmlLangEmpty',
                'type': 'err',
                'cat': 'language',
                'xpath': '/html',
                'html': f"<html lang=\"{lang_data['htmlLang']}\">",
                'fpTempId': '0'
            })
            lang_check['failed'] = 1
            results['elements_failed'] += 1
        else:
            # Validate HTML lang code
            is_valid_format, is_recognized, primary_lang = validate_language_code(lang_data['htmlLang'])

            if not is_valid_format:
                # Invalid format
                results['errors'].append({
                    'err': 'ErrInvalidLanguageCode',
                    'type': 'err',
                    'cat': 'language',
                    'found': lang_data['htmlLang'],
                    'xpath': '/html',
                    'html': f"<html lang=\"{lang_data['htmlLang']}\">",
                    'fpTempId': '0'
                })
                lang_check['failed'] = 1
                results['elements_failed'] += 1
            elif not is_recognized:
                # Valid format but unrecognized code
                results['errors'].append({
                    'err': 'ErrPrimaryLangUnrecognized',
                    'type': 'err',
                    'cat': 'language',
                    'found': lang_data['htmlLang'],
                    'xpath': '/html',
                    'html': f"<html lang=\"{lang_data['htmlLang']}\">",
                    'fpTempId': '0'
                })
                lang_check['failed'] = 1
                results['elements_failed'] += 1
            else:
                # Valid and recognized
                results['passes'].append({
                    'check': 'page_language',
                    'language': lang_data['htmlLang'],
                    'xpath': '/html',
                    'wcag': ['3.1.1'],
                    'reason': 'Page has valid language declaration'
                })
                lang_check['passed'] = 1
                results['elements_passed'] += 1

        results['elements_tested'] += 1
        results['checks'].append(lang_check)

        # Test 2: Language changes on other elements
        if lang_data['elementsWithLang']:
            lang_change_check = {
                'description': 'Language changes properly marked',
                'wcag': ['3.1.2'],
                'total': len(lang_data['elementsWithLang']),
                'passed': 0,
                'failed': 0
            }

            for element in lang_data['elementsWithLang']:
                results['elements_tested'] += 1
                lang = element['lang']

                if not lang or not lang.strip():
                    # Empty lang attribute
                    results['errors'].append({
                        'err': 'ErrEmptyLanguageAttribute',
                        'type': 'err',
                        'cat': 'language',
                        'element': element['tagName'],
                        'xpath': element['xpath'],
                        'html': element['html'],
                        'fpTempId': '0'
                    })
                    lang_change_check['failed'] += 1
                    results['elements_failed'] += 1
                else:
                    # Validate element lang code
                    is_valid_format, is_recognized, primary_lang = validate_language_code(lang)

                    if not is_valid_format:
                        # Invalid format
                        results['errors'].append({
                            'err': 'ErrInvalidLangChange',
                            'type': 'err',
                            'cat': 'language',
                            'element': element['tagName'],
                            'found': lang,
                            'xpath': element['xpath'],
                            'html': element['html'],
                            'fpTempId': '0'
                        })
                        lang_change_check['failed'] += 1
                        results['elements_failed'] += 1
                    elif not is_recognized:
                        # Valid format but unrecognized code
                        results['errors'].append({
                            'err': 'ErrElementPrimaryLangNotRecognized',
                            'type': 'err',
                            'cat': 'language',
                            'element': element['tagName'],
                            'found': lang,
                            'xpath': element['xpath'],
                            'html': element['html'],
                            'fpTempId': '0'
                        })
                        lang_change_check['failed'] += 1
                        results['elements_failed'] += 1
                    else:
                        # Valid and recognized
                        results['passes'].append({
                            'check': 'language_change',
                            'element': element['tagName'],
                            'language': lang,
                            'xpath': element['xpath'],
                            'wcag': ['3.1.2'],
                            'reason': 'Language change properly marked'
                        })
                        lang_change_check['passed'] += 1
                        results['elements_passed'] += 1

            results['checks'].append(lang_change_check)

        return results

    except Exception as e:
        logger.error(f"Error in test_language: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'discovery': [],
            'passes': []
        }
