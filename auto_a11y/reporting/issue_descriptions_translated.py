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
    """Apply metadata substitution to description fields using {placeholder} syntax."""
    if not metadata:
        return desc
    
    translatable_fields = ('title', 'what', 'what_generic', 'why', 'who', 'remediation')
    
    for field in translatable_fields:
        if field in desc and isinstance(desc[field], str):
            text = desc[field]
            
            # Special handling for contrast ratio placeholders
            # The test sends: textColor, backgroundColor, contrastRatio
            # But descriptions use: {fg}, {bg}, {ratio}
            if '{ratio}' in text and 'contrastRatio' in metadata:
                contrast_ratio = metadata.get('contrastRatio', '')
                if isinstance(contrast_ratio, str) and contrast_ratio.endswith(':1'):
                    contrast_ratio = contrast_ratio[:-2]
                text = text.replace('{ratio}', str(contrast_ratio))
            
            if '{fg}' in text and 'textColor' in metadata:
                text = text.replace('{fg}', str(metadata.get('textColor', '')))
            
            if '{bg}' in text and 'backgroundColor' in metadata:
                text = text.replace('{bg}', str(metadata.get('backgroundColor', '')))
            
            # Special handling for calculated line height minimum
            if '{minLineHeight}' in text and 'fontSize' in metadata:
                font_size = float(metadata.get('fontSize', 16))
                min_line_height = font_size * 1.5
                text = text.replace('{minLineHeight}', f"{min_line_height:.2f}")
            
            # Handle plural/singular forms
            if '{sizeCount_singular_size}' in text and 'sizeCount' in metadata:
                count = metadata.get('sizeCount', 0)
                text = text.replace('{sizeCount_singular_size}', 'size' if count == 1 else 'different sizes')
            
            if '{fieldCount_plural}' in text and 'fieldCount' in metadata:
                count = metadata.get('fieldCount', 0)
                text = text.replace('{fieldCount_plural}', 's' if count != 1 else '')
            
            # Handle search context placeholders
            if '{searchContext_title}' in text:
                text = text.replace('{searchContext_title}', metadata.get('searchContext', {}).get('title', ''))
            if '{searchContext_remediation}' in text:
                text = text.replace('{searchContext_remediation}', metadata.get('searchContext', {}).get('remediation', ''))
            
            # Handle label descriptions
            for label_key in ['asideLabel_description', 'footerLabel_description', 'headerLabel_description']:
                if '{' + label_key + '}' in text:
                    base_key = label_key.replace('_description', '')
                    label_data = metadata.get(base_key, {})
                    if isinstance(label_data, dict):
                        text = text.replace('{' + label_key + '}', label_data.get('description', ''))
            
            # Handle link count plural
            if '{linkCount_plural}' in text and 'linkCount' in metadata:
                count = metadata.get('linkCount', 0)
                text = text.replace('{linkCount_plural}', 's' if count != 1 else '')
            
            # Replace standard {key} placeholders from metadata
            nested_pattern = r'\{([^}]+)\}'
            
            def replace_nested(match):
                path = match.group(1)
                
                # Skip special placeholders already handled above
                if path in ['fontSizes_list', 'sizeCount_plural', 'sizeCount_singular_size', 'fieldCount_plural', 
                            'fieldTypes_summary', 'searchContext_title', 'searchContext_description', 
                            'searchContext_remediation', 'minLineHeight', 'ratio', 'fg', 'bg',
                            'asideLabel_description', 'footerLabel_description', 'headerLabel_description',
                            'linkCount_plural']:
                    return match.group(0)
                
                parts = path.split('.')
                
                # Navigate through nested dict/objects
                value = metadata
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return match.group(0)  # Return original if path not found
                
                return str(value) if value is not None else match.group(0)
            
            text = re.sub(nested_pattern, replace_nested, text)
            desc[field] = text
    
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
