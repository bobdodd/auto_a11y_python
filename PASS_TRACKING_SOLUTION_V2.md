# Solution: Adding Pass Tracking with Applicability Handling

## The Problem with Current Approach
Currently, we only report failures, but we also need to distinguish between:
- ✅ **PASS**: Element was tested and meets accessibility criteria
- ❌ **FAIL**: Element was tested and violates accessibility criteria  
- ➖ **NOT APPLICABLE**: No elements of this type exist to test
- ⏭️ **SKIPPED**: Test was not run for some reason

## Critical Insight: Applicability Matters

A page without forms shouldn't be penalized for "not passing" form tests - those tests simply don't apply. Similarly:
- A page with no images shouldn't fail image alt text tests
- A page with no tables shouldn't fail table accessibility tests
- A page with no videos shouldn't fail caption tests

## Proposed Test Result Structure

```javascript
{
    "test_name": "forms",
    "applicable": true,  // Were there elements to test?
    "elements_found": 5,
    "elements_tested": 5,
    "elements_passed": 3,
    "elements_failed": 2,
    "checks": [
        {
            "id": "form_labels",
            "description": "All form inputs have labels",
            "wcag": ["1.3.1", "3.3.2"],
            "applicable": true,
            "total": 5,
            "passed": 3,
            "failed": 2
        }
    ],
    "errors": [...],
    "passes": [...],
    "not_applicable_reason": null  // or "No form elements found on page"
}
```

## Implementation Examples

### 1. Form Test with Applicability Check

```javascript
function formsScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // First, check if this test is even applicable
    const allForms = document.querySelectorAll('form');
    const allInputs = document.querySelectorAll('input, select, textarea');
    const formElements = document.querySelectorAll('input:not([type="hidden"]), select, textarea');
    
    // If no form elements exist, test is not applicable
    if (formElements.length === 0) {
        return {
            test_name: 'forms',
            applicable: false,
            not_applicable_reason: 'No form elements found on page',
            elements_found: 0,
            elements_tested: 0,
            elements_passed: 0,
            elements_failed: 0,
            errors: [],
            passes: [],
            checks: [{
                id: 'form_labels',
                description: 'All form inputs have labels',
                wcag: ['1.3.1', '3.3.2'],
                applicable: false,
                total: 0,
                passed: 0,
                failed: 0
            }]
        };
    }
    
    // Test IS applicable - check each element
    let labelCheck = {
        id: 'form_labels',
        description: 'All form inputs have labels',
        wcag: ['1.3.1', '3.3.2'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
    
    formElements.forEach(element => {
        labelCheck.total++;
        const hasLabel = hasAssociatedLabel(element);
        const xpath = Elements.DOMPath.xPath(element, true);
        
        if (hasLabel) {
            labelCheck.passed++;
            passList.push({
                check: 'form_label',
                element: element.tagName,
                type: element.type,
                xpath: xpath,
                wcag: ['1.3.1', '3.3.2'],
                reason: 'Form input has associated label'
            });
        } else {
            labelCheck.failed++;
            errorList.push({
                err: 'ErrNoLabel',
                element: element.tagName,
                type: element.type,
                xpath: xpath,
                // ... other error details
            });
        }
    });
    
    checks.push(labelCheck);
    
    return {
        test_name: 'forms',
        applicable: true,
        elements_found: formElements.length,
        elements_tested: formElements.length,
        elements_passed: labelCheck.passed,
        elements_failed: labelCheck.failed,
        errors: errorList,
        passes: passList,
        checks: checks
    };
}
```

### 2. Image Test with Applicability

```javascript
function imagesScrape() {
    const allImages = document.querySelectorAll('img');
    
    // No images? Test not applicable
    if (allImages.length === 0) {
        return {
            test_name: 'images',
            applicable: false,
            not_applicable_reason: 'No images found on page',
            elements_found: 0,
            elements_tested: 0,
            elements_passed: 0,
            elements_failed: 0,
            errors: [],
            passes: [],
            checks: [{
                id: 'image_alt_text',
                description: 'All images have appropriate alt text',
                wcag: ['1.1.1'],
                applicable: false,
                total: 0,
                passed: 0,
                failed: 0
            }]
        };
    }
    
    // Images exist - run tests
    // ... rest of image testing logic
}
```

## Compliance Score Calculation

### Current (Incorrect) Method
```
Total Tests: 50
Failed Tests: 10
Compliance: 80%  // But what if 30 tests weren't applicable?
```

