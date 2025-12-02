#!/usr/bin/env python3
"""
Add French translations for touchpoint names (accessibility testing categories).
"""

import polib
import sys

# Translation mapping for touchpoint names
translations = {
    # Touchpoint category names
    "Accessible Names": "Noms accessibles",
    "Animation": "Animation",
    "ARIA": "ARIA",
    "Buttons": "Boutons",
    "Colors & Contrast": "Couleurs et contraste",
    "Dialogs & Modals": "Dialogues et modales",
    "Documents": "Documents",
    "Event Handling": "Gestion des événements",
    "Focus Management": "Gestion du focus",
    "Forms": "Formulaires",
    "Headings": "En-têtes",
    "Iframes": "Iframes",
    "Inline Styles": "Styles en ligne",
    "Images": "Images",
    "Keyboard Navigation": "Navigation au clavier",
    "Landmarks": "Points de repère",
    "Language": "Langue",
    "Links": "Liens",
    "Lists": "Listes",
    "Maps": "Cartes",
    "Media": "Médias",
    "Navigation": "Navigation",
    "Page": "Page",
    "Reading Order": "Ordre de lecture",
    "Semantic Structure": "Structure sémantique",
    "Tables": "Tableaux",
    "Timing": "Minuterie",
    "Title Attributes": "Attributs title",
    "Fonts": "Polices",
    "Other": "Autre",
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
