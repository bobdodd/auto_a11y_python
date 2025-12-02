#!/usr/bin/env python3
"""
Add remaining French translations for multi-line help strings with correct formatting
"""

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1
    pattern1 = '''msgid ""
"This score reflects true WCAG compliance. A test passes only if it has "
"zero violations."
msgstr ""'''

    replacement1 = '''msgid ""
"This score reflects true WCAG compliance. A test passes only if it has "
"zero violations."
msgstr ""
"Ce score reflète la véritable conformité WCAG. Un test est réussi "
"seulement s'il n'a aucune violation."'''

    # Pattern 2
    pattern2 = '''msgid ""
"Tests are marked \"Not Applicable\" when there are no relevant elements on "
"the page."
msgstr ""'''

    replacement2 = '''msgid ""
"Tests are marked \"Not Applicable\" when there are no relevant elements on "
"the page."
msgstr ""
"Les tests sont marqués « Non applicable » lorsqu'il n'y a aucun élément "
"pertinent sur la page."'''

    # Pattern 3
    pattern3 = '''msgid ""
"If a page has no images, the images test will be marked as not applicable "
"and won't affect your score."
msgstr ""'''

    replacement3 = '''msgid ""
"If a page has no images, the images test will be marked as not applicable "
"and won't affect your score."
msgstr ""
"Si une page n'a pas d'images, le test des images sera marqué comme non "
"applicable et n'affectera pas votre score."'''

    # Pattern 4 - FAQ with %%
    pattern4 = '''msgid ""
"The compliance score requires perfect passes (zero violations) for each "
"test, while the accessibility score gives credit for partial passes. Even "
"if 90%% of your checks pass, a single violation makes that test non-"
"compliant."
msgstr ""'''

    replacement4 = '''msgid ""
"The compliance score requires perfect passes (zero violations) for each "
"test, while the accessibility score gives credit for partial passes. Even "
"if 90%% of your checks pass, a single violation makes that test non-"
"compliant."
msgstr ""
"Le score de conformité nécessite des réussites parfaites (zéro violation) "
"pour chaque test, tandis que le score d'accessibilité accorde du crédit "
"pour les réussites partielles. Même si 90 %% de vos vérifications "
"réussissent, une seule violation rend ce test non conforme."'''

    patterns = [
        (pattern1, replacement1, "This score reflects true WCAG"),
        (pattern2, replacement2, "Tests are marked Not Applicable"),
        (pattern3, replacement3, "If a page has no images"),
        (pattern4, replacement4, "The compliance score requires"),
    ]

    translations_added = 0
    for pattern, replacement, name in patterns:
        if pattern in content:
            content = content.replace(pattern, replacement)
            translations_added += 1
            print(f"✓ Added: {name}")
        else:
            print(f"✗ Not found: {name}")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
