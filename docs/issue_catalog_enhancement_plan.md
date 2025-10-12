# Issue Catalog Enhancement Plan

## Current Status

### Overall Statistics (205 Total Error Codes)
- **Enhanced descriptions** (≥100 chars): 42 codes (20%)
- **Basic descriptions** (<100 chars): 163 codes (79%)
- **Need documentation**: 0 codes (0%)

**Total needing enhancement: 163 codes (79%)**

### Page-Specific Analysis

On the test page `http://127.0.0.1:5001/pages/68eb2691e95773ae013159ed`:
- **32 unique error codes** appear on this page
- **16 codes missing** from catalog (50%)
- **8 codes need enhancement** (25%)
- **8 codes have enhanced descriptions** (25%)

## Problem Statement

The issue catalog currently has **163 out of 205 error codes** (79%) with basic descriptions under 100 characters. These brief descriptions don't provide:

1. **Comprehensive explanations** of what the test detects
2. **Context** on why the issue matters for accessibility
3. **User impact** information (who is affected and how)
4. **Actionable guidance** on how to fix violations

This limits the usefulness of:
- The new **test details help modal** in Create/Edit Project pages
- Error descriptions shown to testers on page test results
- Developer understanding of accessibility issues
- Training and onboarding of new team members

## Enhancement Goals

### Primary Goals
1. Add **16 missing error codes** to the catalog (codes appearing on test pages but not in catalog)
2. Enhance **163 basic descriptions** to comprehensive format (at least 200+ characters each)
3. Ensure all descriptions include the **4 key fields**:
   - `description`: What the test detects
   - `why_it_matters`: Accessibility importance
   - `who_it_affects`: User groups impacted
   - `how_to_fix`: Practical remediation steps

### Quality Standards

Each enhanced description should:
- **Be comprehensive**: 200-500 characters per field
- **Be user-focused**: Explain impact on real users, not just technical requirements
- **Be actionable**: Provide specific steps to fix issues
- **Be accurate**: Match WCAG criteria and best practices
- **Be consistent**: Follow the format of existing enhanced descriptions

### Example Format

```python
"ErrImageWithNoAlt": {
    "id": "ErrImageWithNoAlt",
    "type": "Error",
    "impact": "High",
    "wcag": ["1.1.1"],
    "wcag_full": "1.1.1 Non-text Content (Level A)",
    "category": "images",
    "description": "Images are missing alternative text attributes, preventing assistive technologies from conveying their content or purpose to users",
    "why_it_matters": "Screen readers cannot describe image content to users who are blind or have low vision, creating information barriers that may prevent understanding of essential content, navigation, or task completion. This also affects users with cognitive disabilities who benefit from text alternatives and users on slow connections where images fail to load.",
    "who_it_affects": "Blind users using screen readers, users with low vision using screen readers with magnification, users with cognitive disabilities who rely on text alternatives, voice control users who need text labels to reference elements, and users on slow internet connections",
    "how_to_fix": "Add descriptive alt attributes for informative images (alt=\"Sales chart showing 40% increase\"), use empty alt attributes for decorative images (alt=\"\"), describe the function for interactive images (alt=\"Search\" not alt=\"magnifying glass icon\"), and provide detailed descriptions via aria-describedby for complex images like charts or diagrams."
}
```

## Prioritization Strategy

### Phase 1: Critical Missing Codes (Priority: HIGHEST)
**16 codes appearing on test pages but missing from catalog**

These codes are actively used in tests but have NO documentation:

| Code | Category | Estimated Impact |
|------|----------|-----------------|
| ErrAltTooLong | images | High |
| ErrDuplicateLandmarkWithoutName | landmarks | High |
| ErrDuplicateNavNames | navigation | High |
| ErrFakeListImplementation | lists | Medium |
| ErrFormLandmarkMustHaveAccessibleName | landmarks | High |
| ErrInappropriateMenuRole | navigation | Medium |
| ErrNavMissingAccessibleName | navigation | High |
| ErrSVGNoAccessibleName | images | High |
| InfoHeadingNearLengthLimit | headings | Low |
| InfoNoColorSchemeSupport | colors | Low |
| InfoNoContrastSupport | colors | Low |
| WarnContentOutsideLandmarks | landmarks | Medium |
| WarnNoCurrentPageIndicator | navigation | Medium |
| WarnSVGNoRole | images | Medium |
| WarnSmallLineHeight | fonts | Medium |
| WarnUnlabelledForm | forms | Medium |

