#!/usr/bin/env python3
"""
Add French translations for testing/configure page
"""

TRANSLATIONS = {
    # Page title and headers
    "Settings": "Paramètres",
    "Testing Configuration": "Configuration des tests",
    "System Maintenance": "Maintenance du système",

    # Testing configuration form
    "Parallel Tests": "Tests parallèles",
    "Number of tests to run in parallel": "Nombre de tests à exécuter en parallèle",
    "Test Timeout (seconds)": "Délai d'attente des tests (secondes)",
    "Maximum time per page test": "Temps maximum par test de page",
    "Enable AI Analysis": "Activer l'analyse IA",
    "Use Claude AI for visual accessibility analysis": "Utiliser Claude IA pour l'analyse visuelle de l'accessibilité",
    "Headless Browser": "Navigateur sans tête",
    "Run browser in headless mode": "Exécuter le navigateur en mode sans tête",
    "Viewport Width": "Largeur de la fenêtre",
    "Viewport Height": "Hauteur de la fenêtre",
    "UI Pagination Settings": "Paramètres de pagination de l'interface",
    "Pages Per Page": "Pages par page",
    "Default number of pages shown per view": "Nombre par défaut de pages affichées par vue",
    "Maximum Pages Per Page": "Maximum de pages par page",
    "Maximum allowed per page (for ?per_page parameter)": "Maximum autorisé par page (pour le paramètre ?per_page)",
    "Save Configuration": "Enregistrer la configuration",

    # System maintenance
    "Warning:": "Attention :",
    "These actions cannot be undone.": "Ces actions ne peuvent pas être annulées.",
    "Clear Outstanding Jobs": "Effacer les tâches en cours",
    "Reset all running and pending scrapes and tests. Use this if the system appears stuck.":
        "Réinitialiser toutes les explorations et tests en cours et en attente. Utilisez ceci si le système semble bloqué.",
    "Clear All Jobs": "Effacer toutes les tâches",
    "Clear Stale Jobs": "Effacer les tâches obsolètes",
    "Remove jobs that have been running for more than 24 hours.":
        "Supprimer les tâches en cours d'exécution depuis plus de 24 heures.",
    "Clean Page Data": "Nettoyer les données de page",
    "Reset violation counts for pages that haven't been tested yet. Fixes data inconsistencies.":
        "Réinitialiser les compteurs de violations pour les pages qui n'ont pas encore été testées. Corrige les incohérences de données.",
    "System Status": "État du système",
    "Loading...": "Chargement...",
    "Loading job statistics...": "Chargement des statistiques des tâches...",

    # Modal
    "Confirm Action": "Confirmer l'action",
    "Cancel": "Annuler",
    "Confirm": "Confirmer",

    # JavaScript strings
    "Running:": "En cours :",
    "Pending:": "En attente :",
    "Cancelling:": "Annulation :",
    "Completed (24h):": "Terminées (24h) :",
    "Failed (24h):": "Échouées (24h) :",
    "jobs": "tâches",
    "Failed to load statistics": "Échec du chargement des statistiques",
    "This will clear ALL running and pending jobs. This action cannot be undone. Are you sure?":
        "Ceci effacera TOUTES les tâches en cours et en attente. Cette action ne peut pas être annulée. Êtes-vous sûr ?",
    "Successfully cleared": "Effacement réussi de",
    "Failed to clear jobs": "Échec de l'effacement des tâches",
    "An error occurred while clearing jobs": "Une erreur s'est produite lors de l'effacement des tâches",
    "This will clear all jobs that have been running for more than 24 hours. Are you sure?":
        "Ceci effacera toutes les tâches en cours d'exécution depuis plus de 24 heures. Êtes-vous sûr ?",
    "stale jobs": "tâches obsolètes",
    "Failed to clear stale jobs": "Échec de l'effacement des tâches obsolètes",
    "An error occurred while clearing stale jobs": "Une erreur s'est produite lors de l'effacement des tâches obsolètes",
    "Configuration saved successfully": "Configuration enregistrée avec succès",
    "Failed to save configuration": "Échec de l'enregistrement de la configuration",
    "An error occurred while saving configuration": "Une erreur s'est produite lors de l'enregistrement de la configuration",
    "This will reset violation counts for all pages that haven't been tested yet. Continue?":
        "Ceci réinitialisera les compteurs de violations pour toutes les pages qui n'ont pas encore été testées. Continuer ?",
    "Successfully cleaned": "Nettoyage réussi de",
    "pages": "pages",
    "Failed to clean page data": "Échec du nettoyage des données de page",
    "An error occurred while cleaning page data": "Une erreur s'est produite lors du nettoyage des données de page",
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
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
