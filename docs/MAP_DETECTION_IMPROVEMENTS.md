# Map Detection Improvements Plan

## Overview
This document outlines improvements to enhance map detection capabilities in the Carnforth Web A11y tool, particularly for SVG and div-based maps.

## 1. SVG Map Detection Enhancements

### 1.1 Choropleth Pattern Detection
**Priority**: High  
**Complexity**: Medium  
**Location**: `js/touchpoints/maps.js` - `svgMaps` filter function (line ~782)

**Implementation**:
```javascript
// Add to SVG detection logic
const hasChoroplethPattern = () => {
  const paths = svg.querySelectorAll('path');
  if (paths.length < 5) return false; // Choropleth maps typically have many regions
  
  // Check if paths have data attributes suggesting regions
  const pathsWithData = Array.from(paths).filter(path => {
    const attrs = Array.from(path.attributes);
    return attrs.some(attr => 
      attr.name.startsWith('data-') && 
      (attr.name.includes('value') || attr.name.includes('region') || 
       attr.name.includes('id') || attr.name.includes('name'))
    );
  });
  
  // If >50% of paths have data attributes, likely a choropleth
  return pathsWithData.length > paths.length * 0.5;
};
```

### 1.2 Geographic Coordinate Detection
**Priority**: Medium  
**Complexity**: High  
**Location**: Same SVG filter function

**Implementation**:
```javascript
// Check for coordinate-like transform attributes
const hasGeoTransforms = () => {
  const transforms = svg.querySelectorAll('[transform]');
  const geoPattern = /translate\s*\(\s*-?\d+\.?\d*\s*,\s*-?\d+\.?\d*\s*\)/;
  const coordPattern = /\b\d{1,3}\.\d{3,}\b/; // Decimal coordinates
  
  return Array.from(transforms).some(el => {
    const transform = el.getAttribute('transform');
    const d = el.getAttribute('d') || '';
    return geoPattern.test(transform) || coordPattern.test(d);
  });
};
```

### 1.3 GeoJSON/TopoJSON Detection
**Priority**: High  
**Complexity**: Low  
**Location**: Add to SVG detection and provider identification

**Implementation**:
```javascript
// Check for geo data references
const hasGeoDataReference = () => {
  // Check script tags for geo data
  const scripts = document.querySelectorAll('script');
  const geoDataPattern = /\b(geojson|topojson|geo\.json|topo\.json)\b/i;
  
  return Array.from(scripts).some(script => 
    geoDataPattern.test(script.src || '') || 
    geoDataPattern.test(script.textContent || '')
  );
};

// Add to provider detection
if (hasGeoDataReference()) {
  provider = 'GeoJSON/TopoJSON Map';
}
```

### 1.4 D3.js Map Pattern Detection
**Priority**: Medium  
**Complexity**: Medium  
**Location**: Enhance provider detection

**Implementation**:
```javascript
// Detect D3.js specific patterns
const isD3Map = () => {
  // Check for D3 projection patterns
  const hasProjection = svg.querySelector('g.graticule, .projection, [class*="meridian"], [class*="parallel"]');
  
  // Check for D3 geo path patterns
  const paths = svg.querySelectorAll('path');
  const hasComplexPaths = Array.from(paths).some(path => {
    const d = path.getAttribute('d') || '';
    return d.length > 100 && /[MC]/.test(d); // Complex path with moves and curves
  });
  
  // Check for D3 library
  const hasD3Lib = !!document.querySelector('script[src*="d3"]');
  
  return hasD3Lib && (hasProjection || hasComplexPaths);
};
```

## 2. Div Map Detection Enhancements

### 2.1 Web Components Detection
**Priority**: High  
**Complexity**: High  
**Location**: `js/touchpoints/maps.js` - `isDivBasedMap` function (line ~647)

**Implementation**:
```javascript
// Add to div detection logic
const isWebComponentMap = (element) => {
  // Check for custom element names that suggest maps
  const tagName = element.tagName.toLowerCase();
  const mapComponentNames = [
    'google-map', 'gmap-', 'map-box', 'leaflet-map', 
    'osm-map', 'arcgis-map', 'here-map', 'map-component'
  ];
  
  if (mapComponentNames.some(name => tagName.includes(name))) {
    return true;
  }
  
  // Check for map-related custom elements in children
  const customElements = element.querySelectorAll('*');
  return Array.from(customElements).some(el => 
    el.tagName.includes('-') && 
    mapComponentNames.some(name => el.tagName.toLowerCase().includes(name))
  );
};
```

### 2.2 Shadow DOM Inspection
**Priority**: Medium  
**Complexity**: High  
**Location**: New utility function, called from isDivBasedMap

**Implementation**:
```javascript
// Utility to check shadow DOM for map content
const hasShadowMapContent = (element) => {
  if (!element.shadowRoot) return false;
  
  try {
    // Check for map indicators in shadow DOM
    const shadowContent = element.shadowRoot.innerHTML.toLowerCase();
    const mapIndicators = ['map', 'marker', 'zoom', 'tile', 'layer'];
    
    return mapIndicators.some(indicator => shadowContent.includes(indicator));
  } catch (e) {
    // Some shadow DOMs are closed and can't be accessed
    return false;
  }
};

// Add to isDivBasedMap checks
if (div.shadowRoot && hasShadowMapContent(div)) {
  return true;
}
```

