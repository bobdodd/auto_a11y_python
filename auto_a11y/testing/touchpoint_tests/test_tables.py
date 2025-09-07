"""
Tables touchpoint test module
Evaluates HTML tables for proper semantic structure and accessibility features.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Table Accessibility Analysis",
    "touchpoint": "tables",
    "description": "Evaluates HTML tables for proper semantic structure and accessibility features essential for screen reader users. This test checks for captions, headers, proper table structure, and scope attributes to ensure data tables are navigable and understandable.",
    "version": "1.1.0",
    "wcagCriteria": ["1.3.1", "2.4.6"],
    "tests": [
        {
            "id": "table-caption",
            "name": "Table Caption Presence",
            "description": "Checks whether tables have captions that provide a title or summary of the table content.",
            "impact": "high",
            "wcagCriteria": ["1.3.1", "2.4.6"],
        },
        {
            "id": "table-structure",
            "name": "Table Structure",
            "description": "Evaluates if tables use proper structural elements like thead, tbody, and tfoot.",
            "impact": "medium",
            "wcagCriteria": ["1.3.1"],
        },
        {
            "id": "table-headers",
            "name": "Table Headers",
            "description": "Checks if tables have proper column and row headers.",
            "impact": "high",
            "wcagCriteria": ["1.3.1"],
        },
        {
            "id": "table-scope",
            "name": "Header Cell Scope Attributes",
            "description": "Verifies that header cells have appropriate scope attributes to associate them with data cells.",
            "impact": "high",
            "wcagCriteria": ["1.3.1"],
        }
    ]
}

async def test_tables(page) -> Dict[str, Any]:
    """
    Test HTML tables for accessibility requirements
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze tables
        results = await page.evaluate('''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'tables',
                    checks: []
                };
                
                // Function to generate XPath for elements
                function getFullXPath(element) {
                    if (!element) return '';
                    
                    function getElementIdx(el) {
                        let count = 1;
                        for (let sib = el.previousSibling; sib; sib = sib.previousSibling) {
                            if (sib.nodeType === 1 && sib.tagName === el.tagName) {
                                count++;
                            }
                        }
                        return count;
                    }
                    
                    let path = '';
                    while (element && element.nodeType === 1) {
                        const idx = getElementIdx(element);
                        const tagName = element.tagName.toLowerCase();
                        path = `/${tagName}[${idx}]${path}`;
                        element = element.parentNode;
                    }
                    return path;
                }
                
                // Analyze table structure
                function analyzeTable(table) {
                    const analysis = {
                        hasCaption: false,
                        hasTheadSection: false,
                        hasTbodySection: false,
                        totalRows: 0,
                        totalCols: 0,
                        colHeaders: [],
                        rowHeaders: [],
                        violations: []
                    };

                    // Check caption
                    const caption = table.querySelector('caption');
                    analysis.hasCaption = !!caption;
                    if (!caption) {
                        analysis.violations.push({
                            type: 'missing-caption',
                            message: 'Table lacks a caption element'
                        });
                    }

                    // Check table sections
                    analysis.hasTheadSection = !!table.querySelector('thead');
                    analysis.hasTbodySection = !!table.querySelector('tbody');
                    
                    if (!analysis.hasTheadSection) {
                        analysis.violations.push({
                            type: 'missing-thead',
                            message: 'Table lacks a thead section'
                        });
                    }

                    // Analyze headers
                    const thElements = table.querySelectorAll('th');
                    thElements.forEach(th => {
                        const scope = th.getAttribute('scope');
                        if (!scope) {
                            analysis.violations.push({
                                type: 'missing-scope',
                                text: th.textContent.trim(),
                                message: 'Header cell lacks scope attribute'
                            });
                        } else if (scope === 'col') {
                            analysis.colHeaders.push({
                                text: th.textContent.trim(),
                                scope: scope
                            });
                        } else if (scope === 'row') {
                            analysis.rowHeaders.push({
                                text: th.textContent.trim(),
                                scope: scope
                            });
                        }
                    });

                    // Get table dimensions
                    const rows = table.rows;
                    analysis.totalRows = rows.length;
                    analysis.totalCols = rows.length > 0 ? rows[0].cells.length : 0;

                    // Check if all rows have headers
                    const firstRow = rows[0];
                    if (firstRow) {
                        const firstRowHeaders = firstRow.querySelectorAll('th[scope="col"]');
                        if (firstRowHeaders.length === 0) {
                            analysis.violations.push({
                                type: 'no-column-headers',
                                message: 'First row contains no column headers'
                            });
                        }
                    }

                    return analysis;
                }
                
                // Find all tables
                const tables = Array.from(document.querySelectorAll('table'));
                
                if (tables.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No tables found on the page';
                    return results;
                }
                
                results.elements_tested = tables.length;
                
                let missingCaptions = 0;
                let missingHeaders = 0;
                let missingScopes = 0;
                let missingTheadSection = 0;
                
                tables.forEach((table, index) => {
                    const analysis = analyzeTable(table);
                    let hasViolation = false;
                    
                    analysis.violations.forEach(violation => {
                        hasViolation = true;
                        
                        switch(violation.type) {
                            case 'missing-caption':
                                missingCaptions++;
                                results.errors.push({
                                    err: 'ErrTableMissingCaption',
                                    type: 'err',
                                    cat: 'tables',
                                    element: 'table',
                                    xpath: getFullXPath(table),
                                    html: table.outerHTML.substring(0, 200),
                                    description: 'Table lacks a caption element',
                                    tableIndex: index + 1
                                });
                                break;
                                
                            case 'missing-thead':
                                missingTheadSection++;
                                results.warnings.push({
                                    err: 'WarnTableMissingThead',
                                    type: 'warn',
                                    cat: 'tables',
                                    element: 'table',
                                    xpath: getFullXPath(table),
                                    html: table.outerHTML.substring(0, 200),
                                    description: 'Table lacks a thead section',
                                    tableIndex: index + 1
                                });
                                break;
                                
                            case 'missing-scope':
                                missingScopes++;
                                results.errors.push({
                                    err: 'ErrHeaderMissingScope',
                                    type: 'err',
                                    cat: 'tables',
                                    element: 'th',
                                    xpath: getFullXPath(table),
                                    html: table.outerHTML.substring(0, 200),
                                    description: `Header cell "${violation.text}" lacks scope attribute`,
                                    headerText: violation.text,
                                    tableIndex: index + 1
                                });
                                break;
                                
                            case 'no-column-headers':
                                missingHeaders++;
                                results.errors.push({
                                    err: 'ErrTableNoColumnHeaders',
                                    type: 'err',
                                    cat: 'tables',
                                    element: 'table',
                                    xpath: getFullXPath(table),
                                    html: table.outerHTML.substring(0, 200),
                                    description: 'Table first row contains no column headers',
                                    tableIndex: index + 1
                                });
                                break;
                        }
                    });
                    
                    if (!hasViolation) {
                        results.elements_passed++;
                    } else {
                        results.elements_failed++;
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Table captions',
                    wcag: ['1.3.1', '2.4.6'],
                    total: tables.length,
                    passed: tables.length - missingCaptions,
                    failed: missingCaptions
                });
                
                results.checks.push({
                    description: 'Table structure',
                    wcag: ['1.3.1'],
                    total: tables.length,
                    passed: tables.length - missingTheadSection,
                    failed: missingTheadSection
                });
                
                if (missingHeaders > 0) {
                    results.checks.push({
                        description: 'Table headers',
                        wcag: ['1.3.1'],
                        total: tables.length,
                        passed: tables.length - missingHeaders,
                        failed: missingHeaders
                    });
                }
                
                if (missingScopes > 0) {
                    results.checks.push({
                        description: 'Header scope attributes',
                        wcag: ['1.3.1'],
                        total: tables.length,
                        passed: tables.length - missingScopes,
                        failed: missingScopes
                    });
                }
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_tables: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }