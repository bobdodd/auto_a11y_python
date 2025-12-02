#!/usr/bin/env python3
"""
Add French translations for multi-line help strings
"""

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Multi-line string 1
    pattern1 = '''msgid ""
"Each uses similar scoring models but are calculated independently based "
"on their respective test results."
msgstr ""'''

    replacement1 = '''msgid ""
"Each uses similar scoring models but are calculated independently based "
"on their respective test results."
msgstr ""
"Chacun utilise des modèles de notation similaires mais est calculé "
"indépendamment en fonction de ses résultats de test respectifs."'''

    # Multi-line string 2
    pattern2 = '''msgid ""
"Generated from automated scanning tools that check pages for technical "
"accessibility issues."
msgstr ""'''

    replacement2 = '''msgid ""
"Generated from automated scanning tools that check pages for technical "
"accessibility issues."
msgstr ""
"Généré à partir d'outils d'analyse automatisés qui vérifient les pages "
"pour détecter les problèmes techniques d'accessibilité."'''

    # Multi-line string 3
    pattern3 = '''msgid ""
"This score helps you track progress. Each successful check counts toward "
"your score, even if the overall test fails."
msgstr ""'''

    replacement3 = '''msgid ""
"This score helps you track progress. Each successful check counts toward "
"your score, even if the overall test fails."
msgstr ""
"Ce score vous aide à suivre la progression. Chaque vérification réussie "
"compte pour votre score, même si le test global échoue."'''

    # Multi-line string 4
    pattern4 = '''msgid ""
"This score reflects true WCAG compliance. A test passes only if it has zero "
"violations."
msgstr ""'''

    replacement4 = '''msgid ""
"This score reflects true WCAG compliance. A test passes only if it has zero "
"violations."
msgstr ""
"Ce score reflète la véritable conformité WCAG. Un test est réussi seulement "
"s'il n'a aucune violation."'''

    # Multi-line string 5
    pattern5 = '''msgid ""
"Tests are marked \"Not Applicable\" when there are no relevant elements on "
"the page."
msgstr ""'''

    replacement5 = '''msgid ""
"Tests are marked \"Not Applicable\" when there are no relevant elements on "
"the page."
msgstr ""
"Les tests sont marqués « Non applicable » lorsqu'il n'y a aucun élément "
"pertinent sur la page."'''

    # Multi-line string 6
    pattern6 = '''msgid ""
"If a page has no images, the images test will be marked as not applicable "
"and won't affect your score."
msgstr ""'''

    replacement6 = '''msgid ""
"If a page has no images, the images test will be marked as not applicable "
"and won't affect your score."
msgstr ""
"Si une page n'a pas d'images, le test des images sera marqué comme non "
"applicable et n'affectera pas votre score."'''

    # Multi-line string 7
    pattern7 = '''msgid ""
"Our tests track both failures and successes to provide comprehensive "
"feedback."
msgstr ""'''

    replacement7 = '''msgid ""
"Our tests track both failures and successes to provide comprehensive "
"feedback."
msgstr ""
"Nos tests suivent à la fois les échecs et les réussites pour fournir un "
"retour complet."'''

    # Multi-line string 8 - FAQ answer
    pattern8 = '''msgid ""
"The compliance score requires perfect passes (zero violations) for each "
"test, while the accessibility score gives credit for partial passes. Even if "
"90%% of your checks pass, a single violation makes that test non-compliant."
msgstr ""'''

    replacement8 = '''msgid ""
"The compliance score requires perfect passes (zero violations) for each "
"test, while the accessibility score gives credit for partial passes. Even if "
"90%% of your checks pass, a single violation makes that test non-compliant."
msgstr ""
"Le score de conformité nécessite des réussites parfaites (zéro violation) "
"pour chaque test, tandis que le score d'accessibilité accorde du crédit pour "
"les réussites partielles. Même si 90 %% de vos vérifications réussissent, une "
"seule violation rend ce test non conforme."'''

    patterns = [
        (pattern1, replacement1, "Each uses similar scoring models"),
        (pattern2, replacement2, "Generated from automated scanning"),
        (pattern3, replacement3, "This score helps you track progress"),
        (pattern4, replacement4, "This score reflects true WCAG"),
        (pattern5, replacement5, "Tests are marked Not Applicable"),
        (pattern6, replacement6, "If a page has no images"),
        (pattern7, replacement7, "Our tests track both failures"),
        (pattern8, replacement8, "The compliance score requires"),
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
