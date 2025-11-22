#!/usr/bin/env python3
"""
Script to add French translations for help and about page templates
"""

# French translations for help and about pages
TRANSLATIONS = {
    # Page titles and headings
    "Help & Documentation": "Aide et documentation",
    "Help & Documentation - Auto A11y": "Aide et documentation - Auto A11y",
    "Page Not Found": "Page non trouvée",
    "Internal Server Error": "Erreur interne du serveur",
    "Server Error": "Erreur serveur",

    # Error messages
    "The page you're looking for doesn't exist.": "La page que vous recherchez n'existe pas.",
    "Something went wrong on our end.": "Quelque chose s'est mal passé de notre côté.",
    "Go Home": "Retour à l'accueil",

    # Main sections
    "FAQ": "FAQ",
    "Frequently Asked Questions": "Foire aux questions",
    "Reports & Exports": "Rapports et exports",
    "Issue Impact Levels": "Niveaux d'impact des problèmes",
    "WCAG Data Attribution": "Attribution des données WCAG",
    "Features": "Fonctionnalités",

    # Scoring explanations
    "Why Do I Have Two Different Scores?": "Pourquoi ai-je deux scores différents ?",
    "Auto A11y provides two types of scores based on your testing approach:": "Auto A11y fournit deux types de scores en fonction de votre approche de test :",
    "Within each testing type (automated or manual), you'll see two scores:": "Au sein de chaque type de test (automatisé ou manuel), vous verrez deux scores :",
    "Measures the percentage of individual checks/issues that passed": "Mesure le pourcentage de vérifications/problèmes individuels réussis",
    "Measures the percentage of WCAG Success Criteria passed": "Mesure le pourcentage de critères de succès WCAG réussis",

    # Score formulas
    "(Passed Checks / Applicable Checks) × 100": "(Vérifications réussies / Vérifications applicables) × 100",
    "(Tests with Zero Violations / Total Tests) × 100": "(Tests sans violations / Total des tests) × 100",
    "Counts partial successes": "Compte les succès partiels",
    "No penalties for missing elements": "Aucune pénalité pour les éléments manquants",
    "Shows progress toward compliance": "Montre la progression vers la conformité",
    "Shows true WCAG conformance": "Montre la véritable conformité WCAG",

    # Score ranges
    "100%:": "100% :",
    "90-99%:": "90-99% :",
    "70-89%:": "70-89% :",
    "50-69%:": "50-69% :",
    "Below 50%:": "Moins de 50% :",
    "Below 90%:": "Moins de 90% :",
    "90-100%:": "90-100% :",

    # Score descriptions
    "Excellent - Minor issues only": "Excellent - Problèmes mineurs uniquement",
    "Good - Some barriers remain": "Bon - Quelques obstacles subsistent",
    "Fair - Significant issues": "Passable - Problèmes significatifs",
    "Poor - Major accessibility problems": "Médiocre - Problèmes d'accessibilité majeurs",
    "More accurate scoring": "Notation plus précise",
    "Good for tracking improvements": "Bon pour suivre les améliorations",

    # Score examples
    "1 missing label ✗": "1 étiquette manquante ✗",
    "9 have proper labels ✓": "9 ont des étiquettes correctes ✓",
    "90% (9/10 passed)": "90% (9/10 réussis)",
    "Elements with violations": "Éléments avec violations",
    "Total elements that could be tested": "Total des éléments testables",

    # WCAG levels
    "Auto A11y tests against all three WCAG conformance levels:": "Auto A11y teste les trois niveaux de conformité WCAG :",
    "Minimum level of conformance": "Niveau minimum de conformité",
    "Essential for any site": "Essentiel pour tout site",
    "Standard level (most common target)": "Niveau standard (objectif le plus courant)",
    "Removes major barriers": "Élimine les obstacles majeurs",
    "Highest level of conformance": "Niveau de conformité le plus élevé",
    "Best practices and recommendations": "Meilleures pratiques et recommandations",

    # Contrast ratios
    "4.5:1 contrast ratio": "Ratio de contraste 4.5:1",
    "7:1 contrast ratio": "Ratio de contraste 7:1",

    # Impact levels
    "Completely blocks access for some users": "Bloque complètement l'accès pour certains utilisateurs",
    "Fix immediately": "Corriger immédiatement",
    "Significantly degrades experience": "Dégrade significativement l'expérience",
    "Fix soon": "Corriger rapidement",
    "Minor inconvenience": "Inconvénient mineur",
    "Fix when convenient": "Corriger quand c'est pratique",
    "Optimization opportunities": "Opportunités d'optimisation",
    "Focus on actual issues": "Se concentrer sur les problèmes réels",

    # Example issues
    "Missing form labels": "Étiquettes de formulaire manquantes",
    "Poor color contrast": "Mauvais contraste de couleur",
    "Missing landmarks": "Points de repère manquants",
    "Unclear link text": "Texte de lien peu clair",
    "Missing alt text on images": "Texte alternatif manquant sur les images",
    "Redundant alt text": "Texte alternatif redondant",

    # Testing approaches
    "Auto A11y supports multiple testing approaches:": "Auto A11y prend en charge plusieurs approches de test :",
    "Using axe-core engine": "Utilisant le moteur axe-core",
    "Fast, consistent, repeatable": "Rapide, cohérent, reproductible",
    "Benefits:": "Avantages :",
    "Available for tested pages": "Disponible pour les pages testées",
    "Human expert evaluation": "Évaluation par un expert humain",
    "Catches issues automation misses": "Détecte les problèmes que l'automatisation manque",
    "Subjective, context-aware testing": "Tests subjectifs, sensibles au contexte",
    "Tests user experience and workflows": "Teste l'expérience utilisateur et les flux de travail",

    # FAQ questions and answers
    "What's the difference between automated and manual testing?": "Quelle est la différence entre les tests automatisés et manuels ?",
    "How often should I run accessibility tests?": "À quelle fréquence dois-je effectuer des tests d'accessibilité ?",
    "What WCAG level should I aim for?": "Quel niveau WCAG dois-je viser ?",
    "Why is my compliance score so much lower than my accessibility score?": "Pourquoi mon score de conformité est-il beaucoup plus bas que mon score d'accessibilité ?",

    # About page
    "Basic features": "Fonctionnalités de base",
    "Comprehensive reporting and issue tracking": "Rapports complets et suivi des problèmes",
    "Project and test user management": "Gestion de projet et d'utilisateurs de test",

    # WCAG attribution
    "The WCAG Success Criteria data used in this application is sourced from:": "Les données des critères de succès WCAG utilisées dans cette application proviennent de :",
    "W3C Web Accessibility Initiative (WAI)": "Initiative pour l'accessibilité du Web du W3C (WAI)",
    "Web Content Accessibility Guidelines (WCAG) 2.2": "Règles pour l'accessibilité des contenus Web (WCAG) 2.2",
    "WCAG 2.2 JSON Data": "Données WCAG 2.2 JSON",
    "Techniques for WCAG 2.2": "Techniques pour WCAG 2.2",
    "October 2023": "Octobre 2023",

    # Copyright
    "Copyright": "Droits d'auteur",
    "Copyright (c) 2008-2023 World Wide Web Consortium.": "Copyright (c) 2008-2023 World Wide Web Consortium.",
    "Copyright © 2008-2023 World Wide Web Consortium.": "Copyright © 2008-2023 World Wide Web Consortium.",
    "applies to the WCAG content.": "s'applique au contenu WCAG.",
    "Important Notice": "Avis important",

    # Already translated strings appearing in new contexts
    "An error occurred while loading the test details. Please try again.": "Une erreur s'est produite lors du chargement des détails du test. Veuillez réessayer.",
    "Clear cookies and storage before testing to ensure a clean starting state": "Effacer les cookies et le stockage avant les tests pour garantir un état de départ propre",
    "Comma-separated list of user roles for testing role-based content": "Liste de rôles d'utilisateur séparés par des virgules pour tester le contenu basé sur les rôles",
    "Define the actions to perform. Steps execute in order from top to bottom.": "Définir les actions à effectuer. Les étapes s'exécutent dans l'ordre de haut en bas.",
    "DOM Content Loaded (Fast, for sites with heavy background activity)": "Contenu DOM chargé (rapide, pour les sites avec beaucoup d'activité en arrière-plan)",
    "Enhanced compliance (7:1 contrast for normal text, 4.5:1 for large text)": "Conformité renforcée (contraste 7:1 pour le texte normal, 4.5:1 pour le texte large)",
    "Enter font names, one per line (e.g., 'Custom Font Name')": "Entrez les noms de police, un par ligne (par ex., 'Nom de police personnalisée')",
    "Leave the password field blank to keep the current password unchanged.": "Laissez le champ mot de passe vide pour conserver le mot de passe actuel inchangé.",
    "No test users configured. Discovery will run as guest.": "Aucun utilisateur de test configuré. La découverte s'exécutera en tant qu'invité.",
    "No test users configured. Testing will run as guest.": "Aucun utilisateur de test configuré. Les tests s'exécuteront en tant qu'invité.",
    "No violations found! The page passes all automated accessibility checks.": "Aucune violation trouvée ! La page réussit tous les tests d'accessibilité automatisés.",
    "No websites added yet. Add a website to start testing.": "Aucun site web ajouté pour le moment. Ajoutez un site web pour commencer les tests.",
    "Please add at least one step to the script.": "Veuillez ajouter au moins une étape au script.",
    "Please select at least one test user (or Guest) to continue.": "Veuillez sélectionner au moins un utilisateur de test (ou Invité) pour continuer.",
    "Please select at least one user for discovery (or Guest).": "Veuillez sélectionner au moins un utilisateur pour la découverte (ou Invité).",
    "Real browser testing with Puppeteer ensures accurate DOM-based results": "Les tests avec un navigateur réel via Puppeteer garantissent des résultats précis basés sur le DOM",
    "Recommended for cookie banner testing - ensures banner appears": "Recommandé pour les tests de bannière de cookies - garantit l'apparition de la bannière",
    "Roles help you test content that varies based on user permissions.": "Les rôles vous aident à tester le contenu qui varie en fonction des autorisations utilisateur.",
    "Run browser invisibly (faster, less resource intensive)": "Exécuter le navigateur de manière invisible (plus rapide, moins de ressources)",
    "Standard compliance (4.5:1 contrast for normal text, 3:1 for large text)": "Conformité standard (contraste 4.5:1 pour le texte normal, 3:1 pour le texte large)",
    "The accessibility test is running. The page will refresh when complete.": "Le test d'accessibilité est en cours. La page se rafraîchira une fois terminé.",
    "The compliance score is calculated based on WCAG 2.2 Level AA criteria": "Le score de conformité est calculé sur la base des critères WCAG 2.2 niveau AA",
    "This will also delete all test results for this page.": "Cela supprimera également tous les résultats de test pour cette page.",
    "Usually checked - test the page in its final state after setup": "Généralement coché - tester la page dans son état final après la configuration",
    "Verifies logical reading sequence matches visual layout": "Vérifie que la séquence de lecture logique correspond à la disposition visuelle",
    "Wait until network has ≤2 connections (best for dynamic sites)": "Attendre jusqu'à ce que le réseau ait ≤2 connexions (idéal pour les sites dynamiques)",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    translations_added = 0

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Check if this is a msgid line
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            # Extract the msgid value
            msgid = line[7:-2]  # Remove 'msgid "' and '"\n'

            # Check if next line is msgstr ""
            if i + 1 < len(lines) and lines[i + 1] == 'msgstr ""\n':
                # Check if we have a translation for this
                if msgid in TRANSLATIONS:
                    new_lines.append(f'msgstr "{TRANSLATIONS[msgid]}"\n')
                    translations_added += 1
                    i += 2  # Skip the empty msgstr line
                    continue

        i += 1

    # Write back
    with open(po_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"✓ Added {translations_added} French translations to {po_path}")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
