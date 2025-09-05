#!/usr/bin/env python3
"""
Simple test to verify metadata replacement works
"""

import importlib.util

# Load the enhanced descriptions module directly
spec = importlib.util.spec_from_file_location(
    'issue_descriptions_enhanced', 
    '/Users/bob3/Desktop/auto_a11y_python/auto_a11y/reporting/issue_descriptions_enhanced.py'
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

print("=" * 60)
print("Testing Metadata Replacement in Enhanced Descriptions")
print("=" * 60)

test_cases = [
    {
        'name': 'Color Contrast',
        'issue_id': 'color_ErrTextContrast',
        'metadata': {
            'err': 'ErrTextContrast',
            'fg': '#777777',
            'bg': '#ffffff',
            'ratio': '3.5'
        },
        'expected': 'Text has insufficient contrast ratio of 3.5:1 (foreground: #777777, background: #ffffff)'
    },
    {
        'name': 'Font Detection',
        'issue_id': 'fonts_DiscoFontFound',
        'metadata': {'found': 'Arial, Helvetica, sans-serif'},
        'expected': "Font 'Arial, Helvetica, sans-serif' detected"
    },
    {
        'name': 'Heading Level Skip',
        'issue_id': 'headings_ErrSkippedHeadingLevel',
        'metadata': {'skippedFrom': '2', 'skippedTo': '4'},
        'expected': 'jumped from h2 to h4'
    },
    {
        'name': 'Large Text Contrast',
        'issue_id': 'color_ErrLargeTextContrast',
        'metadata': {
            'ratio': '2.8',
            'fg': '#888888',
            'bg': '#f0f0f0'
        },
        'expected': 'Large text has insufficient contrast ratio of 2.8:1'
    }
]

all_passed = True
for test_case in test_cases:
    print(f"\n{test_case['name']}:")
    print("-" * 40)
    result = module.get_detailed_issue_description(test_case['issue_id'], test_case['metadata'])
    what_text = result.get('what', '')
    
    # Check if expected text is in the result
    if test_case['expected'] in what_text:
        print(f"✓ PASS: {what_text}")
    else:
        print(f"✗ FAIL: Expected '{test_case['expected']}' in output")
        print(f"  Got: {what_text}")
        all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("✓ SUCCESS: All metadata replacements working correctly!")
    print("\nThe fix has been applied successfully. The enhanced descriptions")
    print("with metadata placeholders are now properly replacing values with")
    print("actual data from the JavaScript tests.")
    print("\nKey changes made:")
    print("1. Added metadata placeholders to ISSUE_CATALOG_TEMPLATE.md")
    print("2. Implemented replacement logic in generate_issue_catalog.py")
    print("3. Result processor stores enhanced descriptions with replaced values")
    print("4. Pages.py now preserves metadata instead of overwriting it")
else:
    print("✗ Some tests failed. Check the output above.")
print("=" * 60)