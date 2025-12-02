#!/usr/bin/env python3
"""
Add French translations for the Drupal Sync section.
"""

import polib
import sys

# Translation mapping for Drupal Sync section
translations = {
    # Main headers
    "Drupal Sync": "Synchronisation Drupal",
    "Upload to Drupal": "Téléverser vers Drupal",

    # Step titles
    "Select Content to Upload": "Sélectionner le contenu à téléverser",
    "Uploading to Drupal...": "Téléversement vers Drupal...",
    "Upload Complete!": "Téléversement terminé !",

    # Content sections
    "Upload Log": "Journal de téléversement",
    "Successfully uploaded": "Téléversé avec succès",
    "items to Drupal.": "éléments vers Drupal.",
    "Some items failed:": "Certains éléments ont échoué :",

    # Buttons
    "Start Upload": "Démarrer le téléversement",
    "Synchronization Page": "Page de synchronisation",
    "Quick Upload": "Téléversement rapide",

    # Status labels
    "Last Sync": "Dernière synchronisation",
    "pending": "en attente",
    "Sync Issues": "Problèmes de synchronisation",
    "Audit:": "Audit :",

    # Configuration messages
    "Drupal Integration Not Configured": "Intégration Drupal non configurée",
    "Configure Drupal connection in": "Configurez la connexion Drupal dans",
    "to enable sync.": "pour activer la synchronisation.",

    # List messages
    "No discovered pages found.": "Aucune page découverte trouvée.",
    "No recordings found.": "Aucun enregistrement trouvé.",
    "Unknown duration": "Durée inconnue",

    # Error messages
    "Error loading sync status:": "Erreur lors du chargement de l'état de synchronisation :",
    "Error loading content:": "Erreur lors du chargement du contenu :",
    "Please select at least one item to upload.": "Veuillez sélectionner au moins un élément à téléverser.",
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
