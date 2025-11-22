#!/usr/bin/env python3
"""
Script to add French translations for scripts templates and remaining strings
"""

# French translations for scripts templates and remaining strings
TRANSLATIONS = {
    # Scripts general
    "Page-Specific Scripts": "Scripts spécifiques à la page",
    "Create Page Setup Script - Auto A11y": "Créer un script de configuration de page - Auto A11y",
    "Edit Script: %(name)s - Auto A11y": "Modifier le script : %(name)s - Auto A11y",
    "Quick Help": "Aide rapide",
    "Multi-State": "Multi-état",
    "Trigger": "Déclencheur",

    # Script form labels
    "A descriptive name for this script": "Un nom descriptif pour ce script",
    "e.g., Dismiss Cookie Banner": "par ex., Fermer la bannière de cookies",
    "Uncheck to disable this script without deleting it": "Décocher pour désactiver ce script sans le supprimer",

    # Multi-state testing
    "Test BEFORE executing script": "Tester AVANT l'exécution du script",
    "Test AFTER executing script": "Tester APRÈS l'exécution du script",
    "Usually checked - test the page in its final state after setup": "Généralement coché - tester la page dans son état final après la configuration",
    "Tests both before and after script": "Teste avant et après le script",
    "Before & After": "Avant et après",
    "Tests before script only": "Teste avant le script uniquement",
    "Before Only": "Avant uniquement",
    "Tests after script only": "Teste après le script uniquement",
    "After Only": "Après uniquement",
    "Both": "Les deux",
    "Before": "Avant",

    # Script scope
    "Script Applies To:": "Le script s'applique à :",
    "This script will run for all pages in the website": "Ce script s'exécutera pour toutes les pages du site web",
    "This script only runs on this specific page": "Ce script s'exécute uniquement sur cette page spécifique",
    "What are Website-Level Scripts?": "Que sont les scripts au niveau du site web ?",
    "What are Page-Level Scripts?": "Que sont les scripts au niveau de la page ?",

    # Execution trigger
    "Execution Trigger": "Déclencheur d'exécution",
    "When should this script run?": "Quand ce script doit-il s'exécuter ?",
    "Select when this script should execute during testing": "Sélectionner quand ce script doit s'exécuter pendant les tests",
    "Conditional Selector": "Sélecteur conditionnel",
    "Script will only run if this element exists on the page": "Le script ne s'exécutera que si cet élément existe sur la page",
    "Wait for element to appear": "Attendre l'apparition de l'élément",
    "e.g., Wait for cookie banner to appear": "par ex., Attendre l'apparition de la bannière de cookies",
    "Wait Timeout (ms)": "Délai d'attente (ms)",
    "Maximum time to wait for element (milliseconds)": "Temps maximum d'attente de l'élément (millisecondes)",

    # Clean state options
    "Clean State Options": "Options d'état propre",
    "Clear cookies and storage before testing to ensure a clean starting state": "Effacer les cookies et le stockage avant les tests pour garantir un état de départ propre",
    "Clear Cookies Before Script": "Effacer les cookies avant le script",
    "Recommended for cookie banner testing - ensures banner appears": "Recommandé pour les tests de bannière de cookies - garantit l'apparition de la bannière",
    "Clear Local Storage Before Script": "Effacer le stockage local avant le script",
    "Clear localStorage and sessionStorage before running": "Effacer localStorage et sessionStorage avant l'exécution",

    # State validation
    "Expected Visible Elements:": "Éléments visibles attendus :",
    "Expected Hidden Elements:": "Éléments cachés attendus :",
    "Elements That Should Be <strong>Visible</strong> After Script": "Éléments qui doivent être <strong>visibles</strong> après le script",
    "Elements That Should Be <strong>Hidden</strong> After Script": "Éléments qui doivent être <strong>cachés</strong> après le script",

    # Script steps
    "%(count)s steps": "%(count)s étapes",
    "Define the actions to perform. Steps execute in order from top to bottom.": "Définir les actions à effectuer. Les étapes s'exécutent dans l'ordre de haut en bas.",
    "Please add at least one step to the script.": "Veuillez ajouter au moins une étape au script.",
    "-- Select Action --": "-- Sélectionner une action --",
    "Click a button/link": "Cliquer sur un bouton/lien",
    "Wait until element appears": "Attendre l'apparition de l'élément",
    "Pause for X milliseconds": "Pause de X millisecondes",
    "Selector (CSS or XPath)": "Sélecteur (CSS ou XPath)",
    "CSS selector or XPath (XPath must start with / or //)": "Sélecteur CSS ou XPath (XPath doit commencer par / ou //)",
    "Text to type or value to set": "Texte à saisir ou valeur à définir",
    "Value": "Valeur",
    "Wait After (ms)": "Attente après (ms)",
    "Attribute": "Attribut",
    "Click:": "Cliquer :",
    "Wait (Fixed):": "Attente (fixe) :",

    # Cookie banner example
    "Cookie Banner:": "Bannière de cookies :",

    # Confirmation messages
    "Toggle this script (enable/disable)?": "Basculer ce script (activer/désactiver) ?",

    # Test configuration strings
    "DOM Content Loaded (Fast, for sites with heavy background activity)": "Contenu DOM chargé (rapide, pour les sites avec beaucoup d'activité en arrière-plan)",
    "Wait until network has ≤2 connections (best for dynamic sites)": "Attendre jusqu'à ce que le réseau ait ≤2 connexions (idéal pour les sites dynamiques)",
    "Run browser invisibly (faster, less resource intensive)": "Exécuter le navigateur de manière invisible (plus rapide, moins de ressources)",
    "Verifies logical reading sequence matches visual layout": "Vérifie que la séquence de lecture logique correspond à la disposition visuelle",
    "Enter font names, one per line (e.g., 'Custom Font Name')": "Entrez les noms de police, un par ligne (par ex., 'Nom de police personnalisée')",

    # WCAG and accessibility
    "Standard compliance (4.5:1 contrast for normal text, 3:1 for large text)": "Conformité standard (contraste 4.5:1 pour le texte normal, 3:1 pour le texte large)",
    "Enhanced compliance (7:1 contrast for normal text, 4.5:1 for large text)": "Conformité renforcée (contraste 7:1 pour le texte normal, 4.5:1 pour le texte large)",
    "The compliance score is calculated based on WCAG 2.2 Level AA criteria": "Le score de conformité est calculé sur la base des critères WCAG 2.2 niveau AA",
    "More about": "En savoir plus sur",
    "Ways to meet": "Façons de respecter",

    # Test results
    "No violations found! The page passes all automated accessibility checks.": "Aucune violation trouvée ! La page réussit tous les tests d'accessibilité automatisés.",
    "The accessibility test is running. The page will refresh when complete.": "Le test d'accessibilité est en cours. La page se rafraîchira une fois terminé.",
    "Real browser testing with Puppeteer ensures accurate DOM-based results": "Les tests avec un navigateur réel via Puppeteer garantissent des résultats précis basés sur le DOM",
    "An error occurred while loading the test details. Please try again.": "Une erreur s'est produite lors du chargement des détails du test. Veuillez réessayer.",

    # Screenshots and visual
    "Page Thumbnail (at time of test)": "Vignette de la page (au moment du test)",
    "Thumbnail of": "Vignette de",
    "Thumbnail not available": "Vignette non disponible",
    "Click to view full size": "Cliquer pour voir en taille réelle",
    "Copy XPath to clipboard": "Copier le XPath dans le presse-papiers",
    "CSS State:": "État CSS :",

    # Visual analysis
    "This issue was detected through visual analysis.": "Ce problème a été détecté par analyse visuelle.",
    "Confidence:": "Confiance :",

    # User management
    "No test users configured. Discovery will run as guest.": "Aucun utilisateur de test configuré. La découverte s'exécutera en tant qu'invité.",
    "No test users configured. Testing will run as guest.": "Aucun utilisateur de test configuré. Les tests s'exécuteront en tant qu'invité.",
    "Please select at least one user for discovery (or Guest).": "Veuillez sélectionner au moins un utilisateur pour la découverte (ou Invité).",
    "Please select at least one test user (or Guest) to continue.": "Veuillez sélectionner au moins un utilisateur de test (ou Invité) pour continuer.",

    # Other
    "No websites added yet. Add a website to start testing.": "Aucun site web ajouté pour le moment. Ajoutez un site web pour commencer les tests.",
    "This will also delete all test results for this page.": "Cela supprimera également tous les résultats de test pour cette page.",
    "Report Generation": "Génération de rapport",
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
