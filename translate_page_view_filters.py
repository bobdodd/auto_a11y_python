#!/usr/bin/env python3
"""
Add French translations for page view filters and related UI elements.
"""

import polib
import sys

# Translation mapping for page view filters and UI
translations = {
    # Filter UI labels
    "Filter Test Results": "Filtrer les résultats des tests",
    "Clear All": "Tout effacer",
    "Active Filters:": "Filtres actifs :",
    "Showing:": "Affichage :",
    "of": "de",
    "items": "éléments",
    "Issue Type": "Type de problème",
    "Errors": "Erreurs",
    "Warnings": "Avertissements",
    "Info": "Info",
    "Discovery": "Découverte",
    "Impact Level": "Niveau d'impact",
    "High": "Élevé",
    "Medium": "Moyen",
    "Low": "Faible",
    "WCAG Criteria": "Critères WCAG",
    "Touchpoint": "Point de contact",
    "Affected User Groups": "Groupes d'utilisateurs affectés",
    "Vision": "Vision",
    "Hearing": "Audition",
    "Motor": "Motricité",
    "Cognitive": "Cognitif",
    "Seizure": "Épilepsie",
    "Test User": "Utilisateur de test",
    "Quick Search": "Recherche rapide",
    "Search in issue descriptions, IDs, or code...": "Rechercher dans les descriptions, ID ou code...",

    # Test Check Details table headers
    "Test": "Test",
    "Check": "Vérification",
    "Tested": "Testé",
    "Passed": "Réussi",
    "Failed": "Échoué",
    "Pass Rate": "Taux de réussite",
    "Totals": "Totaux",
    "N/A checks": "vérifications N/D",
    "skipped": "ignoré",

    # Latest Test Results section
    "Tested on": "Testé le",
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
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
