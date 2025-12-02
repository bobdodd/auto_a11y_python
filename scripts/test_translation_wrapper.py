#!/usr/bin/env python3
"""
Test script to verify the translation wrapper works correctly.

This script tests:
1. The wrapper module can be imported
2. get_detailed_issue_description() returns descriptions
3. Placeholder conversion works
4. Translation infrastructure is functioning
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_wrapper_import():
    """Test that the wrapper module can be imported"""
    print("Testing wrapper import...")
    try:
        from auto_a11y.reporting.issue_descriptions_translated import (
            get_detailed_issue_description,
            convert_placeholders,
            ImpactScale
        )
        print("✓ Wrapper module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import wrapper: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality of the wrapper"""
    print("\nTesting basic functionality...")
    try:
        from auto_a11y.reporting.issue_descriptions_translated import get_detailed_issue_description

        # Test with a simple issue code
        desc = get_detailed_issue_description('ErrNoAlt')

        if not desc:
            print("✗ No description returned")
            return False

        print(f"✓ Got description for ErrNoAlt")
        print(f"  Title: {desc.get('title', 'N/A')[:80]}...")
        print(f"  Fields: {list(desc.keys())}")

        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_placeholder_conversion():
    """Test placeholder conversion"""
    print("\nTesting placeholder conversion...")
    try:
        from auto_a11y.reporting.issue_descriptions_translated import convert_placeholders

        test_cases = [
            ("{variable}", "%(variable)s"),
            ("{element_text}", "%(element_text)s"),
            ("{element.tag}", "%(element_tag)s"),
            ("Text with {var} and {other.attr}", "Text with %(var)s and %(other_attr)s"),
            ("No placeholders", "No placeholders"),
        ]

        all_passed = True
        for input_text, expected in test_cases:
            result = convert_placeholders(input_text)
            if result == expected:
                print(f"✓ '{input_text}' -> '{result}'")
            else:
                print(f"✗ '{input_text}' -> '{result}' (expected '{expected}')")
                all_passed = False

        return all_passed
    except Exception as e:
        print(f"✗ Placeholder conversion test failed: {e}")
        return False


def test_with_metadata():
    """Test with metadata (placeholders should be handled by original function)"""
    print("\nTesting with metadata...")
    try:
        from auto_a11y.reporting.issue_descriptions_translated import get_detailed_issue_description

        # Test with issue that has placeholders
        metadata = {
            'element_text': 'Test Image',
            'element_tag': 'img'
        }

        desc = get_detailed_issue_description('ErrNoAlt', metadata)

        if not desc:
            print("✗ No description returned with metadata")
            return False

        print(f"✓ Got description with metadata")
        print(f"  Title: {desc.get('title', 'N/A')}")

        # Check if placeholders were replaced (should be replaced by original function)
        if 'element_text' in desc.get('title', '').lower() or 'element_tag' in desc.get('title', '').lower():
            print("  Note: Title contains metadata keys (placeholders may not be replaced)")

        return True
    except Exception as e:
        print(f"✗ Metadata test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_issues():
    """Test multiple different issue types"""
    print("\nTesting multiple issue types...")
    try:
        from auto_a11y.reporting.issue_descriptions_translated import get_detailed_issue_description

        test_issues = [
            'ErrNoAlt',
            'ErrEmptyHeading',
            'ErrNoLabel',
            'ErrInsufficientContrast',
            'AI_ErrDialogWithoutARIA'
        ]

        all_passed = True
        for issue_code in test_issues:
            desc = get_detailed_issue_description(issue_code)
            if desc and 'title' in desc:
                print(f"✓ {issue_code}: {desc['title'][:60]}...")
            else:
                print(f"✗ {issue_code}: Failed to get description")
                all_passed = False

        return all_passed
    except Exception as e:
        print(f"✗ Multiple issues test failed: {e}")
        return False


def main():
    print("="*60)
    print("Translation Wrapper Test Suite")
    print("="*60)

    tests = [
        test_wrapper_import,
        test_basic_functionality,
        test_placeholder_conversion,
        test_with_metadata,
        test_multiple_issues,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "="*60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*60)

    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
