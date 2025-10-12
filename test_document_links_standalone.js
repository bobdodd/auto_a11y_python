#!/usr/bin/env node
/**
 * Standalone test for document link detection
 * Tests ErrDocumentLinkMissingFileType without Python
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function testFixture(fixturePath, expectedErrors) {
    console.log(`\nTesting: ${path.basename(fixturePath)}`);
    console.log('='.repeat(60));

    const browser = await puppeteer.launch({ headless: true });

    try {
        const page = await browser.newPage();

        // Load fixture
        const fileUrl = `file://${path.resolve(fixturePath)}`;
        await page.goto(fileUrl, { waitUntil: 'networkidle0' });

        // Run the document links test (same JavaScript as in test_document_links.py)
        const results = await page.evaluate(() => {
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
                        err: 'ErrDocumentLinkMissingFileType',
                        type: 'err',
                        cat: 'links',
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
                            cat: 'links',
                            element: 'A',
                            xpath: getFullXPath(link),
                            html: link.outerHTML.substring(0, 200),
                            description: `Document link could benefit from additional metadata (file size, etc.)`,
                            linkText: text,
                            fileType: fileType.toUpperCase()
                        });
                    }
                }
            });

            return results;
        });

        // Display results
        console.log(`Applicable: ${results.applicable}`);
        console.log(`Elements tested: ${results.elements_tested}`);
        console.log(`Elements passed: ${results.elements_passed}`);
        console.log(`Elements failed: ${results.elements_failed}`);

        if (results.errors && results.errors.length > 0) {
            console.log(`\n✅ Errors found: ${results.errors.length}`);
            results.errors.forEach((error, i) => {
                console.log(`  ${i + 1}. ${error.err} - ${(error.description || '').substring(0, 80)}`);
                console.log(`     Link text: '${error.linkText || 'N/A'}'`);
                console.log(`     File type: ${error.fileType || 'N/A'}`);
            });
        } else {
            console.log('\n✅ No errors found (all document links properly labeled)');
        }

        // Verify expected results
        const actualErrors = results.errors.length;
        if (actualErrors === expectedErrors) {
            console.log(`\n✅ SUCCESS: Found expected ${expectedErrors} error(s)`);
            return true;
        } else {
            console.log(`\n❌ FAIL: Expected ${expectedErrors} error(s), found ${actualErrors}`);
            return false;
        }

    } finally {
        await browser.close();
    }
}

async function main() {
    const fixturesDir = path.join(__dirname, 'Fixtures', 'Links');

    // Test violation fixture
    const violationFixture = path.join(fixturesDir, 'ErrDocumentLinkMissingFileType_001_violations_basic.html');
    if (fs.existsSync(violationFixture)) {
        await testFixture(violationFixture, 3);
    }

    // Test passing fixture
    const passingFixture = path.join(fixturesDir, 'ErrDocumentLinkMissingFileType_002_correct_with_file_type.html');
    if (fs.existsSync(passingFixture)) {
        await testFixture(passingFixture, 0);
    }
}

main().catch(console.error);
