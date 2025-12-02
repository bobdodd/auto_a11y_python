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

# ISO 3166-1 alpha-2 region codes (subset of most common ones)
VALID_REGION_CODES: Set[str] = {
    'AD', 'AE', 'AF', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU', 'AZ',
    'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BN', 'BO', 'BR', 'BS', 'BT', 'BW', 'BY', 'BZ',
    'CA', 'CD', 'CF', 'CG', 'CH', 'CI', 'CL', 'CM', 'CN', 'CO', 'CR', 'CU', 'CV', 'CY', 'CZ',
    'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ',
    'EC', 'EE', 'EG', 'ER', 'ES', 'ET',
    'FI', 'FJ', 'FM', 'FR',
    'GA', 'GB', 'GD', 'GE', 'GH', 'GM', 'GN', 'GQ', 'GR', 'GT', 'GW', 'GY',
    'HK', 'HN', 'HR', 'HT', 'HU',
    'ID', 'IE', 'IL', 'IN', 'IQ', 'IR', 'IS', 'IT',
    'JM', 'JO', 'JP',
    'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KR', 'KW', 'KZ',
    'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY',
    'MA', 'MC', 'MD', 'ME', 'MG', 'MH', 'MK', 'ML', 'MM', 'MN', 'MO', 'MR', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ',
    'NA', 'NE', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NZ',
    'OM',
    'PA', 'PE', 'PG', 'PH', 'PK', 'PL', 'PS', 'PT', 'PW', 'PY',
    'QA',
    'RO', 'RS', 'RU', 'RW',
    'SA', 'SB', 'SC', 'SD', 'SE', 'SG', 'SI', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SY', 'SZ',
    'TD', 'TG', 'TH', 'TJ', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ',
    'UA', 'UG', 'US', 'UY', 'UZ',
    'VA', 'VC', 'VE', 'VN', 'VU',
    'WS',
    'YE',
    'ZA', 'ZM', 'ZW'
}

# Regex pattern for valid language code format: 2-3 letters optionally followed by region code
# We allow any letter sequence after dash or underscore to catch formatting errors and invalid region codes
LANG_FORMAT_PATTERN = re.compile(r'^[a-z]{2,3}([-_][A-Za-z]+)?$', re.IGNORECASE)

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


def validate_language_code(lang_code: str) -> tuple[bool, bool, bool, bool, str, str]:
    """
    Validate a language code.

    Args:
        lang_code: The language code to validate

    Returns:
        Tuple of (is_valid_format, is_correctly_formatted, is_recognized_lang, is_recognized_region, primary_language, region_code)
    """
    if not lang_code or not lang_code.strip():
        return (False, False, False, False, '', '')

    # Check for formatting issues BEFORE normalization
    is_correctly_formatted = True

    # Check for whitespace (leading, trailing, or internal)
    if lang_code != lang_code.strip() or '  ' in lang_code:
        is_correctly_formatted = False

    # Check for underscore separator (common mistake - should be hyphen)
    if '_' in lang_code:
        is_correctly_formatted = False

    # Check basic format pattern (allows any case to detect case issues)
    if not LANG_FORMAT_PATTERN.match(lang_code):
        return (False, False, False, False, '', '')

    # If format matches, check case sensitivity
    if '-' in lang_code:
        parts = lang_code.split('-')
        # Language code should be lowercase, region should be uppercase
        if parts[0] != parts[0].lower() or parts[1] != parts[1].upper():
            is_correctly_formatted = False

    # Extract primary language code and region code (normalized for validation)
    parts = lang_code.split('-')
    primary_lang = parts[0].lower()
    region_code = parts[1].upper() if len(parts) > 1 else ''

    # Check if primary language is recognized
    is_recognized_lang = primary_lang in VALID_LANGUAGE_CODES

    # Check if region code is recognized (empty region is valid)
    is_recognized_region = region_code == '' or region_code in VALID_REGION_CODES

    return (True, is_correctly_formatted, is_recognized_lang, is_recognized_region, primary_lang, region_code)


