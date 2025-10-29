# Maps Touchpoint Implementation Plan

## Overview
Comprehensive rewrite of Maps touchpoint testing to implement advanced detection, proper accessibility testing for interactive vs non-interactive maps, and metadata discovery reporting.

## Phase 1: Core Detection Infrastructure

### 1.1 Enhanced Map Type Detection
**File**: `auto_a11y/testing/touchpoint_tests/test_maps.py`

**Implement detection for:**
- **Iframe Maps**: Google, Bing, Mapbox, Leaflet, OpenStreetMap, Apple, HERE, TomTom, ArcGIS, Waze
- **Additional Global Providers**: Baidu, Amap, Naver, Kakao, 2GIS, Mapy.cz, Maptiler, Ordnance Survey
- **Div-based Maps**: Mapbox GL, Leaflet, Google Maps JS, OpenLayers, ArcGIS JS, HERE, Carto, Mapfit
- **SVG Maps**: D3.js, GeoJSON/TopoJSON, Choropleth patterns, custom geographic visualizations
- **Web Components**: Custom map elements with shadow DOM
- **WebGL Maps**: Mapbox GL, Deck.gl, Cesium

**Detection Methods:**
- Provider identification via URL patterns
- Script/library detection
- Class/ID pattern matching
- GeoJSON/TopoJSON data references
- Shadow DOM inspection (where accessible)
- WebGL context detection
- Choropleth pattern detection (multiple paths with data attributes)

### 1.2 Interactivity Detection
**Function**: `isInteractiveMap(element)`

**Check for focusable elements within map:**
- Semantic interactive elements: `button`, `a`, `input`, `select`, `textarea`
- Elements with `tabindex` >= 0
- Elements with interactive ARIA roles: `button`, `link`, `checkbox`, `radio`, `slider`, `spinbutton`, `switch`, `tab`, `menuitem`
- Custom controls with event handlers

**Returns**: Boolean indicating if map contains interactive elements

### 1.3 Provider Identification
**Function**: `identifyMapProvider(element, mapType)`

**Enhanced provider detection for:**
- Iframe src URL analysis
- Script tag inspection for library CDNs
- Class/ID naming patterns
- Data attributes
- GeoJSON/TopoJSON references
- Library-specific DOM patterns (D3 projections, Leaflet markers, etc.)

**Returns**: Provider name string or "Unknown Map Provider"

## Phase 2: Accessibility Tests Implementation

### 2.1 Interactive Map Violations

#### ErrMapAriaHidden (WCAG 1.3.1 - Level A)
**Description**: Interactive map has `aria-hidden="true"` which hides focusable controls
**Detection**:
- Map is interactive (contains focusable elements)
- Has `aria-hidden="true"` on map container or iframe
**Severity**: ERROR
**Applies to**: Iframe maps, div maps, SVG maps

#### ErrMapRolePresentation (NEW - WCAG 4.1.2 - Level A)
**Description**: Interactive map has `role="presentation"` which removes semantics from focusable elements
**Detection**:
- Map is interactive
- Has `role="presentation"` on map container or iframe
**Severity**: ERROR
**Applies to**: Iframe maps, div maps, SVG maps

#### WarnMapPotentialContentHiding (NEW - WCAG 1.1.1 - Level A - AT RISK)
**Description**: Interactive map may hide content from screen readers without alternative
**Detection**:
- Map is interactive
- Has either `aria-hidden="true"` OR `role="presentation"`
**Severity**: WARNING
**Message**: "Cannot verify if map information is provided elsewhere - requires manual review"
**Applies to**: All interactive maps with hiding attributes

### 2.2 Map Naming Requirements

#### ErrMapMissingTitle (WCAG 4.1.2 - Level A)
**Description**: Map iframe lacks accessible name
**Detection** (for iframe maps):
- No `title` attribute
- No `aria-label` attribute
- No `aria-labelledby` attribute
**Severity**: ERROR

#### ErrSvgMapMissingName (NEW - WCAG 4.1.2 - Level A)
**Description**: SVG map lacks accessible name
**Detection** (for SVG maps):
- No `<title>` element as first child
- No `aria-label` attribute
- No `aria-labelledby` attribute
- No proper `role` attribute (`role="img"` or `role="graphics-document"`)
**Severity**: ERROR

#### ErrMapGenericName (NEW - WCAG 1.1.1 - Level A)
**Description**: Map has non-descriptive, generic name
**Detection**:
- Name is one of: "map", "image", "graphic", "img", "picture", "location"
- Name is too short (< 5 characters)
**Severity**: ERROR
**Applies to**: All maps with accessible names

#### ErrDivMapMissingStructure (NEW - WCAG 1.3.1 - Level A)
**Description**: Div-based map lacks proper landmark or heading structure
**Detection** (for div maps):
- Not contained within `<section>`, `<aside>`, `<main>`, or `[role="region"]`
- Not preceded by heading (`h1`-`h6`) that describes the map
**Severity**: ERROR (if no landmark AND no heading)

