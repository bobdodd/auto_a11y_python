#!/usr/bin/env python3
"""
Add French translations for the testing/configure page.
"""

import polib
import sys

# Translation mapping for configure page
translations = {
    # Page title and headers
    "Testing Configuration": "Configuration des tests",
    "System Maintenance": "Maintenance du système",
    "UI Pagination Settings": "Paramètres de pagination de l'interface",

    # Form labels
    "Parallel Tests": "Tests parallèles",
    "Test Timeout (seconds)": "Délai d'expiration du test (secondes)",
    "Enable AI Analysis": "Activer l'analyse IA",
    "Headless Browser": "Navigateur sans interface",
    "Viewport Width": "Largeur de la fenêtre",
    "Viewport Height": "Hauteur de la fenêtre",
    "Pages Per Page": "Pages par page",
    "Maximum Pages Per Page": "Maximum de pages par page",

    # Form help text
    "Number of tests to run in parallel": "Nombre de tests à exécuter en parallèle",
    "Maximum time per page test": "Temps maximum par test de page",
    "Use Claude AI for visual accessibility analysis": "Utiliser Claude IA pour l'analyse visuelle de l'accessibilité",
    "Run browser in headless mode": "Exécuter le navigateur en mode sans interface",
    "Default number of pages shown per view": "Nombre par défaut de pages affichées par vue",
    "Maximum allowed per page (for ?per_page parameter)": "Maximum autorisé par page (pour le paramètre ?per_page)",

    # Buttons
    "Save Configuration": "Enregistrer la configuration",
    "Clear All Jobs": "Effacer tous les travaux",
    "Clear Stale Jobs": "Effacer les travaux périmés",
    "Clean Page Data": "Nettoyer les données de page",

    # System Maintenance section
    "Warning:": "Avertissement :",
    "These actions cannot be undone.": "Ces actions ne peuvent pas être annulées.",
    "Clear Outstanding Jobs": "Effacer les travaux en suspens",
    "Reset all running and pending scrapes and tests. Use this if the system appears stuck.": "Réinitialiser toutes les extractions et tests en cours et en attente. Utilisez ceci si le système semble bloqué.",
    "Remove jobs that have been running for more than 24 hours.": "Supprimer les travaux en cours depuis plus de 24 heures.",
    "Reset violation counts for pages that haven't been tested yet. Fixes data inconsistencies.": "Réinitialiser les décomptes de violations pour les pages qui n'ont pas encore été testées. Corrige les incohérences de données.",

    # System Status
    "System Status": "État du système",
    "Loading job statistics...": "Chargement des statistiques des travaux...",

    # Modal
    "Confirm Action": "Confirmer l'action",

    # JavaScript strings - Job stats
    "Running:": "En cours :",
    "Pending:": "En attente :",
    "Cancelling:": "Annulation :",
    "Completed (24h):": "Terminés (24h) :",
    "Failed (24h):": "Échoués (24h) :",
    "jobs": "travaux",
    "Failed to load statistics": "Échec du chargement des statistiques",

    # JavaScript strings - Confirmation messages
    "This will clear ALL running and pending jobs. This action cannot be undone. Are you sure?": "Ceci effacera TOUS les travaux en cours et en attente. Cette action ne peut pas être annulée. Êtes-vous sûr ?",
    "This will clear all jobs that have been running for more than 24 hours. Are you sure?": "Ceci effacera tous les travaux en cours depuis plus de 24 heures. Êtes-vous sûr ?",
    "This will reset violation counts for all pages that haven't been tested yet. Continue?": "Ceci réinitialisera les décomptes de violations pour toutes les pages qui n'ont pas encore été testées. Continuer ?",

    # JavaScript strings - Success/Error messages
    "Successfully cleared": "Effacé avec succès",
    "stale jobs": "travaux périmés",
    "Failed to clear jobs": "Échec de l'effacement des travaux",
    "An error occurred while clearing jobs": "Une erreur s'est produite lors de l'effacement des travaux",
    "Failed to clear stale jobs": "Échec de l'effacement des travaux périmés",
    "An error occurred while clearing stale jobs": "Une erreur s'est produite lors de l'effacement des travaux périmés",
    "Configuration saved successfully": "Configuration enregistrée avec succès",
    "Failed to save configuration": "Échec de l'enregistrement de la configuration",
    "An error occurred while saving configuration": "Une erreur s'est produite lors de l'enregistrement de la configuration",
    "Successfully cleaned": "Nettoyé avec succès",
    "pages": "pages",
    "Failed to clean page data": "Échec du nettoyage des données de page",
    "An error occurred while cleaning page data": "Une erreur s'est produite lors du nettoyage des données de page",
}

def main():
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'

    try:
        po = polib.pofile(po_file)
        print(f"Loaded {po_file}")
        print(f"Total entries: {len(po)}")

        updates = 0
        for msgid, msgstr in translations.items():
            entry = po.find(msgid)
            if entry:
                if not entry.msgstr or entry.msgstr == msgid or 'fuzzy' in entry.flags:
                    entry.msgstr = msgstr
                    if 'fuzzy' in entry.flags:
                        entry.flags.remove('fuzzy')
                    updates += 1
                    print(f"✓ Updated: {msgid}")
                else:
                    print(f"  Skipped (already translated): {msgid}")
            else:
                print(f"✗ Not found: {msgid}")

        print(f"\nUpdated {updates} translations")

        # Save the file
        po.save(po_file)
        print(f"Saved {po_file}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
