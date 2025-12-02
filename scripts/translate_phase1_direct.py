#!/usr/bin/env python3
"""
Direct translation script for Phase 1 accessibility strings.

This script will be executed by Claude Code which will provide the translations
directly rather than calling an external API.
"""

import json
import sys
from pathlib import Path

def main():
    # Load template
    template_file = 'phase1_translation_template.json'
    if not Path(template_file).exists():
        print(f"Error: {template_file} not found", file=sys.stderr)
        return 1

    with open(template_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entries = data['entries']

    print(f"Loaded {len(entries)} entries to translate")
    print(f"\nBreakdown by category:")
    for category, count in data['metadata']['by_category'].items():
        print(f"  {category}: {count} strings")

    print(f"\n{'='*60}")
    print("Ready for translation")
    print(f"{'='*60}")
    print("\nThis script will output entries in a format for translation.")
    print("Output will be saved to: phase1_for_translation.json")

    # Save in a format that's easy to process
    output_file = 'phase1_for_translation.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {output_file}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
