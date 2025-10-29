#!/usr/bin/env python3
"""
Quick script to check if ErrButtonTextLowContrast is in the IssueCatalog
"""

import sys

# Force module reload
if 'auto_a11y.reporting.issue_catalog' in sys.modules:
    del sys.modules['auto_a11y.reporting.issue_catalog']

from auto_a11y.reporting.issue_catalog import IssueCatalog

# Check if it exists
if 'ErrButtonTextLowContrast' in IssueCatalog.ISSUES:
    print("❌ ERROR: ErrButtonTextLowContrast IS STILL IN IssueCatalog.ISSUES!")
    print(f"   Value: {IssueCatalog.ISSUES['ErrButtonTextLowContrast']}")
    sys.exit(1)
else:
    print("✓ SUCCESS: ErrButtonTextLowContrast is NOT in IssueCatalog.ISSUES")

# List all button-related tests
button_tests = [k for k in IssueCatalog.ISSUES.keys() if 'Button' in k]
print(f"\nButton tests found ({len(button_tests)}):")
for test in sorted(button_tests):
    print(f"  - {test}")

sys.exit(0)
