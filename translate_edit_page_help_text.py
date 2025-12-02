#!/usr/bin/env python3
"""
Add French translations for the project edit page help text.
"""

import polib
import sys

# Translation mapping for help text
translations = {
    "Maximum recommended characters for page titles. Default is 60. Titles longer than this will generate a warning.":
        "Nombre maximum recommandé de caractères pour les titres de page. La valeur par défaut est 60. Les titres plus longs que cela généreront un avertissement.",

    "Browser tabs typically show ~30 characters, search results show ~50-60 characters.":
        "Les onglets du navigateur affichent généralement environ 30 caractères, les résultats de recherche affichent environ 50-60 caractères.",

    "Maximum recommended characters for headings (h1-h6). Default is 60. Headings longer than this will generate a warning.":
        "Nombre maximum recommandé de caractères pour les en-têtes (h1-h6). La valeur par défaut est 60. Les en-têtes plus longs que cela généreront un avertissement.",

    "Headings approaching this limit (above 67%% of the limit) will generate an info message.":
        "Les en-têtes approchant cette limite (au-dessus de 67 %% de la limite) généreront un message d'information.",
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
                    print(f"✓ Updated: {msgid[:60]}...")
                else:
                    print(f"  Skipped (already translated): {msgid[:60]}...")
            else:
                print(f"✗ Not found: {msgid[:60]}...")

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
