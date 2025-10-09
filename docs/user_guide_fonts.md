# User Guide: Inaccessible Fonts Configuration

## Quick Start

The Auto A11y system automatically detects fonts that are difficult to read for users with dyslexia, low vision, or reading disabilities. You can customize which fonts are flagged for each project.

---

## Accessing Font Settings

1. Navigate to your project
2. Click **"Edit Project"** button
3. Scroll to **"Inaccessible Fonts Configuration"** section
4. Make your changes
5. Click **"Update Project"** to save

---

## Configuration Options

### 1. Use System Defaults ✅

**What it does:** Includes 50+ research-backed problematic fonts (Comic Sans, Papyrus, Impact, Old English, etc.)

**Default:** Checked ✅

**When to uncheck:**
- You want complete control over which fonts are flagged
- You're building a custom list from scratch

**Recommendation:** ✅ Keep checked for most projects

---

### 2. Additional Fonts to Flag

**What it does:** Add fonts specific to your project that should be flagged

**Format:** One font name per line, lowercase

**Example:**
```
corporate display font
custom brand typeface
special heading font
```

**When to use:**
- Your brand uses a custom font that's hard to read
- You want to flag a font not in system defaults

---

### 3. Fonts to Exclude

**What it does:** Remove fonts from the system default list

**Format:** One font name per line, lowercase

**Example:**
```
comic sans ms
papyrus
```

**When to use:**
- Brand guidelines require a font that's normally flagged
- Building a children's website that uses Comic Sans
- Design system mandates a specific decorative font

---

## Common Scenarios

### Scenario 1: Standard Website
**"I want to use research-backed defaults with no exceptions"**

**Configuration:**
- ✅ Use system defaults: **Checked**
- Additional fonts: *(leave empty)*
- Excluded fonts: *(leave empty)*

**Result:** Flags 50+ problematic fonts based on accessibility research

---

### Scenario 2: Brand Exception
**"My brand requires Comic Sans for children's content"**

**Configuration:**
- ✅ Use system defaults: **Checked**
- Additional fonts: *(leave empty)*
- Excluded fonts:
  ```
  comic sans
  comic sans ms
  ```

**Result:** Flags all defaults except Comic Sans

---

### Scenario 3: Custom Corporate Font
**"Our company uses 'Acme Display' which is hard to read"**

**Configuration:**
- ✅ Use system defaults: **Checked**
- Additional fonts:
  ```
  acme display
  ```
- Excluded fonts: *(leave empty)*

**Result:** Flags all defaults + your custom font

---

### Scenario 4: Complete Custom Control
**"I only want to flag 3 specific fonts"**

**Configuration:**
- ❌ Use system defaults: **Unchecked**
- Additional fonts:
  ```
  problematic font 1
  problematic font 2
  problematic font 3
  ```
- Excluded fonts: *(leave empty)*

**Result:** Only flags the 3 fonts you specified

---

## What Gets Flagged?

The system checks the **primary font** (first in font-family stack) used on your website and compares it against the configured list.

### System Default Categories

#### Script/Cursive (16 fonts)
Why problematic: Connected letters are hard to distinguish
- Comic Sans, Brush Script, Bradley Hand, Lucida Handwriting, etc.

#### Decorative (16 fonts)
Why problematic: Aesthetics over readability
- Papyrus, Curlz, Jokerman, Ravie, Chiller, etc.

#### Narrow/Condensed (2 fonts)
Why problematic: Tight spacing reduces legibility
- Arial Narrow, Impact

#### Blackletter/Gothic (5 fonts)
Why problematic: Complex historical letterforms
- Old English, Fraktur, Blackletter

**View full list:** Click "View System Default Inaccessible Fonts List" in project settings

---

## Error Report

When an inaccessible font is detected:

**Error Code:** `ErrInaccessibleFont`

**Severity:** Error (High Impact)

**Message Example:**
> **Font 'Comic Sans MS' is difficult to read**
>
> This font is categorized as script/cursive: Script and cursive fonts with connected letters are difficult to distinguish, particularly problematic for users with dyslexia.
>
> **Fix:** Replace Comic Sans MS with Arial, Verdana, Helvetica, or Tahoma

---

## Tips & Best Practices

### ✅ DO

- **Start with defaults** - They're based on accessibility research
- **Document exceptions** - Note why you excluded fonts in project description
- **Use lowercase** - Always enter font names in lowercase
- **Test after changes** - Run tests after updating configuration
- **Be specific** - Include font variant if needed (e.g., "comic sans ms" not just "comic sans")

### ❌ DON'T

- **Don't disable defaults without reason** - Research-backed list catches most issues
- **Don't exclude many fonts** - If you're excluding 5+ fonts, reconsider your design
- **Don't use decorative fonts for body text** - Reserve for headings/logos only
- **Don't mix case** - Always lowercase (system won't match "Comic Sans MS")

---

## Troubleshooting

### "Font not being flagged but should be"

**Check:**
1. Is the font name spelled exactly as it appears in browser DevTools?
2. Did you use lowercase?
3. Is it excluded in project settings?
4. Are system defaults enabled?

**Solution:**
- Right-click element → Inspect → Check "Computed" tab → "font-family"
- Copy the exact name (lowercase) to Additional Fonts

---

### "Too many fonts being flagged"

**Check:**
1. Are brand fonts in the excluded list?
2. Do you really need those decorative fonts?

**Solution:**
- Add necessary brand fonts to "Fonts to Exclude"
- Consider using accessible fonts instead

---

### "Changes not taking effect"

**Check:**
1. Did you click "Update Project"?
2. Did you refresh the test page?

**Solution:**
- Save settings again
- Clear cache and re-run tests

---

## Getting Help

**View System Defaults:**
- In project settings, expand "View System Default Inaccessible Fonts List"

**Documentation:**
- Full technical docs: `docs/inaccessible_fonts_configuration.md`

**Support:**
- Contact your system administrator
- Report issues via your team's bug tracker

---

## Quick Reference Card

| Task | Configuration |
|------|--------------|
| Use research defaults | ✅ Use defaults, empty fields |
| Exclude brand font | ✅ Use defaults, add font to "Excluded" |
| Add custom font | ✅ Use defaults, add font to "Additional" |
| Custom list only | ❌ Uncheck defaults, add to "Additional" |
| No font checking | ❌ Uncheck defaults, leave fields empty |

---

**Version:** 1.0.0
**Last Updated:** 2025-10-09