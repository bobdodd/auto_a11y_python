"""
Document Links touchpoint test module
Identifies links to electronic documents like PDFs, Word documents, spreadsheets, etc.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Electronic Document Link Analysis",
    "touchpoint": "document_links",
    "description": "Identifies links to electronic documents like PDFs, Word documents, spreadsheets, etc., and evaluates whether they have appropriate accessibility information. This test helps ensure that users are properly informed about document format before downloading, as different formats may require specific software or have accessibility limitations.",
    "version": "1.0.0",
    "wcagCriteria": ["2.4.4", "2.4.9", "3.2.4", "3.3.2"],
    "tests": [
        {
            "id": "document-link-identification",
            "name": "Document Link Detection",
            "description": "Identifies links to electronic documents such as PDFs, Word files, Excel spreadsheets, etc. This helps ensure that users are aware of what content they're accessing.",
            "impact": "medium",
            "wcagCriteria": ["2.4.4", "2.4.9"],
        },
        {
            "id": "document-link-labeling",
            "name": "Document Link Labeling",
            "description": "Checks if document links have accessible names that include the document type. Users should know when a link will open a document and what format it will be in.",
            "impact": "high",
            "wcagCriteria": ["2.4.4", "3.2.4"],
        },
        {
            "id": "document-metadata",
            "name": "Document Metadata",
            "description": "Evaluates if document links provide supplementary information like file size, modification date, or version. This helps users make informed decisions before downloading.",
            "impact": "medium",
            "wcagCriteria": ["3.3.2"],
        }
    ]
}

async def test_document_links(page) -> Dict[str, Any]:
    """
    Test for links to electronic documents (PDF, DOC, DOCX, XLS, XLSX, etc.)
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze document links
        results = await page.evaluate('''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    discovery: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'document_links',
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
                
                // Document file extensions
                const documentExtensions = [
                    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
                    '.ppt', '.pptx', '.rtf', '.odt', '.ods',
                    '.odp', '.txt', '.csv'
                ];
                
                // Find all links
                const allLinks = Array.from(document.querySelectorAll('a[href]'));
                
                // Filter for document links
                const documentLinks = allLinks.filter(link => {
                    const href = link.href.toLowerCase();
                    return documentExtensions.some(ext => href.endsWith(ext));
                });
                
                if (documentLinks.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No document links found on the page';
                    return results;
                }
                
                results.elements_tested = documentLinks.length;
                
                // Check each document link
                documentLinks.forEach(link => {
                    const href = link.href;
                    const text = link.textContent.trim();
                    const ariaLabel = link.getAttribute('aria-label');
                    const title = link.getAttribute('title');
                    const fileType = href.split('.').pop().toLowerCase();
                    
                    let hasTypeIndication = false;
                    let hasMetadata = false;
                    
                    // Check if link text includes file type
                    const linkContent = (text + ' ' + (ariaLabel || '') + ' ' + (title || '')).toLowerCase();
                    const typeKeywords = [fileType, 'pdf', 'doc', 'word', 'excel', 'powerpoint', 'presentation'];
                    hasTypeIndication = typeKeywords.some(keyword => linkContent.includes(keyword));
                    
                    // Check for metadata indicators
                    const metadataKeywords = ['mb', 'kb', 'bytes', 'size', 'download', 'file'];
                    hasMetadata = metadataKeywords.some(keyword => linkContent.includes(keyword));
                    
                    if (!hasTypeIndication) {
                        results.errors.push({
                            err: 'ErrMissingDocumentType',
                            type: 'err',
                            cat: 'document_links',
                            element: 'A',
                            xpath: getFullXPath(link),
                            html: link.outerHTML.substring(0, 200),
                            description: `Document link does not indicate file type (${fileType.toUpperCase()}) in accessible name`,
                            linkText: text,
                            fileType: fileType.toUpperCase(),
                            href: href
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                        
                        // Check for additional metadata
                        if (!hasMetadata) {
                            results.warnings.push({
                                err: 'WarnMissingDocumentMetadata',
                                type: 'warn',
                                cat: 'document_links',
                                element: 'A',
                                xpath: getFullXPath(link),
                                html: link.outerHTML.substring(0, 200),
                                description: `Document link could benefit from additional metadata (file size, etc.)`,
                                linkText: text,
                                fileType: fileType.toUpperCase()
                            });
                        }
                    }
                    
                    // Check for generic link text
                    const genericTexts = ['click here', 'download', 'here', 'link', 'file', 'document'];
                    if (genericTexts.some(generic => text.toLowerCase().includes(generic)) && text.length < 20) {
                        results.warnings.push({
                            err: 'WarnGenericDocumentLinkText',
                            type: 'warn',
                            cat: 'document_links',
                            element: 'A',
                            xpath: getFullXPath(link),
                            html: link.outerHTML.substring(0, 200),
                            description: `Document link has generic text that may not be descriptive enough`,
                            linkText: text
                        });
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Document link labeling',
                    wcag: ['2.4.4', '3.2.4'],
                    total: documentLinks.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });

                // DISCOVERY: Report PDF links
                const pdfLinks = allLinks.filter(link => {
                    const href = link.href || '';
                    return href.toLowerCase().endsWith('.pdf');
                });

                pdfLinks.forEach(link => {
                    results.warnings.push({
                        err: 'DiscoPDFLinksFound',
                        type: 'disco',
                        cat: 'document_links',
                        element: 'a',
                        xpath: getFullXPath(link),
                        html: link.outerHTML.substring(0, 200),
                        description: 'PDF link detected - ensure PDF is accessible',
                        href: link.href
                    });
                });

                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_document_links: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }