#!/usr/bin/env python3
"""
Add French translation for accessibility check descriptions.
"""

import polib
import sys

# Translation mapping for check descriptions
translations = {
    "Accessibility checks for %(touchpoint)s": "Vérifications d'accessibilité pour %(touchpoint)s",
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
