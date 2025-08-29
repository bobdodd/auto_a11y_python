#!/usr/bin/env python3
"""
Test to demonstrate Info and Discovery are not counted as violations
"""

def test_violation_counting():
    """Demonstrate the correct counting of violations vs info/discovery"""
    
    # Simulate test results
    test_results = {
        'error': 30,      # Actual violations
        'warning': 30,    # Actual violations
        'info': 55,       # NOT violations - informational only
        'discovery': 61   # NOT violations - areas for manual review
    }
    
    print("UNDERSTANDING ACCESSIBILITY TEST RESULTS")
    print("=" * 60)
    print("\n📊 Test Result Categories:")
    print("-" * 60)
    
    # OLD (WRONG) approach - counting everything as violations
    print("\n❌ OLD APPROACH (Incorrect):")
    total_issues_wrong = sum(test_results.values())
    print(f"  Total 'Violations': {total_issues_wrong}")
    print(f"  Compliance Score: {0 / total_issues_wrong * 100:.1f}%")
    print("  Problem: This counts INFO and DISCOVERY as violations!")
    
    # NEW (CORRECT) approach - only errors + warnings are violations
    print("\n✅ NEW APPROACH (Correct):")
    actual_violations = test_results['error'] + test_results['warning']
    info_items = test_results['info']
    discovery_items = test_results['discovery']
    
    print(f"  Accessibility Violations: {actual_violations} (errors + warnings only)")
    print(f"  Info Items: {info_items} (non-violations, for awareness)")
    print(f"  Discovery Items: {discovery_items} (areas needing manual review)")
    print(f"  Compliance Score: Based on {actual_violations} violations only")
    
    print("\n📋 DETAILED BREAKDOWN:")
    print("-" * 60)
    
    print("\n🔴 VIOLATIONS (Count toward compliance):")
    print(f"  • Errors: {test_results['error']} - WCAG failures that must be fixed")
    print(f"  • Warnings: {test_results['warning']} - Potential issues to address")
    print(f"  Total Violations: {actual_violations}")
    
    print("\n🔵 INFO (Do NOT count as violations):")
    print(f"  • Count: {info_items}")
    print("  • Purpose: General reporting of non-violating items")
    print("  • Examples:")
    print("    - Reporting that alt text exists (good!)")
    print("    - Noting the presence of ARIA labels")
    print("    - Confirming proper heading structure")
    
    print("\n🟣 DISCOVERY (Do NOT count as violations):")
    print(f"  • Count: {discovery_items}")
    print("  • Purpose: Guide manual testing efforts")
    print("  • Examples:")
    print("    - Forms detected (need interaction testing)")
    print("    - PDF links found (check document accessibility)")
    print("    - Decorative fonts used (review for readability)")
    print("    - Complex widgets (test keyboard navigation)")
    print("    - Video content (verify captions)")
    
    print("\n💡 KEY INSIGHT:")
    print("-" * 60)
    print("Only ERRORS and WARNINGS are accessibility violations.")
    print("INFO and DISCOVERY items are helpful insights but NOT violations.")
    print(f"\nYour actual violation count: {actual_violations} (not {total_issues_wrong})")
    print(f"Difference: {total_issues_wrong - actual_violations} items incorrectly counted before")

if __name__ == "__main__":
    test_violation_counting()