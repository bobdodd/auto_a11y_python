#!/usr/bin/env python3
"""
Add French translation for recordings list description
"""

def add_translation(po_path):
    """Add the missing translation"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The multiline msgid entry
    old_entry = '''msgid ""
"Manual audit recordings from Dictaphone and expert reviews. These "
"complement automated test results with human observations and lived "
"experience findings."
msgstr ""'''

    new_entry = '''msgid ""
"Manual audit recordings from Dictaphone and expert reviews. These "
"complement automated test results with human observations and lived "
"experience findings."
msgstr ""
"Enregistrements d'audits manuels de Dictaphone et de revues d'experts. "
"Ceux-ci complètent les résultats de tests automatisés avec des "
"observations humaines et des constatations d'expérience vécue."'''

    if old_entry in content:
        content = content.replace(old_entry, new_entry)
        print("✓ Added: Manual audit recordings description")
    else:
        print("✗ Entry not found or already translated")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    add_translation(po_file)
