#!/usr/bin/env python3
"""
Fix all remaining fuzzy translations on reports dashboard
"""

def fix_translations(po_path):
    """Fix all fuzzy translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fixes = [
        {
            "old": '''#, fuzzy
msgid "Generate Offline Report"
msgstr "Générer un rapport"''',
            "new": '''msgid "Generate Offline Report"
msgstr "Générer un rapport hors ligne"'''
        },
        {
            "old": '''#, fuzzy
msgid "Generate Deduplicated Report"
msgstr "Générer un rapport"''',
            "new": '''msgid "Generate Deduplicated Report"
msgstr "Générer un rapport dédupliqué"'''
        }
    ]

    fixed_count = 0
    for fix in fixes:
        if fix["old"] in content:
            content = content.replace(fix["old"], fix["new"])
            fixed_count += 1
            msgid_line = fix["new"].split('\n')[0].replace('msgid "', '').strip('"')
            print(f"✓ Fixed: {msgid_line}")
        else:
            msgid_line = fix["new"].split('\n')[0].replace('msgid "', '').strip('"')
            print(f"✗ Not found: {msgid_line}")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Fixed {fixed_count} fuzzy translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    fix_translations(po_file)
