#!/usr/bin/env python3
"""
Test the analytics fix directly
"""

from collections import defaultdict, Counter

# Simulate the fixed analytics code
def test_analytics():
    # Simulate test data - multiple occurrences of same issue on one page
    all_issues = [
        ('error', type('Issue', (), {'id': 'fonts_WarnFontNotInRecommenedListForA11y', 'impact': type('Impact', (), {'value': 'medium'}), 'wcag_criteria': ['1.3.1'], 'category': 'fonts'})(), 'https://example.com/page1'),
        ('error', type('Issue', (), {'id': 'fonts_WarnFontNotInRecommenedListForA11y', 'impact': type('Impact', (), {'value': 'medium'}), 'wcag_criteria': ['1.3.1'], 'category': 'fonts'})(), 'https://example.com/page1'),
        ('error', type('Issue', (), {'id': 'fonts_WarnFontNotInRecommenedListForA11y', 'impact': type('Impact', (), {'value': 'medium'}), 'wcag_criteria': ['1.3.1'], 'category': 'fonts'})(), 'https://example.com/page1'),
        ('error', type('Issue', (), {'id': 'landmarks_ErrElementNotContainedInALandmark', 'impact': type('Impact', (), {'value': 'medium'}), 'wcag_criteria': ['1.3.1'], 'category': 'landmarks'})(), 'https://example.com/page1'),
        ('error', type('Issue', (), {'id': 'landmarks_ErrElementNotContainedInALandmark', 'impact': type('Impact', (), {'value': 'medium'}), 'wcag_criteria': ['1.3.1'], 'category': 'landmarks'})(), 'https://example.com/page1'),
    ]
    
    # OLD CODE (wrong - counts occurrences)
    print("OLD APPROACH (Wrong):")
    print("-" * 50)
    issue_frequency_old = Counter()
    for issue_type, issue, page in all_issues:
        if hasattr(issue, 'id'):
            issue_frequency_old[issue.id] += 1
    
    for issue_id, count in issue_frequency_old.most_common():
        print(f"  {issue_id}:")
        print(f"    Occurrences: {count}")
        print(f"    Affected Pages: {count} (WRONG - this is counting occurrences, not unique pages!)")
    
    # NEW CODE (correct - tracks unique pages)
    print("\nNEW APPROACH (Correct):")
    print("-" * 50)
    issue_frequency = Counter()
    issue_pages = defaultdict(set)  # Track unique pages per issue
    issue_details = {}  # Store issue details
    
    for issue_type, issue, page in all_issues:
        if hasattr(issue, 'id'):
            issue_frequency[issue.id] += 1
            issue_pages[issue.id].add(page)  # Add page to set (duplicates automatically ignored)
            
            # Store issue details if we haven't seen this issue before
            if issue.id not in issue_details:
                issue_details[issue.id] = {
                    'description': getattr(issue, 'description', ''),
                    'impact': getattr(issue, 'impact', 'unknown'),
                    'wcag_criteria': getattr(issue, 'wcag_criteria', []),
                    'category': getattr(issue, 'category', 'general')
                }
    
    for issue_id, count in issue_frequency.most_common():
        unique_pages = len(issue_pages.get(issue_id, set()))
        print(f"  {issue_id}:")
        print(f"    Occurrences: {count}")
        print(f"    Affected Pages: {unique_pages} (CORRECT - counting unique pages)")
        print(f"    Pages: {list(issue_pages[issue_id])}")
    
    print("\nFIX SUMMARY:")
    print("-" * 50)
    print("✓ The old code was counting issue occurrences as 'Affected Pages'")
    print("✓ The new code correctly tracks unique pages using a set")
    print("✓ In this example: 5 occurrences across 1 unique page")

if __name__ == "__main__":
    test_analytics()