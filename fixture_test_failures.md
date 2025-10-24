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
- [ ] **AI_ErrAccordionWithoutARIA**
  ```
  ❌ Failed: 3
  Success rate: 40.0%
  ```

- [ ] **AI_ErrAlertWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrAmbiguousLinkText**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrAudioWithoutTranscript**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrAutocompleteWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrAutoplayMedia**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrBreadcrumbsWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrCardWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrCarouselWithoutARIA**
  ```
  ❌ Failed: 3
  Success rate: 40.0%
  ```

- [ ] **AI_ErrCheckboxGroupWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrClickableWithoutKeyboard**
  ```
  ❌ Failed: 3
  Success rate: 25.0%
  ```

- [ ] **AI_ErrDatePickerWithoutARIA**
  ```
  ❌ Failed: 2
  Success rate: 0.0%
  ```

- [ ] **AI_ErrDialogMissingRole**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrDialogWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 0.0%
  ```

- [ ] **AI_ErrDisclosureWithoutARIA**
  ```
  ❌ Failed: 2
  Success rate: 0.0%
  ```

- [ ] **AI_ErrDropdownWithoutARIA**
  ```
  ❌ Failed: 3
  Success rate: 40.0%
  ```

- [ ] **AI_ErrFeedWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrFlashingContent**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrFormErrorNotAnnounced**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrHeadingLevelMismatch**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrIframeWithoutTitle**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrInteractiveElementIssue**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrLandmarkWithoutLabel**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrLinkWithoutText**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrLoadingStateNotAnnounced**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrMenuWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrMeterWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrMissingFocusIndicator**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrMissingInteractiveRole**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **AI_ErrMissingLiveRegion**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrMissingPageTitle**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrMissingSkipLink**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrModalFocusTrap**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrModalWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrMotionWithoutControl**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrNonSemanticButton**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **AI_ErrNotificationWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrOrientationLocked**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrPaginationWithoutARIA**
  ```
  ❌ Failed: 2
  Success rate: 0.0%
  ```

- [ ] **AI_ErrProgressBarWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrRadioGroupWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrReadingOrderMismatch**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **AI_ErrSearchWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrSkippedHeading**
  ```
  ❌ Failed: 3
  Success rate: 25.0%
  ```

- [ ] **AI_ErrSkippedHeading_01**
  ```
  ❌ Failed: 0
    print(f"  Success rate: {(success_count/len(fixtures)*100):.1f}%")
  ```

- [ ] **AI_ErrSkippedHeading_02**
  ```
  ❌ Failed: 0
    print(f"  Success rate: {(success_count/len(fixtures)*100):.1f}%")
  ```

- [ ] **AI_ErrSliderWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrSpinbuttonWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrTabpanelWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrTabsWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrTargetSizeTooSmall**
  ```
  ❌ Failed: 2
  Success rate: 0.0%
  ```

- [ ] **AI_ErrTextSpacingIssue**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrTimeLimitNoWarning**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrToggleWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrToggleWithoutState**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrTooltipWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrTreeViewWithoutARIA**
  ```
  ❌ Failed: 2
  Success rate: 0.0%
  ```

- [ ] **AI_ErrVideoWithoutCaptions**
  ```
  ❌ Failed: 2
  Success rate: 0.0%
  ```

- [ ] **AI_ErrVisualHeadingNotMarked**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_ErrZoomDisabled**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_InfoContentOrder**
  ```
  ❌ Failed: 1
  Success rate: 0.0%
  ```

- [ ] **AI_InfoVisualCue**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnBannerRoleOnHeader**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnComplementaryRoleOnAside**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnContentinfoRoleOnFooter**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnFormRoleOnForm**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnMainRoleOnMain**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnMixedLanguage**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnModalMissingLabel**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnModalWithoutFocusTrap**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnNavigationRoleOnNav**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnPossibleReadingOrderIssue**
  ```
  ❌ Failed: 1
  Success rate: 0.0%
  ```

- [ ] **AI_WarnRegionWithoutLabel**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnSearchRoleOnForm**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnSliderWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnSwitchWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnTableWithComplexStructure**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnTreeviewWithoutARIA**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnVideoWithoutCaptions**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **AI_WarnVideoWithoutTranscript**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **DiscoStyleAttrOnElements**
  ```
  ❌ Failed: 2
  Success rate: 0.0%
  ```

- [ ] **DiscoStyleElementOnPage**
  ```
  ❌ Failed: 2
  Success rate: 0.0%
  ```

- [ ] **ErrAltOnElementThatDoesntTakeIt**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrAutoStartTimers**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrBannerLandmarkAccessibleNameIsBlank**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrBannerLandmarkHasAriaLabelAndAriaLabelledByAttrs**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrBannerLandmarkMayNotBeChildOfAnotherLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrButtonOutlineNoneNoBoxShadow**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrButtonTextLowContrast**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrColorStyleDefinedExplicitlyInElement**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrColorStyleDefinedExplicitlyInStyleTag**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrComplementaryLandmarkAccessibleNameIsBlank**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **ErrComplementaryLandmarkHasAriaLabelAndAriaLabelledByAttrs**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrComplementaryLandmarkMayNotBeChildOfAnotherLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrCompletelyEmptyNavLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrContentInfoLandmarkAccessibleNameIsBlank**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrContentInfoLandmarkHasAriaLabelAndAriaLabelledByAttrs**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrContentinfoLandmarkMayNotBeChildOfAnotherLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrContentObscuring**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrDivMapMissingAttributes**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **ErrDuplicateLabelForBannerLandmark**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrDuplicateLabelForComplementaryLandmark**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrDuplicateLabelForContentinfoLandmark**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrDuplicateLabelForFormLandmark**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrDuplicateLabelForNavLandmark**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrDuplicateLabelForRegionLandmark**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrDuplicateLabelForSearchLandmark**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrElementNotContainedInALandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrEmptyAriaLabelledByOnField**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrEmptyAriaLabelOnField**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFieldAriaRefDoesNotExist**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFieldLabelledUsingAriaLabel**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFieldReferenceDoesNotExist**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFielLabelledBySomethingNotALabel**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFocusBackgroundColorOnly**
  ```
  ❌ Failed: 4
  Success rate: 42.9%
  ```

- [ ] **ErrFormAriaLabelledByIsBlank**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFormAriaLabelledByReferenceDIsHidden**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFormAriaLabelledByReferenceDoesNotExist**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFormAriaLabelledByReferenceDoesNotReferenceAHeading**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrFormEmptyHasNoChildNodes**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFormEmptyHasNoInteractiveElements**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFormLandmarkAccessibleNameIsBlank**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFormLandmarkHasAriaLabelAndAriaLabelledByAttrs**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFormUsesAriaLabelInsteadOfVisibleElement**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrFormUsesTitleAttribute**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrImageAltContainsHTML**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrImageWithEmptyAlt**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrImageWithImgFileExtensionAlt**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrImageWithNoAlt**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrImageWithURLAsAlt**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrInPageTargetWrongTabindex**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrInputFocusContrastFail**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrInsufficientContrast**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrInvalidTabindex**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrLabelContainsMultipleFields**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrLabelMismatchOfAccessibleNameAndLabelText**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrLargeTextContrastAA**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **ErrLargeTextContrastAAA**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrMainLandmarkAccessibleNameIsBlank**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrMainLandmarkHasAriaLabelAndAriaLabelledByAttrs**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrMainLandmarkHasTabindexOfZeroCanOnlyHaveMinusOneAtMost**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrMainLandmarkIsHidden**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrMainLandmarkMayNotbeChildOfAnotherLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrMapAriaHidden**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrMissingTabindex**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrModalMissingClose**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **ErrModalMissingHeading**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **ErrModalWithoutEscape**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **ErrMouseOnlyHandler**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrMultipleBannerLandmarks**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrMultipleContentinfoLandmarks**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrMultipleMainLandmarks**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrNavigationLandmarkAccessibleNameIsBlank**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrNavLandmarkAccessibleNameIsBlank**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrNavLandmarkContainsOnlyWhiteSpace**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrNavLandmarkHasAriaLabelAndAriaLabelledByAttrs**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrNegativeTabindex**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrNestedNavLandmarks**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrNoBannerLandmarkOnPage**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrNoCurrentPageIndicator**
  ```
  ❌ Failed: 1
  Success rate: 0.0%
  ```

- [ ] **ErrNoFocusIndicator**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **ErrNoMainLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrNoOutlineOffsetDefined**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrOrphanLabelWithNoId**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrOutlineIsNoneOnInteractiveElement**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrRegionLandmarkAccessibleNameIsBlank**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrRegionLandmarkHasAriaLabelAndAriaLabelledByAttrs**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrRegionLandmarkMustHaveAccessibleName**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrSvgImageNoLabel**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrTabindexOfZeroOnNonInteractiveElement**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrTabOrderViolation**
  ```
  ❌ Failed: 2
  Success rate: 60.0%
  ```

- [ ] **ErrTextContrastAA**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **ErrTextContrastAAA**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrTransparentFocusIndicator**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrTTabindexOnNonInteractiveElement**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **ErrUnlabelledField**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **ErrWrongTabindexForInteractiveElement**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **forms_DiscoNoSubmitButton**
  ```
  ❌ Failed: 1
  Success rate: 75.0%
  ```

- [ ] **forms_DiscoPlaceholderAsLabel**
  ```
  ❌ Failed: 1
  Success rate: 75.0%
  ```

- [ ] **forms_ErrInputMissingLabel**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **forms_ErrNoButtonText**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **forms_WarnGenericButtonText**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **forms_WarnNoFieldset**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **forms_WarnRequiredNotIndicated**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **RegionLandmarkAccessibleNameIsBlank**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnBannerLandmarkAccessibleNameUsesBanner**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnButtonFocusGradientBackground**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnButtonFocusImageBackground**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnColorRelatedStyleDefinedExplicitlyInElement**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnColorRelatedStyleDefinedExplicitlyInStyleTag**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnComplementaryLandmarkAccessibleNameUsesComplementary**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnComplementaryLandmarkHasNoLabel**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **WarnContentinfoLandmarkAccessibleNameUsesContentinfo**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnContentInfoLandmarkHasNoLabel**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **WarnContentOutsideLandmarks**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnElementNotInLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnFieldLabelledByElementThatIsNotALabel**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **WarnFieldLabelledByMultipleElements**
  ```
  ❌ Failed: 2
  Success rate: 50.0%
  ```

- [ ] **WarnFormHasNoLabel**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **WarnFormHasNoLabelSoIsNotLandmark**
  ```
  ❌ Failed: 2
  Success rate: 50.0%
  ```

- [ ] **WarnFormLandmarkAccessibleNameUsesForm**
  ```
  ❌ Failed: 2
  Success rate: 50.0%
  ```

- [ ] **WarnHeadingFoundInLandmarkButIsLabelledByAnAriaLabelledBy**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnHeadingFoundInsideLandmarkButDoesntLabelLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnLinkLooksLikeButton**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **WarnMissingAriaLabelledby**
  ```
  ❌ Failed: 2
  Success rate: 50.0%
  ```

- [ ] **WarnMissingAriaModal**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **WarnMissingDocumentMetadata**
  ```
  ❌ Failed: 1
  Success rate: 75.0%
  ```

- [ ] **WarnMissingNegativeTabindex**
  ```
  ❌ Failed: 3
  Success rate: 25.0%
  ```

- [ ] **WarnMissingRequiredIndication**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnModalNoFocusableElements**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **WarnMultipleBannerLandmarksButNotAllHaveLabels**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnMultipleComplementaryLandmarksButNotAllHaveLabels**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnMultipleContentInfoLandmarksButNotAllHaveLabels**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnMultipleNavLandmarksButNotAllHaveLabels**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnMultipleNavNeedsLabel**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnMultipleRegionLandmarksButNotAllHaveLabels**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnNavLandmarkAccessibleNameUsesNavigation**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnNavLandmarkHasNoLabel**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnNavMissingAccessibleName**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnNegativeTabindex**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **WarnNoBannerLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnNoContentinfoLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnNoCurrentPageIndicator**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnNoCursorPointer**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnNoNavigationLandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnRegionLandmarkAccessibleNameUsesNavigation**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnRegionLandmarkHasNoLabelSoIsNotConsideredALandmark**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnSVGNoRole**
  ```
  ❌ Failed: 2
  Success rate: 33.3%
  ```

- [ ] **WarnUnlabelledRegion**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

- [ ] **WarnVisualHierarchy**
  ```
  ❌ Failed: 1
  Success rate: 66.7%
  ```

- [ ] **WarnZeroOutlineOffset**
  ```
  ❌ Failed: 1
  Success rate: 50.0%
  ```

