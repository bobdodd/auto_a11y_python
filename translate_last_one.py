#!/usr/bin/env python3
"""
Add the last translation with correct escaping
"""

def update_po_file(po_path):
    """Update the .po file with French translation"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern with correct escaping
    pattern = '''msgid ""
"Tests are marked \\"Not Applicable\\" when there are no relevant elements "
"on the page."
msgstr ""'''

    replacement = '''msgid ""
"Tests are marked \\"Not Applicable\\" when there are no relevant elements "
"on the page."
msgstr ""
"Les tests sont marqués « Non applicable » lorsqu'il n'y a aucun élément "
"pertinent sur la page."'''

    if pattern in content:
        content = content.replace(pattern, replacement)
        print("✓ Added: Tests are marked Not Applicable")
    else:
        print("✗ Not found - trying different escape pattern")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
