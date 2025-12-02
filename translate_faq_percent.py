#!/usr/bin/env python3
"""
Add French translation for FAQ answer with percent sign
"""

def update_po_file(po_path):
    """Update the .po file with French translation"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The string with %% for python-format
    english = '''msgid ""
"Automated testing (like Auto A11y) can catch about 30-40%% of "
"accessibility issues quickly and consistently. Manual testing is needed "
"for subjective criteria like whether alt text is meaningful or if the "
"reading order makes sense. Use both for comprehensive coverage."
msgstr ""'''

    french = '''msgid ""
"Automated testing (like Auto A11y) can catch about 30-40%% of "
"accessibility issues quickly and consistently. Manual testing is needed "
"for subjective criteria like whether alt text is meaningful or if the "
"reading order makes sense. Use both for comprehensive coverage."
msgstr ""
"Les tests automatisés (comme Auto A11y) peuvent détecter environ 30 à 40 %% "
"des problèmes d'accessibilité rapidement et de manière cohérente. Les tests "
"manuels sont nécessaires pour les critères subjectifs comme savoir si le "
"texte alternatif est significatif ou si l'ordre de lecture a du sens. "
"Utilisez les deux pour une couverture complète."'''

    if english in content:
        content = content.replace(english, french)
        print("✓ Added FAQ translation for automated testing")
    else:
        print("✗ Could not find the exact pattern")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
