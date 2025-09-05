# WCAG AA/AAA Contrast Testing Separation - Summary

## Overview
Implemented separate error codes and descriptions for WCAG Level AA and Level AAA contrast failures, ensuring accurate reporting of which standard was tested and which Success Criterion applies.

## Changes Made

### 1. New Error Codes Created

#### Level AA Error Codes
- **ErrTextContrastAA** - Normal text fails WCAG Level AA (SC 1.4.3)
- **ErrLargeTextContrastAA** - Large text fails WCAG Level AA (SC 1.4.3)

#### Level AAA Error Codes  
- **ErrTextContrastAAA** - Normal text fails WCAG Level AAA (SC 1.4.6)
- **ErrLargeTextContrastAAA** - Large text fails WCAG Level AAA (SC 1.4.6)

### 2. WCAG Success Criteria

#### SC 1.4.3 Contrast (Minimum) - Level AA
- Normal text: 4.5:1 minimum contrast ratio
- Large text: 3:1 minimum contrast ratio
- Used by: ErrTextContrastAA, ErrLargeTextContrastAA

#### SC 1.4.6 Contrast (Enhanced) - Level AAA
- Normal text: 7:1 minimum contrast ratio
- Large text: 4.5:1 minimum contrast ratio
- Used by: ErrTextContrastAAA, ErrLargeTextContrastAAA

### 3. JavaScript Updates
**File:** `/auto_a11y/scripts/tests/color.js`

The code now:
1. Checks the project's WCAG level (from `window.WCAG_LEVEL`)
2. Determines if text is normal or large
3. Selects the appropriate error code based on level and text size
4. Reports the specific error with correct WCAG reference

### 4. Issue Descriptions
**File:** `/ISSUE_CATALOG_TEMPLATE.md`

Each error code has its own description that:
- Specifies which WCAG level was tested (AA or AAA)
- References the correct Success Criterion (1.4.3 or 1.4.6)
- States the exact contrast requirement for that level
- Provides level-appropriate remediation advice

## Testing Scenarios

### Example 1: Text with 4.69:1 Contrast Ratio

#### When Project Tests for Level AA:
- Normal text (14px): **PASSES** (needs 4.5:1)
- Large text (24px): **PASSES** (needs 3:1)

#### When Project Tests for Level AAA:
- Normal text (14px): **FAILS** with `ErrTextContrastAAA` (needs 7:1)
- Large text (24px): **PASSES** (needs 4.5:1)

### Example 2: Text with 3.5:1 Contrast Ratio

#### When Project Tests for Level AA:
- Normal text (14px): **FAILS** with `ErrTextContrastAA` (needs 4.5:1)
- Large text (24px): **PASSES** (needs 3:1)

#### When Project Tests for Level AAA:
- Normal text (14px): **FAILS** with `ErrTextContrastAAA` (needs 7:1)
- Large text (24px): **FAILS** with `ErrLargeTextContrastAAA` (needs 4.5:1)

## Benefits

1. **Accuracy**: Reports correctly indicate which WCAG level was tested
2. **Clarity**: Error messages reference the correct Success Criterion
3. **Compliance**: Organizations can accurately assess their compliance level
4. **Actionable**: Developers know exactly what threshold they need to meet

## Test File
Created `test_aa_aaa_contrast.html` to verify the implementation with various contrast scenarios.

## Summary
The tool now properly distinguishes between AA and AAA compliance testing, using the correct error codes and WCAG Success Criteria references based on the project's specified compliance level. This ensures accurate, standard-compliant accessibility testing and reporting.