**Timeline**: 1-2 weeks (1-2 codes per day)

### Phase 2: High-Visibility Codes (Priority: HIGH)
**8 codes on test page with basic descriptions**

These codes appear frequently and need better documentation:

| Code | Current Length | Category |
|------|---------------|----------|
| ErrIframeWithNoTitleAttr | 55 chars | title |
| ErrLinkOpensNewWindowNoWarning | 51 chars | links |
| ErrLinkTextNotDescriptive | 73 chars | links |
| ErrMultiplePageTitles | 78 chars | page |
| ErrTabindexNoVisibleFocus | 95 chars | event_handling |
| WarnHeadingOver60CharsLong | 35 chars | headings |
| WarnInputDefaultFocus | 92 chars | forms |
| WarnTabindexDefaultFocus | 95 chars | event_handling |

**Timeline**: 1 week (1 code per day)

### Phase 3: Common Error Codes (Priority: MEDIUM)
**~60 codes that appear frequently in test results**

Focus on codes that:
- Appear in multiple fixture tests
- Map to critical WCAG criteria (Level A, AA)
- Have high/medium impact levels

Categories to prioritize:
1. **Forms** (23 codes) - Critical for user interaction
2. **Landmarks** (60 codes) - Essential for navigation
3. **Headings** (10 codes) - Important for structure
4. **Images** (remaining codes) - High user impact
5. **Colors** (5 codes) - Affects readability

**Timeline**: 4-6 weeks

### Phase 4: Remaining Codes (Priority: LOW)
**~95 remaining codes with basic descriptions**

Focus on:
- Less common error codes
- Discovery codes (Disco*)
- Info-level messages
- Edge case warnings

**Timeline**: 6-8 weeks

## Implementation Approach

### Option 1: Manual Documentation (Most Accurate)
**Pros:**
- Highest quality and accuracy
- Deep understanding of accessibility requirements
- Context-aware descriptions
- Can include real-world examples

**Cons:**
- Time-intensive (15-30 min per code)
- Requires accessibility expertise
- ~82 hours total for all 163 codes

**Recommended for:** Phases 1 & 2 (24 critical codes)

### Option 2: AI-Assisted Documentation (Faster)
**Pros:**
- Faster generation (5-10 min per code including review)
- Consistent format
- Can be reviewed and refined by humans
- ~27 hours total for all 163 codes

**Cons:**
- Requires careful review for accuracy
- May miss nuanced accessibility considerations
- Generic descriptions need customization

**Recommended for:** Phases 3 & 4 (139 remaining codes)

### Option 3: Hybrid Approach (Recommended)
**Process:**
1. **AI generates** initial description using:
   - Error code name
   - WCAG criteria
   - Category
   - Template from enhanced examples
2. **Human reviews** and enhances:
   - Adds specific technical details
   - Includes real-world examples
   - Ensures accuracy and completeness
   - Customizes for context

**Timeline:** ~35-40 hours total
- Phase 1: 8 hours (manual, high priority)
- Phase 2: 4 hours (manual, high visibility)
- Phase 3: 15 hours (hybrid)
- Phase 4: 10 hours (hybrid)

## Resource Requirements

### Personnel
- **Accessibility specialist**: Review all descriptions for accuracy (10-15 hours)
- **Technical writer/developer**: Create/enhance descriptions (25-35 hours)
- **QA tester**: Verify descriptions match actual test behavior (5-10 hours)

### Tools
- **AI assistant** (Claude, GPT-4): Generate initial drafts for hybrid approach
- **WCAG documentation**: Reference for accurate criteria mapping
- **Test fixtures**: Validate descriptions against actual test behavior
- **Issue catalog template**: Ensure consistent formatting

### Testing
- **Manual verification**: Test help modal with new descriptions
- **Fixture validation**: Ensure error codes exist and are used correctly
- **User testing**: Get feedback from testers on description clarity

## Execution Plan

### Week 1-2: Phase 1 - Missing Codes
**Goal:** Add 16 missing error codes to catalog

