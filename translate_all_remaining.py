#!/usr/bin/env python3
"""
Add all remaining French translations for the application
"""

TRANSLATIONS = {
    # Help page strings that appear untranslated
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

    # Testing and configuration strings
    "Real browser testing with Puppeteer ensures accurate DOM-based results":
        "Les tests de navigateur réel avec Puppeteer garantissent des résultats précis basés sur le DOM",

    "The accessibility test is running. The page will refresh when complete.":
        "Le test d'accessibilité est en cours d'exécution. La page se rafraîchira une fois terminé.",

    "Comma-separated list of user roles for testing role-based content":
        "Liste de rôles d'utilisateurs séparés par des virgules pour tester le contenu basé sur les rôles",

    "Roles help you test content that varies based on user permissions.":
        "Les rôles vous aident à tester le contenu qui varie en fonction des autorisations de l'utilisateur.",

    "Leave the password field blank to keep the current password unchanged.":
        "Laissez le champ de mot de passe vide pour conserver le mot de passe actuel inchangé.",

    "Standard compliance (4.5:1 contrast for normal text, 3:1 for large text)":
        "Conformité standard (contraste 4,5:1 pour le texte normal, 3:1 pour le texte large)",

    "Enhanced compliance (7:1 contrast for normal text, 4.5:1 for large text)":
        "Conformité améliorée (contraste 7:1 pour le texte normal, 4,5:1 pour le texte large)",

    "DOM Content Loaded (Fast, for sites with heavy background activity)":
        "DOM Content Loaded (Rapide, pour les sites avec une activité d'arrière-plan importante)",

    "Wait until network has ≤2 connections (best for dynamic sites)":
        "Attendre que le réseau ait ≤2 connexions (meilleur pour les sites dynamiques)",

    "Run browser invisibly (faster, less resource intensive)":
        "Exécuter le navigateur de manière invisible (plus rapide, moins gourmand en ressources)",

    "Verifies logical reading sequence matches visual layout":
        "Vérifie que l'ordre de lecture logique correspond à la disposition visuelle",

    "This test documentation is pending review and may be incomplete.":
        "Cette documentation de test est en attente de révision et peut être incomplète.",

    "An error occurred while loading the test details. Please try again.":
        "Une erreur s'est produite lors du chargement des détails du test. Veuillez réessayer.",

    "Enter font names, one per line (e.g., 'Custom Font Name')":
        "Entrez les noms de polices, un par ligne (par ex. 'Nom de police personnalisée')",

    "No websites added yet. Add a website to start testing.":
        "Aucun site Web ajouté pour le moment. Ajoutez un site Web pour commencer les tests.",

    "Please select at least one user for discovery (or Guest).":
        "Veuillez sélectionner au moins un utilisateur pour la découverte (ou Invité).",

    "The compliance score is calculated based on WCAG 2.2 Level AA criteria":
        "Le score de conformité est calculé sur la base des critères WCAG 2.2 Niveau AA",

    "Usually checked - test the page in its final state after setup":
        "Généralement coché - teste la page dans son état final après configuration",

    "Clear cookies and storage before testing to ensure a clean starting state":
        "Effacer les cookies et le stockage avant le test pour assurer un état de départ propre",

    "Recommended for cookie banner testing - ensures banner appears":
        "Recommandé pour le test des bannières de cookies - garantit l'apparition de la bannière",

    "Define the actions to perform. Steps execute in order from top to bottom.":
        "Définissez les actions à effectuer. Les étapes s'exécutent dans l'ordre de haut en bas.",

    "Please add at least one step to the script.":
        "Veuillez ajouter au moins une étape au script.",

    "No violations found! The page passes all automated accessibility checks.":
        "Aucune violation trouvée ! La page réussit tous les contrôles d'accessibilité automatisés.",

    "No test users configured. Discovery will run as guest.":
        "Aucun utilisateur de test configuré. La découverte s'exécutera en tant qu'invité.",

    "No test users configured. Testing will run as guest.":
        "Aucun utilisateur de test configuré. Les tests s'exécuteront en tant qu'invité.",

    "Please select at least one test user (or Guest) to continue.":
        "Veuillez sélectionner au moins un utilisateur de test (ou Invité) pour continuer.",

    "This will also delete all test results for this page.":
        "Ceci supprimera également tous les résultats de test pour cette page.",

    # Reports dashboard strings
    "Warnings": "Avertissements",
    "Screenshots (increases file size)": "Captures d'écran (augmente la taille du fichier)",
    "Generate Report": "Générer un rapport",
    "Timecodes": "Codes temporels",
    "Group Issues by Touchpoint": "Grouper les problèmes par point de contact",
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
