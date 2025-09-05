/**
 * Helper functions for pass tracking and applicability
 * To be included in all test files
 */

/**
 * Create a not applicable result for a test
 * @param {string} testName - Name of the test
 * @param {string} reason - Reason why test is not applicable
 * @param {Array} checkDefinitions - Array of check definitions for this test
 * @returns {Object} Not applicable test result
 */
function createNotApplicableResult(testName, reason, checkDefinitions) {
    const checks = checkDefinitions.map(check => ({
        ...check,
        applicable: false,
        total: 0,
        passed: 0,
        failed: 0
    }));
    
    return {
        test_name: testName,
        applicable: false,
        not_applicable_reason: reason,
        elements_found: 0,
        elements_tested: 0,
        elements_passed: 0,
        elements_failed: 0,
        errors: [],
        passes: [],
        checks: checks
    };
}

/**
 * Create an applicable test result
 * @param {string} testName - Name of the test
 * @param {number} elementsFound - Number of elements found
 * @param {number} elementsPassed - Number of elements that passed
 * @param {number} elementsFailed - Number of elements that failed
 * @param {Array} errors - Array of errors
 * @param {Array} passes - Array of passes
 * @param {Array} checks - Array of check results
 * @returns {Object} Applicable test result
 */
function createApplicableResult(testName, elementsFound, elementsPassed, elementsFailed, errors, passes, checks) {
    return {
        test_name: testName,
        applicable: true,
        elements_found: elementsFound,
        elements_tested: elementsFound,
        elements_passed: elementsPassed,
        elements_failed: elementsFailed,
        errors: errors || [],
        passes: passes || [],
        checks: checks || []
    };
}

/**
 * Initialize a check tracker
 * @param {string} id - Check ID
 * @param {string} description - Check description
 * @param {Array} wcag - WCAG criteria
 * @returns {Object} Check tracker object
 */
function initializeCheck(id, description, wcag) {
    return {
        id: id,
        description: description,
        wcag: wcag || [],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
}

/**
 * Record a pass for an element
 * @param {Object} check - Check tracker to update
 * @param {Array} passList - Pass list to add to
 * @param {Object} passData - Data about the pass
 */
function recordPass(check, passList, passData) {
    check.passed++;
    check.total++;
    passList.push(passData);
}

/**
 * Record a failure for an element
 * @param {Object} check - Check tracker to update
 * @param {Array} errorList - Error list to add to
 * @param {Object} errorData - Data about the error
 */
function recordFailure(check, errorList, errorData) {
    check.failed++;
    check.total++;
    errorList.push(errorData);
}

/**
 * Legacy result format for backwards compatibility
 * @param {Array} errors - Array of errors
 * @param {Array} warnings - Array of warnings
 * @param {Array} passes - Array of passes
 * @returns {Object} Legacy format result
 */
function createLegacyResult(errors, warnings, passes) {
    return {
        errors: errors || [],
        warnings: warnings || [],
        passes: passes || []
    };
}