**Daily tasks:**
1. Identify where code is generated in test files
2. Understand what the test actually checks
3. Research relevant WCAG criteria
4. Write comprehensive 4-field description
5. Add to issue catalog
6. Test in help modal

**Deliverables:**
- 16 new catalog entries
- Documentation of test behavior
- Updated touchpoint mappings if needed

### Week 3: Phase 2 - High-Visibility Codes
**Goal:** Enhance 8 basic descriptions on test page

**Daily tasks:**
1. Review current basic description
2. Expand to 4-field format
3. Add specific examples
4. Test in help modal
5. Get accessibility review

**Deliverables:**
- 8 enhanced catalog entries
- Before/after comparison showing improvement

### Week 4-9: Phase 3 - Common Error Codes
**Goal:** Enhance ~60 frequently-used codes

**Weekly process:**
1. **Monday-Tuesday:** AI generates 10-12 initial descriptions
2. **Wednesday-Thursday:** Human reviews and enhances 10-12 descriptions
3. **Friday:** Accessibility specialist reviews batch, provides feedback

**Deliverables:**
- 60 enhanced catalog entries
- Quality metrics (avg description length, completeness)

### Week 10-15: Phase 4 - Remaining Codes
**Goal:** Complete all 163 enhancements

**Similar process to Phase 3:**
- Batch processing with AI assistance
- Human review and refinement
- Regular quality checks

**Deliverables:**
- 95 enhanced catalog entries
- Complete catalog with 100% enhanced descriptions
- Final quality report

## Quality Assurance

### Review Checklist
For each enhanced description, verify:
- [ ] All 4 fields present (description, why_it_matters, who_it_affects, how_to_fix)
- [ ] Description is ≥200 characters total
- [ ] WCAG criteria correctly mapped
- [ ] Matches actual test behavior
- [ ] No technical jargon without explanation
- [ ] Includes specific, actionable fix steps
- [ ] Mentions affected user groups
- [ ] Grammar and spelling correct
- [ ] Consistent with existing enhanced descriptions

### Testing Process
1. **Unit test:** Verify catalog entry loads correctly
2. **Integration test:** Check help modal displays properly
3. **User test:** Ensure descriptions are clear and helpful
4. **Accessibility test:** Confirm WCAG mappings are accurate

### Success Metrics
- **Coverage:** 100% of codes have enhanced descriptions
- **Quality:** Average description length ≥300 characters per field
- **Accuracy:** <5% corrections needed after accessibility review
- **Usability:** User feedback rating ≥4/5 for description clarity

## AI-Assisted Enhancement Process

### Prompt Template for AI Generation

```
Generate an enhanced accessibility issue catalog entry for the error code [CODE_NAME].

Current information:
- Error code: [CODE_NAME]
- Category: [CATEGORY]
- WCAG criteria: [WCAG_CODES]
- Current basic description: [CURRENT_DESC]

Please provide a comprehensive description in this format:

1. **Description** (200-300 chars): What does this test detect? What specific issue does it identify?

2. **Why it matters** (200-300 chars): Why is this important for accessibility? What barriers does it create? What are the consequences of not fixing this?

3. **Who it affects** (150-250 chars): Which user groups are impacted? Include specific disabilities and assistive technologies affected.

4. **How to fix** (200-400 chars): Provide specific, actionable steps to remediate this issue. Include code examples or best practices where relevant.

Style guidelines:
- Use clear, plain language
- Focus on user impact, not just technical requirements
- Provide specific examples
- Be actionable and practical
- Maintain professional but accessible tone
```

### Example AI Workflow

For `ErrNavMissingAccessibleName`:

1. **Input to AI:**
   - Code: ErrNavMissingAccessibleName
   - Category: navigation
   - WCAG: 4.1.2
   - Current: (missing)

2. **AI generates draft**

3. **Human reviews and enhances:**
   - Verify technical accuracy
   - Add specific examples from fixtures
   - Customize for project context
   - Ensure WCAG mapping correct

4. **Add to catalog**

5. **Test in help modal**

## Maintenance Plan

### Ongoing Process
When adding new error codes:
1. **Immediately create** enhanced catalog entry
2. **Include all 4 fields** from the start
3. **Add fixtures** to validate behavior
4. **Test help modal** displays correctly
5. **Document** in touchpoint mapping if new category