### 2.3 WebGL Context Detection
**Priority**: Medium  
**Complexity**: Medium  
**Location**: Add to isDivBasedMap function

**Implementation**:
```javascript
// Check for WebGL canvas (used by Mapbox GL, Deck.gl, etc.)
const hasWebGLMap = (div) => {
  const canvases = div.querySelectorAll('canvas');
  
  return Array.from(canvases).some(canvas => {
    try {
      const gl = canvas.getContext('webgl') || canvas.getContext('webgl2');
      // Check if canvas has significant size (maps are usually large)
      return gl && canvas.width > 200 && canvas.height > 200;
    } catch (e) {
      return false;
    }
  });
};
```

### 2.4 Custom Map Implementation Detection
**Priority**: High  
**Complexity**: Medium  
**Location**: Enhance isDivBasedMap function

**Implementation**:
```javascript
// Enhanced heuristics for custom maps
const hasCustomMapPatterns = (div) => {
  // Check for tile loading patterns
  const hasTileImages = div.querySelectorAll('img[src*="tile"], img[src*="/z/"], img[src*="/{z}/"]').length > 0;
  
  // Check for coordinate-based positioning
  const hasCoordinateStyles = Array.from(div.querySelectorAll('*')).some(el => {
    const style = el.style;
    return style.left && style.top && 
           (style.position === 'absolute' || style.position === 'fixed');
  });
  
  // Check for pan/zoom event listeners (indirect check via attributes)
  const hasPanZoomAttrs = div.querySelector('[draggable], [data-zoom], [data-pan]') !== null;
  
  return hasTileImages || (hasCoordinateStyles && hasPanZoomAttrs);
};
```

## 3. General Improvements

### 3.1 New Map Library Detection
**Priority**: High  
**Complexity**: Low  
**Location**: Update provider detection functions

**Libraries to add**:
- Cesium (3D globe)
- Deck.gl (WebGL maps)
- Tangram
- MapLibre GL
- OpenLayers 6+
- Esri ArcGIS API 4.x
- Maps4HTML proposals

### 3.2 ARIA Landmark Detection
**Priority**: Medium  
**Complexity**: Low  
**Location**: Add to all map detection functions

**Implementation**:
```javascript
// Check for map-related ARIA landmarks
const hasMapLandmarks = (element) => {
  const landmarks = element.querySelectorAll('[role="region"][aria-label*="map"], [role="application"][aria-label*="map"]');
  return landmarks.length > 0;
};
```

### 3.3 Performance Optimization
**Priority**: Low  
**Complexity**: Medium  
**Location**: Throughout maps.js

**Improvements**:
- Cache detection results for repeated elements
- Use more efficient selectors
- Implement early exit strategies
- Batch DOM queries

## 4. Testing Strategy

### 4.1 Test Pages to Create
1. **SVG Choropleth Map** - Using D3.js with GeoJSON data
2. **Web Component Map** - Custom element with shadow DOM
3. **WebGL Map** - Using Mapbox GL or Deck.gl
4. **Custom Tile Map** - Hand-rolled implementation
5. **Mixed Map Page** - Multiple map types on one page

### 4.2 Edge Cases to Test
- Maps loaded dynamically after page load
- Maps in iframes with different origins
- Maps with overlays and popups
- Responsive maps that change type based on viewport
- Maps with accessibility features already implemented

## 5. Implementation Order

### Phase 1 (High Priority - Current Session)
1. Add GeoJSON/TopoJSON detection to SVG maps
2. Implement Web Components detection for div maps
3. Add new map library detection
4. Create basic test page with examples

### Phase 2 (Medium Priority - Next Session)
1. Implement choropleth pattern detection
2. Add WebGL context detection
3. Implement custom map patterns
4. Add ARIA landmark detection

### Phase 3 (Low Priority - Future)
1. Add geographic coordinate detection
2. Implement Shadow DOM inspection
3. Performance optimizations
4. Comprehensive test suite

## 6. Code Integration Points

### Files to Modify:
- `js/touchpoints/maps.js` - Main implementation
- `js/touchpoints/maps-debug-example.js` - Test examples
- `test_fixtures.md` - Document new test cases

### Key Functions to Update:
- `isDivBasedMap()` - lines 647-736
- `svgMaps` filter - lines 782-824  
- Provider detection logic - various locations
- `analyzeMapAccessibility()` results processing

## 7. Documentation Updates

### Add to inline comments:
- Explanation of new detection strategies
- Examples of each map type detected
- Performance considerations
- Accessibility implications

### Update touchpoint description:
- List all supported map types
- Clarify detection accuracy
- Note limitations

---

*This plan provides a comprehensive roadmap for enhancing map detection capabilities while maintaining code quality and performance.*