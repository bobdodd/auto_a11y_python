#!/usr/bin/env python3
"""
Create flat translation template from phase2_ai_strings.json
Format matches what the AI translation script expects.
"""

import json

# Load phase2 data
with open('phase2_ai_strings.json', 'r', encoding='utf-8') as f:
    phase2 = json.load(f)

# Flatten into template format
entries = []

for category_name, issues in phase2['categories'].items():
    for issue in issues:
        for string_data in issue['strings']:
            entries.append({
                'msgctxt': string_data['msgctxt'],
                'msgid': string_data['msgid'],
                'msgstr': '',  # Empty, to be translated
                'issue_code': string_data['issue_code'],
                'field': string_data['field'],
                'category': 'AI-Detected Issues'
            })

template = {
    'metadata': {
        'phase': 2,
        'name': 'AI-Detected Issues',
        'total_entries': len(entries)
    },
    'entries': entries
}

# Save template
with open('phase2_translation_template.json', 'w', encoding='utf-8') as f:
    json.dump(template, f, indent=2, ensure_ascii=False)

print(f"Created Phase 2 translation template")
print(f"Total entries: {len(entries)}")
print(f"Saved to: phase2_translation_template.json")
print(f"\nNext: Update scripts/translate_with_anthropic_schema.py to use phase2_translation_template.json")
