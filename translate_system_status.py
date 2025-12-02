#!/usr/bin/env python3
"""
Add French translations for System Status dynamic strings
"""

TRANSLATIONS = {
    "Running:": "En cours :",
    "Pending:": "En attente :",
    "Cancelling:": "Annulation :",
    "Completed (24h):": "Terminées (24h) :",
    "Failed (24h):": "Échouées (24h) :",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    for english, french in TRANSLATIONS.items():
        english_escaped = english.replace('"', '\\"')
        french_escaped = french.replace('"', '\\"')

        pattern = f'msgid "{english_escaped}"\nmsgstr ""'
        replacement = f'msgid "{english_escaped}"\nmsgstr "{french_escaped}"'

        if pattern in content:
            content = content.replace(pattern, replacement)
            translations_added += 1
            print(f"✓ Added: {english}")
        else:
            print(f"✗ Not found: {english}")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
