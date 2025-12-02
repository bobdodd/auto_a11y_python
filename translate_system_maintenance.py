#!/usr/bin/env python3
"""
Add French translations for system maintenance help text
"""

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1 - Reset all running
    pattern1 = '''msgid ""
"Reset all running and pending scrapes and tests. Use this if the system "
"appears stuck."
msgstr ""'''

    replacement1 = '''msgid ""
"Reset all running and pending scrapes and tests. Use this if the system "
"appears stuck."
msgstr ""
"Réinitialiser toutes les explorations et tests en cours et en attente. "
"Utilisez ceci si le système semble bloqué."'''

    # Pattern 2 - Remove jobs
    pattern2 = '''msgid "Remove jobs that have been running for more than 24 hours."
msgstr ""'''

    replacement2 = '''msgid "Remove jobs that have been running for more than 24 hours."
msgstr "Supprimer les tâches en cours d'exécution depuis plus de 24 heures."'''

    # Pattern 3 - Reset violation counts (note: no space after "data")
    pattern3 = '''msgid ""
"Reset violation counts for pages that haven't been tested yet. Fixes data"
" inconsistencies."
msgstr ""'''

    replacement3 = '''msgid ""
"Reset violation counts for pages that haven't been tested yet. Fixes data"
" inconsistencies."
msgstr ""
"Réinitialiser les compteurs de violations pour les pages qui n'ont pas "
"encore été testées. Corrige les incohérences de données."'''

    patterns = [
        (pattern1, replacement1, "Reset all running and pending scrapes"),
        (pattern2, replacement2, "Remove jobs that have been running"),
        (pattern3, replacement3, "Reset violation counts"),
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
