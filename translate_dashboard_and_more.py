#!/usr/bin/env python3
"""
Add French translations for dashboard and other key pages
"""

TRANSLATIONS = {
    # Dashboard
    "Dashboard": "Tableau de bord",
    "Total Pages": "Total des pages",
    "Tested Pages": "Pages testées",
    "Total Issues": "Total des problèmes",
    "Info Notes": "Notes d'information",
    "Quick Actions": "Actions rapides",
    "New Project": "Nouveau projet",
    "Run Tests": "Lancer les tests",
    "Generate Report": "Générer un rapport",
    "Test Coverage": "Couverture des tests",
    "Tested": "Testé",
    "%(tested)d of %(total)d pages tested": "%(tested)d sur %(total)d pages testées",
    "System Status": "État du système",
    "Database": "Base de données",
    "Connected": "Connecté",
    "Browser Engine": "Moteur de navigateur",
    "Ready": "Prêt",
    "AI Analysis": "Analyse IA",
    "Enabled": "Activé",
    "Disabled": "Désactivé",
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
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
