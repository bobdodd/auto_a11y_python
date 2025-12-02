#!/usr/bin/env python3
"""
AI translation for Phase 5: Errors: Other (151 strings)
Uses the same successful approach with JSON Schema.
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import List, Dict

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed", file=sys.stderr)
    print("Install with: pip install anthropic", file=sys.stderr)
    sys.exit(1)

# JSON Schema for the translation response
TRANSLATION_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "translations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "translation": {"type": "string"}
                },
                "required": ["index", "translation"]
            }
        }
    },
    "required": ["translations"]
}

TRANSLATION_PROMPT_TEMPLATE = """You are translating accessibility issue descriptions from English to French for a web accessibility testing tool.

**Critical Requirements:**
1. PRESERVE ALL PLACEHOLDERS EXACTLY: Any text in %(variable)s format MUST remain unchanged
2. Use W3C WCAG 2.2 official French terminology for accessibility terms
3. Maintain professional, technical tone appropriate for accessibility professionals
4. Keep translations concise and clear

**Key terminology to use:**
- screen reader users → utilisateurs de lecteurs d'écran
- keyboard users → utilisateurs de clavier
- blind users → utilisateurs aveugles
- low vision users → utilisateurs malvoyants
- landmark/landmark region → région repère
- banner landmark → région repère bannière
- contentinfo landmark → région repère contentinfo
- main landmark → région repère principale
- navigation landmark → région repère navigation
- complementary landmark → région repère complémentaire
- region → région
- accessible name → nom accessible
- aria-label → aria-label
- aria-labelledby → aria-labelledby
- nested → imbriqué
- parent landmark → région repère parente
- child → enfant
- empty → vide
- duplicate → dupliqué
- multiple → multiple

**Category Context:** Errors: Other - ARIA landmark regions that help users navigate page structure

**Translate these {count} accessibility messages to French:**

{entries}

**IMPORTANT:** Return a JSON object with a "translations" array containing objects with "index" and "translation" fields.

Ensure ALL placeholders in %(variable)s format are preserved exactly!
"""


def create_batch_prompt(entries: List[Dict], category: str) -> str:
    """Create translation prompt for a batch of entries"""
    entries_text = []
    for i, entry in enumerate(entries):
        entries_text.append(f"[{i}] {entry['msgid']}")

    return TRANSLATION_PROMPT_TEMPLATE.format(
        category=category,
        count=len(entries),
        entries='\n\n'.join(entries_text)
    )


def validate_translation(original: str, translation: str) -> tuple[bool, str]:
    """Validate that placeholders are preserved"""
    # Extract placeholders
    orig_placeholders = set(re.findall(r'%\([a-zA-Z_][a-zA-Z0-9_]*\)s', original))
    trans_placeholders = set(re.findall(r'%\([a-zA-Z_][a-zA-Z0-9_]*\)s', translation))

    if orig_placeholders != trans_placeholders:
        return False, f"Placeholders mismatch: {orig_placeholders} vs {trans_placeholders}"

    return True, "OK"


def translate_batch(client: anthropic.Anthropic, entries: List[Dict], category: str) -> List[Dict]:
    """Translate a batch of entries using Claude API with tool calling for structured output"""
    prompt = create_batch_prompt(entries, category)

    try:
        # Define the translation tool
        tools = [{
            "name": "provide_translations",
            "description": "Provide the translated strings in a structured format",
            "input_schema": TRANSLATION_RESPONSE_SCHEMA
        }]

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            tools=tools,
            tool_choice={"type": "tool", "name": "provide_translations"}
        )

        # Extract tool use from response
        tool_use = next((block for block in message.content if block.type == "tool_use"), None)
        if not tool_use:
            raise ValueError("No tool use found in response")

        response_data = tool_use.input
        translations = response_data['translations']

        # Validate and match translations to entries
        results = []
        for trans in translations:
            idx = trans['index']
            translation = trans['translation']
            entry = entries[idx].copy()

            # Validate placeholders
            is_valid, msg = validate_translation(entry['msgid'], translation)
            if not is_valid:
                print(f"  ⚠ Warning: {entry['issue_code']}.{entry['field']}: {msg}", file=sys.stderr)
                # Keep original if validation fails
                entry['msgstr'] = entry['msgid']
                entry['validation_failed'] = True
            else:
                entry['msgstr'] = translation
                entry['validation_failed'] = False

            results.append(entry)

        return results

    except Exception as e:
        print(f"  ✗ Error translating batch: {e}", file=sys.stderr)
        # Return entries with original text if translation fails
        for entry in entries:
            entry['msgstr'] = entry['msgid']
            entry['translation_failed'] = True
        return entries


def main():
    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('CLAUDE_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY or CLAUDE_API_KEY environment variable not set", file=sys.stderr)
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'", file=sys.stderr)
        return 1

    # Load template
    template_file = 'phase5_translation_template.json'
    if not Path(template_file).exists():
        print(f"Error: {template_file} not found", file=sys.stderr)
        return 1

    with open(template_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entries = data['entries']
    print(f"Loaded {len(entries)} entries to translate")

    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Process in batches
    batch_size = 15
    all_translated = []

    print(f"\nTranslating {len(entries)} strings in batches of {batch_size}...")
    print("=" * 60)

    total_batches = (len(entries) + batch_size - 1) // batch_size

    for i in range(0, len(entries), batch_size):
        batch = entries[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        print(f"Batch {batch_num}/{total_batches} ({len(batch)} strings)...", end=' ', flush=True)

        translated = translate_batch(client, batch, 'Errors: Other')
        all_translated.extend(translated)

        # Count successes/failures
        success = sum(1 for e in translated if not e.get('validation_failed') and not e.get('translation_failed'))
        print(f"✓ {success}/{len(batch)} OK")

    # Save results
    output_file = 'phase5_translated.json'
    output_data = {
        'metadata': {
            'phase': 4,
            'name': 'Errors: Other',
            'total_entries': len(all_translated),
            'translated': sum(1 for e in all_translated if e.get('msgstr') and e['msgstr'] != e['msgid']),
            'failed': sum(1 for e in all_translated if e.get('translation_failed', False)),
            'validation_warnings': sum(1 for e in all_translated if e.get('validation_failed', False))
        },
        'entries': all_translated
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Translation Complete!")
    print(f"{'=' * 60}")
    print(f"Total entries: {output_data['metadata']['total_entries']}")
    print(f"Translated: {output_data['metadata']['translated']}")
    print(f"Failed: {output_data['metadata']['failed']}")
    print(f"Warnings: {output_data['metadata']['validation_warnings']}")
    print(f"\nSaved to: {output_file}")
    print(f"\nNext: python scripts/import_translations.py {output_file}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