#### WarnDivMapNoLandmark (NEW - Best Practice)
**Description**: Div-based map has heading but no landmark container
**Detection** (for div maps):
- Has preceding heading
- But not in landmark region
**Severity**: WARNING

### 2.3 Non-Interactive Map Handling
**Note**: Non-interactive maps (without focusable elements) CAN have `aria-hidden` or `role="presentation"` if equivalent information is provided elsewhere. These should not trigger errors, only discovery reporting.

## Phase 3: Discovery Reporting

### 3.1 DiscoMapFound (Discovery - Informational)
**Description**: Reports metadata about each digital map found on the page
**Type**: Discovery (not error/warning)
**Information Reported**:
- Map type: "iframe", "div", "svg", "web-component", "canvas"
- Provider: e.g., "Google Maps", "Mapbox GL", "D3.js", "Unknown"
- Is interactive: Boolean
- Has accessible name: Boolean
- Name quality: "descriptive", "generic", "missing"
- Container type: "landmark", "heading", "none"
- Hiding attributes: "aria-hidden", "role=presentation", "none"
- Dimensions: width x height (if available)
- Source/ID: iframe src, div id/class, SVG id

**Example output**:
```json
{
  "disco": "DiscoMapFound",
  "type": "disco",
  "cat": "maps",
  "mapType": "iframe",
  "provider": "Google Maps",
  "isInteractive": true,
  "hasAccessibleName": true,
  "nameQuality": "descriptive",
  "accessibleName": "Map showing downtown office location",
  "containerType": "landmark",
  "hidingAttributes": "none",
  "dimensions": "600x450",
  "source": "https://www.google.com/maps/embed?pb=...",
  "xpath": "/html/body/main/section[2]/iframe"
}
```

## Phase 4: Error Code Definitions

### New Error Codes to Add

1. **ErrMapAriaHidden** (already exists - update description)
   - Category: maps
   - WCAG: 1.3.1 (Level A)
   - Description: "Interactive map has aria-hidden='true' hiding focusable controls from screen readers"

2. **ErrMapRolePresentation** (NEW)
   - Category: maps
   - WCAG: 4.1.2 (Level A)
   - Description: "Interactive map has role='presentation' removing semantics from focusable elements"

3. **ErrSvgMapMissingName** (NEW)
   - Category: maps
   - WCAG: 4.1.2 (Level A)
   - Description: "SVG map lacks accessible name via title element, aria-label, or aria-labelledby"

4. **ErrMapGenericName** (NEW)
   - Category: maps
   - WCAG: 1.1.1 (Level A)
   - Description: "Map has generic, non-descriptive name that doesn't convey purpose"

5. **ErrDivMapMissingStructure** (NEW)
   - Category: maps
   - WCAG: 1.3.1 (Level A)
   - Description: "Div-based map lacks landmark region or associated heading for context"

6. **WarnMapPotentialContentHiding** (NEW)
   - Category: maps
   - WCAG: 1.1.1 (Level A - AT RISK)
   - Description: "Interactive map may hide content from assistive technologies - verify information is provided elsewhere"

7. **WarnDivMapNoLandmark** (NEW)
   - Category: maps
   - Best Practice
   - Description: "Div-based map has heading but not contained in landmark region"

8. **DiscoMapFound** (NEW - Discovery)
   - Category: maps
   - Type: Informational
   - Description: "Digital map detected - metadata and accessibility information"

## Phase 5: Implementation Details

### 5.1 Main Test Function Structure
```python
async def test_maps(page) -> Dict[str, Any]:
    # JavaScript evaluation returns:
    results = await page.evaluate('''
        () => {
            // 1. Detect all maps (iframes, divs, SVGs, web components)
            const allMaps = detectAllMaps();

            // 2. For each map:
            for (const map of allMaps) {
                // 2.1 Identify provider
                const provider = identifyMapProvider(map);

                // 2.2 Check interactivity
                const isInteractive = isInteractiveMap(map);

                // 2.3 Check accessible naming
                const naming = checkMapNaming(map);

                // 2.4 Check structure (for div maps)
                const structure = checkMapStructure(map);

                // 2.5 Add discovery report
                addDiscoveryReport(map, provider, isInteractive, naming, structure);

                // 2.6 Run accessibility tests
                if (isInteractive) {
                    checkInteractiveMapViolations(map);
                }
                checkNamingViolations(map, naming);
                checkStructureViolations(map, structure);
            }

            return results;
        }
    ''')
```

