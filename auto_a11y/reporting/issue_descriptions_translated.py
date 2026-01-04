"""
Translation wrapper for issue descriptions.

This module wraps get_detailed_issue_description() to provide runtime translation
of accessibility issue descriptions using built-in translations stored in JSON.

The translations are loaded from issue_translations_fr.json which was extracted
from the PO file. This approach avoids pybabel update issues that comment out
translations for strings not found in direct _() calls.
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

from auto_a11y.reporting.issue_descriptions_enhanced import (
    get_detailed_issue_description as _get_original_description,
    ImpactScale,
    format_issue_for_display as _format_issue_for_display
)

_TRANSLATIONS_CACHE: Dict[str, Dict[str, Dict[str, str]]] = {}


def _load_translations(lang: str) -> Dict[str, Dict[str, str]]:
    """Load translations for a language from JSON file."""
    if lang in _TRANSLATIONS_CACHE:
        return _TRANSLATIONS_CACHE[lang]
    
    translations_file = Path(__file__).parent / f'issue_translations_{lang}.json'
    if translations_file.exists():
        try:
            with open(translations_file, 'r', encoding='utf-8') as f:
                _TRANSLATIONS_CACHE[lang] = json.load(f)
                logger.debug(f"Loaded {len(_TRANSLATIONS_CACHE[lang])} issue translations for {lang}")
        except Exception as e:
            logger.warning(f"Failed to load translations for {lang}: {e}")
            _TRANSLATIONS_CACHE[lang] = {}
    else:
        _TRANSLATIONS_CACHE[lang] = {}
    
    return _TRANSLATIONS_CACHE[lang]


def _get_current_locale() -> str:
    """Get the current locale from Flask-Babel."""
    try:
        from flask_babel import get_locale
        locale = get_locale()
        if locale:
            return str(locale.language)
    except Exception:
        pass
    return 'en'


def _extract_error_type(issue_code: str) -> str:
    """Extract the error type from an issue code."""
    if issue_code.startswith('AI_'):
        return issue_code
    
    if '_' in issue_code:
        parts = issue_code.split('_')
        for i, part in enumerate(parts):
            if part.startswith(('Err', 'Warn', 'Info', 'Disco')):
                return '_'.join(parts[i:])
    
    return issue_code


def get_detailed_issue_description(issue_code: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get detailed translated description for an issue code.

    Uses built-in JSON translations instead of pgettext for reliability.

    Args:
        issue_code: The issue code (e.g., 'headings_ErrEmptyHeading')
        metadata: Additional context about the specific issue instance

    Returns:
        Dictionary with translated description fields
    """
    desc = _get_original_description(issue_code, metadata)

    if not desc:
        return desc

    translated_desc = desc.copy()
    
    lang = _get_current_locale()
    
    if lang == 'en':
        return _apply_metadata(translated_desc, metadata)
    
    translations = _load_translations(lang)
    error_type = _extract_error_type(issue_code)
    
    if error_type in translations:
        issue_trans = translations[error_type]
        translatable_fields = ('title', 'what', 'what_generic', 'why', 'who', 'remediation')
        
        for field in translatable_fields:
            if field in issue_trans and issue_trans[field]:
                translated_desc[field] = issue_trans[field]
    
    return _apply_metadata(translated_desc, metadata)


def _apply_metadata(desc: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Apply metadata substitution to description fields."""
    if not metadata:
        return desc
    
    translatable_fields = ('title', 'what', 'what_generic', 'why', 'who', 'remediation')
    
    for field in translatable_fields:
        if field in desc and isinstance(desc[field], str):
            try:
                text = desc[field]
                escaped_text = re.sub(r'%(?!\()', '%%', text)
                desc[field] = escaped_text % metadata
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Placeholder substitution failed for field {field}: {e}")
    
    return desc


def format_issue_for_display(issue_code: str, violation_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Format an issue with all its metadata for display (translated).
    """
    description = get_detailed_issue_description(issue_code, violation_data)

    description['issue_id'] = issue_code
    description['location'] = violation_data.get('xpath', 'Not specified')
    description['element'] = violation_data.get('element', 'Not specified')
    description['url'] = violation_data.get('url', 'Not specified')

    return description


__all__ = [
    'get_detailed_issue_description',
    'format_issue_for_display',
    'ImpactScale',
]
