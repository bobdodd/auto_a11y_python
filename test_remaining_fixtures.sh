#!/bin/bash
# Script to test remaining fixtures in batches with memory management

# Activate virtual environment
source venv/bin/activate

# Configuration
BATCH_SIZE=20  # Test 20 codes at a time to avoid memory issues
RESULTS_FILE="fixture_test_results_summary.md"
FAILURES_FILE="fixture_test_failures.md"
TEMP_LOG="/tmp/fixture_test.log"
COMPLETED_FILE="/tmp/completed_tests.txt"
REMAINING_FILE="/tmp/remaining_tests.txt"

# Extract already completed tests
if [ -f "$RESULTS_FILE" ]; then
    grep -E "^\- \[" "$RESULTS_FILE" | awk '{print $3}' | sort > "$COMPLETED_FILE"
    echo "Found $(wc -l < $COMPLETED_FILE) already completed tests"
else
    touch "$COMPLETED_FILE"
    echo "No previous results found, starting fresh"
fi

# Get all unique codes
find Fixtures -name "*.html" | sed 's/.*\///' | sed 's/_[0-9]*_.*.html$//' | sed 's/\.html$//' | sort -u > /tmp/all_codes.txt

# Find remaining tests (codes not yet completed)
comm -23 /tmp/all_codes.txt "$COMPLETED_FILE" > "$REMAINING_FILE"
remaining_count=$(wc -l < "$REMAINING_FILE")

echo "=========================================="
echo "Remaining tests to run: $remaining_count"
echo "Batch size: $BATCH_SIZE"
echo "Estimated batches: $(( ($remaining_count + $BATCH_SIZE - 1) / $BATCH_SIZE ))"
echo "=========================================="

# If no results file exists, create header
if [ ! -f "$RESULTS_FILE" ]; then
    echo "# Fixture Test Results" > "$RESULTS_FILE"
    echo "Generated: $(date)" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"
fi

if [ ! -f "$FAILURES_FILE" ]; then
    echo "# Failing Fixtures Checklist" > "$FAILURES_FILE"
    echo "Generated: $(date)" >> "$FAILURES_FILE"
    echo "" >> "$FAILURES_FILE"
fi

# Counter variables
batch_num=0
total_tested=0
total_passed=0
total_failed=0

# Process remaining tests in batches
while IFS= read -r code; do
    ((total_tested++))

    # Calculate batch number
    if (( total_tested % BATCH_SIZE == 1 )); then
        ((batch_num++))
        echo ""
        echo "=========================================="
        echo "BATCH $batch_num: Testing codes $total_tested to $(( total_tested + BATCH_SIZE - 1 ))"
        echo "=========================================="
    fi

    echo "[$total_tested/$remaining_count] Testing: $code"

    # Run test and capture output
    python test_fixtures.py --code "$code" > "$TEMP_LOG" 2>&1

    # Check if test passed
    if grep -q "Success rate: 100.0%" "$TEMP_LOG"; then
        ((total_passed++))
        echo "  ✅ PASSED"
        echo "- [x] $code" >> "$RESULTS_FILE"
    else
        ((total_failed++))
        echo "  ❌ FAILED"
        echo "- [ ] $code" >> "$RESULTS_FILE"
        echo "- [ ] **$code**" >> "$FAILURES_FILE"

        # Extract failure summary
        echo "  \`\`\`" >> "$FAILURES_FILE"
        grep -E "(❌ Failed:|Success rate:)" "$TEMP_LOG" | head -5 >> "$FAILURES_FILE"
        echo "  \`\`\`" >> "$FAILURES_FILE"
        echo "" >> "$FAILURES_FILE"
    fi

    # After each batch, give system time to release memory
    if (( total_tested % BATCH_SIZE == 0 )); then
        echo ""
        echo "Batch $batch_num complete. Pausing 5 seconds for memory cleanup..."
        sleep 5

        # Kill any zombie browser processes
        pkill -f "chrome" 2>/dev/null || true
        pkill -f "chromium" 2>/dev/null || true

        echo "Progress: $total_tested/$remaining_count tests | Passed: $total_passed | Failed: $total_failed"
        echo ""
    fi

done < "$REMAINING_FILE"

# Final summary
echo "" >> "$RESULTS_FILE"
echo "## Summary" >> "$RESULTS_FILE"
echo "- Total codes tested: $(($(wc -l < $COMPLETED_FILE) + total_tested))" >> "$RESULTS_FILE"
echo "- Passed: $(($(grep -c "\[x\]" $RESULTS_FILE 2>/dev/null || echo 0)))" >> "$RESULTS_FILE"
echo "- Failed: $(($(grep -c "\[ \]" $RESULTS_FILE 2>/dev/null || echo 0)))" >> "$RESULTS_FILE"

echo ""
echo "=========================================="
echo "ALL TESTING COMPLETE!"
echo "New tests run: $total_tested"
echo "Newly passed: $total_passed"
echo "Newly failed: $total_failed"
echo "Results saved to: $RESULTS_FILE"
echo "Failures checklist saved to: $FAILURES_FILE"
echo "=========================================="