### 5.2 Helper Functions to Implement
1. `detectAllMaps()` - Find all map types
2. `identifyMapProvider(map)` - Determine provider
3. `isInteractiveMap(map)` - Check for focusable elements
4. `checkMapNaming(map)` - Analyze accessible name
5. `checkMapStructure(map)` - Check landmark/heading context
6. `checkInteractiveMapViolations(map)` - Test interactive map rules
7. `checkNamingViolations(map, naming)` - Test naming rules
8. `checkStructureViolations(map, structure)` - Test structure rules
9. `addDiscoveryReport(...)` - Create DiscoMapFound entry

### 5.3 Generic Name Detection
```javascript
const genericNames = ['map', 'maps', 'image', 'img', 'graphic', 'picture', 'location', 'chart'];
const isGeneric = (name) => {
    const nameLower = name.toLowerCase().trim();
    return genericNames.includes(nameLower) || nameLower.length < 5;
};
```

## Phase 6: Comprehensive Fixtures

### 6.1 Fixtures to Create

**Fixtures/Maps/ErrMapAriaHidden_001_iframe_violations.html**
- 3 violations: Google Maps, Mapbox, OpenStreetMap iframes with aria-hidden

**Fixtures/Maps/ErrMapAriaHidden_002_div_violations.html**
- 3 violations: Mapbox GL, Leaflet, D3 SVG divs with aria-hidden

**Fixtures/Maps/ErrMapRolePresentation_001_violations.html**
- 3 violations: Maps with role="presentation"

**Fixtures/Maps/ErrMapGenericName_001_violations.html**
- 4 violations: Maps named "map", "image", "img", "location"

**Fixtures/Maps/ErrSvgMapMissingName_001_violations.html**
- 3 violations: SVG maps without title/aria-label

**Fixtures/Maps/ErrDivMapMissingStructure_001_violations.html**
- 3 violations: Div maps without landmarks or headings

**Fixtures/Maps/WarnDivMapNoLandmark_001_warnings.html**
- 3 warnings: Div maps with headings but no landmarks

**Fixtures/Maps/DiscoMapFound_001_comprehensive.html**
- Multiple map types for discovery testing
- Google Maps, Mapbox, Leaflet, D3, OpenStreetMap
- Mix of interactive and non-interactive
- Various providers and configurations

**Fixtures/Maps/Maps_002_correct_accessible.html**
- Positive test: All maps properly configured
- Interactive maps without hiding
- Proper naming
- Proper structure

**Fixtures/Maps/Maps_003_global_providers.html**
- Test global providers: Baidu, Amap, Naver, Kakao, 2GIS

## Phase 7: Testing and Validation

### 7.1 Test All Fixtures
```bash
python test_fixtures.py --touchpoint maps
```

### 7.2 Verify Error Code Coverage
- All 8 error/warning/discovery codes should be detected
- Success rate should be 100%

### 7.3 Manual Validation
- Check that DiscoMapFound reports accurate metadata
- Verify interactive detection works correctly
- Confirm generic name detection catches obvious cases

## Phase 8: Documentation Updates

### 8.1 Update issue_descriptions_enhanced.py
Add descriptions for all new error codes with:
- Title
- What (description)
- Why (accessibility impact)
- Who (affected users)
- Impact level
- WCAG criteria
- Remediation steps

### 8.2 Update touchpoint_tests.py
Ensure all error codes are in the 'maps' touchpoint list

### 8.3 Update touchpoints.py
Map all new error codes to TouchpointID.MAPS

## Implementation Order

### Step 1: Update test_maps.py with new detection logic (60 min)
- Enhanced provider detection
- Interactivity detection
- SVG/WebGL/Web Component detection
- Global provider support

### Step 2: Implement all 8 error codes (45 min)
- Update existing ErrMapAriaHidden
- Add 6 new error/warning codes
- Add DiscoMapFound discovery

### Step 3: Create comprehensive fixtures (30 min)
- 10 fixture files covering all scenarios
- Mix of violations, warnings, discoveries, and passing tests

### Step 4: Update error code mappings (15 min)
- issue_descriptions_enhanced.py
- touchpoint_tests.py
- touchpoints.py

### Step 5: Test everything (20 min)
- Run all fixtures
- Verify 100% pass rate
- Check DiscoMapFound metadata

**Total Estimated Time: ~2.5 hours**

## Success Criteria

1. ✅ All map types detected (iframe, div, SVG, web component, WebGL)
2. ✅ 20+ map providers identified
3. ✅ Interactive vs non-interactive maps properly distinguished
4. ✅ All 7 error/warning codes working
5. ✅ DiscoMapFound reports complete metadata
6. ✅ All fixtures pass at 100%
7. ✅ No false positives on non-interactive maps
8. ✅ Generic name detection accurate
9. ✅ Global providers (Baidu, Amap, etc.) supported
10. ✅ Production ready

---

**Ready to implement!** This plan provides comprehensive map accessibility testing while maintaining clarity and proper WCAG mapping.
