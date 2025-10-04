# Fixture Testing Quick Reference

## Common Commands

### Test by Type (Fastest Development Testing)
```bash
python test_fixtures.py --type Disco    # Discovery tests (~5 min)
python test_fixtures.py --type Err      # Error tests
python test_fixtures.py --type Warn     # Warning tests
python test_fixtures.py --type Info     # Info tests
```

### Test by Category/Touchpoint
```bash
python test_fixtures.py --category Forms
python test_fixtures.py --category Images
python test_fixtures.py --category Headings
python test_fixtures.py --category ColorsAndContrast
```

### Test Specific Error Code
```bash
python test_fixtures.py --code DiscoFormOnPage
python test_fixtures.py --code ErrNoAlt
python test_fixtures.py --code WarnHeadingOver60CharsLong
```

### Quick Tests
```bash
python test_fixtures.py --limit 20               # Smoke test (first 20)
python test_fixtures.py --type Err --limit 10    # First 10 errors
```

### Combine Filters
```bash
python test_fixtures.py --type Disco --category Forms
python test_fixtures.py --type Err --category Images --limit 5
```

### Full Test Suite
```bash
python test_fixtures.py    # All ~900 fixtures (~1 hour)
```

## View Results

### Web Interface
http://localhost:5001/testing/fixture-status

**Features:**
- Filter by: Status (All Pass, Partial Pass, All Fail)
- Filter by: Type (Err, Warn, Info, Disco)
- Search: By error code name
- See: Which fixtures passed/failed
- Click: "All Pass" button to see enabled tests

### Command Line
Results saved to:
- `fixture_test_results.json` - Local JSON file
- MongoDB database - For web interface

## Test Status Meanings

| Status | Icon | Production | Meaning |
|--------|------|------------|---------|
| **All Pass** | ✅ | ENABLED | All fixtures pass - test is reliable |
| **Partial Pass** | ⚠️ | DISABLED | Some fail - test has bugs/false positives |
| **All Fail** | ❌ | DISABLED | All fail - test not implemented or broken |

## Quick Workflow

### Fixing a Broken Test
```bash
# 1. Test just that code
python test_fixtures.py --code ErrNoAlt

# 2. Fix the test in Python
# Edit: auto_a11y/testing/touchpoint_tests/test_images.py

# 3. Retest (Flask auto-reloads)
python test_fixtures.py --code ErrNoAlt

# 4. Verify in web UI
# http://localhost:5001/testing/fixture-status
```

### Testing Your Changes
```bash
# Test the category you changed
python test_fixtures.py --category Forms

# Or test the type you changed
python test_fixtures.py --type Disco

# Or test the specific code
python test_fixtures.py --code DiscoFormOnPage
```

## Filter Options Summary

| Filter | Option | Example |
|--------|--------|---------|
| **Type** | `--type` | `--type Disco` |
| **Category** | `--category` | `--category Forms` |
| **Error Code** | `--code` | `--code ErrNoAlt` |
| **Limit** | `--limit` | `--limit 20` |

## Available Types
- `Err` - Errors (high severity)
- `Warn` - Warnings (medium severity)
- `Info` - Information (low severity)
- `Disco` - Discovery (element detection)
- `AI` - AI-powered tests (requires API key)

## Common Categories
AccessibleNames, Animation, ARIA, Buttons, ColorsAndContrast, Focus, Fonts, Forms, Headings, IFrames, Images, Interactive, JavaScript, Keyboard, Landmarks, Language, Links, Lists, Maps, Media, Metadata, Modals, Navigation, Page, PDF, ReadingOrder, Style, SVG, Tabindex, Tables, Typography

## Tips

✅ **DO:**
- Use filters during development for fast iteration
- Test specific codes after fixing bugs
- Run `--type Disco` to quickly validate Discovery tests
- Check web interface for visual status overview

❌ **DON'T:**
- Run full suite every time (takes 1 hour)
- Commit without testing your changes
- Enable tests that show "Partial Pass" (false positives)

## Need Help?

📖 Full docs: `docs/FIXTURE_TESTING.md`
🌐 Web interface: http://localhost:5001/testing/fixture-status