### Proposed (Correct) Method
```python
def calculate_compliance_score(test_results):
    applicable_checks = 0
    passed_checks = 0
    
    for test in test_results:
        if test['applicable']:
            applicable_checks += test['elements_tested']
            passed_checks += test['elements_passed']
    
    if applicable_checks == 0:
        # No applicable tests - perfect score
        return {
            'score': 100,
            'reason': 'No applicable accessibility tests',
            'details': {
                'applicable_checks': 0,
                'passed_checks': 0,
                'not_applicable_tests': len([t for t in test_results if not t['applicable']])
            }
        }
    
    score = (passed_checks / applicable_checks) * 100
    
    return {
        'score': score,
        'reason': f'{passed_checks} of {applicable_checks} checks passed',
        'details': {
            'applicable_checks': applicable_checks,
            'passed_checks': passed_checks,
            'failed_checks': applicable_checks - passed_checks,
            'not_applicable_tests': len([t for t in test_results if not t['applicable']])
        }
    }
```

## Reporting Display

### Summary View
```
Accessibility Score: 85%
Based on applicable tests only

✅ 127 checks passed
❌ 23 checks failed
➖ 45 checks not applicable (no elements to test)
📊 150 applicable checks performed
```

### Detailed Test Breakdown
```
FORMS (Applicable ✓)
├─ Elements found: 8
├─ Elements tested: 8
├─ Passed: 6 (75%)
└─ Failed: 2 (25%)
   ├─ ✅ 6 inputs have labels
   └─ ❌ 2 inputs missing labels

IMAGES (Applicable ✓)
├─ Elements found: 15
├─ Elements tested: 15
├─ Passed: 15 (100%)
└─ Failed: 0 (0%)
   └─ ✅ All images have alt text

TABLES (Not Applicable ➖)
└─ No table elements found on page

VIDEO/AUDIO (Not Applicable ➖)
└─ No media elements found on page

COLOR CONTRAST (Applicable ✓)
├─ Elements found: 234
├─ Elements tested: 234
├─ Passed: 220 (94%)
└─ Failed: 14 (6%)
   ├─ ✅ 220 elements have sufficient contrast
   └─ ❌ 14 elements have insufficient contrast
```

## Test Categories and Applicability Rules

| Test Category | Applicable When | Not Applicable When |
|--------------|-----------------|-------------------|
| **Forms** | Page contains `<input>`, `<select>`, `<textarea>` | No form elements present |
| **Images** | Page contains `<img>` elements | No images present |
| **Tables** | Page contains `<table>` elements | No tables present |
| **Headings** | Page contains `<h1>`-`<h6>` elements | No headings present |
| **Landmarks** | Always applicable | Never (all pages should have landmarks) |
| **Language** | Always applicable | Never (all pages need lang attribute) |
| **Title** | Always applicable | Never (all pages need title) |
| **Color** | Page has text content | No text content (rare) |
| **Links** | Page contains `<a>` elements | No links present |
| **Video** | Page contains `<video>` elements | No video elements |
| **Audio** | Page contains `<audio>` elements | No audio elements |
| **ARIA** | Elements have ARIA attributes | No ARIA usage |
| **Keyboard** | Page has interactive elements | No interactive elements |

## Benefits of This Approach

1. **Accurate Scoring**: Only score on applicable tests
2. **Fair Comparison**: Pages aren't penalized for not having certain elements
3. **Better Insights**: Know what wasn't tested vs. what failed
4. **Meaningful Progress**: Track improvement on applicable items
5. **Context-Aware**: Different page types scored appropriately

## Example Score Calculations

### Scenario 1: Simple Landing Page
- No forms (forms test N/A)
- 10 images (all pass)
- Good color contrast
- Proper headings
- **Score: 100%** (all applicable tests pass)

### Scenario 2: Complex Form Page
- 20 form fields (18 pass, 2 fail)
- 5 images (all pass)
- Some contrast issues (90% pass)
- **Score: 94%** (based only on applicable elements)

### Scenario 3: Text-Only Page
- No forms (N/A)
- No images (N/A)
- No videos (N/A)
- Only headings and text
- **Score: 100%** (if headings and contrast pass)

## Database Schema Updates

Add fields to track applicability:

```sql
ALTER TABLE test_results ADD COLUMN total_checks INTEGER DEFAULT 0;
ALTER TABLE test_results ADD COLUMN applicable_checks INTEGER DEFAULT 0;
ALTER TABLE test_results ADD COLUMN not_applicable_checks INTEGER DEFAULT 0;
ALTER TABLE test_results ADD COLUMN skipped_checks INTEGER DEFAULT 0;
ALTER TABLE test_results ADD COLUMN compliance_score DECIMAL(5,2);
```

## UI Updates for Filtering

Add new filter options:
- ✅ Show Passed Checks
- ❌ Show Failed Checks  
- ➖ Show Not Applicable
- 📊 Show All Applicable Tests

## Implementation Priority

1. **Update test return structure** to include applicability
2. **Modify ResultProcessor** to handle N/A tests
3. **Update compliance calculation** to exclude N/A
4. **Update reporting** to show N/A separately
5. **Add filters** for pass/fail/N/A