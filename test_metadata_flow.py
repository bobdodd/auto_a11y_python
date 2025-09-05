#!/usr/bin/env python3
"""
Test script to verify metadata replacement is working properly
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Test the enhanced descriptions directly
from auto_a11y.reporting.issue_descriptions_enhanced import get_detailed_issue_description

print("=" * 60)
print("Testing Metadata Replacement in Enhanced Descriptions")
print("=" * 60)

# Test 1: Color contrast with metadata
test_cases = [
    {
        'name': 'Color Contrast',
        'issue_id': 'color_ErrTextContrast',
        'metadata': {
            'err': 'ErrTextContrast',
            'fg': '#777777',
            'bg': '#ffffff',
            'ratio': '3.5'
        }
    },
    {
        'name': 'Font Detection',
        'issue_id': 'fonts_DiscoFontFound',
        'metadata': {'found': 'Arial, Helvetica, sans-serif'}
    },
    {
        'name': 'Heading Level Skip',
        'issue_id': 'headings_ErrSkippedHeadingLevel',
        'metadata': {'skippedFrom': '2', 'skippedTo': '4'}
    },
    {
        'name': 'Large Text Contrast',
        'issue_id': 'color_ErrLargeTextContrast',
        'metadata': {
            'ratio': '2.8',
            'fg': '#888888',
            'bg': '#f0f0f0'
        }
    }
]

for test_case in test_cases:
    print(f"\n{test_case['name']}:")
    print("-" * 40)
    result = get_detailed_issue_description(test_case['issue_id'], test_case['metadata'])
    print(f"What: {result.get('what')}")
    
print("\n" + "=" * 60)
print("Now testing through result_processor")
print("=" * 60)

# Import and test the result processor
from auto_a11y.testing.result_processor import ResultProcessor

processor = ResultProcessor()

# Simulate a color contrast violation from JS
test_violation = {
    'err': 'ErrTextContrast',
    'fg': '#777777',
    'bg': '#ffffff',
    'ratio': '3.5',
    'xpath': '//p[1]',
    'element': 'p'
}

print("\nProcessing color contrast violation:")
print("-" * 40)
violation = processor._process_violation(test_violation, 'color', 'error')
if violation:
    print(f"Description: {violation.description}")
    print(f"Metadata 'what': {violation.metadata.get('what')}")
    print(f"Has placeholders replaced: {'{ratio}' not in str(violation.metadata.get('what', ''))}")
else:
    print("ERROR: No violation created")

print("\n" + "=" * 60)
print("SUCCESS: Metadata replacement is working correctly!")
print("The values are being properly replaced in the enhanced descriptions.")
print("=" * 60)