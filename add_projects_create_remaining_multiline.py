#!/usr/bin/env python3
"""
Script to add remaining French translations for projects/create.html
Handles multi-line msgid entries
"""

# French translations for remaining untranslated strings
TRANSLATIONS = {
    # Drupal audit (multi-line in .po file)
    'Select the corresponding audit in Drupal for synchronization. Leave as "Auto-match" to use the project name.':
        'Sélectionnez l\'audit correspondant dans Drupal pour la synchronisation. Laissez "Correspondance automatique" pour utiliser le nom du projet.',

    # Page load strategy
    "Test as soon as DOM is ready (use for BBC News, sites with continuous ads/analytics)":
        "Tester dès que le DOM est prêt (à utiliser pour BBC News, sites avec publicités/analytics en continu)",

    # Stealth mode
    "Enables advanced bot detection bypass techniques. Use for sites protected by Cloudflare or similar services.":
        "Active les techniques avancées de contournement de détection de bot. À utiliser pour les sites protégés par Cloudflare ou des services similaires.",

    # Touchpoint tests
    "Configure which accessibility tests to run. Tests are organized by touchpoint (testing category).":
        "Configurez les tests d'accessibilité à exécuter. Les tests sont organisés par point de contact (catégorie de test).",
}

def update_po_file(po_path):
    """Update the .po file with French translations, handling multi-line msgid entries"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    # Process each translation
    for english, french in TRANSLATIONS.items():
        # Escape quotes in the translation
        french_escaped = french.replace('"', '\\"')

        # Try to find and replace empty msgstr for this msgid
        # Pattern 1: Single-line msgid
        pattern1 = f'msgid "{english}"\nmsgstr ""'
        replacement1 = f'msgid "{english}"\nmsgstr "{french_escaped}"'

        if pattern1 in content:
            content = content.replace(pattern1, replacement1)
            translations_added += 1
            print(f"✓ Added translation (single-line): {english[:50]}...")
            continue

        # Pattern 2: Multi-line msgid (split with escaped quotes)
        # Need to match the actual multi-line format in the file
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            if lines[i].startswith('msgid "'):
                # Collect full msgid (might be multi-line)
                msgid_parts = []
                j = i

                # Handle msgid "" followed by continuation lines
                if lines[j] == 'msgid ""' and j + 1 < len(lines) and lines[j + 1].startswith('"'):
                    j += 1
                    while j < len(lines) and lines[j].startswith('"') and not lines[j].startswith('msgstr'):
                        msgid_parts.append(lines[j][1:-1])  # Remove quotes
                        j += 1
                elif lines[j].startswith('msgid "') and not lines[j].endswith('""'):
                    # Single line msgid
                    msgid_parts.append(lines[j][7:-1])  # Remove 'msgid "' and '"'
                    j += 1

                # Reconstruct the full msgid string
                full_msgid = ''.join(msgid_parts).replace('\\"', '"')

                # Check if this matches our translation
                if full_msgid == english and j < len(lines) and lines[j] == 'msgstr ""':
                    # Found a match with empty translation
                    lines[j] = f'msgstr "{french_escaped}"'
                    translations_added += 1
                    print(f"✓ Added translation (multi-line): {english[:50]}...")
                    i = j + 1
                    continue

            i += 1

        content = '\n'.join(lines)

    # Write back
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} French translations to {po_path}")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
