#!/usr/bin/env python3
"""
Add French translations for dashboard page
"""

TRANSLATIONS = {
    # Page title
    "Dashboard": "Tableau de bord",

    # Statistics cards
    "Projects": "Projets",
    "Total Pages": "Total des pages",
    "Tested Pages": "Pages testées",
    "Total Issues": "Total des problèmes",
    "Errors": "Erreurs",
    "Warnings": "Avertissements",
    "Info Notes": "Notes d'information",
    "Discovery": "Découverte",

    # Quick Actions
    "Quick Actions": "Actions rapides",
    "New Project": "Nouveau projet",
    "Run Tests": "Exécuter les tests",
    "Generate Report": "Générer un rapport",

    # Test Coverage
    "Test Coverage": "Couverture des tests",
    "Tested": "Testées",
    "of": "sur",
    "pages tested": "pages testées",

    # System Status
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
        # First try to match with empty msgstr
        pattern = f'msgid "{english}"\nmsgstr ""'
        replacement = f'msgid "{english}"\nmsgstr "{french}"'

        if pattern in content:
            content = content.replace(pattern, replacement)
            translations_added += 1
            print(f"✓ Added: {english}")
        else:
            # Try to update existing translation
            import re
            pattern_existing = f'msgid "{re.escape(english)}"\nmsgstr "[^"]*"'
            replacement_existing = f'msgid "{english}"\nmsgstr "{french}"'
            if re.search(pattern_existing, content):
                content = re.sub(pattern_existing, replacement_existing, content)
                translations_added += 1
                print(f"✓ Updated: {english}")
            else:
                print(f"✗ Not found: {english}")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added/Updated {translations_added} translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
