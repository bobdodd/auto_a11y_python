# Failing Fixtures Checklist

**Generated:** October 23, 2025
**Status:** Partial run (89 of 412 tests completed before system crash)
**Passed:** 9
**Failed:** 80

⚠️ **Note:** The test script caused system memory exhaustion and crashed after 89 tests. Many AI_ tests are expected to fail as they are not yet implemented.

---

## How to Test Individual Fixtures

```bash
source venv/bin/activate
python test_fixtures.py --code <CODE_NAME>
```

---

## Failed Fixtures (Need Fixing)

### AI Tests (Not Yet Implemented)
- [ ] AI_ErrAccordionWithoutARIA
- [ ] AI_ErrAlertWithoutARIA
- [ ] AI_ErrAmbiguousLinkText
- [ ] AI_ErrAudioWithoutTranscript
- [ ] AI_ErrAutocompleteWithoutARIA
- [ ] AI_ErrAutoplayMedia
- [ ] AI_ErrBreadcrumbsWithoutARIA
- [ ] AI_ErrCardWithoutARIA
- [ ] AI_ErrCarouselWithoutARIA
- [ ] AI_ErrCheckboxGroupWithoutARIA
- [ ] AI_ErrClickableWithoutKeyboard
- [ ] AI_ErrDatePickerWithoutARIA
- [ ] AI_ErrDialogMissingRole
- [ ] AI_ErrDisclosureWithoutARIA
- [ ] AI_ErrDropdownWithoutARIA
- [ ] AI_ErrFeedWithoutARIA
- [ ] AI_ErrFlashingContent
- [ ] AI_ErrIframeMissingTitle
- [ ] AI_ErrInlineFrameMissingTitle
- [ ] AI_ErrLinkNoTarget
- [ ] AI_ErrLiveRegionWithoutARIA
- [ ] AI_ErrMapWithoutARIA
- [ ] AI_ErrMeterWithoutARIA
- [ ] AI_ErrModalWithoutARIA
- [ ] AI_ErrModalWithoutFocusTrap
- [ ] AI_ErrMotionWithoutPreference
- [ ] AI_ErrNavBurgerWithoutARIA
- [ ] AI_ErrNavWithoutSkipLink
- [ ] AI_ErrNotificationWithoutARIA
- [ ] AI_ErrOrientationLocked
- [ ] AI_ErrPaginationWithoutARIA
- [ ] AI_ErrProgressWithoutARIA
- [ ] AI_ErrRadioGroupWithoutARIA
- [ ] AI_ErrSearchWithoutARIA
- [ ] AI_ErrSelectWithoutARIA
- [ ] AI_ErrSliderWithoutARIA
- [ ] AI_ErrSpinbuttonWithoutARIA
- [ ] AI_ErrStatusWithoutARIA
- [ ] AI_ErrSvgMissingRole
- [ ] AI_ErrTabContentNotDescribed
- [ ] AI_ErrTabindexGreaterThanZero
- [ ] AI_ErrTableCaptionVerbose
- [ ] AI_ErrTableMissingCaptionOrSummary
- [ ] AI_ErrTargetSizeTooSmall
- [ ] AI_ErrTextSpacingFixed
- [ ] AI_ErrTimeLimitNoControl
- [ ] AI_ErrTimingNotAdjustable
- [ ] AI_ErrToggleWithoutARIA
- [ ] AI_ErrTreeViewWithoutARIA
- [ ] AI_ErrVideoControlsMissing
- [ ] AI_ErrVideoWithoutCaptions
- [ ] AI_WarnAmbiguousAriaLabel
- [ ] AI_WarnButtonRoleOnDiv
- [ ] AI_WarnClickableDiv
- [ ] AI_WarnContentNotZoomable
- [ ] AI_WarnDivUsedAsButton
- [ ] AI_WarnDivUsedAsHeading
- [ ] AI_WarnEmptyButton
- [ ] AI_WarnEmptyHeading
- [ ] AI_WarnExcessiveTabindex
- [ ] AI_WarnGenericARIALabel
- [ ] AI_WarnHeadingSkipped
- [ ] AI_WarnLinkGenericText
- [ ] AI_WarnLinkNoDescriptiveText
- [ ] AI_WarnLinkNotDescriptive
- [ ] AI_WarnLinkUnderlineRemoved
- [ ] AI_WarnMultipleH1
- [ ] AI_WarnNoDoctype
- [ ] AI_WarnRedundantARIARole
- [ ] AI_WarnTabindexZero
- [ ] AI_WarnTextNotScalable
- [ ] AI_WarnVideoWithoutCaptions
- [ ] AI_WarnVideoWithoutTranscript

### Standard Tests (Actual Failures)
- [ ] DiscoAsideFound
- [ ] DiscoFontFound
- [ ] DiscoFooterFound
- [ ] DiscoFormOnPage
- [ ] DiscoFoundInlineSvg
- [ ] DiscoFoundJS
- [ ] DiscoFoundSvgImage
- [ ] DiscoHeaderFound
- [ ] DiscoHeadingWithID

---

## Passed Tests (Working Correctly) ✅
- [x] ErrButtonMissingAccessibleName
- [x] ErrClickToCloseNoKeyboard
- [x] ErrColorContrastFail
- [x] ErrColorContrastIssue
- [x] ErrColorOnlyUsedForMeaning
- [x] ErrDocumentMissingLang
- [x] ErrDuplicateFormLabel
- [x] ErrDuplicateNavNames
- [x] ErrEventMouseOnlyNoKeyboard

---

## Tests Not Yet Run (323 remaining)

Due to system crash, 323 fixture codes were not tested. To complete testing:

1. Fix the memory issue in test_fixtures.py (ensure browsers are properly closed)
2. Run remaining tests in smaller batches
3. Consider testing by category instead of all at once:
   ```bash
   python test_fixtures.py --category Images
   python test_fixtures.py --category Forms
   python test_fixtures.py --category Links
   # etc.
   ```

---

## Summary Statistics

**Completed:** 89 / 412 (21.6%)
**Pass Rate (of completed):** 10.1% (9 passed, 80 failed)
**Known Issues:** Most AI_ tests are not implemented yet
**Recommended Action:** Fix memory leak, then test remaining codes in batches
