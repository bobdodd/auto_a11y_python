#!/usr/bin/env python3
"""
Fix dashboard translations - the strings exist but have wrong translations
because they matched to different contexts
"""

# Correct French translations for dashboard-specific context
TRANSLATIONS = {
    "Errors": "Erreurs",  # Currently "Rapports" - wrong!
    "Total Pages": "Total des pages",  # Currently just "pages"
    "Tested Pages": "Pages testées",  # Currently "Tester tous les sites"
    "Total Issues": "Total des problèmes",  # Currently just "pages"
    "Quick Actions": "Actions rapides",  # Currently just "Actions"
    "Run Tests": "Lancer les tests",  # Currently just "Tester"
    "Generate Report": "Générer un rapport",  # Currently "Génération du rapport d'accessibilité en"
    "Test Coverage": "Couverture des tests",  # Currently just "couverture"
    "System Status": "État du système",  # Currently "État de la synchronisation"
    "Database": "Base de données",  # Currently "Date"
    "Connected": "Connecté",  # Currently "Testées"
    "Browser Engine": "Moteur de navigateur",  # Currently "Tests de navigateur"
    "Ready": "Prêt",  # Currently "Créé :"
    "AI Analysis": "Analyse IA",  # Currently "Analyse par IA" - close but let's be consistent
}

def update_po_file(po_path):
    """Update the .po file with correct French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    translations_fixed = 0
    i = 0

    while i < len(lines):
        # Check if this is a msgid line
        if lines[i].startswith('msgid "'):
            # Extract the msgid value
            msgid_line = lines[i].strip()
            if msgid_line == 'msgid ""':
                i += 1
                continue

            # Get the English text
            msgid_text = msgid_line[7:-1]  # Remove 'msgid "' and '"'

            # Check if this is one we need to fix and if next line has wrong translation
            if msgid_text in TRANSLATIONS and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('msgstr "') and next_line != 'msgstr ""':
                    # This has a translation - let's replace it with correct one
                    french = TRANSLATIONS[msgid_text].replace('"', '\\"')
                    lines[i + 1] = f'msgstr "{french}"\n'
                    translations_fixed += 1
                    print(f"✓ Fixed: {msgid_text} -> {TRANSLATIONS[msgid_text]}")
        i += 1

    # Write back
    with open(po_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"\n✓ Total: Fixed {translations_fixed} translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
