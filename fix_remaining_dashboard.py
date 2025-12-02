#!/usr/bin/env python3
"""
Fix remaining dashboard translation issues
"""

TRANSLATIONS = {
    "Tested": "Testé",  # Currently "Testées" which is feminine plural
}

def update_po_file(po_path):
    """Update the .po file with corrected French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_fixed = 0

    for english, french in TRANSLATIONS.items():
        english_escaped = english.replace('"', '\\"')
        french_escaped = french.replace('"', '\\"')

        # Replace the translation
        pattern = f'msgid "{english_escaped}"\nmsgstr "'
        if pattern in content:
            # Find the full line and replace
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line == f'msgid "{english_escaped}"':
                    if i + 1 < len(lines) and lines[i + 1].startswith('msgstr "'):
                        # Replace this msgstr
                        lines[i + 1] = f'msgstr "{french_escaped}"'
                        translations_fixed += 1
                        print(f"✓ Fixed: {english} -> {french}")
                        break
            content = '\n'.join(lines)

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Fixed {translations_fixed} translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
