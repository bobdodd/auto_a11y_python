# Inaccessible Fonts Configuration

## Overview

The Auto A11y system includes a sophisticated two-tier font accessibility testing system that flags fonts which are difficult to read for users with dyslexia, low vision, or reading disabilities. The system uses research-backed defaults that can be customized per project.

## Architecture

### Two-Tier Design

1. **System Defaults** - Centrally maintained, research-backed list of problematic fonts
2. **Project Overrides** - Per-project customization to add, exclude, or disable defaults

This design ensures:
- ✅ Easy to maintain a single source of truth for accessibility research
- ✅ Projects can customize without modifying system files
- ✅ Projects can exclude fonts if brand requirements mandate them
- ✅ Projects can add custom fonts specific to their needs

---

## System Defaults

### Location
**File:** `auto_a11y/config/inaccessible_fonts_defaults.json`

### Structure
```json
{
  "version": "1.0.0",
  "last_updated": "2025-10-09",
  "description": "Default list of fonts that are difficult to read...",
  "sources": [
    "https://dyslexichelp.org/what-fonts-should-dyslexics-avoid/",
    "https://www.section508.gov/develop/fonts-typography/",
    "https://webaim.org/techniques/fonts/"
  ],
  "categories": {
    "script_cursive": {
      "description": "Script and cursive fonts with connected letters...",
      "fonts": ["brush script", "comic sans ms", "bradley hand", ...]
    },
    "decorative": {
      "description": "Highly decorative fonts that prioritize aesthetics...",
      "fonts": ["curlz", "papyrus", "jokerman", ...]
    },
    "narrow_condensed": {
      "description": "Narrow and condensed fonts with tight letter spacing...",
      "fonts": ["arial narrow", "impact"]
    },
    "blackletter_gothic": {
      "description": "Historical blackletter and gothic fonts...",
      "fonts": ["old english", "blackletter", "fraktur", ...]
    }
  }
}
```

### Font Categories

#### 1. Script/Cursive Fonts
**Why Problematic:** Connected letters make it difficult to distinguish individual characters, particularly problematic for users with dyslexia.

**Examples:**
- Brush Script, Brush Script MT
- Comic Sans, Comic Sans MS
- Bradley Hand, Bradley Hand ITC
- Lucida Handwriting, Lucida Calligraphy
- Freestyle Script, French Script, Edwardian Script

#### 2. Decorative Fonts
**Why Problematic:** Highly decorative fonts prioritize aesthetics over readability, making them difficult to read for extended periods.

**Examples:**
- Curlz, Curlz MT
- Papyrus
- Jokerman, Ravie, Chiller
- Magneto, Algerian, Stencil
- Showcard Gothic, Broadway, Bauhaus 93

#### 3. Narrow/Condensed Fonts
**Why Problematic:** Tight letter spacing reduces legibility, especially for users with low vision who need clear character distinction.

**Examples:**
- Arial Narrow
- Impact (when used for body text)

#### 4. Blackletter/Gothic Fonts
**Why Problematic:** Complex historical letterforms are extremely difficult to read for modern readers.

**Examples:**
- Old English, Old English Text MT
- Blackletter
- Fraktur
- Blackadder ITC

### Maintaining System Defaults

**To add a font to the system defaults:**

1. Open `auto_a11y/config/inaccessible_fonts_defaults.json`
2. Add the font name (lowercase) to the appropriate category
3. Update the `last_updated` field
4. Optionally add research sources to `sources` array

**Example:**
```json
{
  "decorative": {
    "description": "...",
    "fonts": [
      "curlz",
      "papyrus",
      "my new problematic font"  // Add here
    ]
  }
}
```

**Note:** All font names must be lowercase for consistent matching.

---

## Project-Level Configuration

### Accessing Configuration

1. Navigate to your project
2. Click **Edit Project**
3. Scroll to **Inaccessible Fonts Configuration** section

### Configuration Options

#### 1. Use System Default List
**Checkbox:** "Use system default inaccessible fonts list"

