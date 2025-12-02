#!/usr/bin/env python3
"""
Fix fuzzy translations on reports dashboard with proper French translations
"""

def fix_translations(po_path):
    """Fix all fuzzy translations for reports dashboard"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the fuzzy entries to fix
    fixes = [
        {
            "old": '''#, fuzzy
msgid "Comprehensive accessibility testing results"
msgstr "Plateforme de tests d'accessibilité automatisés"''',
            "new": '''msgid "Comprehensive accessibility testing results"
msgstr "Résultats complets des tests d'accessibilité"'''
        },
        {
            "old": '''#, fuzzy
msgid "Discovery Report"
msgstr "Découvrir les pages"''',
            "new": '''msgid "Discovery Report"
msgstr "Rapport de découverte"'''
        },
        {
            "old": '''#, fuzzy
msgid "Discover content requiring manual inspection"
msgstr "Cet élément nécessite une inspection manuelle."''',
            "new": '''msgid "Discover content requiring manual inspection"
msgstr "Découvrir le contenu nécessitant une inspection manuelle"'''
        },
        {
            "old": '''#, fuzzy
msgid "Generate Discovery Report"
msgstr "Générer un rapport"''',
            "new": '''msgid "Generate Discovery Report"
msgstr "Générer un rapport de découverte"'''
        },
        {
            "old": '''#, fuzzy
msgid "Generate Structure"
msgstr "Structure du site"''',
            "new": '''msgid "Generate Structure"
msgstr "Générer la structure"'''
        },
        {
            "old": '''#, fuzzy
msgid "Recordings Report"
msgstr "enregistrements"''',
            "new": '''msgid "Recordings Report"
msgstr "Rapport d'enregistrements"'''
        },
        {
            "old": '''#, fuzzy
msgid "Manual accessibility audit findings from recorded testing sessions"
msgstr "Plateforme de tests d'accessibilité automatisés"''',
            "new": '''msgid "Manual accessibility audit findings from recorded testing sessions"
msgstr "Constatations d'audits d'accessibilité manuels issues de sessions de test enregistrées"'''
        },
        {
            "old": '''#, fuzzy
msgid "Generate Recordings Report"
msgstr "Générer un rapport"''',
            "new": '''msgid "Generate Recordings Report"
msgstr "Générer un rapport d'enregistrements"'''
        },
        {
            "old": '''#, fuzzy
msgid "Recent Reports"
msgstr "Générer un rapport"''',
            "new": '''msgid "Recent Reports"
msgstr "Rapports récents"'''
        }
    ]

    fixed_count = 0
    for fix in fixes:
        if fix["old"] in content:
            content = content.replace(fix["old"], fix["new"])
            fixed_count += 1
            # Extract first line of msgid for display
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
