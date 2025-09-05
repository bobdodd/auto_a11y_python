# JavaScript Test Metadata Analysis

## Issues with Metadata Fields

Based on scanning all JavaScript test files, here are all the issues that return metadata:

### Color Tests (color.js)
- **ErrTextContrastAA/AAA, ErrLargeTextContrastAA/AAA**
  - `fg`: foreground color hex
  - `bg`: background color hex  
  - `ratio`: contrast ratio
  - `fontSize`: font size in pixels
  - `isBold`: boolean for bold text
  - `isLargeText`: boolean for large text
  - `wcagLevel`: AA or AAA
  - `passesAA`: boolean
  - `passesAAA`: boolean

### Font Tests (fonts.js)
- **DiscoFontFound**
  - `found`: font name detected
- **WarnFontNotInRecommenedListForA11y**
  - `found`: font name not recommended
- **WarnFontsizeIsBelow16px**
  - `fontSize`: actual font size in pixels

### Forms Tests (forms2.js, forms_enhanced.js)
- **ErrLabelContainsMultipleFields**
  - `count`: number of fields in label
- **InfoFieldLabelledUsingAriaLabel**
  - `found`: aria-label value
- **WarnFieldLabelledByMultipleElements**
  - `count`: number of labelling elements
- **ErrFieldAriaRefDoesNotExist**
  - `found`: invalid aria reference ID
- **WarnFieldLabelledByElementThatIsNotALabel**
  - `found`: element ID that's not a label
- **forms_ErrInputMissingLabel**
  - `name`: input name attribute
  - `message`: descriptive message
- **forms_WarnGenericButtonText**
  - `text`: actual button text
  - `message`: descriptive message
- **forms_ErrNoButtonText**
  - No specific metadata

### Headings Tests (headings.js)
- **ErrEmptyHeading**
  - `text`: trimmed text content (first 50 chars)
- **WarnHeadingOver60CharsLong**
  - `text`: heading text
- **ErrSkippedHeadingLevel**
  - `level`: heading level that was skipped
  - `skippedFrom`: previous level
  - `skippedTo`: current level
- **ErrMultipleH1**
  - `count`: number of H1 elements
- **WarnNoH1**
  - No specific metadata

### Landmarks Tests (landmarks.js)
- **ErrMultipleMainLandmarks**
  - `count`: number of main landmarks
- **ErrMultipleBannerLandmarks**
  - `count`: number of banner landmarks
- **ErrMultipleContentinfoLandmarks**
  - `count`: number of footer landmarks

### Language Tests (language.js)
- **ErrInvalidLanguageCode**
  - `found`: invalid language code
- **WarnInvalidLangChange**
  - `found`: invalid language code

### Page Title Tests (pageTitle.js)
- **WarnPageTitleTooShort**
  - `found`: actual title text
  - `length`: title length
- **WarnPageTitleTooLong**
  - `found`: actual title text
  - `length`: title length
  - `title`: truncated title (60 chars + ...)
- **WarnMultipleTitleElements**
  - `count`: number of title elements

### Title Attribute Tests (titleAttr.js)
- **Various title attribute issues**
  - `title`: title attribute value
- **WarnIframeTitleNotDescriptive**
  - `title`: iframe title value

### Focus Tests (focus.js)
- No specific metadata fields beyond standard

### Images Tests (images.js)
- No specific metadata fields beyond standard

### SVG Tests (svg.js)
- No specific metadata fields beyond standard

### Tabindex Tests (tabindex.js)  
- No specific metadata fields beyond standard

## Summary of Metadata Fields to Add

The following issues need their templates updated with metadata placeholders:

1. **Font size issues** - Need `{fontSize}` placeholder
2. **Font detection** - Need `{found}` placeholder
3. **Form field counts** - Need `{count}` placeholder
4. **Heading levels** - Need `{level}`, `{skippedFrom}`, `{skippedTo}` placeholders
5. **Language codes** - Need `{found}` placeholder
6. **Title lengths** - Need `{found}`, `{length}` placeholders
7. **Multiple elements** - Need `{count}` placeholder
8. **Button text** - Need `{text}` placeholder
9. **ARIA references** - Need `{found}` placeholder
10. **Title attributes** - Need `{title}` placeholder