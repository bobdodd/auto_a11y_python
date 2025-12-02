#!/usr/bin/env python3
"""
Add French translations for JavaScript strings from recordings/upload page
"""
import re

JS_TRANSLATIONS = {
    "Select a test user...": "Sélectionner un utilisateur de test...",
    "Select a tester...": "Sélectionner un testeur...",
    "Select a supervisor...": "Sélectionner un superviseur...",
    "Loading discovered pages...": "Chargement des pages découvertes...",
    "Manage project users": "Gérer les utilisateurs du projet",
    "No test users configured for this project.": "Aucun utilisateur de test configuré pour ce projet.",
    "Add test users": "Ajouter des utilisateurs de test",
    "Error loading testers.": "Erreur lors du chargement des testeurs.",
    "Error loading supervisors.": "Erreur lors du chargement des superviseurs.",
    "No discovered pages found for this project.": "Aucune page découverte trouvée pour ce projet.",
    "Error loading discovered pages.": "Erreur lors du chargement des pages découvertes.",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    for english, french in JS_TRANSLATIONS.items():
        # Try to match with empty msgstr
        pattern = f'msgid "{english}"\nmsgstr ""'
        replacement = f'msgid "{english}"\nmsgstr "{french}"'

        if pattern in content:
            content = content.replace(pattern, replacement)
            translations_added += 1
            print(f"✓ Added: {english}")
        else:
            # Try to update existing translation
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
