#!/usr/bin/env python3
"""
Script to add French translations to messages.po file
"""

# Common French translations
TRANSLATIONS = {
    # Project management
    "Create Project": "Créer un projet",
    "Create New Project": "Créer un nouveau projet",
    "Project Name": "Nom du projet",
    "Project Type": "Type de projet",
    "Description": "Description",
    "Choose a unique name for your project": "Choisissez un nom unique pour votre projet",
    "Optional description of the project goals": "Description optionnelle des objectifs du projet",

    # Project types
    "Website": "Site web",
    "App": "Application",
    "Tangible Device": "Appareil tangible",
    "Nav and Wayfinding": "Navigation et orientation",
    "Select the type of project you're testing": "Sélectionnez le type de projet que vous testez",

    # Fields
    "App Identifier": "Identifiant de l'application",
    "Device Model": "Modèle d'appareil",
    "Location": "Emplacement",
    "e.g., com.example.myapp or Bundle ID": "par ex., com.exemple.monapp ou Bundle ID",
    "e.g., NCR SelfServ 84, Diebold ATM": "par ex., NCR SelfServ 84, Diebold ATM",
    "e.g., Building A, Floor 2 or Downtown Campus": "par ex., Bâtiment A, Étage 2 ou Campus Centre-ville",
    "Optional: Package name (Android) or Bundle ID (iOS)": "Optionnel : Nom du paquet (Android) ou Bundle ID (iOS)",
    "Optional: Manufacturer and model of the device": "Optionnel : Fabricant et modèle de l'appareil",
    "Optional: Physical location of the navigation system": "Optionnel : Emplacement physique du système de navigation",

    # Debug mode
    "Debug Mode Active:": "Mode débogage actif :",
    "All tests are available regardless of fixture status.": "Tous les tests sont disponibles indépendamment de l'état des fixtures.",
    "Test Availability:": "Disponibilité des tests :",
    "Only tests that passed fixture validation are enabled.": "Seuls les tests ayant réussi la validation des fixtures sont activés.",
    "View Fixture Status": "Voir l'état des fixtures",

    # Drupal
    "Drupal Audit (Optional)": "Audit Drupal (Optionnel)",
    "Auto-match by project name": "Correspondance automatique par nom de projet",
    "Loading audits...": "Chargement des audits...",
    'Select the corresponding audit in Drupal for synchronization. Leave as "Auto-match" to use the project name.': 'Sélectionnez l\'audit correspondant dans Drupal pour la synchronisation. Laissez "Correspondance automatique" pour utiliser le nom du projet.',

    # WCAG
    "WCAG Compliance Level": "Niveau de conformité WCAG",
    "Level AA (Recommended)": "Niveau AA (Recommandé)",
    "Level AAA (Enhanced)": "Niveau AAA (Amélioré)",
    "Level AA:": "Niveau AA :",
    "Standard compliance (4.5:1 contrast for normal text, 3:1 for large text)": "Conformité standard (contraste 4.5:1 pour le texte normal, 3:1 pour le texte large)",
    "Level AAA:": "Niveau AAA :",
    "Enhanced compliance (7:1 contrast for normal text, 4.5:1 for large text)": "Conformité améliorée (contraste 7:1 pour le texte normal, 4.5:1 pour le texte large)",

    # Page load strategy
    "Page Load Strategy": "Stratégie de chargement de page",
    "Network Idle 2 (Default - Best for most sites)": "Network Idle 2 (Par défaut - Optimal pour la plupart des sites)",
    "Network Idle 0 (Very thorough, slowest)": "Network Idle 0 (Très complet, le plus lent)",
    "DOM Content Loaded (Fast, for sites with heavy background activity)": "DOM Content Loaded (Rapide, pour les sites avec beaucoup d'activité en arrière-plan)",
    "Load Event (Middle ground)": "Load Event (Compromis)",

    # Browser mode
    "Browser Display Mode": "Mode d'affichage du navigateur",
    "Headless (No visible browser)": "Sans interface (Navigateur invisible)",
    "Visible Browser (Show Chrome window)": "Navigateur visible (Afficher la fenêtre Chrome)",

    # Stealth mode
    "Enable Stealth Mode (for Cloudflare-protected sites)": "Activer le mode furtif (pour les sites protégés par Cloudflare)",
    "Enables advanced bot detection bypass techniques. Use for sites protected by Cloudflare or similar services.": "Active les techniques avancées de contournement de détection de robots. À utiliser pour les sites protégés par Cloudflare ou services similaires.",
    "Note:": "Remarque :",
    "Stealth mode significantly slows down page discovery and testing (~5-15 seconds per page).": "Le mode furtif ralentit considérablement la découverte et les tests de pages (~5-15 secondes par page).",

    # AI Testing
    "AI-Assisted Testing": "Tests assistés par IA",
    "Enable AI-assisted accessibility testing": "Activer les tests d'accessibilité assistés par IA",
    "AI testing uses Claude to analyze screenshots and HTML for issues that automated tests might miss.": "Les tests IA utilisent Claude pour analyser les captures d'écran et le HTML afin de détecter les problèmes que les tests automatisés pourraient manquer.",
    "AI testing incurs API costs based on usage.": "Les tests IA entraînent des coûts d'API en fonction de l'utilisation.",
    "Select AI Tests to Run:": "Sélectionner les tests IA à exécuter :",
    "Heading Analysis": "Analyse des titres",
    "Detects visual headings not properly marked up": "Détecte les titres visuels non correctement balisés",
    "Reading Order": "Ordre de lecture",
    "Verifies logical reading sequence matches visual layout": "Vérifie que la séquence de lecture logique correspond à la mise en page visuelle",
    "Modal Dialogs": "Boîtes de dialogue modales",
    "Analyzes popup and overlay accessibility": "Analyse l'accessibilité des popups et overlays",
    "Language Detection": "Détection de langue",
    "Identifies mixed languages and missing declarations": "Identifie les langues mixtes et les déclarations manquantes",
    "Animations": "Animations",
    "Detects potentially problematic motion": "Détecte les mouvements potentiellement problématiques",
    "Interactive Elements": "Éléments interactifs",
    "Analyzes buttons, links, and form controls": "Analyse les boutons, liens et contrôles de formulaire",
    "Select All": "Tout sélectionner",
    "Deselect All": "Tout désélectionner",

    # Touchpoint configuration
    "Touchpoint Tests Configuration": "Configuration des tests par point de contact",
    "Configure which accessibility tests to run. Tests are organized by touchpoint (testing category).": "Configurez les tests d'accessibilité à exécuter. Les tests sont organisés par point de contact (catégorie de test).",
    "Enable All": "Tout activer",
    "Disable All": "Tout désactiver",
    "Minimal": "Minimal",
    "WCAG AA": "WCAG AA",

    # Buttons
    "Create": "Créer",
    "Cancel": "Annuler",
    "Save": "Enregistrer",
    "Delete": "Supprimer",
    "Edit": "Modifier",
    "Update": "Mettre à jour",
    "Close": "Fermer",

    # Status
    "Active": "Actif",
    "Paused": "En pause",
    "Completed": "Terminé",
    "Archived": "Archivé",

    # Common terms
    "Loading...": "Chargement...",
    "Error": "Erreur",
    "Success": "Succès",
    "Warning": "Avertissement",
    "Info": "Information",

    # Test details modal
    "Test Details": "Détails du test",
    "Loading test details...": "Chargement des détails du test...",
    "What This Test Detects": "Ce que ce test détecte",
    "Why It Matters": "Pourquoi c'est important",
    "Who It Affects": "Qui est affecté",
    "How to Fix": "Comment corriger",
    "Test Information Not Available": "Informations sur le test non disponibles",
    "Details for test": "Détails pour le test",
    "are not available in the catalog.": "ne sont pas disponibles dans le catalogue.",
    "Error Loading Test Details": "Erreur de chargement des détails du test",
    "An error occurred while loading the test details. Please try again.": "Une erreur s'est produite lors du chargement des détails du test. Veuillez réessayer.",

    # Projects list
    "All": "Tous",
    "Created": "Créé",
    "Updated": "Mis à jour",
    "View": "Voir",
    "Status": "Statut",
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
