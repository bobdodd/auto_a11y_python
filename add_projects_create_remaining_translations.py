#!/usr/bin/env python3
"""
Script to add remaining French translations for projects/create.html
"""

# French translations for remaining untranslated strings
TRANSLATIONS = {
    # Drupal audit
    "Select the corresponding audit in Drupal for synchronization. Leave as \"Auto-match\" to use the project name.": "Sélectionnez l'audit correspondant dans Drupal pour la synchronisation. Laissez \"Correspondance automatique\" pour utiliser le nom du projet.",

    # Page load strategy
    "Test as soon as DOM is ready (use for BBC News, sites with continuous ads/analytics)": "Tester dès que le DOM est prêt (à utiliser pour BBC News, sites avec publicités/analytics en continu)",

    # Stealth mode
    "Enables advanced bot detection bypass techniques. Use for sites protected by Cloudflare or similar services.": "Active les techniques avancées de contournement de détection de bot. À utiliser pour les sites protégés par Cloudflare ou des services similaires.",

    # Touchpoint tests
    "Configure which accessibility tests to run. Tests are organized by touchpoint (testing category).": "Configurez les tests d'accessibilité à exécuter. Les tests sont organisés par point de contact (catégorie de test).",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    translations_added = 0

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Check if this is a msgid line
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            # Extract the msgid value
            msgid = line[7:-2]  # Remove 'msgid "' and '"\n'

            # Check if next line is msgstr ""
            if i + 1 < len(lines) and lines[i + 1] == 'msgstr ""\n':
                # Check if we have a translation for this
                if msgid in TRANSLATIONS:
                    new_lines.append(f'msgstr "{TRANSLATIONS[msgid]}"\n')
                    translations_added += 1
                    i += 2  # Skip the empty msgstr line
                    continue

        i += 1

    # Write back
    with open(po_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"✓ Added {translations_added} French translations to {po_path}")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
