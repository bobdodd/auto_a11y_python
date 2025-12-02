#!/usr/bin/env python3
"""
Fix incorrect translation for 'to get started.' in recordings list
"""

def fix_translation(po_path):
    """Fix the incorrect translation"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the incorrect translation
    old_entry = 'msgid "to get started."\nmsgstr "Testées"'
    new_entry = 'msgid "to get started."\nmsgstr "pour commencer."'

    if old_entry in content:
        content = content.replace(old_entry, new_entry)
        print("✓ Fixed: 'to get started.' → 'pour commencer.'")
    else:
        print("✗ Entry not found or already fixed")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    fix_translation(po_file)
