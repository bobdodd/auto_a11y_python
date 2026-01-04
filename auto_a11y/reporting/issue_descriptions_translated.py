"""
Translation wrapper for issue descriptions.

This module wraps get_detailed_issue_description() to provide runtime translation
of accessibility issue descriptions using Flask-Babel.

Phase 1 (Beta Demo): Temporary wrapper approach
Phase 2 (Post-Demo): Will be replaced by regenerated source with built-in translations
"""

import re
from typing import Dict, Any
from flask_babel import gettext as _, pgettext

# Import everything from the original module
from auto_a11y.reporting.issue_descriptions_enhanced import (
    get_detailed_issue_description as _get_original_description,
    ImpactScale,
    format_issue_for_display as _format_issue_for_display
)


def convert_placeholders(text: str) -> str:
    """
    Convert Python f-string style placeholders to gettext format.

    Converts:
        {variable} → %(variable)s
        {object.attribute} → %(object_attribute)s

    Args:
        text: String with {placeholder} format

    Returns:
        String with %(placeholder)s format
    """
    if not text or not isinstance(text, str):
        return text

    # Pattern to match {variable} or {object.attribute}
    pattern = r'\{([a-zA-Z_][a-zA-Z0-9_\.]*)\}'

    def replacer(match):
        var_name = match.group(1)
        # Convert dot notation to underscore: {element.tag} → %(element_tag)s
        var_name = var_name.replace('.', '_')
        return f'%({var_name})s'

    return re.sub(pattern, replacer, text)


def get_detailed_issue_description(issue_code: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get detailed translated description for an issue code.

    This wrapper:
    1. Calls the original get_detailed_issue_description()
    2. Translates each text field using Flask-Babel gettext
    3. Converts placeholders to gettext format

    Args:
        issue_code: The issue code (e.g., 'headings_ErrEmptyHeading')
        metadata: Additional context about the specific issue instance

    Returns:
        Dictionary with translated description fields
    """
    # Get original English description with placeholder replacement already done
    desc = _get_original_description(issue_code, metadata)

    if not desc:
        return desc

    # Make a copy to avoid modifying the original
    translated_desc = desc.copy()

    # Extract the error type for msgctxt (strip category prefix if present)
    error_type = issue_code
    if '_' in issue_code:
        parts = issue_code.split('_')
        for i, part in enumerate(parts):
            if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI_')):
                error_type = '_'.join(parts[i:])
                break

    # Translate each text field with context
    translatable_fields = ('title', 'what', 'what_generic', 'why', 'who', 'remediation')

    for field in translatable_fields:
        if field in desc and isinstance(desc[field], str):
            # Create context-specific msgctxt
            msgctxt = f'issue_{error_type}_{field}'

            # Convert placeholders in original text
            converted_text = convert_placeholders(desc[field])

            # Translate with context using pgettext (context, message)
            translated_text = pgettext(msgctxt, converted_text)

            # If translation returned the same text, it means no translation exists
            # In that case, keep the original English text
            translated_desc[field] = translated_text

    # Apply metadata substitution to translated text
    # The translated text has %(variable)s placeholders that need to be filled
    if metadata:
        for field in translatable_fields:
            if field in translated_desc and isinstance(translated_desc[field], str):
                try:
                    # Escape literal % characters that are NOT format specifiers
                    # before applying % formatting. This handles cases like "8% of men"
                    # where the % is literal text, not a format specifier.
                    text = translated_desc[field]
                    # Replace % with %% EXCEPT when followed by ( which indicates %(name)s
                    escaped_text = re.sub(r'%(?!\()', '%%', text)
                    translated_desc[field] = escaped_text % metadata
                except (KeyError, ValueError, TypeError) as e:
                    # Log the error for debugging but don't fail
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Placeholder substitution failed for {issue_code}: {e}, keys available: {list(metadata.keys())}")

    return translated_desc


def format_issue_for_display(issue_code: str, violation_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Format an issue with all its metadata for display (translated).

    This is a pass-through wrapper that uses our translated get_detailed_issue_description.
    """
    # Get the translated description using our wrapper
    description = get_detailed_issue_description(issue_code, violation_data)

    # Add any additional runtime data (same as original)
    description['issue_id'] = issue_code
    description['location'] = violation_data.get('xpath', 'Not specified')
    description['element'] = violation_data.get('element', 'Not specified')
    description['url'] = violation_data.get('url', 'Not specified')

    return description


# Re-export ImpactScale for convenience
__all__ = [
    'get_detailed_issue_description',
    'format_issue_for_display',
    'ImpactScale',
    'convert_placeholders',
]
