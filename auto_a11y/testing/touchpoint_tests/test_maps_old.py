"""
Maps touchpoint test module
Evaluates embedded digital maps for proper accessibility attributes and alternative content.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Digital Maps Accessibility Analysis",
    "touchpoint": "maps",
    "description": "Evaluates embedded digital maps for proper accessibility attributes and alternative content. This test identifies common map implementations including Google Maps, Mapbox, and Leaflet, and checks that they are properly labeled and accessible to screen reader users.",
    "version": "1.0.0",
    "wcagCriteria": ["2.4.1", "4.1.2", "1.1.1"],
    "tests": [
        {
            "id": "map-title",
            "name": "Map Title Attribute",
            "description": "Checks if embedded map iframes have descriptive title attributes to identify their purpose.",
            "impact": "high",
            "wcagCriteria": ["2.4.1", "4.1.2"],
        },
        {
            "id": "map-aria-hidden",
            "name": "Maps with aria-hidden",
            "description": "Identifies maps that have been hidden from screen readers with aria-hidden attribute.",
            "impact": "high",
            "wcagCriteria": ["1.1.1"],
        },
        {
            "id": "div-map-accessibility",
            "name": "Div-based Map Accessibility",
            "description": "Checks if div-based maps (like Leaflet or Mapbox) have proper ARIA attributes for accessibility.",
            "impact": "high",
            "wcagCriteria": ["1.1.1", "4.1.2"],
        },
        {
            "id": "map-identification",
            "name": "Map Provider Identification",
            "description": "Identifies the map providers used on the page for informational purposes.",
            "impact": "informational",
            "wcagCriteria": [],
        }
    ]
}

async def test_maps(page) -> Dict[str, Any]:
    """
    Test for embedded digital maps and their accessibility attributes
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze maps
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
                    test_name: 'maps',
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
                
                // Identify map provider from src URL
                function identifyMapProvider(src) {
                    const srcLower = src.toLowerCase();
                    if (srcLower.includes('google.com/maps')) return 'Google Maps';
                    if (srcLower.includes('bing.com/maps')) return 'Bing Maps';
                    if (srcLower.includes('openstreetmap.org')) return 'OpenStreetMap';
                    if (srcLower.includes('waze.com')) return 'Waze';
                    if (srcLower.includes('mapbox.com')) return 'Mapbox';
                    if (srcLower.includes('leafletjs.com') || srcLower.includes('leaflet')) return 'Leaflet';
                    if (srcLower.includes('arcgis.com')) return 'ArcGIS';
                    if (srcLower.includes('here.com')) return 'HERE Maps';
                    if (srcLower.includes('tomtom.com')) return 'TomTom';
                    if (srcLower.includes('maps.apple.com')) return 'Apple Maps';
                    return 'Unknown Map Provider';
                }
                
                // Find map iframes
                const mapIframes = Array.from(document.querySelectorAll('iframe')).filter(iframe => {
                    const src = iframe.src || '';
                    return src.includes('map') || 
                           src.includes('maps.google') ||
                           src.includes('maps.bing') ||
                           src.includes('openstreetmap') ||
                           src.includes('waze') ||
                           src.includes('mapbox') ||
                           src.includes('arcgis') ||
                           src.includes('here.com') ||
                           src.includes('tomtom');
                });
                
                // Find div-based maps
                const mapDivs = Array.from(document.querySelectorAll('div[class*="map"], div[id*="map"]'))
                    .filter(div => {
                        const classAndId = (div.className + ' ' + (div.id || '')).toLowerCase();
                        return classAndId.includes('map') && 
                               !classAndId.includes('sitemap') && // Exclude sitemaps
                               !classAndId.includes('heatmap'); // Exclude heatmaps
                    });
                
                const allMaps = [...mapIframes, ...mapDivs];
                
                if (allMaps.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No maps found on the page';
                    return results;
                }
                
                results.elements_tested = allMaps.length;
                
                // Process iframe-based maps
                mapIframes.forEach(iframe => {
                    const provider = identifyMapProvider(iframe.src);
                    const title = iframe.getAttribute('title');
                    const ariaHidden = iframe.getAttribute('aria-hidden');
                    
                    // Check for missing title
                    if (!title) {
                        results.errors.push({
                            err: 'ErrMapMissingTitle',
                            type: 'err',
                            cat: 'maps',
                            element: 'iframe',
                            xpath: getFullXPath(iframe),
                            html: iframe.outerHTML.substring(0, 200),
                            description: 'Map iframe is missing a descriptive title attribute',
                            provider: provider,
                            src: iframe.src
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                    
                    // Check for aria-hidden
                    if (ariaHidden === 'true') {
                        results.errors.push({
                            err: 'ErrMapAriaHidden',
                            type: 'err',
                            cat: 'maps',
                            element: 'iframe',
                            xpath: getFullXPath(iframe),
                            html: iframe.outerHTML.substring(0, 200),
                            description: 'Map is hidden from screen readers with aria-hidden="true"',
                            provider: provider,
                            title: title
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });
                
                // Process div-based maps
                mapDivs.forEach(div => {
                    // Look for known map provider scripts or styles
                    const hasMapboxGL = document.querySelector('script[src*="mapbox-gl"]');
                    const hasLeaflet = document.querySelector('link[href*="leaflet"]');
                    const hasGoogleMaps = document.querySelector('script[src*="maps.google"]');

                    let provider = 'Unknown Map Provider';
                    if (hasMapboxGL) provider = 'Mapbox';
                    if (hasLeaflet) provider = 'Leaflet';
                    if (hasGoogleMaps) provider = 'Google Maps';

                    const ariaLabel = div.getAttribute('aria-label');
                    const role = div.getAttribute('role');
                    const ariaHidden = div.getAttribute('aria-hidden');

                    // Check for aria-hidden on div-based maps
                    if (ariaHidden === 'true') {
                        results.errors.push({
                            err: 'ErrMapAriaHidden',
                            type: 'err',
                            cat: 'maps',
                            element: 'div',
                            xpath: getFullXPath(div),
                            html: div.outerHTML.substring(0, 200),
                            description: 'Interactive map is hidden from screen readers with aria-hidden="true"',
                            provider: provider,
                            id: div.id || null,
                            className: div.className
                        });
                        results.elements_failed++;
                    }

                    // Check for accessibility attributes on div-based maps
                    if (!ariaLabel && !role) {
                        results.errors.push({
                            err: 'ErrDivMapMissingAttributes',
                            type: 'err',
                            cat: 'maps',
                            element: 'div',
                            xpath: getFullXPath(div),
                            html: div.outerHTML.substring(0, 200),
                            description: 'Div-based map lacks proper ARIA attributes (aria-label or role)',
                            provider: provider,
                            id: div.id || null,
                            className: div.className
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Map accessibility attributes',
                    wcag: ['2.4.1', '4.1.2', '1.1.1'],
                    total: allMaps.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_maps: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }