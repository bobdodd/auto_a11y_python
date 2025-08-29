#!/usr/bin/env python3
"""
Test the remediation text improvements
"""

def get_remediation_text_old(issue_id, details):
    """OLD approach - always returns the same text"""
    return "See detailed recommendations"

def get_remediation_text_new(issue_id, details):
    """NEW approach - provides specific remediation text"""
    remediation_map = {
        'fonts_WarnFontNotInRecommenedListForA11y': 'Use standard web fonts',
        'fonts_DiscoFontFound': 'Replace decorative fonts',
        'landmarks_ErrElementNotContainedInALandmark': 'Add proper landmarks',
        'focus_ErrOutlineIsNoneOnInteractiveElement': 'Add visible focus styles',
        'focus_ErrZeroOutlineOffset': 'Adjust outline offset',
        'forms_ErrInputMissingLabel': 'Add form labels',
        'color_ErrContrastRatio': 'Improve color contrast',
        'headings_ErrBrokenHierarchy': 'Fix heading structure',
        'images_ErrImageMissingAlt': 'Add alt text',
        'links_ErrEmptyLink': 'Add link text'
    }
    
    # Check if we have a known remediation
    for key, text in remediation_map.items():
        if key in issue_id:
            return text
    
    # If not, provide generic text based on category
    category = details.get('category', '').lower()
    if 'form' in category:
        return 'Fix form accessibility'
    elif 'color' in category or 'contrast' in category:
        return 'Fix color contrast'
    elif 'landmark' in category:
        return 'Add landmarks'
    elif 'heading' in category:
        return 'Fix heading hierarchy'
    else:
        return 'Review accessibility'

# Test various issue IDs
test_issues = [
    ('fonts_WarnFontNotInRecommenedListForA11y', {'category': 'fonts'}),
    ('landmarks_ErrElementNotContainedInALandmark', {'category': 'landmarks'}),
    ('focus_ErrOutlineIsNoneOnInteractiveElement', {'category': 'focus'}),
    ('forms_ErrInputMissingLabel', {'category': 'forms'}),
    ('color_ErrContrastRatio', {'category': 'color'}),
    ('unknown_issue_id', {'category': 'forms'}),
    ('another_unknown', {'category': 'color'}),
    ('generic_issue', {'category': 'other'})
]

print("OLD APPROACH (Useless):")
print("-" * 70)
print(f"{'Issue ID':<50} | {'Remediation':<20}")
print("-" * 70)
for issue_id, details in test_issues:
    remediation = get_remediation_text_old(issue_id, details)
    print(f"{issue_id[:50]:<50} | {remediation:<20}")

print("\nNEW APPROACH (Helpful):")
print("-" * 70)
print(f"{'Issue ID':<50} | {'Remediation':<20}")
print("-" * 70)
for issue_id, details in test_issues:
    remediation = get_remediation_text_new(issue_id, details)
    print(f"{issue_id[:50]:<50} | {remediation:<20}")

print("\nIMPROVEMENT SUMMARY:")
print("-" * 70)
print("✓ OLD: Always showed 'See detailed recommendations' (not helpful)")
print("✓ NEW: Shows specific, actionable remediation text")
print("✓ NEW: Falls back to category-based suggestions for unknown issues")
print("✓ NEW: Provides immediate value to users in the summary table")