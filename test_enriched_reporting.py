#!/usr/bin/env python3
"""
Test script to demonstrate the enriched reporting with issue catalog
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly from the generated module
from auto_a11y.reporting.issue_catalog import IssueCatalog


def test_issue_catalog():
    """Test the issue catalog functionality"""
    
    print("=" * 80)
    print("ACCESSIBILITY ISSUE CATALOG TEST")
    print("=" * 80)
    
    # Test getting a specific issue
    test_issues = [
        'ErrImageWithNoAlt',
        'ErrUnlabelledField',
        'ErrNoMainLandmarkOnPage',
        'ErrTextContrast',
        'ErrPositiveTabIndex'
    ]
    
    print("\n1. TESTING SPECIFIC ISSUES:")
    print("-" * 40)
    
    for issue_id in test_issues:
        issue = IssueCatalog.get_issue(issue_id)
        print(f"\n{issue_id}:")
        print(f"  Type: {issue['type']}")
        print(f"  Impact: {issue['impact']}")
        print(f"  Category: {issue['category']}")
        print(f"  WCAG: {', '.join(issue['wcag'])}")
        print(f"  Description: {issue['description'][:100]}...")
    
    # Test enriching a basic issue
    print("\n\n2. TESTING ISSUE ENRICHMENT:")
    print("-" * 40)
    
    # Simulate a basic issue from test results
    basic_issue = {
        'id': 'ErrEmptyHeading',
        'xpath': '/html/body/h2[3]',
        'element': '<h2></h2>',
        'count': 1
    }
    
    print(f"\nBefore enrichment: {basic_issue}")
    
    enriched = IssueCatalog.enrich_issue(basic_issue)
    
    print(f"\nAfter enrichment:")
    print(f"  Description: {enriched['description_full'][:100]}...")
    print(f"  Why it matters: {enriched['why_it_matters'][:100]}...")
    print(f"  Who it affects: {enriched['who_it_affects'][:100]}...")
    print(f"  How to fix: {enriched['how_to_fix'][:100]}...")
    
    # Test getting issues by category
    print("\n\n3. TESTING CATEGORY FILTERING:")
    print("-" * 40)
    
    categories = ['images', 'forms', 'headings', 'landmarks']
    
    for category in categories:
        issues = IssueCatalog.get_issues_by_category(category)
        print(f"\n{category.upper()}: {len(issues)} issues")
        # Show first 3 issues in each category
        for issue in issues[:3]:
            print(f"  - {issue['id']}: {issue['description'][:50]}...")
    
    # Test getting issues by impact level
    print("\n\n4. TESTING IMPACT LEVEL FILTERING:")
    print("-" * 40)
    
    for impact in ['High', 'Medium', 'Low']:
        issues = IssueCatalog.get_issues_by_impact(impact)
        print(f"\n{impact} Impact: {len(issues)} issues")
    
    # Test handling unknown issue
    print("\n\n5. TESTING UNKNOWN ISSUE HANDLING:")
    print("-" * 40)
    
    unknown_issue = IssueCatalog.get_issue('UnknownIssueCode')
    print(f"\nUnknown issue fallback:")
    print(f"  ID: {unknown_issue['id']}")
    print(f"  Description: {unknown_issue['description']}")
    print(f"  Why it matters: {unknown_issue['why_it_matters'][:100]}...")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


def demonstrate_report_enrichment():
    """Demonstrate how reports are enriched with catalog data"""
    
    print("\n\n" + "=" * 80)
    print("REPORT ENRICHMENT DEMONSTRATION")
    print("=" * 80)
    
    # Simulate test results
    mock_violations = [
        {
            'id': 'ErrImageWithNoAlt',
            'count': 5,
            'elements': ['img1.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg', 'img5.jpg']
        },
        {
            'id': 'ErrHeadingLevelsSkipped',
            'count': 2,
            'elements': ['h1 -> h3', 'h2 -> h4']
        },
        {
            'id': 'ErrTextContrast',
            'count': 8,
            'elements': ['paragraph text', 'button text', 'link text']
        }
    ]
    
    print("\nOriginal violations (basic data):")
    for v in mock_violations:
        print(f"  - {v['id']}: {v['count']} instances")
    
    print("\n" + "-" * 40)
    print("Enriched violations (with full descriptions):\n")
    
    for violation in mock_violations:
        enriched = IssueCatalog.enrich_issue(violation)
        print(f"Issue: {enriched['id']}")
        print(f"Count: {enriched['count']} instances")
        print(f"Impact: {enriched['impact']}")
        print(f"WCAG: {enriched['wcag_full']}")
        print(f"\nWhat's wrong:")
        print(f"  {enriched['description_full']}")
        print(f"\nWhy this matters:")
        print(f"  {enriched['why_it_matters']}")
        print(f"\nWho is affected:")
        print(f"  {enriched['who_it_affects']}")
        print(f"\nHow to fix it:")
        print(f"  {enriched['how_to_fix']}")
        print("\n" + "=" * 80 + "\n")
    
    print("This enriched data is now included in all generated reports!")
    print("Developers get comprehensive guidance for fixing each issue.")


if __name__ == "__main__":
    # Run tests
    test_issue_catalog()
    demonstrate_report_enrichment()