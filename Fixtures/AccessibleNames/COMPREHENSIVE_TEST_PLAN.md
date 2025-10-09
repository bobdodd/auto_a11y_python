# Comprehensive ErrMissingAccessibleName Test Plan

## Categories to Test

### 1. HTML Interactive Elements
- `<button>` ✓ (partially covered)
- `<input>` all types ✓ (partially covered)
- `<textarea>` ✓ (partially covered)
- `<select>` ✓ (partially covered)
- `<a href>` ✓ (covered)
- `<img>` ✓ (covered)
- `<iframe>` ✓ (mentioned in docs)
- `<area>` (image map) ❌ NOT COVERED
- `<dialog>` ❌ NOT COVERED
- `<summary>` (details/summary) ❌ NOT COVERED

### 2. ARIA Widget Roles (All from WAI-ARIA 1.2)

#### Composite Widget Roles
- `role="combobox"` ✓ (in test)
- `role="grid"` ❌ NOT COVERED
- `role="gridcell"` ❌ NOT COVERED
- `role="listbox"` ✓ (in test)
- `role="menu"` ✓ (in test)
- `role="menubar"` ✓ (in test)
- `role="radiogroup"` ❌ NOT COVERED
- `role="tablist"` ❌ NOT COVERED
- `role="tree"` ✓ (in test)
- `role="treegrid"` ❌ NOT COVERED

#### Standalone Widget Roles
- `role="button"` ✓ (in test)
- `role="checkbox"` ✓ (in test)
- `role="menuitem"` ✓ (in test)
- `role="menuitemcheckbox"` ❌ NOT COVERED
- `role="menuitemradio"` ❌ NOT COVERED
- `role="option"` ❌ NOT COVERED
- `role="radio"` ✓ (in test)
- `role="scrollbar"` ❌ NOT COVERED
- `role="searchbox"` ❌ NOT COVERED
- `role="separator"` (when focusable) ❌ NOT COVERED
- `role="slider"` ❌ NOT COVERED
- `role="spinbutton"` ❌ NOT COVERED
- `role="switch"` ❌ NOT COVERED
- `role="tab"` ✓ (in test)
- `role="tabpanel"` ✓ (in test)
- `role="textbox"` ✓ (in test)
- `role="treeitem"` ✓ (in test)

#### Additional Interactive Roles
- `role="link"` ✓ (in test)
- `role="progressbar"` ❌ NOT COVERED
- `role="scrollbar"` ❌ NOT COVERED
- `role="searchbox"` ❌ NOT COVERED
- `role="toolbar"` ✓ (in test)

### 3. Elements with Event Handlers (Make Interactive)
- `<div onclick="...">` ❌ NOT COVERED
- `<span onclick="...">` ❌ NOT COVERED
- `<div onkeydown="...">` ❌ NOT COVERED
- `<div tabindex="0" onclick="...">` ❌ NOT COVERED
- Elements with JavaScript event listeners ❌ NOT COVERED

### 4. Edge Cases
- Hidden elements (should not be tested) ❌ NOT COVERED
- Disabled elements ❌ NOT COVERED
- aria-hidden="true" elements ❌ NOT COVERED
- Decorative images (alt="") ✓ (covered)
- Links with only icon/image children ✓ (covered)
- Form inputs in fieldsets with legends ❌ NOT COVERED
- Custom elements with widget roles ❌ NOT COVERED

## Fixture Files Needed

### High Priority (Core Interactive Elements)
1. `_012_violations_aria_widget_roles.html` - All ARIA widget roles without names
2. `_013_correct_aria_widget_roles.html` - All ARIA widget roles with proper names
3. `_014_violations_event_handlers.html` - Divs/spans with onclick but no role/name
4. `_015_correct_event_handlers.html` - Interactive divs with proper roles and names
5. `_016_violations_composite_widgets.html` - Combobox, listbox, menu without names
6. `_017_correct_composite_widgets.html` - Composite widgets with proper names

### Medium Priority (Comprehensive Coverage)
7. `_018_violations_input_types.html` - All input types without labels
8. `_019_correct_input_types.html` - All input types with labels
9. `_020_violations_dialog_summary.html` - Dialog and summary without names
10. `_021_correct_dialog_summary.html` - Dialog and summary with names
11. `_022_violations_switches_sliders.html` - Switch, slider, spinbutton without names
12. `_023_correct_switches_sliders.html` - Switch, slider, spinbutton with names

### Lower Priority (Edge Cases)
13. `_024_correct_hidden_disabled.html` - Hidden/disabled elements (should pass)
14. `_025_violations_image_maps.html` - Area elements without alt
15. `_026_correct_image_maps.html` - Area elements with alt
16. `_027_violations_custom_widgets.html` - Custom elements with roles but no names
17. `_028_correct_custom_widgets.html` - Custom elements properly labeled

## Test Enhancement Needed

The test itself may need updates to check:
- Elements with event handlers (onclick, onkeydown, etc.)
- More comprehensive ARIA role coverage
- Role="separator" when focusable (tabindex >= 0)
- Custom elements with widget roles