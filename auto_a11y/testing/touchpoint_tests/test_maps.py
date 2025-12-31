"""
Maps touchpoint test module - Comprehensive Implementation
Evaluates embedded digital maps for proper accessibility, distinguishing between
interactive and non-interactive maps with appropriate requirements for each.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Digital Maps Accessibility Analysis",
    "touchpoint": "maps",
    "description": "Comprehensive evaluation of embedded digital maps including iframe, div-based, SVG, and WebGL maps. Tests interactive vs non-interactive maps with appropriate accessibility requirements for each type.",
    "version": "2.0.0",
    "wcagCriteria": ["1.1.1", "1.3.1", "4.1.2"],
    "tests": [
        {
            "id": "interactive-map-hiding",
            "name": "Interactive Map Hiding Violations",
            "description": "Detects interactive maps with aria-hidden or role=presentation that hide focusable controls.",
            "impact": "critical",
            "wcagCriteria": ["1.3.1", "4.1.2"],
        },
        {
            "id": "map-naming",
            "name": "Map Accessible Naming",
            "description": "Validates that maps have proper accessible names that are descriptive, not generic.",
            "impact": "high",
            "wcagCriteria": ["1.1.1", "4.1.2"],
        },
        {
            "id": "div-map-structure",
            "name": "Div-based Map Structure",
            "description": "Checks that div-based maps are properly contained in landmarks or associated with headings.",
            "impact": "high",
            "wcagCriteria": ["1.3.1"],
        },
        {
            "id": "map-discovery",
            "name": "Map Provider Discovery",
            "description": "Identifies all maps on the page with metadata about provider, type, and accessibility features.",
            "impact": "informational",
            "wcagCriteria": [],
        }
    ]
}

async def test_maps(page) -> Dict[str, Any]:
    """
    Comprehensive map accessibility testing with enhanced detection

    Detects:
    - Iframe maps (Google, Bing, Mapbox, Leaflet, global providers)
    - Div-based maps (Mapbox GL, Leaflet, OpenLayers, etc.)
    - SVG maps (D3.js, GeoJSON, choropleth)
    - Web Components (custom map elements)
    - WebGL maps (Cesium, Deck.gl)

    Tests:
    - Interactive vs non-interactive distinction
    - Proper hiding attribute usage
    - Accessible naming requirements
    - Structural requirements for div maps

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results with errors, warnings, and discoveries
    """
    try:
        results = await page.evaluate('''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    info: [],
                    discoveries: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'maps',
                    checks: []
                };

                // ============================================================
                // UTILITY FUNCTIONS
                // ============================================================

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

                // ============================================================
                // PROVIDER IDENTIFICATION
                // ============================================================

                function identifyIframeMapProvider(src) {
                    const srcLower = src.toLowerCase();

                    // Major Western providers
                    if (srcLower.includes('google.com/maps')) return 'Google Maps';
                    if (srcLower.includes('bing.com/maps')) return 'Bing Maps';
                    if (srcLower.includes('openstreetmap.org')) return 'OpenStreetMap';
                    if (srcLower.includes('waze.com')) return 'Waze';
                    if (srcLower.includes('mapbox.com')) return 'Mapbox';
                    if (srcLower.includes('leafletjs.com') || srcLower.includes('leaflet')) return 'Leaflet';
                    if (srcLower.includes('arcgis.com') || srcLower.includes('esri.com')) return 'ArcGIS';
                    if (srcLower.includes('here.com')) return 'HERE Maps';
                    if (srcLower.includes('tomtom.com')) return 'TomTom';
                    if (srcLower.includes('maps.apple.com')) return 'Apple Maps';

                    // Asian providers
                    if (srcLower.includes('map.baidu.com') || srcLower.includes('api.map.baidu.com')) return 'Baidu Maps';
                    if (srcLower.includes('amap.com') || srcLower.includes('webapi.amap.com')) return 'Amap (Gaode)';
                    if (srcLower.includes('map.naver.com') || srcLower.includes('openapi.naver.com')) return 'Naver Maps';
                    if (srcLower.includes('map.kakao.com') || srcLower.includes('dapi.kakao.com')) return 'Kakao Maps';

                    // European/Other providers
                    if (srcLower.includes('2gis.com') || srcLower.includes('maps.2gis.com')) return '2GIS';
                    if (srcLower.includes('mapy.cz') || srcLower.includes('api.mapy.cz')) return 'Mapy.cz';
                    if (srcLower.includes('maptiler.com') || srcLower.includes('api.maptiler.com')) return 'Maptiler';
                    if (srcLower.includes('viamichelin.com')) return 'ViaMichelin';
                    if (srcLower.includes('ordnancesurvey.co.uk') || srcLower.includes('api.os.uk')) return 'Ordnance Survey';
                    if (srcLower.includes('yandex') && srcLower.includes('map')) return 'Yandex Maps';

                    return 'Unknown Map Provider';
                }

                function identifyDivMapProvider() {
                    // Check for map library scripts and classes
                    const checks = {
                        'Mapbox GL': document.querySelector('script[src*="mapbox-gl"]') || document.querySelector('.mapboxgl-map'),
                        'Mapbox': document.querySelector('script[src*="mapbox.js"]') || document.querySelector('.mapbox-'),
                        'Leaflet': document.querySelector('link[href*="leaflet"]') || document.querySelector('.leaflet-container'),
                        'Google Maps': document.querySelector('script[src*="maps.google"]') || document.querySelector('script[src*="maps.googleapis"]'),
                        'OpenLayers': document.querySelector('script[src*="openlayers"]') || document.querySelector('.ol-viewport'),
                        'ArcGIS': document.querySelector('script[src*="arcgis"]') || document.querySelector('script[src*="esri"]'),
                        'HERE Maps': document.querySelector('script[src*="here.com"]'),
                        'Carto': document.querySelector('script[src*="carto.com"]') || document.querySelector('[class*="carto"]'),
                        'Mapfit': document.querySelector('script[src*="mapfit"]'),
                        'TomTom': document.querySelector('script[src*="tomtom"]'),
                        'D3.js': document.querySelector('script[src*="d3.js"]') || document.querySelector('script[src*="d3.min"]'),
                        'Deck.gl': document.querySelector('script[src*="deck.gl"]'),
                        'Cesium': document.querySelector('script[src*="cesium"]'),
                        'MapLibre': document.querySelector('script[src*="maplibre"]'),
                        'Tangram': document.querySelector('script[src*="tangram"]'),

                        // Asian providers
                        'Baidu Maps': document.querySelector('script[src*="api.map.baidu.com"]'),
                        'Amap': document.querySelector('script[src*="webapi.amap.com"]'),
                        'Naver Maps': document.querySelector('script[src*="openapi.map.naver.com"]'),
                        'Kakao Maps': document.querySelector('script[src*="dapi.kakao.com"]'),
                        '2GIS': document.querySelector('script[src*="maps.api.2gis.ru"]'),
                        'Mapy.cz': document.querySelector('script[src*="api.mapy.cz"]')
                    };

                    for (const [provider, hasLibrary] of Object.entries(checks)) {
                        if (hasLibrary) return provider;
                    }

                    return 'Unknown Map Provider';
                }

                function identifySvgMapProvider(svg) {
                    // Check for D3.js patterns
                    const hasD3Lib = !!document.querySelector('script[src*="d3"]');
                    const hasProjection = svg.querySelector('g.graticule, .projection, [class*="meridian"], [class*="parallel"]');

                    if (hasD3Lib && hasProjection) return 'D3.js Geographic Map';
                    if (hasD3Lib) return 'D3.js Visualization';

                    // Check for GeoJSON/TopoJSON
                    const scripts = document.querySelectorAll('script');
                    const hasGeoData = Array.from(scripts).some(script =>
                        /\b(geojson|topojson|geo\.json|topo\.json)\b/i.test(script.src || script.textContent || '')
                    );

                    if (hasGeoData) return 'GeoJSON/TopoJSON Map';

                    // Check for choropleth pattern (many paths with data attributes)
                    const paths = svg.querySelectorAll('path');
                    if (paths.length >= 5) {
                        const pathsWithData = Array.from(paths).filter(path => {
                            const attrs = Array.from(path.attributes);
                            return attrs.some(attr =>
                                attr.name.startsWith('data-') &&
                                (attr.name.includes('value') || attr.name.includes('region') ||
                                 attr.name.includes('id') || attr.name.includes('name'))
                            );
                        });

                        if (pathsWithData.length > paths.length * 0.5) {
                            return 'Choropleth Map';
                        }
                    }

                    return 'SVG Geographic Map';
                }

                // ============================================================
                // INTERACTIVITY DETECTION
                // ============================================================

                function isInteractiveMap(element) {
                    // Check for focusable elements within the map
                    const interactiveTags = ['button', 'a', 'input', 'select', 'textarea', 'video', 'audio'];
                    const interactiveRoles = ['button', 'link', 'checkbox', 'radio', 'slider', 'spinbutton',
                                             'switch', 'tab', 'menuitem', 'option', 'textbox', 'searchbox'];

                    // Check for semantic interactive elements
                    const hasInteractiveTags = interactiveTags.some(tag =>
                        element.querySelector(tag) !== null
                    );

                    if (hasInteractiveTags) return true;

                    // Check for elements with tabindex >= 0
                    const hasFocusableElements = element.querySelector('[tabindex="0"], [tabindex]:not([tabindex="-1"])') !== null;
                    if (hasFocusableElements) return true;

                    // Check for interactive ARIA roles
                    const elementsWithRoles = element.querySelectorAll('[role]');
                    const hasInteractiveRoles = Array.from(elementsWithRoles).some(el => {
                        const role = el.getAttribute('role');
                        return interactiveRoles.includes(role);
                    });

                    return hasInteractiveRoles;
                }

                // ============================================================
                // MAP NAMING CHECKS
                // ============================================================

                function checkMapNaming(element, mapType) {
                    const result = {
                        hasName: false,
                        name: '',
                        isGeneric: false,
                        source: ''
                    };

                    if (mapType === 'iframe') {
                        const title = element.getAttribute('title');
                        const ariaLabel = element.getAttribute('aria-label');
                        const ariaLabelledby = element.getAttribute('aria-labelledby');

                        if (title) {
                            result.hasName = true;
                            result.name = title;
                            result.source = 'title';
                        } else if (ariaLabel) {
                            result.hasName = true;
                            result.name = ariaLabel;
                            result.source = 'aria-label';
                        } else if (ariaLabelledby) {
                            const labelElement = document.getElementById(ariaLabelledby);
                            if (labelElement) {
                                result.hasName = true;
                                result.name = labelElement.textContent.trim();
                                result.source = 'aria-labelledby';
                            }
                        }
                    } else if (mapType === 'svg') {
                        const titleElement = element.querySelector('title');
                        const ariaLabel = element.getAttribute('aria-label');
                        const ariaLabelledby = element.getAttribute('aria-labelledby');

                        if (titleElement && titleElement === element.firstElementChild) {
                            result.hasName = true;
                            result.name = titleElement.textContent.trim();
                            result.source = 'title element';
                        } else if (ariaLabel) {
                            result.hasName = true;
                            result.name = ariaLabel;
                            result.source = 'aria-label';
                        } else if (ariaLabelledby) {
                            const labelElement = document.getElementById(ariaLabelledby);
                            if (labelElement) {
                                result.hasName = true;
                                result.name = labelElement.textContent.trim();
                                result.source = 'aria-labelledby';
                            }
                        }
                    } else if (mapType === 'div') {
                        const ariaLabel = element.getAttribute('aria-label');
                        const ariaLabelledby = element.getAttribute('aria-labelledby');

                        if (ariaLabel) {
                            result.hasName = true;
                            result.name = ariaLabel;
                            result.source = 'aria-label';
                        } else if (ariaLabelledby) {
                            const labelElement = document.getElementById(ariaLabelledby);
                            if (labelElement) {
                                result.hasName = true;
                                result.name = labelElement.textContent.trim();
                                result.source = 'aria-labelledby';
                            }
                        }
                    }

                    // Check if name is generic
                    if (result.hasName) {
                        const nameLower = result.name.toLowerCase().trim();
                        const genericNames = ['map', 'maps', 'image', 'img', 'graphic', 'picture', 'location', 'chart'];
                        result.isGeneric = genericNames.includes(nameLower) || nameLower.length < 5;
                    }

                    return result;
                }

                // ============================================================
                // STRUCTURE CHECKS (for div maps)
                // ============================================================

                function checkMapStructure(element) {
                    const result = {
                        inLandmark: false,
                        landmarkType: '',
                        hasHeading: false,
                        headingLevel: 0
                    };

                    // Check if in landmark
                    let current = element.parentElement;
                    while (current && current !== document.body) {
                        const tagName = current.tagName.toLowerCase();
                        const role = current.getAttribute('role');

                        if (['section', 'aside', 'main', 'nav', 'article'].includes(tagName)) {
                            result.inLandmark = true;
                            result.landmarkType = tagName;
                            break;
                        }

                        if (role && ['region', 'complementary', 'main', 'navigation'].includes(role)) {
                            result.inLandmark = true;
                            result.landmarkType = role;
                            break;
                        }

                        current = current.parentElement;
                    }

                    // Check for preceding heading
                    let prev = element.previousElementSibling;
                    while (prev) {
                        const tagName = prev.tagName.toLowerCase();
                        if (/^h[1-6]$/.test(tagName)) {
                            result.hasHeading = true;
                            result.headingLevel = parseInt(tagName[1]);
                            break;
                        }
                        prev = prev.previousElementSibling;
                    }

                    return result;
                }

                // ============================================================
                // MAP DETECTION
                // ============================================================

                // Find iframe-based maps
                const mapIframes = Array.from(document.querySelectorAll('iframe')).filter(iframe => {
                    const src = iframe.src || '';
                    const srcLower = src.toLowerCase();
                    return srcLower.includes('map') ||
                           srcLower.includes('google.com/maps') ||
                           srcLower.includes('bing.com/maps') ||
                           srcLower.includes('openstreetmap') ||
                           srcLower.includes('mapbox') ||
                           srcLower.includes('leaflet') ||
                           srcLower.includes('baidu.com') ||
                           srcLower.includes('amap.com') ||
                           srcLower.includes('naver.com') ||
                           srcLower.includes('kakao.com');
                });

                // Find div-based maps
                const mapDivs = Array.from(document.querySelectorAll('div[class*="map"], div[id*="map"]'))
                    .filter(div => {
                        const classAndId = (div.className + ' ' + (div.id || '')).toLowerCase();
                        
                        // Exclude common non-map patterns
                        const excludePatterns = [
                            'sitemap', 'heatmap', 'roadmap', 'mindmap',
                            'list', 'menu', 'nav', 'description', 'legend', 'info',
                            'controls', 'control', 'toolbar', 'buttons', 'overlay',
                            'tooltip', 'popup', 'marker', 'pin', 'icon', 'wrapper'
                        ];
                        
                        const isExcluded = excludePatterns.some(pattern => classAndId.includes(pattern));
                        if (isExcluded) return false;
                        
                        // Must have map-related class/id
                        const hasMapPattern = classAndId.includes('map') || classAndId.includes('leaflet') ||
                                              classAndId.includes('mapbox') || classAndId.includes('google');
                        if (!hasMapPattern) return false;
                        
                        // Must be visible
                        if (div.offsetHeight === 0) return false;
                        
                        // Additional check: should be a container, not a child control
                        // A map container typically has significant size or contains an iframe/canvas
                        const hasMapContent = div.querySelector('iframe, canvas, svg') !== null;
                        const isLargeEnough = div.offsetHeight >= 100 && div.offsetWidth >= 100;
                        
                        // If it's nested inside another map div, skip it (it's probably a control)
                        const parentMapDiv = div.parentElement?.closest('div[class*="map"], div[id*="map"]');
                        if (parentMapDiv) return false;
                        
                        return hasMapContent || isLargeEnough;
                    });

                // Find SVG maps
                const svgMaps = Array.from(document.querySelectorAll('svg')).filter(svg => {
                    // Check for geographic patterns
                    const paths = svg.querySelectorAll('path');
                    if (paths.length < 3) return false;

                    // Check for map-related classes or IDs
                    const classAndId = (svg.className.baseVal || '' + ' ' + (svg.id || '')).toLowerCase();
                    if (classAndId.includes('map') || classAndId.includes('geo') ||
                        classAndId.includes('choropleth')) return true;

                    // Check for D3 geographic patterns
                    const hasProjection = svg.querySelector('g.graticule, .projection') !== null;
                    if (hasProjection) return true;

                    // Check for choropleth patterns (many paths)
                    return paths.length >= 10;
                });

                // Find Web Component maps
                const webComponentMaps = Array.from(document.querySelectorAll('*')).filter(el => {
                    const tagName = el.tagName.toLowerCase();
                    return tagName.includes('-') &&
                           (tagName.includes('map') || tagName.includes('gmap') ||
                            tagName.includes('leaflet') || tagName.includes('mapbox'));
                });

                const allMaps = [
                    ...mapIframes.map(m => ({ element: m, type: 'iframe' })),
                    ...mapDivs.map(m => ({ element: m, type: 'div' })),
                    ...svgMaps.map(m => ({ element: m, type: 'svg' })),
                    ...webComponentMaps.map(m => ({ element: m, type: 'web-component' }))
                ];

                if (allMaps.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No maps found on the page';
                    return results;
                }

                results.elements_tested = allMaps.length;

                // ============================================================
                // PROCESS EACH MAP
                // ============================================================

                allMaps.forEach(({ element, type }) => {
                    const xpath = getFullXPath(element);
                    let provider = 'Unknown';

                    // Identify provider
                    if (type === 'iframe') {
                        provider = identifyIframeMapProvider(element.src);
                    } else if (type === 'div' || type === 'web-component') {
                        provider = identifyDivMapProvider();
                    } else if (type === 'svg') {
                        provider = identifySvgMapProvider(element);
                    }

                    // Check interactivity
                    const isInteractive = isInteractiveMap(element);

                    // Check naming
                    const naming = checkMapNaming(element, type);

                    // Check structure (for div maps)
                    const structure = type === 'div' ? checkMapStructure(element) : null;

                    // Get hiding attributes
                    const ariaHidden = element.getAttribute('aria-hidden');
                    const role = element.getAttribute('role');

                    // Discovery reporting - metadata about this map
                    results.warnings.push({
                        err: 'DiscoMapFound',
                        type: 'disco',
                        cat: 'maps',
                        element: type,
                        xpath: xpath,
                        html: element.outerHTML.substring(0, 200),
                        description: `${provider} ${type} map detected - ${isInteractive ? 'interactive' : 'non-interactive'}`,
                        mapType: type,
                        provider: provider,
                        isInteractive: isInteractive,
                        hasAccessibleName: naming.hasName,
                        accessibleName: naming.name,
                        nameSource: naming.source,
                        nameQuality: naming.isGeneric ? 'generic' : naming.hasName ? 'descriptive' : 'missing',
                        containerType: structure ? (structure.inLandmark ? 'landmark' : structure.hasHeading ? 'heading' : 'none') : 'n/a',
                        landmarkType: structure ? structure.landmarkType : 'n/a',
                        hidingAttributes: (ariaHidden === 'true' ? 'aria-hidden ' : '') + (role === 'presentation' ? 'role=presentation' : ''),
                        dimensions: element.offsetWidth && element.offsetHeight ? `${element.offsetWidth}x${element.offsetHeight}` : 'unknown',
                        source: type === 'iframe' ? element.src : (element.id || element.className)
                    });

                    // ============================================================
                    // PHASE 2: INTERACTIVE MAP VIOLATION TESTS
                    // ============================================================

                    let hasViolation = false;

                    // Test 1: ErrMapAriaHidden - Interactive map with aria-hidden="true"
                    if (isInteractive && ariaHidden === 'true') {
                        results.errors.push({
                            err: 'ErrMapAriaHidden',
                            type: 'err',
                            cat: 'maps',
                            element: type,
                            xpath: xpath,
                            html: element.outerHTML.substring(0, 200),
                            description: 'Interactive map has aria-hidden="true" which hides focusable controls from screen readers (silent focus trap)',
                            wcag: '1.3.1',
                            provider: provider,
                            mapType: type,
                            isInteractive: true
                        });
                        hasViolation = true;
                        results.elements_failed++;
                    }

                    // Test 2: ErrMapRolePresentation - Interactive map with role="presentation"
                    if (isInteractive && role === 'presentation') {
                        results.errors.push({
                            err: 'ErrMapRolePresentation',
                            type: 'err',
                            cat: 'maps',
                            element: type,
                            xpath: xpath,
                            html: element.outerHTML.substring(0, 200),
                            description: 'Interactive map has role="presentation" which removes semantics from focusable elements',
                            wcag: '4.1.2',
                            provider: provider,
                            mapType: type,
                            isInteractive: true
                        });
                        hasViolation = true;
                        results.elements_failed++;
                    }

                    // Test 3: WarnMapPotentialContentHiding - Warning for potential 1.1.1 violation
                    if (isInteractive && (ariaHidden === 'true' || role === 'presentation')) {
                        results.warnings.push({
                            err: 'WarnMapPotentialContentHiding',
                            type: 'warn',
                            cat: 'maps',
                            element: type,
                            xpath: xpath,
                            html: element.outerHTML.substring(0, 200),
                            description: 'Interactive map may hide content from screen readers - verify map information is provided elsewhere as text alternative',
                            wcag: '1.1.1',
                            provider: provider,
                            mapType: type,
                            isInteractive: true,
                            note: 'Cannot automatically verify if equivalent information exists - requires manual review'
                        });
                    }

                    // ============================================================
                    // PHASE 3: NAMING AND STRUCTURE TESTS
                    // ============================================================

                    // Test 4: ErrMapMissingTitle - Iframe map without title
                    if (type === 'iframe' && !naming.hasName) {
                        results.errors.push({
                            err: 'ErrMapMissingTitle',
                            type: 'err',
                            cat: 'maps',
                            element: 'iframe',
                            xpath: xpath,
                            html: element.outerHTML.substring(0, 200),
                            description: 'Map iframe lacks accessible name (title, aria-label, or aria-labelledby)',
                            wcag: '4.1.2',
                            provider: provider
                        });
                        hasViolation = true;
                        results.elements_failed++;
                    }

                    // Test 5: ErrSvgMapMissingName - SVG map without accessible name
                    if (type === 'svg' && !naming.hasName) {
                        results.errors.push({
                            err: 'ErrSvgMapMissingName',
                            type: 'err',
                            cat: 'maps',
                            element: 'svg',
                            xpath: xpath,
                            html: element.outerHTML.substring(0, 200),
                            description: 'SVG map lacks accessible name (title element, aria-label, or aria-labelledby)',
                            wcag: '4.1.2',
                            provider: provider,
                            note: 'SVG maps should also have role="img" or role="graphics-document"'
                        });
                        hasViolation = true;
                        results.elements_failed++;
                    }

                    // Test 6: ErrMapGenericName - Map has generic, non-descriptive name
                    if (naming.hasName && naming.isGeneric) {
                        results.errors.push({
                            err: 'ErrMapGenericName',
                            type: 'err',
                            cat: 'maps',
                            element: type,
                            xpath: xpath,
                            html: element.outerHTML.substring(0, 200),
                            description: `Map has generic name "${naming.name}" which doesn't describe its purpose`,
                            wcag: '1.1.1',
                            provider: provider,
                            genericName: naming.name,
                            nameSource: naming.source
                        });
                        hasViolation = true;
                        results.elements_failed++;
                    }

                    // Test 7: ErrDivMapMissingStructure - Div map without landmark or heading
                    if (type === 'div' && structure && !structure.inLandmark && !structure.hasHeading) {
                        results.errors.push({
                            err: 'ErrDivMapMissingStructure',
                            type: 'err',
                            cat: 'maps',
                            element: 'div',
                            xpath: xpath,
                            html: element.outerHTML.substring(0, 200),
                            description: 'Div-based map lacks proper structure (not in landmark region and no associated heading)',
                            wcag: '1.3.1',
                            provider: provider,
                            remediation: 'Wrap map in <section> with aria-label, or precede with descriptive heading'
                        });
                        hasViolation = true;
                        results.elements_failed++;
                    }

                    // Test 8: WarnDivMapNoLandmark - Div map has heading but no landmark
                    if (type === 'div' && structure && !structure.inLandmark && structure.hasHeading) {
                        results.warnings.push({
                            err: 'WarnDivMapNoLandmark',
                            type: 'warn',
                            cat: 'maps',
                            element: 'div',
                            xpath: xpath,
                            html: element.outerHTML.substring(0, 200),
                            description: `Div-based map has preceding heading (h${structure.headingLevel}) but not in landmark region`,
                            provider: provider,
                            headingLevel: structure.headingLevel,
                            note: 'Best practice: wrap map in landmark region like <section> with aria-label'
                        });
                    }

                    // Test 9: ErrDivMapMissingAttributes - Div map with NO ARIA attributes at all
                    if (type === 'div') {
                        const hasRole = element.hasAttribute('role');
                        const hasAriaLabel = element.hasAttribute('aria-label');
                        const hasAriaLabelledby = element.hasAttribute('aria-labelledby');
                        const hasTitle = element.hasAttribute('title');

                        // Only flag if it has NONE of the key accessibility attributes
                        if (!hasRole && !hasAriaLabel && !hasAriaLabelledby && !hasTitle) {
                            // Build a descriptive element identifier
                            const elemId = element.id ? `#${element.id}` : '';
                            const elemClass = element.className ? `.${element.className.toString().split(' ').slice(0, 2).join('.')}` : '';
                            const elemIdentifier = elemId || elemClass || 'div';
                            
                            // Check what's inside to provide context
                            const hasIframe = element.querySelector('iframe') !== null;
                            const hasCanvas = element.querySelector('canvas') !== null;
                            const hasButtons = element.querySelectorAll('button').length;
                            const hasSvg = element.querySelector('svg') !== null;
                            
                            // Build content description
                            let contentDesc = [];
                            if (hasIframe) contentDesc.push('embedded iframe');
                            if (hasCanvas) contentDesc.push('canvas element');
                            if (hasButtons > 0) contentDesc.push(`${hasButtons} button(s)`);
                            if (hasSvg) contentDesc.push('SVG graphics');
                            const contentStr = contentDesc.length > 0 ? ` containing ${contentDesc.join(', ')}` : '';
                            
                            // Determine what attributes would be expected based on interactivity
                            let roleNeeded = isInteractive ? 'role="region"' : 'role="img"';
                            
                            // Pass structured metadata - let Python/template handle translation
                            results.errors.push({
                                err: 'ErrDivMapMissingAttributes',
                                type: 'err',
                                cat: 'maps',
                                element: 'div',
                                xpath: xpath,
                                html: element.outerHTML.substring(0, 300),
                                wcag: '1.1.1',
                                provider: provider,
                                metadata: {
                                    isInteractive: isInteractive,
                                    elementId: elemIdentifier,
                                    containedContent: contentDesc,
                                    suggestedRole: roleNeeded,
                                    needsAriaLabel: true
                                }
                            });
                            hasViolation = true;
                            results.elements_failed++;
                        }
                    }

                    if (!hasViolation) {
                        results.elements_passed++;
                    }
                });

                // Add summary check information
                if (results.errors.length > 0 || results.warnings.length > 0) {
                    results.checks.push({
                        description: 'Map accessibility violations',
                        wcag: ['1.1.1', '1.3.1', '4.1.2'],
                        total: allMaps.length,
                        passed: results.elements_passed,
                        failed: results.elements_failed
                    });
                }

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
            'discoveries': [],
            'passes': []
        }
