#!/usr/bin/env python3
"""
Add French translations for modal dialog strings
"""

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1 - Clear all jobs confirmation
    pattern1 = '''msgid ""
"This will clear ALL running and pending jobs. This action cannot be "
"undone. Are you sure?"
msgstr ""'''

    replacement1 = '''msgid ""
"This will clear ALL running and pending jobs. This action cannot be "
"undone. Are you sure?"
msgstr ""
"Ceci effacera TOUTES les tâches en cours et en attente. Cette action ne "
"peut pas être annulée. Êtes-vous sûr ?"'''

    # Pattern 2 - Clear stale jobs confirmation
    pattern2 = '''msgid ""
"This will clear all jobs that have been running for more than 24 hours. "
"Are you sure?"
msgstr ""'''

    replacement2 = '''msgid ""
"This will clear all jobs that have been running for more than 24 hours. "
"Are you sure?"
msgstr ""
"Ceci effacera toutes les tâches en cours d'exécution depuis plus de 24 "
"heures. Êtes-vous sûr ?"'''

    # Pattern 3 - Clean page data confirmation (with escaped backslash)
    pattern3 = '''msgid ""
"This will reset violation counts for all pages that haven\\'t been tested"
" yet. Continue?"
msgstr ""'''

    replacement3 = '''msgid ""
"This will reset violation counts for all pages that haven\\'t been tested"
" yet. Continue?"
msgstr ""
"Ceci réinitialisera les compteurs de violations pour toutes les pages qui "
"n'ont pas encore été testées. Continuer ?"'''

    patterns = [
        (pattern1, replacement1, "Clear all jobs confirmation"),
        (pattern2, replacement2, "Clear stale jobs confirmation"),
        (pattern3, replacement3, "Clean page data confirmation"),
    ]

    translations_added = 0
    for pattern, replacement, name in patterns:
        if pattern in content:
            content = content.replace(pattern, replacement)
            translations_added += 1
            print(f"✓ Added: {name}")
        else:
            print(f"✗ Not found: {name}")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
