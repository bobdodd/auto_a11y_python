#!/usr/bin/env python3
"""
Script to add French translations for newly marked templates
"""

# French translations for all new template strings
TRANSLATIONS = {
    # Pages view - General
    "Page": "Page",
    "Untitled Page": "Page sans titre",
    "Cancel Test": "Annuler le test",
    "Test as guest (no login)": "Tester en tant qu'invité (sans connexion)",
    "Test in Progress": "Test en cours",
    "The page will automatically refresh when testing completes.": "La page se rafraîchira automatiquement lorsque le test sera terminé.",
    "Queued": "En file d'attente",
    "Error": "Erreur",
    "Priority": "Priorité",
    "Critical": "Critique",
    "High": "Élevé",
    "Low": "Faible",
    "N/A": "N/A",
    "No screenshot available": "Aucune capture d'écran disponible",

    # Accessibility scores
    "Automated Accessibility Score": "Score d'accessibilité automatisé",
    "Get help about accessibility score": "Obtenir de l'aide sur le score d'accessibilité",
    "Automated WCAG Compliance Score": "Score de conformité WCAG automatisé",
    "Get help about compliance score": "Obtenir de l'aide sur le score de conformité",
    "automated tests passed": "tests automatisés réussis",
    "No data available": "Aucune donnée disponible",
    "Accessibility Issues Found": "Problèmes d'accessibilité trouvés",
    "Info": "Info",
    "Overall Pass Rate": "Taux de réussite global",
    "Get help about overall pass rate": "Obtenir de l'aide sur le taux de réussite global",
    "Total Tested": "Total testé",

    # Test results
    "Understanding the Numbers": "Comprendre les chiffres",
    "Example:": "Exemple :",
    "Check": "Vérification",
    "WCAG": "WCAG",
    "Pass Rate": "Taux de réussite",
    "Totals": "Totaux",
    "N/A checks": "vérifications N/A",
    "skipped": "ignorées",
    "Errors:": "Erreurs :",
    "Breakpoint:": "Point d'arrêt :",
    "px width": "px de largeur",
    "Instance": "Instance",
    "About this issue:": "À propos de ce problème :",
    "What the issue is:": "Quel est le problème :",
    "Why this is important:": "Pourquoi c'est important :",
    "Who it affects:": "Qui cela affecte :",
    "How to remediate:": "Comment y remédier :",
    "Relevant test criteria:": "Critères de test pertinents :",
    "WCAG Success Criteria:": "Critères de succès WCAG :",
    "Rule:": "Règle :",
    "How to fix:": "Comment corriger :",
    "Touchpoint:": "Point de contact :",
    "General": "Général",
    "Impact:": "Impact :",
    "Code Snippet": "Extrait de code",
    "XPath:": "XPath :",

    # Info notes
    "Info Notes": "Notes informatives",
    "This is an informational note.": "Ceci est une note informative.",
    "What was found:": "Ce qui a été trouvé :",
    "Why manual review is needed:": "Pourquoi une révision manuelle est nécessaire :",
    "Who could be affected:": "Qui pourrait être affecté :",
    "What to check manually:": "Ce qu'il faut vérifier manuellement :",
    "This item requires manual inspection.": "Cet élément nécessite une inspection manuelle.",

    # Test status messages
    "Screenshot": "Capture d'écran",
    "Running accessibility tests on this page...": "Exécution des tests d'accessibilité sur cette page...",
    "This may take a moment.": "Cela peut prendre un moment.",
    "Refreshing page to show results...": "Actualisation de la page pour afficher les résultats...",
    "The page test has been cancelled.": "Le test de page a été annulé.",
    "The accessibility test is running. The page will refresh when complete.": "Le test d'accessibilité est en cours. La page se rafraîchira une fois terminé.",

    # Font configuration
    "Page Title Length Limit": "Limite de longueur du titre de page",
    "Configure which fonts should be flagged as inaccessible for this project.": "Configurez les polices à signaler comme inaccessibles pour ce projet.",
    "Use system default inaccessible fonts list": "Utiliser la liste système des polices inaccessibles par défaut",
    "Additional Fonts to Flag": "Polices supplémentaires à signaler",
    "Enter font names, one per line (e.g., 'Custom Font Name')": "Entrez les noms de police, un par ligne (par ex., 'Nom de police personnalisée')",
    "Fonts to Exclude from Checking": "Polices à exclure de la vérification",
    "Enter font names, one per line (e.g., 'comic sans ms')": "Entrez les noms de police, un par ligne (par ex., 'comic sans ms')",
    "View System Default Inaccessible Fonts List": "Voir la liste système des polices inaccessibles par défaut",
    "Script/Cursive Fonts (17 fonts)": "Polices script/cursives (17 polices)",
    "Show all 17 fonts...": "Afficher les 17 polices...",
    "Decorative Fonts (16 fonts)": "Polices décoratives (16 polices)",
    "Show all 16 fonts...": "Afficher les 16 polices...",
    "Narrow/Condensed Fonts (2 fonts)": "Polices étroites/condensées (2 polices)",
    "Blackletter/Gothic Fonts (5 fonts)": "Polices gothiques/Blackletter (5 polices)",
    "Total:": "Total :",
    "40 fonts across 4 categories": "40 polices dans 4 catégories",

    # Test details modal
    "Test Information Not Available": "Informations sur le test non disponibles",
    "Details for test": "Détails pour le test",
    "are not available in the catalog.": "ne sont pas disponibles dans le catalogue.",
    "An error occurred while loading the test details. Please try again.": "Une erreur s'est produite lors du chargement des détails du test. Veuillez réessayer.",
    "Could not load audits (Drupal may not be configured)": "Impossible de charger les audits (Drupal n'est peut-être pas configuré)",

    # Websites view
    "No websites added yet. Add a website to start testing.": "Aucun site web ajouté pour le moment. Ajoutez un site web pour commencer les tests.",
    "Documents": "Documents",
    "Setup Scripts": "Scripts de configuration",
    "Site Structure": "Structure du site",
    "page(s) could not be discovered:": "page(s) n'ont pas pu être découvertes :",
    "Show": "Afficher",
    "more failed pages...": "pages échouées supplémentaires...",
    "attempts": "tentatives",
    "depth": "profondeur",
    "Showing": "Affichage",
    "of": "de",
    "No image": "Aucune image",
    "No test users configured. Discovery will run as guest.": "Aucun utilisateur de test configuré. La découverte s'exécutera en tant qu'invité.",
    "Add Page Manually": "Ajouter une page manuellement",
    "Test All Pages Options": "Options de test de toutes les pages",
    "No test users configured. Testing will run as guest.": "Aucun utilisateur de test configuré. Les tests s'exécuteront en tant qu'invité.",

    # JavaScript messages
    "All pages have been tested. Refreshing...": "Toutes les pages ont été testées. Actualisation...",
    "Failed to queue tests": "Échec de la mise en file d'attente des tests",
    "Page queued for testing": "Page mise en file d'attente pour les tests",
    "Page test has been cancelled": "Le test de page a été annulé",
    "Page has been deleted successfully": "La page a été supprimée avec succès",
    "Generating site structure report in": "Génération du rapport de structure de site en",
    "Generating accessibility report in": "Génération du rapport d'accessibilité en",

    # Test result page
    "Back to Page": "Retour à la page",
    "Metadata": "Métadonnées",
    "Learn More:": "En savoir plus :",
    "HTML:": "HTML :",
    "Pseudoclass:": "Pseudo-classe :",
    "No violations found! The page passes all automated accessibility checks.": "Aucune violation trouvée ! La page réussit tous les tests d'accessibilité automatisés.",
    "seconds": "secondes",
    "Rules Run:": "Règles exécutées :",
    "Standard": "Standard",
    "Additional Metadata": "Métadonnées supplémentaires",

    # Common buttons and labels
    "Run Test": "Exécuter le test",
    "Edit": "Modifier",
    "Scripts": "Scripts",
    "Reports": "Rapports",
    "Discovery History": "Historique de découverte",
    "Test Users": "Utilisateurs de test",
    "Discover Pages": "Découvrir les pages",
    "Test All Pages": "Tester toutes les pages",
    "ABORT DISCOVERY": "ANNULER LA DÉCOUVERTE",
    "Cancel Testing": "Annuler les tests",
    "Add Page": "Ajouter une page",

    # Status and filters
    "Status": "Statut",
    "Violations": "Violations",
    "Warnings": "Avertissements",
    "Last Tested": "Dernier test",
    "Actions": "Actions",
    "Never": "Jamais",
    "View Details": "Voir les détails",
    "Run Test": "Exécuter le test",
    "Delete Page": "Supprimer la page",

    # Pagination
    "First": "Premier",
    "Previous": "Précédent",
    "Next": "Suivant",
    "Last": "Dernier",
    "Page navigation": "Navigation de page",

    # Discovery and testing
    "Discovery Options": "Options de découverte",
    "Maximum Pages to Discover": "Nombre maximum de pages à découvrir",
    "Leave empty for unlimited discovery": "Laisser vide pour une découverte illimitée",
    "Limit the number of pages to discover. Default is unlimited (up to 1 million pages).": "Limiter le nombre de pages à découvrir. Par défaut, c'est illimité (jusqu'à 1 million de pages).",
    "Discovery will crawl your website starting from the home page, following links to find all accessible pages.": "La découverte parcourra votre site web à partir de la page d'accueil, en suivant les liens pour trouver toutes les pages accessibles.",
    "Start Discovery": "Démarrer la découverte",
    "Cancel": "Annuler",

    # Add page modal
    "Page URL *": "URL de la page *",
    "Priority": "Priorité",
    "Normal": "Normal",
    "Add Page": "Ajouter une page",

    # Test all modal
    "Select users for testing:": "Sélectionner les utilisateurs pour les tests :",
    "Guest": "Invité",
    "no login": "pas de connexion",
    "This will run accessibility tests on all pages with the selected user(s). Testing multiple users will increase the total test time.": "Cela exécutera des tests d'accessibilité sur toutes les pages avec le(s) utilisateur(s) sélectionné(s). Tester plusieurs utilisateurs augmentera le temps de test total.",
    "Start Testing": "Démarrer les tests",

    # Screenshot modal
    "Screenshot:": "Capture d'écran :",
    "Open in New Tab": "Ouvrir dans un nouvel onglet",
    "Close": "Fermer",

    # Discovery history
    "Discovery History": "Historique de découverte",
    "Date": "Date",
    "Pages Found": "Pages trouvées",
    "Failed": "Échouées",
    "Duration": "Durée",
    "Details": "Détails",
    "Unknown": "Inconnu",
    "Max:": "Max :",
    "pages": "pages",

    # Test history
    "Test History": "Historique des tests",
    "Test Date": "Date du test",
    "Test ID:": "ID du test :",
    "Test Date:": "Date du test :",
    "Duration:": "Durée :",
    "Test Suite:": "Suite de test :",
    "View Screenshot": "Voir la capture d'écran",

    # Test configuration
    "Test Configuration": "Configuration du test",
    "Test Information": "Informations sur le test",
    "AI Analysis:": "Analyse IA :",
    "Enabled": "Activé",
    "Disabled": "Désactivé",
    "Viewport:": "Zone d'affichage :",

    # Format strings
    "format...": "format...",
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
