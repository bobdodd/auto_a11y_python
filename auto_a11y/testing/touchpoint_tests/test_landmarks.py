"""
Landmarks touchpoint test module
Evaluates webpage landmark structure to ensure proper semantic organization and navigation for screen reader users.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "ARIA Landmark Analysis",
    "touchpoint": "landmarks",
    "description": "Evaluates webpage landmark structure to ensure proper semantic organization and navigation for screen reader users. This test checks for required landmarks, proper nesting, and appropriate labeling of content regions.",
    "version": "1.0.0",
    "wcagCriteria": ["1.3.1", "2.4.1"],
    "tests": [
        {
            "id": "main-landmark",
            "name": "Main Landmark Presence",
            "description": "Checks if the page has a main landmark that contains the primary content.",
            "impact": "high",
            "wcagCriteria": ["1.3.1", "2.4.1"],
        },
        {
            "id": "banner-landmark",
            "name": "Banner Landmark",
            "description": "Verifies that the page has a banner landmark for site-wide header content.",
            "impact": "medium",
            "wcagCriteria": ["1.3.1"],
        },
        {
            "id": "contentinfo-landmark",
            "name": "Contentinfo Landmark",
            "description": "Checks if the page has a contentinfo landmark for footer content.",
            "impact": "medium",
            "wcagCriteria": ["1.3.1"],
        },
        {
            "id": "content-in-landmarks",
            "name": "Content Within Landmarks",
            "description": "Evaluates whether all content on the page is contained within appropriate landmarks.",
            "impact": "medium",
            "wcagCriteria": ["1.3.1", "2.4.1"],
        },
        {
            "id": "duplicate-landmarks",
            "name": "Duplicate Landmark Identification",
            "description": "Checks if multiple landmarks of the same type have unique labels to distinguish them.",
            "impact": "high",
            "wcagCriteria": ["1.3.1", "2.4.1"],
        }
    ]
}

async def test_landmarks(page) -> Dict[str, Any]:
    """
    Test page landmark structure and requirements
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze landmarks
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
                    test_name: 'landmarks',
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
                
                // Get accessible name for landmarks
                function getLandmarkName(element) {
                    const ariaLabel = element.getAttribute('aria-label');
                    if (ariaLabel) return ariaLabel.trim();

                    const labelledBy = element.getAttribute('aria-labelledby');
                    if (labelledBy) {
                        const labelElements = labelledBy.split(' ')
                            .map(id => document.getElementById(id))
                            .filter(el => el);
                        if (labelElements.length > 0) {
                            return labelElements.map(el => el.textContent.trim()).join(' ');
                        }
                    }

                    // Check for heading as label for forms
                    if (element.tagName.toLowerCase() === 'form' || element.getAttribute('role') === 'form') {
                        const heading = element.querySelector('h1, h2, h3, h4, h5, h6');
                        if (heading) {
                            return heading.textContent.trim();
                        }
                    }

                    return null;
                }
                
                // Check if element is at top level for header/footer role detection
                function isTopLevelElement(element) {
                    if (element.parentElement === document.body) return true;

                    let parent = element.parentElement;
                    while (parent && parent !== document.body) {
                        const parentTag = parent.tagName.toLowerCase();
                        if (['article', 'aside', 'main', 'nav', 'section'].includes(parentTag)) {
                            return false;
                        }
                        parent = parent.parentElement;
                    }
                    return true;
                }
                
                // Find all landmarks
                const landmarkElements = [
                    ...document.querySelectorAll(
                        'main, [role="main"], header, [role="banner"], footer, [role="contentinfo"], ' +
                        'nav, [role="navigation"], [role="search"], form, [role="form"], ' +
                        'aside, [role="complementary"], section[aria-label], section[aria-labelledby], ' +
                        '[role="region"][aria-label], [role="region"][aria-labelledby]'
                    )
                ];
                
                if (landmarkElements.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No landmarks found on the page';
                    return results;
                }
                
                results.elements_tested = landmarkElements.length;
                
                // Track landmarks found
                const landmarkCounts = {};
                const landmarkNames = {};
                let hasMain = false;
                let hasBanner = false;
                let hasContentinfo = false;
                
                landmarkElements.forEach(element => {
                    const tag = element.tagName.toLowerCase();
                    let role = element.getAttribute('role');
                    const isTopLevel = isTopLevelElement(element);
                    
                    // Handle implicit roles with special cases for header and footer
                    if (!role) {
                        switch (tag) {
                            case 'main': 
                                role = 'main'; 
                                break;
                            case 'header': 
                                role = isTopLevel ? 'banner' : 'region';
                                break;
                            case 'footer': 
                                role = isTopLevel ? 'contentinfo' : 'region';
                                break;
                            case 'nav': 
                                role = 'navigation'; 
                                break;
                            case 'aside': 
                                role = 'complementary'; 
                                break;
                            case 'form': 
                                role = 'form'; 
                                break;
                            case 'section': 
                                role = 'region'; 
                                break;
                        }
                    }
                    
                    const name = getLandmarkName(element);
                    
                    // Track landmark counts and names
                    landmarkCounts[role] = (landmarkCounts[role] || 0) + 1;
                    if (name) {
                        if (!landmarkNames[role]) landmarkNames[role] = new Set();
                        landmarkNames[role].add(name);
                    }
                    
                    // Update summary flags
                    if (role === 'main') hasMain = true;
                    if (role === 'banner' || (tag === 'header' && isTopLevel)) hasBanner = true;
                    if (role === 'contentinfo' || (tag === 'footer' && isTopLevel)) hasContentinfo = true;
                    
                    // Check for violations
                    if (landmarkCounts[role] > 1 && !name) {
                        results.errors.push({
                            err: 'ErrDuplicateLandmarkWithoutName',
                            type: 'err',
                            cat: 'landmarks',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `Multiple ${role} landmarks found, but this one lacks a unique accessible name`,
                            role: role
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                    
                    // Check for forms without labels
                    if (role === 'form' && !name) {
                        results.warnings.push({
                            err: 'WarnUnlabelledForm',
                            type: 'warn',
                            cat: 'landmarks',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Form landmark should have an accessible name'
                        });
                    }
                    
                    // Check for regions without labels
                    if (role === 'region' && !name) {
                        results.warnings.push({
                            err: 'WarnUnlabelledRegion',
                            type: 'warn',
                            cat: 'landmarks',
                            element: tag,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Region landmark should have an accessible name'
                        });
                    }
                });
                
                // Check for missing required landmarks
                if (!hasMain) {
                    results.errors.push({
                        err: 'ErrMissingMainLandmark',
                        type: 'err',
                        cat: 'landmarks',
                        element: 'page',
                        xpath: '/html',
                        html: '<page>',
                        description: 'Page is missing a main landmark'
                    });
                    results.elements_failed++;
                }
                
                if (!hasBanner) {
                    results.warnings.push({
                        err: 'WarnMissingBannerLandmark',
                        type: 'warn',
                        cat: 'landmarks',
                        element: 'page',
                        xpath: '/html',
                        html: '<page>',
                        description: 'Page is missing a banner landmark'
                    });
                }
                
                if (!hasContentinfo) {
                    results.warnings.push({
                        err: 'WarnMissingContentinfoLandmark',
                        type: 'warn',
                        cat: 'landmarks',
                        element: 'page',
                        xpath: '/html',
                        html: '<page>',
                        description: 'Page is missing a contentinfo landmark'
                    });
                }
                
                // Find content outside landmarks
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode: function(node) {
                            if (node.textContent.trim().length === 0) return NodeFilter.FILTER_REJECT;
                            
                            // Check if node is within a landmark
                            let current = node.parentElement;
                            while (current && current !== document.body) {
                                if (current.matches(
                                    'main, [role="main"], header, [role="banner"], ' +
                                    'footer, [role="contentinfo"], nav, [role="navigation"], ' +
                                    '[role="search"], form, [role="form"], aside, ' +
                                    '[role="complementary"], section[aria-label], ' +
                                    'section[aria-labelledby], [role="region"][aria-label], ' +
                                    '[role="region"][aria-labelledby]'
                                )) {
                                    return NodeFilter.FILTER_REJECT;
                                }
                                current = current.parentElement;
                            }
                            return NodeFilter.FILTER_ACCEPT;
                        }
                    }
                );
                
                let contentOutsideLandmarks = 0;
                while (walker.nextNode()) {
                    contentOutsideLandmarks++;
                }
                
                if (contentOutsideLandmarks > 0) {
                    results.warnings.push({
                        err: 'WarnContentOutsideLandmarks',
                        type: 'warn',
                        cat: 'landmarks',
                        element: 'page',
                        xpath: '/html',
                        html: '<page>',
                        description: `Found ${contentOutsideLandmarks} text nodes outside of landmarks`,
                        count: contentOutsideLandmarks
                    });
                }
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Required landmarks',
                    wcag: ['1.3.1', '2.4.1'],
                    total: 3, // main, banner, contentinfo
                    passed: [hasMain, hasBanner, hasContentinfo].filter(Boolean).length,
                    failed: [hasMain, hasBanner, hasContentinfo].filter(x => !x).length
                });
                
                results.checks.push({
                    description: 'Landmark accessibility',
                    wcag: ['1.3.1'],
                    total: landmarkElements.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_landmarks: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }