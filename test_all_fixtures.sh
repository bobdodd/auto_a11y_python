#!/bin/bash
# Script to test all fixture codes and create a markdown checklist of failures

# Activate virtual environment
source venv/bin/activate

# Output files
RESULTS_FILE="fixture_test_results_summary.md"
FAILURES_FILE="fixture_test_failures.md"
TEMP_LOG="/tmp/fixture_test.log"

# Initialize results file
echo "# Fixture Test Results" > "$RESULTS_FILE"
echo "Generated: $(date)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Initialize failures file
echo "# Failing Fixtures Checklist" > "$FAILURES_FILE"
echo "Generated: $(date)" >> "$FAILURES_FILE"
echo "" >> "$FAILURES_FILE"
echo "Use this checklist to track which fixtures need to be fixed:" >> "$FAILURES_FILE"
echo "" >> "$FAILURES_FILE"

# Counter variables
total=0
passed=0
failed=0

# Read all unique codes
while IFS= read -r code; do
    ((total++))
    echo "[$total] Testing: $code"

    # Run test and capture output
    python test_fixtures.py --code "$code" > "$TEMP_LOG" 2>&1

    # Check if test passed
    if grep -q "Success rate: 100.0%" "$TEMP_LOG"; then
        ((passed++))
        echo "  ✅ PASSED"
        echo "- [x] $code" >> "$RESULTS_FILE"
    else
        ((failed++))
        echo "  ❌ FAILED"
        echo "- [ ] $code" >> "$RESULTS_FILE"
        echo "- [ ] **$code**" >> "$FAILURES_FILE"

        # Extract failure details
        echo "  \`\`\`" >> "$FAILURES_FILE"
        grep -A 5 "❌ Failed:" "$TEMP_LOG" | head -10 >> "$FAILURES_FILE"
        echo "  \`\`\`" >> "$FAILURES_FILE"
        echo "" >> "$FAILURES_FILE"
    fi

    # Small delay to avoid overwhelming the system
    sleep 1
done < /tmp/unique_codes.txt

# Write summary
echo "" >> "$RESULTS_FILE"
echo "## Summary" >> "$RESULTS_FILE"
echo "- Total codes tested: $total" >> "$RESULTS_FILE"
echo "- Passed: $passed" >> "$RESULTS_FILE"
echo "- Failed: $failed" >> "$RESULTS_FILE"
echo "- Success rate: $(awk "BEGIN {printf \"%.1f\", ($passed/$total)*100}")%" >> "$RESULTS_FILE"

echo "" >> "$FAILURES_FILE"
echo "## Summary" >> "$FAILURES_FILE"
echo "- Total failing codes: $failed out of $total" >> "$FAILURES_FILE"
echo "" >> "$FAILURES_FILE"

echo ""
echo "=========================================="
echo "Testing complete!"
echo "Total: $total | Passed: $passed | Failed: $failed"
echo "Results saved to: $RESULTS_FILE"
echo "Failures checklist saved to: $FAILURES_FILE"
echo "=========================================="