- ✅ **Checked (Default):** Project uses all 50+ system defaults
- ❌ **Unchecked:** Project ignores system defaults (only uses custom additions)

**Use Case:** Uncheck if you want complete control over which fonts are flagged, without any system defaults.

---

#### 2. Additional Fonts to Flag
**Textarea:** Add project-specific fonts to flag as inaccessible

**Format:** One font name per line, lowercase

**Example:**
```
custom corporate font
brand display font
special heading typeface
```

**Use Case:** Your brand uses a custom font that you know is problematic, but it's not in the system defaults.

---

#### 3. Fonts to Exclude from Checking
**Textarea:** Remove specific fonts from the system default list

**Format:** One font name per line, lowercase

**Example:**
```
comic sans ms
papyrus
```

**Use Case:** Your brand guidelines require using Comic Sans (for a children's website, for example), so you need to exclude it from being flagged.

---

#### 4. View System Defaults
**Accordion:** Collapsible section showing all system default fonts

Displays:
- Script/Cursive fonts (16 fonts)
- Decorative fonts (16 fonts)
- Narrow/Condensed fonts (2 fonts)
- Blackletter/Gothic fonts (5 fonts)

---

## Configuration Storage

Project configuration is stored in the `config` field of the Project document:

```python
project.config = {
    'font_accessibility': {
        'use_defaults': True,  # Boolean
        'additional_inaccessible_fonts': ['custom font'],  # List[str]
        'excluded_fonts': ['comic sans ms']  # List[str]
    }
}
```

---

## How Testing Works

### Test Execution Flow

1. **Page is tested** → `test_fonts(page, project_config)` is called
2. **Configuration loading:**
   - If `project_config` is provided → Load project-specific settings
   - If no `project_config` → Use system defaults only
3. **Font list assembly:**
   - Start with system defaults (if enabled)
   - Add `additional_inaccessible_fonts`
   - Remove `excluded_fonts`
4. **Font detection:**
   - Scan all elements on the page
   - Extract computed font-family for each element
   - Check if primary font is in the inaccessible list
5. **Error reporting:**
   - Report `ErrInaccessibleFont` for each problematic font
   - Include font category and description
   - List all sizes the font is used at

### Code Reference

**Test Function:** `auto_a11y/testing/touchpoint_tests/test_fonts.py`

```python
async def test_fonts(page, project_config: Optional[Dict[str, Any]] = None):
    """
    Test fonts and typography for accessibility requirements

    Args:
        page: Pyppeteer page object
        project_config: Optional project configuration dict
    """
    from auto_a11y.utils.font_config import font_config_manager

    # Load appropriate font list based on project config
    if project_config:
        fonts = font_config_manager.get_project_inaccessible_fonts(project_config)
    else:
        fonts = font_config_manager.get_default_inaccessible_fonts()

    # ... test execution
```

---

## Configuration Examples

### Example 1: Use All Defaults
**Scenario:** Standard project, use research-backed defaults

**Configuration:**
- ✅ Use system default list: **Checked**
- Additional fonts: *(empty)*
- Excluded fonts: *(empty)*

**Result:** Tests against all 50+ default fonts

---

### Example 2: Brand Exception
**Scenario:** Brand requires Comic Sans for children's content

**Configuration:**
- ✅ Use system default list: **Checked**
- Additional fonts: *(empty)*
- Excluded fonts:
  ```
  comic sans
  comic sans ms
  ```

**Result:** Tests against all defaults EXCEPT Comic Sans

---

### Example 3: Custom Font Addition
**Scenario:** Company uses "Corporate Display Bold" which is hard to read

**Configuration:**
- ✅ Use system default list: **Checked**
- Additional fonts:
  ```
  corporate display bold
  ```
- Excluded fonts: *(empty)*

**Result:** Tests against all defaults PLUS the custom corporate font

---

### Example 4: Complete Custom Control
**Scenario:** Want only specific fonts flagged, no defaults

**Configuration:**
- ❌ Use system default list: **Unchecked**
- Additional fonts:
  ```
  custom problematic font 1
  custom problematic font 2
  custom problematic font 3
  ```
- Excluded fonts: *(empty)*

**Result:** Tests ONLY against the 3 custom fonts listed

---

## Error Reporting

### Error Code
**`ErrInaccessibleFont`**

**Type:** Error (High Impact)
**WCAG Criteria:** 1.4.8 (Visual Presentation)

### Error Details

When an inaccessible font is detected, the error includes:

```javascript
{
  err: 'ErrInaccessibleFont',
  type: 'error',
  cat: 'fonts',
  fontName: 'Comic Sans MS',
  category: 'script_cursive',
  reason: 'Script and cursive fonts with connected letters are difficult to distinguish...',
  fontSizes: ['16px', '18px', '24px'],
  sizeCount: 3,
  description: "Font 'Comic Sans MS' is difficult to read. Script and cursive fonts..."
}
```

### Error Message Template

> **Font '{fontName}' is difficult to read**
>
> Using {fontName} font which is known to be difficult to read.
>
> This font is categorized as {category}: {reason}. Research shows these fonts are harder to read, especially for users with dyslexia or low vision.
>
> **Remediation:** Replace {fontName} with a clear, readable sans-serif font like Arial, Verdana, Helvetica, or Tahoma. Avoid decorative, script, cursive, or highly stylized fonts for body text.

---

## Technical Implementation

### Files Modified

1. **`auto_a11y/config/inaccessible_fonts_defaults.json`**
   - System default font list with categories and descriptions

2. **`auto_a11y/utils/font_config.py`**
   - `FontConfigManager` class
   - Methods for loading defaults and merging with project config

3. **`auto_a11y/testing/touchpoint_tests/test_fonts.py`**
   - Updated to accept `project_config` parameter
   - Uses `FontConfigManager` to get appropriate font list

4. **`auto_a11y/web/templates/projects/edit.html`**
   - Added UI section for font configuration
   - Checkboxes, textareas, and accordion for defaults

5. **`auto_a11y/web/routes/projects.py`**
   - Backend to save font configuration
   - Parses textarea input and stores in `project.config`

6. **`auto_a11y/config/touchpoint_tests.py`**
   - Updated touchpoint mapping: `WarnFontNotInRecommenedListForA11y` → `ErrInaccessibleFont`

7. **`auto_a11y/reporting/issue_descriptions_enhanced.py`**
   - Updated issue descriptions with new error details

8. **Fixtures:**
   - `Fixtures/Fonts/ErrInaccessibleFont_001_violations_basic.html` (positive test)
   - `Fixtures/Fonts/ErrInaccessibleFont_002_correct_accessible.html` (negative test)

---

## API Reference

### FontConfigManager

**Location:** `auto_a11y/utils/font_config.py`

#### Methods

##### `get_default_inaccessible_fonts() -> Set[str]`
Returns the system default list of inaccessible fonts.

**Returns:** Set of lowercase font names

**Example:**
```python
from auto_a11y.utils.font_config import font_config_manager

defaults = font_config_manager.get_default_inaccessible_fonts()
# Returns: {'comic sans ms', 'papyrus', 'curlz', ...}
```

---

##### `get_project_inaccessible_fonts(project_config: Dict) -> Set[str]`
Returns the complete font list for a project, merging defaults with project settings.

**Args:**
- `project_config`: Project configuration dictionary

**Returns:** Set of lowercase font names

**Example:**
```python
project_config = {
    'font_accessibility': {
        'use_defaults': True,
        'additional_inaccessible_fonts': ['custom font'],
        'excluded_fonts': ['comic sans ms']
    }
}

fonts = font_config_manager.get_project_inaccessible_fonts(project_config)
# Returns: All defaults except Comic Sans, plus 'custom font'
```

---

##### `is_font_inaccessible(font_name: str, project_config: Optional[Dict] = None) -> bool`
Check if a specific font is considered inaccessible.

**Args:**
- `font_name`: Font name to check
- `project_config`: Optional project configuration

**Returns:** True if font is inaccessible

**Example:**
```python
is_bad = font_config_manager.is_font_inaccessible('Comic Sans MS')
# Returns: True
```

---

##### `get_font_category(font_name: str) -> Optional[str]`
Get the category of an inaccessible font.

**Args:**
- `font_name`: Font name to look up

**Returns:** Category name or None

**Example:**
```python
category = font_config_manager.get_font_category('Comic Sans MS')
# Returns: 'script_cursive'
```

---

## Best Practices

### For System Administrators

1. **Keep defaults updated** - Review accessibility research annually and update `inaccessible_fonts_defaults.json`
2. **Document sources** - Always include research links when adding new fonts
3. **Use lowercase** - All font names must be lowercase for consistent matching
4. **Test after changes** - Run fixture tests after modifying defaults

### For Project Managers

1. **Start with defaults** - Most projects should use system defaults
2. **Document exceptions** - If excluding fonts, document why in project description
3. **Review brand fonts** - If brand uses custom fonts, test them for readability
4. **Regular audits** - Periodically review excluded fonts to ensure they're still necessary

### For Developers

1. **Pass project_config** - Always pass project configuration when running tests
2. **Check fixtures** - Verify fixtures pass before deploying changes
3. **Log configuration** - Test logs show which font list is being used
4. **Handle missing config** - Code gracefully falls back to defaults

---

## Troubleshooting

### Issue: Font not being flagged

**Possible causes:**
1. Font name mismatch (check case sensitivity)
2. Font excluded in project settings
3. System defaults disabled
4. Browser using fallback font

**Solution:**
- Check computed font-family in browser DevTools
- Verify font name in configuration (must be lowercase)
- Check project settings for exclusions

---

### Issue: Too many fonts flagged

**Possible causes:**
1. System defaults too aggressive for your use case
2. Brand fonts not properly excluded

**Solution:**
- Add brand fonts to "Fonts to Exclude" in project settings
- Consider which fonts are truly necessary for your brand

---

### Issue: Configuration not taking effect

**Possible causes:**
1. Project config not saved properly
2. Test not receiving project_config parameter
3. Cache not cleared

**Solution:**
- Verify configuration saved in project edit page
- Check test runner passes project_config
- Restart Flask server to clear caches

---

## Migration Guide

### Upgrading from WarnFontNotInRecommenedListForA11y

**Old System:**
- Warning-level issue
- Tested for fonts IN a recommended list (negative test)
- No project-level configuration

**New System:**
- Error-level issue (higher severity)
- Tests for fonts NOT to use (positive test - easier to prove)
- Project-level configuration available

**Migration Steps:**

1. **Database cleanup** - Old warning entries automatically cleaned up
2. **Fixture updates** - Fixtures renamed to `ErrInaccessibleFont_*`
3. **No action required** - System automatically uses new error code

---

## Research References

The system defaults are based on accessibility research from:

1. **Dyslexic Help** - https://dyslexichelp.org/what-fonts-should-dyslexics-avoid/
2. **Section 508** - https://www.section508.gov/develop/fonts-typography/
3. **WebAIM** - https://webaim.org/techniques/fonts/
4. **Scope UK** - https://business.scope.org.uk/font-accessibility-and-readability-the-basics/

---

## Future Enhancements

Potential improvements for future versions:

1. **Font family detection** - Test font-family stack, not just primary font
2. **Context-aware testing** - Allow decorative fonts for headings but not body text
3. **AI-powered detection** - Use visual analysis to detect custom inaccessible fonts
4. **Font metrics** - Analyze x-height, letter spacing, and other metrics
5. **Import/Export** - Share font configurations between projects
6. **Font recommendations** - Suggest accessible alternatives for flagged fonts

---

## Support

For questions or issues:
- **Documentation:** This file
- **Code:** `auto_a11y/utils/font_config.py`, `auto_a11y/testing/touchpoint_tests/test_fonts.py`
- **Issues:** Report bugs via GitHub issues

---

**Version:** 1.0.0
**Last Updated:** 2025-10-09
**Author:** Auto A11y Development Team