### Quarterly Review
- Review user feedback on description clarity
- Update descriptions based on WCAG updates
- Refine based on common user questions
- Add examples from real test results

### Documentation Standards
- Keep descriptions updated with test behavior
- Document any breaking changes to error codes
- Maintain changelog of significant updates
- Version control all catalog changes

## Next Steps

### Immediate Actions (This Week)
1. **Approve this plan** with stakeholders
2. **Assign resources** (accessibility specialist, technical writer)
3. **Set up tools** (AI access, templates, review process)
4. **Start Phase 1** with highest priority missing codes

### Short-term (Next 2 Weeks)
1. Complete Phase 1 (16 missing codes)
2. Complete Phase 2 (8 high-visibility codes)
3. Document learnings and refine process
4. Begin Phase 3 preparation

### Long-term (Next 3 Months)
1. Complete all 163 enhancements
2. Achieve 100% catalog coverage with enhanced descriptions
3. Gather user feedback on help modal effectiveness
4. Establish maintenance process for ongoing updates

## Success Criteria

The issue catalog enhancement will be considered successful when:

1. ✅ **All 205 codes** have enhanced descriptions (currently 42)
2. ✅ **Zero missing codes** that appear in test results
3. ✅ **Average description length** ≥300 characters per field
4. ✅ **User feedback** rating ≥4/5 for help modal usefulness
5. ✅ **Accessibility review** confirms WCAG accuracy
6. ✅ **Maintenance process** established for new codes
7. ✅ **Documentation** complete for all enhanced entries

## Appendix A: Missing Codes Detail

### Codes Found on Test Page but Missing from Catalog

#### High Priority (Navigation/Landmarks)
1. **ErrNavMissingAccessibleName** - Navigation elements need accessible names for screen readers
2. **ErrDuplicateNavNames** - Multiple navigation elements with same name cause confusion
3. **ErrInappropriateMenuRole** - Incorrect ARIA menu roles on navigation elements
4. **WarnNoCurrentPageIndicator** - Missing visual/programmatic current page indication
5. **ErrDuplicateLandmarkWithoutName** - Multiple landmarks of same type need unique names
6. **ErrFormLandmarkMustHaveAccessibleName** - Form landmarks require accessible names
7. **WarnContentOutsideLandmarks** - Content not contained in proper landmark structure
8. **WarnUnlabelledForm** - Forms missing labels for screen reader users

#### High Priority (Images)
9. **ErrAltTooLong** - Alt text exceeds recommended character length
10. **ErrSVGNoAccessibleName** - SVG graphics missing accessible names
11. **WarnSVGNoRole** - SVG elements missing appropriate ARIA roles

#### Medium Priority (Other)
12. **ErrFakeListImplementation** - List appearance without proper list markup
13. **WarnSmallLineHeight** - Line height too small for comfortable reading
14. **InfoHeadingNearLengthLimit** - Heading approaching recommended character limit
15. **InfoNoColorSchemeSupport** - No support for prefers-color-scheme
16. **InfoNoContrastSupport** - No support for prefers-contrast

## Appendix B: Resources

### Reference Documentation
- **WCAG 2.1 Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
- **WCAG 2.2 Updates**: https://www.w3.org/WAI/WCAG22/quickref/
- **ARIA Authoring Practices**: https://www.w3.org/WAI/ARIA/apg/
- **WebAIM Resources**: https://webaim.org/articles/

### Internal Resources
- **Existing enhanced descriptions**: auto_a11y/reporting/issue_catalog.py (lines 16-50 for examples)
- **Test implementation files**: auto_a11y/scripts/tests/*.js
- **Fixture examples**: Fixtures/*/*.html
- **Touchpoint mapping**: docs/touchpoint_mapping_system.md

### Tools
- **Claude AI**: https://claude.ai/ (for AI-assisted generation)
- **WCAG Validator**: https://validator.w3.org/
- **Screen reader testing**: NVDA (Windows), VoiceOver (Mac)

---

**Document Version**: 1.0
**Last Updated**: January 2025
**Owner**: Auto A11y Development Team
**Status**: Pending Approval
