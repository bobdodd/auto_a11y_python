#!/usr/bin/env python3
"""
Script to add more French translations to messages.po file
"""

# Additional French translations
TRANSLATIONS = {
    # Page load strategy details
    "Controls when testing begins after navigating to a page:": "Contrôle quand les tests commencent après la navigation vers une page :",
    "Network Idle 2": "Network Idle 2",
    "Wait until network has ≤2 connections (best for dynamic sites)": "Attendre que le réseau ait ≤2 connexions (optimal pour les sites dynamiques)",
    "Network Idle 0": "Network Idle 0",
    "Wait until network is completely idle (very thorough but slow)": "Attendre que le réseau soit complètement inactif (très complet mais lent)",
    "DOM Content Loaded": "DOM Content Loaded",
    "Test as soon as DOM is ready (use for BBC News, sites with continuous ads/analytics)": "Tester dès que le DOM est prêt (à utiliser pour BBC News, sites avec publicités/analytics continues)",
    "Load Event": "Load Event",
    "Wait for load event (faster than network idle)": "Attendre l'événement de chargement (plus rapide que network idle)",

    # Browser mode details
    "Headless": "Sans interface",
    "Run browser invisibly (faster, less resource intensive)": "Exécuter le navigateur de manière invisible (plus rapide, moins gourmand en ressources)",
    "Visible Browser": "Navigateur visible",
    "Show the Chrome window (useful for debugging)": "Afficher la fenêtre Chrome (utile pour le débogage)",

    # Stealth mode details
    "Enables advanced bot detection bypass techniques. Use for sites protected by Cloudflare or similar services.": "Active les techniques avancées de contournement de détection de robots. À utiliser pour les sites protégés par Cloudflare ou services similaires.",
    "Stealth mode significantly slows down page discovery and testing (~5-15 seconds per page).": "Le mode furtif ralentit considérablement la découverte et les tests de pages (~5-15 secondes par page).",

    # Touchpoint configuration
    "Touchpoint Tests Configuration": "Configuration des tests par point de contact",
    "Configure which accessibility tests to run. Tests are organized by touchpoint (testing category).": "Configurez les tests d'accessibilité à exécuter. Les tests sont organisés par point de contact (catégorie de test).",

    # AI Testing
    "Enable AI-assisted accessibility testing": "Activer les tests d'accessibilité assistés par IA",
    "AI testing uses Claude to analyze screenshots and HTML for issues that automated tests might miss.": "Les tests IA utilisent Claude pour analyser les captures d'écran et le HTML afin de détecter les problèmes que les tests automatisés pourraient manquer.",

    # Test status words
    "Heading Analysis": "Analyse des titres",
    "Animations": "Animations",
    "Interactive Elements": "Éléments interactifs",
    "Loading...": "Chargement...",

    # Projects list
    "Active": "Actif",
    "Paused": "En pause",
    "Completed": "Terminé",
    "Created:": "Créé :",
    "Updated:": "Mis à jour :",
    "No projects found.": "Aucun projet trouvé.",
    "Create your first project": "Créez votre premier projet",

    # Discovery modal
    "Discovery Options": "Options de découverte",
    "Select users for discovery:": "Sélectionnez les utilisateurs pour la découverte :",
    "Guest": "Invité",
    "no login": "sans connexion",
    "Discovery will run with the selected user(s).": "La découverte s'exécutera avec le(s) utilisateur(s) sélectionné(s).",
    "Manage test users": "Gérer les utilisateurs de test",
    "Add test users": "Ajouter des utilisateurs de test",
    "to discover pages requiring authentication.": "pour découvrir les pages nécessitant une authentification.",
    "Maximum Pages to Discover": "Nombre maximum de pages à découvrir",
    "Leave empty for no limit": "Laisser vide pour aucune limite",
    "Limit the number of pages to discover (useful for large sites)": "Limiter le nombre de pages à découvrir (utile pour les grands sites)",
    "Discovery will crawl the website starting from the home page, following links to find all accessible pages.": "La découverte explorera le site web en partant de la page d'accueil, en suivant les liens pour trouver toutes les pages accessibles.",
    "Start Discovery": "Démarrer la découverte",

    # Test All Websites modal
    "Test All Websites in Project": "Tester tous les sites du projet",
    "This will test all websites in the project": "Ceci testera tous les sites web du projet",
    "website(s)": "site(s) web",
    "will be tested across multiple base URLs.": "seront testés sur plusieurs URL de base.",
    "Test all pages (unchecked = only untested pages)": "Tester toutes les pages (non coché = seulement les pages non testées)",
    "Take screenshots of issues": "Prendre des captures d'écran des problèmes",
    "Run AI analysis (requires OpenAI API key)": "Exécuter l'analyse IA (nécessite une clé API OpenAI)",
    "Start Testing All Websites": "Démarrer les tests de tous les sites",

    # Delete Project modal
    "Delete Project": "Supprimer le projet",
    "Are you sure you want to delete the project": "Êtes-vous sûr de vouloir supprimer le projet",
    "This will permanently delete all websites, pages, and test results associated with this project.": "Ceci supprimera définitivement tous les sites web, pages et résultats de tests associés à ce projet.",

    # Add Website modal
    "Website URL": "URL du site web",
    "https://example.com": "https://exemple.com",
    "Name (Optional)": "Nom (Optionnel)",
    "Main Website": "Site web principal",

    # Recordings
    "No recordings added yet.": "Aucun enregistrement ajouté pour le moment.",
    "Upload a recording": "Télécharger un enregistrement",
    "to track manual accessibility audits.": "pour suivre les audits d'accessibilité manuels.",

    # JavaScript status messages
    "Testing...": "Test en cours...",
    "Just completed": "Vient de se terminer",
    "Testing": "Test en cours",
    "pages": "pages",
    "Discovery is already running for this website. Do you want to cancel it?": "La découverte est déjà en cours pour ce site. Voulez-vous l'annuler ?",
    "Please select at least one user for discovery (or Guest).": "Veuillez sélectionner au moins un utilisateur pour la découverte (ou Invité).",
    "Starting...": "Démarrage...",
    "Discovering pages for": "Découverte des pages pour",
    "max": "max",
    "Discovery Started": "Découverte démarrée",
    "Failed to start discovery": "Échec du démarrage de la découverte",
    "Failed to start page discovery": "Échec du démarrage de la découverte de pages",
    "No discovery job to cancel": "Aucune tâche de découverte à annuler",
    "Cancelling...": "Annulation...",
    "Discovery Cancelled": "Découverte annulée",
    "Failed to cancel discovery:": "Échec de l'annulation de la découverte :",
    "Unknown error": "Erreur inconnue",
    "Failed to cancel discovery": "Échec de l'annulation de la découverte",
    "Cancel the discovery process?": "Annuler le processus de découverte ?",
    "Found": "Trouvé",
    "Discovery Complete": "Découverte terminée",
    "Refreshing...": "Actualisation...",
    "Discovery failed:": "Échec de la découverte :",

    # Page details modal
    "View Details": "Voir les détails",

    # Sync status
    "No data": "Aucune donnée",

    # Common UI elements
    "Yes": "Oui",
    "No": "Non",
    "Confirm": "Confirmer",
    "Submit": "Soumettre",
    "Apply": "Appliquer",
    "Reset": "Réinitialiser",
    "Clear": "Effacer",
    "Search": "Rechercher",
    "Filter": "Filtrer",
    "Sort": "Trier",
    "Export": "Exporter",
    "Import": "Importer",
    "Download": "Télécharger",
    "Upload": "Téléverser",
    "Refresh": "Actualiser",
    "Previous": "Précédent",
    "Next": "Suivant",
    "First": "Premier",
    "Last": "Dernier",
    "Show": "Afficher",
    "Hide": "Masquer",
    "More": "Plus",
    "Less": "Moins",
    "Details": "Détails",
    "Summary": "Résumé",
    "Overview": "Aperçu",
    "Settings": "Paramètres",
    "Options": "Options",
    "Preferences": "Préférences",
    "Help": "Aide",
    "About": "À propos",
    "Documentation": "Documentation",
    "Support": "Support",
    "Contact": "Contact",
    "Terms": "Conditions",
    "Privacy": "Confidentialité",
    "License": "Licence",
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

    print(f"✓ Added {translations_added} more French translations to {po_path}")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
