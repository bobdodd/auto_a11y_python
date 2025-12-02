#!/usr/bin/env python3
"""
Add French translations for testing dashboard page
"""

TRANSLATIONS = {
    # Page title
    "Testing Dashboard - Auto A11y": "Tableau de bord des tests - Auto A11y",
    "Testing Dashboard": "Tableau de bord des tests",

    # Status cards
    "Active Tests": "Tests actifs",
    "Queued Tests": "Tests en file d'attente",
    "Completed Today": "Terminés aujourd'hui",
    "Failed Tests": "Tests échoués",

    # Quick Test section
    "Quick Test": "Test rapide",
    "URL to test": "URL à tester",
    "Enter URL to test (e.g., https://example.com)": "Entrer l'URL à tester (p. ex., https://example.com)",
    "Run Test": "Exécuter le test",

    # Recent Test Results section
    "Recent Test Results": "Résultats de tests récents",
    "Configure": "Configurer",

    # Table headers
    "Page": "Page",
    "Test Date": "Date du test",
    "Duration": "Durée",
    # "Errors": "Erreurs",  # Already translated in dashboard
    # "Warnings": "Avertissements",  # Already translated in dashboard
    # "Info": "Info",  # Already translated elsewhere
    # "Discovery": "Découverte",  # Already translated in dashboard
    "Status": "État",
    "Actions": "Actions",

    # Table content
    "View page details": "Voir les détails de la page",
    "Error": "Erreur",
    "Complete": "Terminé",
    "View": "Voir",

    # Empty state
    "No recent test results": "Aucun résultat de test récent",

    # JavaScript alerts
    "Please enter a URL to test": "Veuillez entrer une URL à tester",
    "Quick test functionality will be implemented": "La fonctionnalité de test rapide sera implémentée",
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
