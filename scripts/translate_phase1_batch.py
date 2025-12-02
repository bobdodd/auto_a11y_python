#!/usr/bin/env python3
"""
AI-assisted translation of Phase 1 issue descriptions to French.

Uses W3C WCAG 2.2 French terminology and Drupal portal translations for consistency.
Preserves placeholders in %(variable)s format.
"""

import json
import sys
import polib
from pathlib import Path

# W3C WCAG 2.2 French terminology (reference)
WCAG_TERMINOLOGY = {
    # User Groups
    'screen reader users': 'utilisateurs de lecteurs d\'écran',
    'keyboard users': 'utilisateurs de clavier',
    'blind users': 'utilisateurs aveugles',
    'low vision users': 'utilisateurs malvoyants',
    'users with cognitive disabilities': 'utilisateurs ayant des troubles cognitifs',
    'users with motor impairments': 'utilisateurs ayant des troubles moteurs',

    # Technical Terms
    'alt text': 'texte alternatif',
    'alternative text': 'texte alternatif',
    'accessible name': 'nom accessible',
    'assistive technology': 'technologie d\'assistance',
    'landmark': 'région repère',
    'heading level': 'niveau de titre',
    'focus indicator': 'indicateur de focus',
    'keyboard navigation': 'navigation au clavier',
    'tab order': 'ordre de tabulation',
    'skip link': 'lien d\'évitement',

    # Actions/Concepts
    'navigate': 'naviguer',
    'screen reader announces': 'le lecteur d\'écran annonce',
    'perceive': 'percevoir',
    'understand': 'comprendre',
    'operate': 'utiliser',
    'distinguish': 'distinguer',
}

# Category-specific context for better translations
CATEGORY_CONTEXT = {
    'Images': """
Context: Accessibility issues related to images, graphics, icons, and visual content.
Focus on: alt text, alternative text descriptions, decorative vs informative images, SVG accessibility.
Key terms: image (image), alt attribute (attribut alt), decorative (décoratif), informative (informatif).
""",
    'Forms': """
Context: Accessibility issues related to form controls, inputs, labels, and interactive elements.
Focus on: form labels, input fields, buttons, fieldsets, legends, form validation.
Key terms: form (formulaire), input (champ de saisie), label (étiquette), button (bouton), control (contrôle).
""",
    'Headings': """
Context: Accessibility issues related to document structure, headings hierarchy, and semantic markup.
Focus on: heading levels (h1-h6), document outline, skipped levels, proper nesting.
Key terms: heading (titre), level (niveau), hierarchy (hiérarchie), structure (structure), outline (plan du document).
""",
    'Contrast': """
Context: Accessibility issues related to color contrast, visual perception, and color usage.
Focus on: contrast ratios, foreground/background colors, text readability, color-only information.
Key terms: contrast (contraste), color (couleur), foreground (premier plan), background (arrière-plan), ratio (rapport).
"""
}


def translate_string_anthropic(msgid, msgctxt, category):
    """
    Translate a string using Claude API (Anthropic).

    This is a placeholder function. In production, you would:
    1. Call Anthropic API with proper authentication
    2. Include WCAG terminology and category context
    3. Validate placeholder preservation
    4. Handle rate limiting and errors

    For now, this returns a manual translation template.
    """
    # TODO: Implement actual Anthropic API call
    # Example:
    # import anthropic
    # client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    # message = client.messages.create(
    #     model="claude-3-5-sonnet-20241022",
    #     max_tokens=1024,
    #     messages=[{
    #         "role": "user",
    #         "content": f"Translate this accessibility message to French...\n{msgid}"
    #     }]
    # )

    # For now, return None to indicate manual translation needed
    return None


def validate_placeholders(original, translated):
    """Validate that all placeholders are preserved in translation"""
    import re

    # Extract placeholders from original
    original_placeholders = set(re.findall(r'%\([a-zA-Z_][a-zA-Z0-9_]*\)s', original))

    # Extract placeholders from translation
    translated_placeholders = set(re.findall(r'%\([a-zA-Z_][a-zA-Z0-9_]*\)s', translated))

    # Check if all placeholders are preserved
    if original_placeholders != translated_placeholders:
        return False, f"Placeholder mismatch: {original_placeholders} != {translated_placeholders}"

    return True, "OK"


def create_translation_template(phase1_file, output_file):
    """
    Create a translation template file for manual or AI-assisted translation.

    Output format is suitable for:
    1. Manual translation in a spreadsheet
    2. Batch AI translation
    3. Import back into .po file
    """
    with open(phase1_file, 'r', encoding='utf-8') as f:
        phase1_data = json.load(f)

    # Prepare translation entries
    translation_entries = []

    for category, issues in phase1_data['categories'].items():
        for issue in issues:
            for string_data in issue['strings']:
                entry = {
                    'category': category,
                    'issue_code': string_data['issue_code'],
                    'field': string_data['field'],
                    'msgctxt': string_data['msgctxt'],
                    'msgid': string_data['msgid'],
                    'original': string_data['original'],
                    'msgstr': '',  # To be filled
                    'notes': f"{category} - {string_data['field']}"
                }
                translation_entries.append(entry)

    # Save as JSON for easy processing
    output_data = {
        'metadata': {
            'total_entries': len(translation_entries),
            'categories': list(phase1_data['categories'].keys()),
            'category_context': CATEGORY_CONTEXT,
            'wcag_terminology': WCAG_TERMINOLOGY
        },
        'entries': translation_entries
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Translation template created: {output_file}")
    print(f"Total entries to translate: {len(translation_entries)}")
    print(f"\nNext steps:")
    print(f"1. Use this file with AI translation service (Claude API)")
    print(f"2. Or export to CSV for manual translation")
    print(f"3. Then run: python scripts/import_translations.py {output_file}")


def main():
    phase1_file = 'phase1_strings.json'

    if not Path(phase1_file).exists():
        print(f"Error: {phase1_file} not found", file=sys.stderr)
        print("Run: python scripts/identify_phase1_issues.py", file=sys.stderr)
        return 1

    # Create translation template
    template_file = 'phase1_translation_template.json'
    create_translation_template(phase1_file, template_file)

    print(f"\n{'='*60}")
    print("AI Translation Setup Complete")
    print(f"{'='*60}")
    print("\nTo proceed with AI translation:")
    print("1. Review the translation template")
    print("2. Use Claude API to translate in batches")
    print("3. Import translations back to .po file")

    return 0


if __name__ == '__main__':
    sys.exit(main())
