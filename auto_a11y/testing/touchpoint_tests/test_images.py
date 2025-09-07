"""
Images touchpoint test module
Evaluates images on the page for proper alternative text and ARIA roles.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import re

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Image Accessibility Analysis",
    "touchpoint": "images",
    "description": "Evaluates images on the page for proper alternative text and ARIA roles to ensure they are accessible to screen reader users.",
    "version": "1.1.0",
    "wcagCriteria": ["1.1.1", "4.1.2"],
    "tests": [
        {
            "id": "image-alt-presence",
            "name": "Alternative Text Presence",
            "description": "Checks whether all non-decorative images have an alt attribute.",
            "impact": "high",
            "wcagCriteria": ["1.1.1"],
        },
        {
            "id": "image-alt-quality",
            "name": "Alternative Text Quality",
            "description": "Evaluates the quality of alternative text to ensure it's meaningful.",
            "impact": "high",
            "wcagCriteria": ["1.1.1"],
        },
        {
            "id": "svg-role",
            "name": "SVG Role Attributes",
            "description": "Checks if SVG elements have proper role attributes.",
            "impact": "medium",
            "wcagCriteria": ["1.1.1", "4.1.2"],
        },
    ]
}

async def test_images(page) -> Dict[str, Any]:
    """
    Test images for proper alt text and role attributes
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze images
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
                    test_name: 'images',
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
                
                // Function to check if alt text is invalid
                function isInvalidAlt(altText) {
                    if (!altText) return false;
                    
                    const lower = altText.toLowerCase();
                    
                    // Check for filename patterns
                    if (/\\.(jpg|jpeg|png|gif|svg|bmp|webp)$/i.test(altText)) {
                        return true;
                    }
                    
                    // Check for generic/redundant text
                    const invalidPatterns = [
                        /^image$/i,
                        /^img$/i,
                        /^photo$/i,
                        /^picture$/i,
                        /^image of/i,
                        /^photo of/i,
                        /^picture of/i,
                        /^graphic of/i,
                        /^untitled/i,
                        /^dsc[0-9]/i,
                        /^img_[0-9]/i,
                        /^image[0-9]/i
                    ];
                    
                    return invalidPatterns.some(pattern => pattern.test(lower));
                }
                
                // Get all images and SVGs
                const images = Array.from(document.querySelectorAll('img'));
                const svgs = Array.from(document.querySelectorAll('svg'));
                const allElements = [...images, ...svgs];
                
                if (allElements.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No images or SVG elements found on the page';
                    return results;
                }
                
                results.elements_tested = allElements.length;
                
                // Test regular images
                images.forEach(img => {
                    const altAttr = img.getAttribute('alt');
                    const src = img.getAttribute('src') || '';
                    
                    // Check for missing alt attribute
                    if (altAttr === null) {
                        results.errors.push({
                            err: 'ErrNoAlt',
                            type: 'err',
                            cat: 'images',
                            element: 'IMG',
                            xpath: getFullXPath(img),
                            html: img.outerHTML.substring(0, 200),
                            description: 'Image is missing alt attribute',
                            src: src
                        });
                        results.elements_failed++;
                    } 
                    // Check for empty alt (decorative image)
                    else if (altAttr === '') {
                        // This is valid for decorative images
                        results.passes.push({
                            element: 'IMG',
                            description: 'Decorative image with empty alt text',
                            xpath: getFullXPath(img)
                        });
                        results.elements_passed++;
                    }
                    // Check for invalid alt text
                    else if (isInvalidAlt(altAttr)) {
                        results.errors.push({
                            err: 'ErrRedundantAlt',
                            type: 'err',
                            cat: 'images',
                            element: 'IMG',
                            xpath: getFullXPath(img),
                            html: img.outerHTML.substring(0, 200),
                            description: `Image has invalid alt text: "${altAttr}"`,
                            alt: altAttr,
                            src: src
                        });
                        results.elements_failed++;
                    }
                    // Check for excessively long alt text
                    else if (altAttr.length > 125) {
                        results.errors.push({
                            err: 'ErrAltTooLong',
                            type: 'err',
                            cat: 'images',
                            element: 'IMG',
                            xpath: getFullXPath(img),
                            html: img.outerHTML.substring(0, 200),
                            description: `Alt text is ${altAttr.length} characters (should be under 125)`,
                            alt: altAttr,
                            src: src
                        });
                        results.elements_failed++;
                    }
                    else {
                        results.elements_passed++;
                    }
                });
                
                // Test SVG elements
                svgs.forEach(svg => {
                    const role = svg.getAttribute('role');
                    const ariaLabel = svg.getAttribute('aria-label');
                    const ariaLabelledby = svg.getAttribute('aria-labelledby');
                    const title = svg.querySelector('title');
                    
                    // Check if SVG is purely decorative
                    const ariaHidden = svg.getAttribute('aria-hidden');
                    if (ariaHidden === 'true') {
                        results.passes.push({
                            element: 'SVG',
                            description: 'Decorative SVG marked with aria-hidden',
                            xpath: getFullXPath(svg)
                        });
                        results.elements_passed++;
                        return;
                    }
                    
                    // Check for missing role
                    if (!role) {
                        results.warnings.push({
                            err: 'WarnSVGNoRole',
                            type: 'warn',
                            cat: 'images',
                            element: 'SVG',
                            xpath: getFullXPath(svg),
                            html: svg.outerHTML.substring(0, 200),
                            description: 'SVG element is missing role attribute'
                        });
                    }
                    
                    // Check for accessible name
                    if (!ariaLabel && !ariaLabelledby && !title) {
                        results.errors.push({
                            err: 'ErrSVGNoAccessibleName',
                            type: 'err',
                            cat: 'images',
                            element: 'SVG',
                            xpath: getFullXPath(svg),
                            html: svg.outerHTML.substring(0, 200),
                            description: 'SVG element lacks accessible name (needs aria-label, aria-labelledby, or title)'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Alternative text presence',
                    wcag: ['1.1.1'],
                    total: images.length,
                    passed: images.filter(img => img.hasAttribute('alt')).length,
                    failed: images.filter(img => !img.hasAttribute('alt')).length
                });
                
                if (svgs.length > 0) {
                    results.checks.push({
                        description: 'SVG accessibility',
                        wcag: ['1.1.1', '4.1.2'],
                        total: svgs.length,
                        passed: svgs.filter(svg => 
                            svg.getAttribute('aria-hidden') === 'true' ||
                            svg.getAttribute('aria-label') ||
                            svg.getAttribute('aria-labelledby') ||
                            svg.querySelector('title')
                        ).length,
                        failed: svgs.filter(svg => 
                            svg.getAttribute('aria-hidden') !== 'true' &&
                            !svg.getAttribute('aria-label') &&
                            !svg.getAttribute('aria-labelledby') &&
                            !svg.querySelector('title')
                        ).length
                    });
                }
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_images: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }