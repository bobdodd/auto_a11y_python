#!/usr/bin/env python3
"""
Add French translations for font configuration help text on project edit page.
"""

import polib
import sys

# Translation mapping for font configuration help text
translations = {
    "Add project-specific fonts that should be flagged as inaccessible. One font name per line, lowercase.":
        "Ajoutez des polices spécifiques au projet qui doivent être signalées comme inaccessibles. Un nom de police par ligne, en minuscules.",

    "Remove specific fonts from the default list if your project requires them. One font name per line, lowercase.":
        "Supprimez des polices spécifiques de la liste par défaut si votre projet les nécessite. Un nom de police par ligne, en minuscules.",
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
