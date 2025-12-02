#!/usr/bin/env python3
"""
Add French translations for FAQ and remaining help content
"""

import re

# Multi-line strings need special handling
MULTILINE_TRANSLATIONS = {
    "Level AA is the recommended target and legal requirement in many jurisdictions. Level A is the absolute minimum, while Level AAA is typically only required for specific content or specialized applications.":
        "Le niveau AA est la cible recommandée et l'exigence légale dans de nombreuses juridictions. Le niveau A est le minimum absolu, tandis que le niveau AAA n'est généralement requis que pour un contenu spécifique ou des applications spécialisées.",

    "Test after every significant change to your site. Set up automated testing in your CI/CD pipeline to catch issues early. Run comprehensive tests at least monthly for active sites.":
        "Testez après chaque modification significative de votre site. Configurez des tests automatisés dans votre pipeline CI/CD pour détecter les problèmes tôt. Effectuez des tests complets au moins mensuellement pour les sites actifs.",

    "Automated testing (like Auto A11y) can catch about 30-40% of accessibility issues quickly and consistently. Manual testing is needed for subjective criteria like whether alt text is meaningful or if the reading order makes sense. Use both for comprehensive coverage.":
        "Les tests automatisés (comme Auto A11y) peuvent détecter environ 30 à 40 % des problèmes d'accessibilité rapidement et de manière cohérente. Les tests manuels sont nécessaires pour les critères subjectifs comme savoir si le texte alternatif est significatif ou si l'ordre de lecture a du sens. Utilisez les deux pour une couverture complète.",

    "Auto A11y is an automated web accessibility testing tool designed to help developers and testers identify and fix accessibility issues in web applications.":
        "Auto A11y est un outil automatisé de test d'accessibilité Web conçu pour aider les développeurs et les testeurs à identifier et corriger les problèmes d'accessibilité dans les applications Web.",

    "This application uses official WCAG (Web Content Accessibility Guidelines) data from the World Wide Web Consortium (W3C).":
        "Cette application utilise les données officielles WCAG (Web Content Accessibility Guidelines) du World Wide Web Consortium (W3C).",

    "The WCAG content is used with attribution as permitted by W3C. The content has not been modified. All additional content, analysis, and features provided by Auto A11y are clearly distinguished from the original W3C WCAG content.":
        "Le contenu WCAG est utilisé avec attribution tel que permis par le W3C. Le contenu n'a pas été modifié. Tout le contenu supplémentaire, les analyses et les fonctionnalités fournies par Auto A11y sont clairement distingués du contenu WCAG original du W3C.",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    for english, french in MULTILINE_TRANSLATIONS.items():
        # Normalize the English text (remove extra spaces, newlines)
        english_normalized = ' '.join(english.split())
        french_normalized = french

        # Try to find and replace the pattern
        # The .po file might have the text split across multiple lines
        # We need to match it with possible line breaks

        # First, try exact match for single-line entries
        pattern = f'msgid "{english}"\nmsgstr ""'
        replacement = f'msgid "{english}"\nmsgstr "{french}"'

        if pattern in content:
            content = content.replace(pattern, replacement)
            translations_added += 1
            print(f"✓ Added (single-line): {english[:60]}...")
            continue

        # For multi-line entries, we need to be more careful
        # Look for patterns like:
        # msgid ""
        # "Line 1 "
        # "Line 2"
        # msgstr ""

        # Create a regex pattern that matches the multi-line msgid
        # Replace spaces with possible line breaks
        words = english.split()
        regex_parts = []
        for i, word in enumerate(words):
            if i < len(words) - 1:
                # Allow for line breaks between words
                regex_parts.append(re.escape(word) + r'\s*(?:"\s*"\s*)?')
            else:
                regex_parts.append(re.escape(word))

        regex_pattern = r'msgid ""\s*\n"' + ''.join(regex_parts) + r'"\s*\nmsgstr ""'

        # Try multi-line format
        if re.search(regex_pattern, content, re.MULTILINE):
            # Replace with French translation
            replacement = f'msgid ""\n"{french}"\nmsgstr ""\n"{french}"'
            content = re.sub(regex_pattern, lambda m: m.group(0).replace('msgstr ""', f'msgstr ""\n"{french}"'), content, count=1)
            translations_added += 1
            print(f"✓ Added (multi-line): {english[:60]}...")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} translations")

    # Now do a second pass for exact matching
    print("\n Running second pass with exact text matching...")
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        if lines[i].startswith('msgid'):
            # Collect the full msgid
            msgid_lines = [lines[i]]
            j = i + 1
            while j < len(lines) and (lines[j].startswith('"') or lines[j].strip() == ''):
                if lines[j].startswith('"'):
                    msgid_lines.append(lines[j])
                j += 1

            # Check if next line is empty msgstr
            if j < len(lines) and lines[j].strip() == 'msgstr ""':
                # Extract the text from msgid
                msgid_text = ''.join(msgid_lines).replace('msgid', '').replace('"', '').replace('\n', ' ').strip()
                msgid_text_normalized = ' '.join(msgid_text.split())

                # Check if we have a translation for this
                for eng_key, fr_val in MULTILINE_TRANSLATIONS.items():
                    eng_normalized = ' '.join(eng_key.split())
                    if msgid_text_normalized == eng_normalized:
                        # Found a match! Update msgstr
                        lines[j] = f'msgstr "{fr_val}"\n'
                        print(f"✓ Updated: {msgid_text_normalized[:60]}...")
                        break
        i += 1

    with open(po_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
