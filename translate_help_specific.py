#!/usr/bin/env python3
"""
Add specific help page French translations that were showing as English
"""

TRANSLATIONS = {
    "Each uses similar scoring models but are calculated independently based on their respective test results.":
        "Chacun utilise des modèles de notation similaires mais est calculé indépendamment en fonction de ses résultats de test respectifs.",

    "Generated from automated scanning tools that check pages for technical accessibility issues.":
        "Généré à partir d'outils d'analyse automatisés qui vérifient les pages pour détecter les problèmes techniques d'accessibilité.",

    "This score helps you track progress. Each successful check counts toward your score, even if the overall test fails.":
        "Ce score vous aide à suivre la progression. Chaque vérification réussie compte pour votre score, même si le test global échoue.",

    "This score reflects true WCAG compliance. A test passes only if it has zero violations.":
        "Ce score reflète la véritable conformité WCAG. Un test est réussi seulement s'il n'a aucune violation.",

    "Tests are marked \"Not Applicable\" when there are no relevant elements on the page.":
        "Les tests sont marqués « Non applicable » lorsqu'il n'y a aucun élément pertinent sur la page.",

    "Our tests track both failures and successes to provide comprehensive feedback.":
        "Nos tests suivent à la fois les échecs et les réussites pour fournir un retour complet.",

    "The compliance score requires perfect passes (zero violations) for each test, while the accessibility score gives credit for partial passes. Even if 90% of your checks pass, a single violation makes that test non-compliant.":
        "Le score de conformité nécessite des réussites parfaites (zéro violation) pour chaque test, tandis que le score d'accessibilité accorde du crédit pour les réussites partielles. Même si 90 % de vos vérifications réussissent, une seule violation rend ce test non conforme.",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    for english, french in TRANSLATIONS.items():
        english_escaped = english.replace('"', '\\"')
        french_escaped = french.replace('"', '\\"')

        pattern1 = f'msgid "{english_escaped}"\nmsgstr ""'
        replacement1 = f'msgid "{english_escaped}"\nmsgstr "{french_escaped}"'

        if pattern1 in content:
            content = content.replace(pattern1, replacement1)
            translations_added += 1
            print(f"✓ Added: {english[:80]}...")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} translations")

if __name__ == '__main__':
    po_file = '/Users/bob3/Desktop/auto_a11y_python/auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
