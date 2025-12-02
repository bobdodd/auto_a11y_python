#!/usr/bin/env python3
"""
Remove fuzzy flags from .po file but keep the translations
"""

def remove_fuzzy_flags(po_path):
    """Remove #, fuzzy lines but keep the translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    filtered_lines = []
    for line in lines:
        # Skip lines that are fuzzy markers
        if line.strip().startswith('#,') and 'fuzzy' in line:
            continue
        filtered_lines.append(line)

    with open(po_path, 'w', encoding='utf-8') as f:
        f.writelines(filtered_lines)

    print(f"✓ Removed fuzzy flags from {po_path}")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    remove_fuzzy_flags(po_file)