async def test_language(page) -> Dict[str, Any]:
    """
    Test language declarations and attributes.

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results
    """
    try:
        # Get HTML element lang/xml:lang attributes, elements with lang, and elements with hreflang
        lang_data = await page.evaluate('''
            () => {
                const htmlElement = document.querySelector('html');
                const htmlLang = htmlElement ? htmlElement.getAttribute('lang') : null;
                const htmlHasLang = htmlElement ? htmlElement.hasAttribute('lang') : false;
                const htmlXmlLang = htmlElement ? htmlElement.getAttribute('xml:lang') : null;
                const htmlHasXmlLang = htmlElement ? htmlElement.hasAttribute('xml:lang') : false;

                // Get all elements with lang attribute (excluding html element)
                const elementsWithLang = Array.from(document.querySelectorAll('[lang]'))
                    .filter(el => el !== htmlElement)
                    .map(el => ({
                        tagName: el.tagName,
                        lang: el.getAttribute('lang'),
                        xmlLang: el.getAttribute('xml:lang'),
                        hasXmlLang: el.hasAttribute('xml:lang'),
                        xpath: getXPath(el),
                        html: el.outerHTML.substring(0, 200)
                    }));

                // Get all elements with hreflang attribute
                const elementsWithHreflang = Array.from(document.querySelectorAll('[hreflang]'))
                    .map(el => ({
                        tagName: el.tagName,
                        hreflang: el.getAttribute('hreflang'),
                        xpath: getXPath(el),
                        html: el.outerHTML.substring(0, 200),
                        isLink: el.tagName === 'A' || el.tagName === 'LINK' || el.tagName === 'AREA'
                    }));

                // Simple XPath generator
                function getXPath(element) {
                    if (!element || element.nodeType !== 1) {
                        return '';
                    }
                    if (element.id) {
                        return `//*[@id="${element.id}"]`;
                    }
                    if (element === document.documentElement) {
                        return '/html';
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    if (!element.parentNode) {
                        return '';
                    }
                    let ix = 0;
                    const siblings = element.parentNode.childNodes;
                    for (let i = 0; i < siblings.length; i++) {
                        const sibling = siblings[i];
                        if (sibling === element) {
                            const parentPath = getXPath(element.parentNode);
                            if (!parentPath) {
                                return '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                            }
                            return parentPath + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                    return '';
                }

                return {
                    htmlHasLang: htmlHasLang,
                    htmlLang: htmlLang,
                    htmlHasXmlLang: htmlHasXmlLang,
                    htmlXmlLang: htmlXmlLang,
                    elementsWithLang: elementsWithLang,
                    elementsWithHreflang: elementsWithHreflang
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
            is_valid_format, is_correctly_formatted, is_recognized_lang, is_recognized_region, primary_lang, region_code = validate_language_code(lang_data['htmlLang'])

            if not is_valid_format:
                # Invalid format (completely unrecognizable)
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
            elif not is_correctly_formatted:
                # Valid structure but incorrect formatting (wrong case, whitespace, underscore)
                results['errors'].append({
                    'err': 'ErrIncorrectlyFormattedPrimaryLang',
                    'type': 'err',
                    'cat': 'language',
                    'found': lang_data['htmlLang'],
                    'xpath': '/html',
                    'html': f"<html lang=\"{lang_data['htmlLang']}\">",
                    'fpTempId': '0'
                })
                lang_check['failed'] = 1
                results['elements_failed'] += 1
            elif not is_recognized_lang:
                # Correctly formatted but unrecognized primary language
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
            elif not is_recognized_region:
                # Correctly formatted and recognized language but unrecognized region code
                results['errors'].append({
                    'err': 'ErrRegionQualifierForPrimaryLangNotRecognized',
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
                    is_valid_format, is_correctly_formatted, is_recognized_lang, is_recognized_region, primary_lang, region_code = validate_language_code(lang)

                    if not is_valid_format:
                        # Invalid format (completely unrecognizable)
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
                    elif not is_correctly_formatted:
                        # Valid structure but incorrect formatting (wrong case, whitespace, underscore)
                        results['errors'].append({
                            'err': 'ErrIncorrectlyFormattedPrimaryLang',
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
                    elif not is_recognized_lang:
                        # Correctly formatted but unrecognized primary language
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
                    elif not is_recognized_region:
                        # Correctly formatted and recognized language but unrecognized region code
                        results['errors'].append({
                            'err': 'ErrElementRegionQualifierNotRecognized',
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
                    elif element['hasXmlLang'] and element['xmlLang'] and element['xmlLang'].strip():
                        # Element has both lang and xml:lang - validate xml:lang first
                        xml_is_valid_format, xml_is_correctly_formatted, xml_is_recognized_lang, xml_is_recognized_region, xml_primary_lang, xml_region_code = validate_language_code(element['xmlLang'])

                        if not xml_is_valid_format or not xml_is_recognized_lang:
                            # xml:lang is invalid or unrecognized - report that error first
                            results['errors'].append({
                                'err': 'ErrPrimaryXmlLangUnrecognized',
                                'type': 'err',
                                'cat': 'language',
                                'element': element['tagName'],
                                'found': element['xmlLang'],
                                'xpath': element['xpath'],
                                'html': element['html'],
                                'fpTempId': '0'
                            })
                            lang_change_check['failed'] += 1
                            results['elements_failed'] += 1
                        elif not xml_is_recognized_region:
                            # xml:lang has unrecognized region
                            results['errors'].append({
                                'err': 'ErrRegionQualifierForPrimaryXmlLangNotRecognized',
                                'type': 'err',
                                'cat': 'language',
                                'element': element['tagName'],
                                'found': element['xmlLang'],
                                'xpath': element['xpath'],
                                'html': element['html'],
                                'fpTempId': '0'
                            })
                            lang_change_check['failed'] += 1
                            results['elements_failed'] += 1
                        elif lang.strip().lower() != element['xmlLang'].strip().lower():
                            # Both are valid but mismatch
                            results['errors'].append({
                                'err': 'ErrPrimaryLangAndXmlLangMismatch',
                                'type': 'err',
                                'cat': 'language',
                                'element': element['tagName'],
                                'found': f"lang=\"{lang}\" xml:lang=\"{element['xmlLang']}\"",
                                'xpath': element['xpath'],
                                'html': element['html'],
                                'fpTempId': '0'
                            })
                            lang_change_check['failed'] += 1
                            results['elements_failed'] += 1
                        else:
                            # Both valid and match
                            results['passes'].append({
                                'check': 'language_change',
                                'element': element['tagName'],
                                'language': lang,
                                'xpath': element['xpath'],
                                'wcag': ['3.1.2'],
                                'reason': 'Language change properly marked with matching xml:lang'
                            })
                            lang_change_check['passed'] += 1
                            results['elements_passed'] += 1
                    else:
                        # Valid and recognized, no xml:lang to worry about
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

        # Test 3: XML:lang attribute on HTML element with full validation
        if lang_data['htmlHasXmlLang']:
            xml_lang_check = {
                'description': 'XML:lang attribute is valid',
                'wcag': ['3.1.1'],
                'total': 1,
                'passed': 0,
                'failed': 0
            }

            if not lang_data['htmlXmlLang'] or not lang_data['htmlXmlLang'].strip():
                # Empty xml:lang attribute
                results['errors'].append({
                    'err': 'ErrEmptyXmlLangAttr',
                    'type': 'err',
                    'cat': 'language',
                    'xpath': '/html',
                    'html': f"<html xml:lang=\"{lang_data['htmlXmlLang'] or ''}\">",
                    'fpTempId': '0'
                })
                xml_lang_check['failed'] = 1
                results['elements_failed'] += 1
            else:
                # Validate xml:lang code
                is_valid_format, is_correctly_formatted, is_recognized_lang, is_recognized_region, primary_lang, region_code = validate_language_code(lang_data['htmlXmlLang'])

                if not is_valid_format:
                    # Invalid format - completely unrecognizable
                    results['errors'].append({
                        'err': 'ErrPrimaryXmlLangUnrecognized',
                        'type': 'err',
                        'cat': 'language',
                        'found': lang_data['htmlXmlLang'],
                        'xpath': '/html',
                        'html': f"<html xml:lang=\"{lang_data['htmlXmlLang']}\">",
                        'fpTempId': '0'
                    })
                    xml_lang_check['failed'] = 1
                    results['elements_failed'] += 1
                elif not is_recognized_lang:
                    # Valid format but unrecognized language code
                    results['errors'].append({
                        'err': 'ErrPrimaryXmlLangUnrecognized',
                        'type': 'err',
                        'cat': 'language',
                        'found': lang_data['htmlXmlLang'],
                        'xpath': '/html',
                        'html': f"<html xml:lang=\"{lang_data['htmlXmlLang']}\">",
                        'fpTempId': '0'
                    })
                    xml_lang_check['failed'] = 1
                    results['elements_failed'] += 1
                elif not is_recognized_region:
                    # Valid language but unrecognized region code
                    results['errors'].append({
                        'err': 'ErrRegionQualifierForPrimaryXmlLangNotRecognized',
                        'type': 'err',
                        'cat': 'language',
                        'found': lang_data['htmlXmlLang'],
                        'xpath': '/html',
                        'html': f"<html xml:lang=\"{lang_data['htmlXmlLang']}\">",
                        'fpTempId': '0'
                    })
                    xml_lang_check['failed'] = 1
                    results['elements_failed'] += 1
                elif lang_data['htmlHasLang'] and lang_data['htmlLang'] and lang_data['htmlLang'].strip():
                    # Both lang and xml:lang are valid - check for mismatch
                    if lang_data['htmlLang'].strip().lower() != lang_data['htmlXmlLang'].strip().lower():
                        # Mismatch between lang and xml:lang
                        results['errors'].append({
                            'err': 'ErrPrimaryLangAndXmlLangMismatch',
                            'type': 'err',
                            'cat': 'language',
                            'found': f"lang=\"{lang_data['htmlLang']}\" xml:lang=\"{lang_data['htmlXmlLang']}\"",
                            'xpath': '/html',
                            'html': f"<html lang=\"{lang_data['htmlLang']}\" xml:lang=\"{lang_data['htmlXmlLang']}\">",
                            'fpTempId': '0'
                        })
                        xml_lang_check['failed'] = 1
                        results['elements_failed'] += 1
                    else:
                        # lang and xml:lang match and are both valid
                        results['passes'].append({
                            'check': 'xml_lang',
                            'language': lang_data['htmlXmlLang'],
                            'xpath': '/html',
                            'wcag': ['3.1.1'],
                            'reason': 'xml:lang matches lang attribute'
                        })
                        xml_lang_check['passed'] = 1
                        results['elements_passed'] += 1
                else:
                    # xml:lang is valid, no lang or lang is empty
                    results['passes'].append({
                        'check': 'xml_lang',
                        'language': lang_data['htmlXmlLang'],
                        'xpath': '/html',
                        'wcag': ['3.1.1'],
                        'reason': 'xml:lang attribute has valid value'
                    })
                    xml_lang_check['passed'] = 1
                    results['elements_passed'] += 1

            results['elements_tested'] += 1
            results['checks'].append(xml_lang_check)

        # Test 4: Hreflang attributes
        if lang_data['elementsWithHreflang']:
            hreflang_check = {
                'description': 'Hreflang attributes properly used',
                'wcag': ['3.1.1'],
                'total': len(lang_data['elementsWithHreflang']),
                'passed': 0,
                'failed': 0
            }

            for element in lang_data['elementsWithHreflang']:
                hreflang = element['hreflang']

                # Check if hreflang is on a link element
                if not element['isLink']:
                    # hreflang on non-link element
                    results['errors'].append({
                        'err': 'ErrHreflangNotOnLink',
                        'type': 'err',
                        'cat': 'language',
                        'element': element['tagName'],
                        'found': hreflang,
                        'xpath': element['xpath'],
                        'html': element['html'],
                        'fpTempId': '0'
                    })
                    hreflang_check['failed'] += 1
                    results['elements_failed'] += 1
                elif not hreflang or not hreflang.strip():
                    # Empty hreflang attribute on link
                    results['errors'].append({
                        'err': 'ErrHreflangAttrEmpty',
                        'type': 'err',
                        'cat': 'language',
                        'element': element['tagName'],
                        'xpath': element['xpath'],
                        'html': element['html'],
                        'fpTempId': '0'
                    })
                    hreflang_check['failed'] += 1
                    results['elements_failed'] += 1
                else:
                    # Validate hreflang language code
                    is_valid_format, is_correctly_formatted, is_recognized_lang, is_recognized_region, primary_lang, region_code = validate_language_code(hreflang)

                    if not is_valid_format:
                        # Invalid format - completely unrecognizable
                        results['errors'].append({
                            'err': 'ErrPrimaryHrefLangNotRecognized',
                            'type': 'err',
                            'cat': 'language',
                            'element': element['tagName'],
                            'found': hreflang,
                            'xpath': element['xpath'],
                            'html': element['html'],
                            'fpTempId': '0'
                        })
                        hreflang_check['failed'] += 1
                        results['elements_failed'] += 1
                    elif not is_recognized_lang:
                        # Valid format but unrecognized language code
                        results['errors'].append({
                            'err': 'ErrPrimaryHrefLangNotRecognized',
                            'type': 'err',
                            'cat': 'language',
                            'element': element['tagName'],
                            'found': hreflang,
                            'xpath': element['xpath'],
                            'html': element['html'],
                            'fpTempId': '0'
                        })
                        hreflang_check['failed'] += 1
                        results['elements_failed'] += 1
                    elif not is_recognized_region:
                        # Valid language but unrecognized region code
                        results['errors'].append({
                            'err': 'ErrRegionQualifierForHreflangUnrecognized',
                            'type': 'err',
                            'cat': 'language',
                            'element': element['tagName'],
                            'found': hreflang,
                            'xpath': element['xpath'],
                            'html': element['html'],
                            'fpTempId': '0'
                        })
                        hreflang_check['failed'] += 1
                        results['elements_failed'] += 1
                    else:
                        # Valid and recognized hreflang
                        results['passes'].append({
                            'check': 'hreflang',
                            'element': element['tagName'],
                            'language': hreflang,
                            'xpath': element['xpath'],
                            'wcag': ['3.1.1'],
                            'reason': 'Hreflang properly used on link element'
                        })
                        hreflang_check['passed'] += 1
                        results['elements_passed'] += 1

            results['checks'].append(hreflang_check)

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
