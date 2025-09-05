#!/usr/bin/env python3
"""
Test the new pass tracking and applicability features
"""

import json
from auto_a11y.testing.result_processor import ResultProcessor

def test_applicability_scoring():
    """Test the new applicability-aware scoring"""
    
    processor = ResultProcessor()
    
    # Simulate test results with applicability
    raw_results = {
        'forms2': {
            'test_name': 'forms2',
            'applicable': True,
            'elements_found': 10,
            'elements_tested': 10,
            'elements_passed': 8,
            'elements_failed': 2,
            'errors': [
                {
                    'err': 'ErrUnlabelledField',
                    'cat': 'form',
                    'xpath': '//input[@id="email"]'
                },
                {
                    'err': 'ErrUnlabelledField', 
                    'cat': 'form',
                    'xpath': '//input[@id="phone"]'
                }
            ],
            'passes': [
                {'check': 'field_has_label', 'element': 'INPUT', 'xpath': '//input[@id="name"]'},
                {'check': 'field_has_label', 'element': 'INPUT', 'xpath': '//input[@id="address"]'},
                # ... 6 more passes
            ],
            'checks': [
                {
                    'id': 'form_labels',
                    'description': 'All form inputs have labels',
                    'wcag': ['1.3.1', '3.3.2'],
                    'applicable': True,
                    'total': 10,
                    'passed': 8,
                    'failed': 2
                }
            ]
        },
        'images': {
            'test_name': 'images',
            'applicable': False,
            'not_applicable_reason': 'No images found on page',
            'elements_found': 0,
            'elements_tested': 0,
            'elements_passed': 0,
            'elements_failed': 0,
            'errors': [],
            'passes': [],
            'checks': []
        },
        'headings': {
            'test_name': 'headings',
            'applicable': True,
            'elements_found': 5,
            'elements_tested': 5,
            'elements_passed': 5,
            'elements_failed': 0,
            'errors': [],
            'passes': [
                {'check': 'heading_hierarchy', 'element': 'H1', 'xpath': '//h1[1]'},
                {'check': 'heading_hierarchy', 'element': 'H2', 'xpath': '//h2[1]'},
                {'check': 'heading_hierarchy', 'element': 'H2', 'xpath': '//h2[2]'},
                {'check': 'heading_hierarchy', 'element': 'H3', 'xpath': '//h3[1]'},
                {'check': 'heading_hierarchy', 'element': 'H3', 'xpath': '//h3[2]'},
            ],
            'checks': [
                {
                    'id': 'heading_hierarchy',
                    'description': 'Headings follow proper hierarchy',
                    'wcag': ['1.3.1'],
                    'applicable': True,
                    'total': 5,
                    'passed': 5,
                    'failed': 0
                }
            ]
        }
    }
    
    # Process the results
    test_result = processor.process_test_results(
        page_id='test-page-1',
        raw_results=raw_results,
        duration_ms=1500
    )
    
    # Calculate score
    score_data = processor.calculate_score(test_result)
    
    print("Test Results Processing Complete")
    print("================================")
    print(f"Method: {score_data.get('method', 'unknown')}")
    print(f"Score: {score_data['score']}%")
    print(f"Grade: {score_data['grade']}")
    print(f"Reason: {score_data.get('reason', 'N/A')}")
    print()
    print("Applicability Stats:")
    print(f"  Applicable checks: {score_data.get('applicable_checks', 0)}")
    print(f"  Passed checks: {score_data.get('passed_checks', 0)}")
    print(f"  Failed checks: {score_data.get('failed_checks', 0)}")
    print(f"  Not applicable tests: {score_data.get('not_applicable_count', 0)}")
    print()
    print("Issue Summary:")
    print(f"  High severity: {score_data['high_issues']}")
    print(f"  Medium severity: {score_data['medium_issues']}")
    print(f"  Low severity: {score_data.get('low_issues', 0)}")
    print(f"  Total issues: {score_data['total_issues']}")
    print()
    
    # Show not applicable tests
    if score_data.get('not_applicable_tests'):
        print("Not Applicable Tests:")
        for na_test in score_data['not_applicable_tests']:
            print(f"  - {na_test['test_name']}: {na_test['reason']}")
    
    # Validate the calculation
    expected_score = (13 / 15) * 100  # 13 passed out of 15 total
    print(f"\nValidation: Expected score ~{expected_score:.1f}%, Got {score_data['score']}%")
    
    # Show metadata checks
    if test_result.metadata.get('checks'):
        print("\nDetailed Check Results:")
        for check in test_result.metadata['checks']:
            print(f"  {check['test_name']}.{check['id']}:")
            print(f"    Description: {check['description']}")
            print(f"    Results: {check['passed']}/{check['total']} passed")
            print(f"    WCAG: {', '.join(check['wcag'])}")

if __name__ == '__main__':
    test_applicability_scoring()