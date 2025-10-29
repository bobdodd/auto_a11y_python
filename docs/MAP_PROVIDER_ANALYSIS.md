# Map Provider Analysis for Carnforth Web A11y

## Current Provider Coverage

### Providers Currently Detected in maps.js

#### Iframe Detection (identifyMapProvider function)
1. **Google Maps** - `google.com/maps`
2. **Bing Maps** - `bing.com/maps`
3. **OpenStreetMap** - `openstreetmap.org`
4. **Waze** - `waze.com`
5. **Mapbox** - `mapbox.com`
6. **Leaflet** - `leafletjs.com` or `leaflet`
7. **ArcGIS** - `arcgis.com`
8. **HERE Maps** - `here.com`
9. **TomTom** - `tomtom.com`
10. **Apple Maps** - `maps.apple.com`

#### Div-based Detection (identifyDivMapProvider function)
1. **Mapbox** - Script/class detection
2. **Leaflet** - Script/class detection  
3. **Google Maps** - Script/class detection
4. **OpenLayers** - Script/class detection
5. **ArcGIS** - Script/class detection
6. **HERE Maps** - Script/class detection
7. **Mapfit** - Script detection
8. **TomTom** - Script/class detection
9. **Bing Maps** - Script detection
10. **Carto** - Script/class detection

#### Static Map Detection
1. **Google Static Maps** - `maps.googleapis.com`
2. **Mapbox Static Maps** - `api.mapbox.com`
3. **OpenStreetMap Static** - `staticmap.openstreetmap`
4. **Yandex Maps** - `static-maps.yandex`
5. **Bing Maps Static** - `dev.virtualearth.net`

## Recommended Additional Providers

### High Priority (Significant Global Usage)

1. **Baidu Maps** (百度地图)
   - Dominant in China
   - URLs: `map.baidu.com`, `api.map.baidu.com`
   - Script: `api.map.baidu.com/api`

2. **Amap/Gaode Maps** (高德地图) 
   - Major provider in China
   - URLs: `amap.com`, `webapi.amap.com`
   - Script: `webapi.amap.com/maps`

3. **Naver Maps**
   - Dominant in South Korea
   - URLs: `map.naver.com`, `openapi.naver.com/maps`
   - Script: `openapi.map.naver.com/openapi/v3/maps.js`

4. **Kakao Maps**
   - Popular in South Korea
   - URLs: `map.kakao.com`, `dapi.kakao.com`
   - Script: `dapi.kakao.com/v2/maps/sdk.js`

### Medium Priority (Regional/Specialized)

5. **2GIS**
   - Popular in Russia/CIS region
   - URLs: `2gis.com`, `maps.2gis.com`
   - Script: `maps.api.2gis.ru`

6. **Mapy.cz**
   - Czech Republic's main mapping service
   - URLs: `mapy.cz`, `api.mapy.cz`
   - Script: `api.mapy.cz/loader.js`

7. **Maptiler**
   - Cloud mapping platform
   - URLs: `maptiler.com`, `api.maptiler.com`
   - Script: `cdn.maptiler.com/maptiler-sdk-js`

8. **ViaMichelin**
   - European route planning
   - URLs: `viamichelin.com`, `maps.viamichelin.com`

9. **Ordnance Survey**
   - UK's national mapping agency
   - URLs: `ordnancesurvey.co.uk`, `api.os.uk`

### Low Priority (Niche/Legacy)

10. **Stamen**
    - Artistic map tiles
    - URLs: `stamen.com`, `tiles.stamen.com`

11. **Thunderforest**
    - OpenStreetMap styles
    - URLs: `thunderforest.com`

12. **IGN Géoportail**
    - French national mapping
    - URLs: `geoportail.gouv.fr`

13. **Sygic**
    - Navigation focus
    - URLs: `sygic.com`, `maps.sygic.com`

## Implementation Recommendations

### 1. Update identifyMapProvider() function:

```javascript
// Add to existing provider checks:
if (srcLower.includes('map.baidu.com') || srcLower.includes('api.map.baidu.com')) return 'Baidu Maps';
if (srcLower.includes('amap.com') || srcLower.includes('webapi.amap.com')) return 'Amap';
if (srcLower.includes('map.naver.com') || srcLower.includes('openapi.naver.com')) return 'Naver Maps';
if (srcLower.includes('map.kakao.com') || srcLower.includes('dapi.kakao.com')) return 'Kakao Maps';
if (srcLower.includes('2gis.com') || srcLower.includes('maps.2gis.com')) return '2GIS';
if (srcLower.includes('mapy.cz') || srcLower.includes('api.mapy.cz')) return 'Mapy.cz';
if (srcLower.includes('maptiler.com') || srcLower.includes('api.maptiler.com')) return 'Maptiler';
if (srcLower.includes('viamichelin.com')) return 'ViaMichelin';
if (srcLower.includes('ordnancesurvey.co.uk') || srcLower.includes('api.os.uk')) return 'Ordnance Survey';
```

### 2. Update identifyDivMapProvider() pageScripts:

```javascript
const pageScripts = {
  // ... existing providers ...
  'Baidu Maps': document.querySelector('script[src*="api.map.baidu.com"]') !== null,
  'Amap': document.querySelector('script[src*="webapi.amap.com/maps"]') !== null,
  'Naver Maps': document.querySelector('script[src*="openapi.map.naver.com"]') !== null,
  'Kakao Maps': document.querySelector('script[src*="dapi.kakao.com"]') !== null,
  '2GIS': document.querySelector('script[src*="maps.api.2gis.ru"]') !== null,
  'Mapy.cz': document.querySelector('script[src*="api.mapy.cz"]') !== null,
  'Maptiler': document.querySelector('script[src*="cdn.maptiler.com"]') !== null,
  'Ordnance Survey': document.querySelector('script[src*="api.os.uk"]') !== null
};
```

### 3. Update interactiveProviders array:

```javascript
const interactiveProviders = [
  // ... existing providers ...
  'map.baidu.com',
  'amap.com',
  'map.naver.com', 
  'map.kakao.com',
  '2gis.com',
  'mapy.cz',
  'maptiler.com'
];
```

### 4. Update static map detection:

```javascript
// Add to static map provider detection
if (src.includes('restapi.amap.com/v3/staticmap')) provider = 'Amap Static';
if (src.includes('map.baidu.com/staticimage')) provider = 'Baidu Static Maps';
if (src.includes('naveropenapi.apigw.ntruss.com/map-static')) provider = 'Naver Static Maps';
```

## Testing Considerations

1. **Internationalization**: Many of these providers serve content in non-Latin scripts (Chinese, Korean, Cyrillic)
2. **API Keys**: Some providers require API keys even for basic embeds
3. **Regional Restrictions**: Some providers may have geographic restrictions
4. **Different Embed Patterns**: Each provider may have unique embed URL structures

## Fixture Updates Needed

The comprehensive fixture file should be updated to include examples of these additional providers, particularly the high-priority ones that have significant global usage.

## Conclusion

The current implementation covers most major Western map providers well. Adding support for Asian providers (Baidu, Amap, Naver, Kakao) would significantly improve global coverage, as these are dominant in their respective markets. The other providers would add value for specific regional or specialized use cases.