#!/usr/bin/env python3
"""
Add remaining French translations for help.html
"""

TRANSLATIONS = {
    "The WCAG Success Criteria data used in this application is sourced from:":
        "Les données des critères de succès WCAG utilisées dans cette application proviennent de :",

    "Auto A11y provides two types of scores based on your testing approach:":
        "Auto A11y fournit deux types de scores en fonction de votre approche de test :",

    "Within each testing type (automated or manual), you'll see two scores:":
        "Dans chaque type de test (automatisé ou manuel), vous verrez deux scores :",

    "Why is my compliance score so much lower than my accessibility score?":
        "Pourquoi mon score de conformité est-il beaucoup plus bas que mon score d'accessibilité ?",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    for english, french in TRANSLATIONS.items():
        english_escaped = english.replace('"', '\\"')
        french_escaped = french.replace('"', '\\"')

        pattern1 = f'msgid "{english_escaped}"\nmsgstr ""'
        replacement1 = f'msgid "{english_escaped}"\nmsgstr "{french_escaped}"'

        if pattern1 in content:
            content = content.replace(pattern1, replacement1)
            translations_added += 1
            print(f"✓ Added: {english}")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} translations")

if __name__ == '__main__':
    po_file = '/Users/bob3/Desktop/auto_a11y_python/auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
