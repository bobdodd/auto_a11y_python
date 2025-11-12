# Drupal Issue Mapping - Gap Analysis and Implementation Plan

## Executive Summary

This document analyzes the mapping between Auto A11y's `Violation` model and Drupal's `Issue` content type, identifies gaps, and proposes implementation changes.

**Key Findings:**
1. ✅ **Good Foundation**: Our `Violation` model already has most needed fields
2. ⚠️ **Lifecycle Gap**: Drupal has workflow states (`field_ticket_status`) we don't track
3. ⚠️ **Multiple WCAG**: Issues can reference multiple WCAG criteria - our model supports this but needs better extraction
4. ⚠️ **Category Mapping**: Need explicit touchpoint → Drupal taxonomy mapping
5. ⚠️ **Non-WCAG Criteria**: Drupal supports 49 EN 301 459 kiosk criteria - we need to support this
6. ✅ **Recording Integration**: Our recording fields map well to manual issue fields

---

## 1. Drupal Issue Lifecycle States

### Drupal Field: `field_ticket_status`

**Available Values:**
- `ticket_status_fail` - Issue failed/needs fixing (default for new issues)
- `ticket_status_pass` - Issue resolved/passed
- `ticket_status_pending` - Under review
- Other workflow states (varies by Drupal configuration)

### Current Auto A11y Model

**Gap**: We don't track issue lifecycle/status at all.

**Impact**:
- Can't track which issues have been fixed
- Can't sync resolved issues back from Drupal
- No way to mark issues as "pending review"

### Proposed Solution

Add lifecycle tracking to `Violation` model:

```python
class ViolationStatus(Enum):
    """Violation lifecycle status"""
    OPEN = "open"              # New, needs fixing
    PENDING = "pending"        # Under review
    RESOLVED = "resolved"      # Fixed/resolved
    WONT_FIX = "wont_fix"     # Accepted as-is
    FALSE_POSITIVE = "false_positive"  # Not actually an issue

class Violation:
    # ... existing fields ...

    # NEW: Lifecycle tracking
    status: ViolationStatus = ViolationStatus.OPEN
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
```

**Mapping:**
```python
# Auto A11y → Drupal
ViolationStatus.OPEN → "ticket_status_fail"
ViolationStatus.PENDING → "ticket_status_pending"
ViolationStatus.RESOLVED → "ticket_status_pass"
ViolationStatus.WONT_FIX → "ticket_status_pass" (with note)
ViolationStatus.FALSE_POSITIVE → (don't export or mark with note)

# Drupal → Auto A11y
"ticket_status_fail" → ViolationStatus.OPEN
"ticket_status_pending" → ViolationStatus.PENDING
"ticket_status_pass" → ViolationStatus.RESOLVED
```

---

## 2. WCAG Criteria Handling

### Drupal Capability

**Field:** `field_wcag_chapter` (Entity Reference, Multiple)
- References `wcag_chapter` content type (50 total chapters)
- **Can reference multiple criteria per issue**
- Example: Unlabeled form field violates 1.3.1, 3.3.2, AND 4.1.2

### Current Auto A11y Model

```python
class Violation:
    wcag_criteria: List[str] = field(default_factory=list)
```

**Status**: ✅ Already supports multiple criteria!

**Gap**: WCAG criteria format inconsistency
- Sometimes: `"1.3.1"`
- Sometimes: `"Success Criterion 1.3.1 Info and Relationships"`
- Sometimes: `["wcag131", "wcag332"]` (tags)

### Proposed Solution

**Standardize WCAG criteria storage:**

```python
class Violation:
    wcag_criteria: List[str] = field(default_factory=list)
    # Format: ["1.3.1", "3.3.2", "4.1.2"]
    # Always store as numeric strings like "X.Y.Z"

    @classmethod
    def normalize_wcag_criterion(cls, criterion: str) -> Optional[str]:
        """
        Extract WCAG number from various formats

        Examples:
            "1.3.1" → "1.3.1"
            "Success Criterion 1.3.1 Info and Relationships" → "1.3.1"
            "wcag131" → "1.3.1"
            "SC 1.3.1" → "1.3.1"
        """
        import re

        # Already normalized
        if re.match(r'^\d+\.\d+\.\d+$', criterion):
            return criterion

        # Extract from full title
        match = re.search(r'(\d+\.\d+\.\d+)', criterion)
        if match:
            return match.group(1)

        # Handle wcag131 format
        match = re.match(r'wcag(\d)(\d)(\d)', criterion.lower())
        if match:
            return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"

        return None

    def add_wcag_criterion(self, criterion: str):
        """Add a WCAG criterion (with normalization)"""
        normalized = self.normalize_wcag_criterion(criterion)
        if normalized and normalized not in self.wcag_criteria:
            self.wcag_criteria.append(normalized)
```

**Implementation in test runners:**

```python
# In touchpoint tests (e.g., test_landmarks.py)
violation = Violation(
    id="ErrDuplicateLabelForRegionLandmark",
    # ...
    wcag_criteria=["1.3.1", "4.1.2"]  # Store normalized
)

# In parsers (e.g., Axe, Pa11y)
for axe_result in results:
    wcag_tags = [tag for tag in axe_result.get('tags', []) if tag.startswith('wcag')]
    normalized = [Violation.normalize_wcag_criterion(tag) for tag in wcag_tags]
    normalized = [c for c in normalized if c]  # Remove None values

    violation = Violation(
        # ...
        wcag_criteria=normalized
    )
```

---

## 3. Impact Level Mapping

### Drupal Field: `field_impact`

**Values:** `"high"`, `"med"`, `"low"`

**Note**: "med" not "medium"!

### Current Auto A11y Model

```python
class ImpactLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"  # ← Different from Drupal!
    HIGH = "high"
```

**Gap**: Enum value mismatch

### Proposed Solution

**Option A: Change enum values (BREAKING CHANGE)**

```python
class ImpactLevel(Enum):
    LOW = "low"
    MEDIUM = "med"  # Changed to match Drupal
    HIGH = "high"
```

**Option B: Keep enum, map in exporter (RECOMMENDED)**

```python
# In IssueExporter
IMPACT_MAPPING = {
    ImpactLevel.LOW: "low",
    ImpactLevel.MEDIUM: "med",  # Map MEDIUM → "med"
    ImpactLevel.HIGH: "high"
}

IMPACT_REVERSE = {
    "low": ImpactLevel.LOW,
    "med": ImpactLevel.MEDIUM,  # Map "med" → MEDIUM
    "medium": ImpactLevel.MEDIUM,  # Also accept "medium" for compatibility
    "high": ImpactLevel.HIGH
}
```

**Recommendation**: Use Option B to avoid breaking existing code and database records.

---

## 4. Issue Type Classification

### Drupal Taxonomy: `issue_type`

**Terms:**
1. **WCAG** - WCAG violations (automated or manual)
2. **Note** - General observations
3. **UX Note** - User experience observations
4. **Best Practice** - Best practice recommendations
5. **Bug** - Technical bugs
6. **Pain Point** - User painpoints from testing

### Current Auto A11y Model

**Gap**: No explicit issue type field

**Current approach**: Inferred from `source_type`
- `source_type="automated"` → WCAG
- `source_type="manual"` → Pain Point (maybe?)

### Proposed Solution

Add explicit issue type:

```python
class IssueType(Enum):
    """Drupal issue type classification"""
    WCAG = "wcag"
    NOTE = "note"
    UX_NOTE = "ux_note"
    BEST_PRACTICE = "best_practice"
    BUG = "bug"
    PAIN_POINT = "pain_point"

class Violation:
    # ... existing fields ...

    # NEW: Explicit issue type
    issue_type: IssueType = IssueType.WCAG  # Default to WCAG
```

**Inference logic:**

```python
def infer_issue_type(violation: Violation) -> IssueType:
    """Infer Drupal issue type from violation properties"""

    # Manual findings from recordings
    if violation.source_type == "manual" and violation.recording_id:
        return IssueType.PAIN_POINT

    # Has WCAG criteria → WCAG violation
    if violation.wcag_criteria:
        return IssueType.WCAG

    # High impact without WCAG → bug
    if violation.impact == ImpactLevel.HIGH:
        return IssueType.BUG

    # Low impact, no WCAG → note or best practice
    if violation.impact == ImpactLevel.LOW:
        return IssueType.BEST_PRACTICE

    # Default
    return IssueType.WCAG
```

**Alternative**: Add to existing field instead:

```python
class Violation:
    source_type: str = "automated"  # Keep as-is

    # Add optional override
    drupal_issue_type: Optional[str] = None  # "WCAG", "Pain Point", etc.
```

---

## 5. Issue Category Mapping

### Drupal Taxonomy: `issue_category` (40 terms)

**Sample Terms:**
- Accordions
- ARIA
- Audio
- Breadcrumbs
- Carousels
- Colour or Contrast
- Focus or Keyboard
- Forms
- Headings or Titles
- Images or Non-Text Content
- Links or Buttons
- Modal Dialog
- Tables
- etc. (40 total)

### Current Auto A11y Model

```python
class Violation:
    touchpoint: str  # e.g., "Forms", "Headings", "Images"
```

**Gap**: Touchpoint names don't exactly match Drupal categories

### Proposed Solution

**Create explicit mapping table:**

```python
# In auto_a11y/drupal/mappings.py

TOUCHPOINT_TO_DRUPAL_CATEGORIES = {
    # Direct matches
    "Forms": ["Forms"],
    "Tables": ["Tables"],
    "ARIA": ["ARIA"],
    "Audio": ["Audio"],
    "IFrames": ["IFrames"],
    "Lists": ["Lists"],
    "Menus": ["Menus"],
    "Tabs": ["Tabs"],
    "Language": ["Language"],
    "Timing": ["Timing"],

    # Name variations
    "Headings": ["Headings or Titles"],
    "Images": ["Images or Non-Text Content"],
    "Color Contrast": ["Colour or Contrast"],
    "Landmarks": ["Page Regions"],
    "Modals": ["Modal Dialog"],
    "Dialogs": ["Modal Dialog"],
    "Fonts": ["Text or Font"],
    "Styles": ["Reflow, Resize or Text Spacing"],
    "Tabindex": ["Sequence or Order"],
    "Animations": ["Motion or Animation"],

    # Multiple categories
    "Links": ["Links or Buttons"],
    "Buttons": ["Links or Buttons"],
    "Focus": ["Focus or Keyboard"],
    "Keyboard": ["Focus or Keyboard"],

    # Complex mappings (can map to multiple)
    "Navigation": ["Navigation or Multiple Ways", "Menus"],
    "Search": ["Search or Filters"],
    "Carousels": ["Carousels"],
    "Accordions": ["Accordions"],
    "Breadcrumbs": ["Breadcrumbs"],
    "Status Messages": ["Status Messages, Errors or Instructions"],
    "Error Messages": ["Status Messages, Errors or Instructions"],
    "Instructions": ["Status Messages, Errors or Instructions"],
    "Autocomplete": ["Autocomplete"],
    "Magnifiers": ["Magnifiers"],
    "Pagination": ["Pagination"],
    "Overlay": ["Overlay content"],
    "Skip Links": ["Skip links"],

    # Fallback for unmapped touchpoints
    # Will use touchpoint name directly and log warning
}

def map_touchpoint_to_categories(touchpoint: str) -> List[str]:
    """
    Map Auto A11y touchpoint to Drupal issue categories

    Returns:
        List of Drupal category names (may be multiple)
    """
    categories = TOUCHPOINT_TO_DRUPAL_CATEGORIES.get(touchpoint)

    if categories:
        return categories

    # Fallback: try direct match
    logger.warning(f"No mapping for touchpoint '{touchpoint}', using as-is")
    return [touchpoint]
```

**Usage in exporter:**

```python
# In IssueExporter
category_names = map_touchpoint_to_categories(violation.touchpoint)
category_uuids = self.taxonomy.lookup_issue_category_uuids(category_names)
```

---

## 6. Non-WCAG Test Criteria Support

### Drupal Content Type: `test_criteria`

**Purpose**: EN 301 459 kiosk/ATM accessibility standards (49 criteria)

**Sample Criteria:**
- 6.3.1.3 - User adjustable font size
- 6.1 - One Task at a Time
- 6.3.1.1 - Easily Distinguish Between Letters
- 6.3.3.2 - Color not sole indicator of information
- 6.3.5.1 - Audio Instructions Provided
- etc. (49 total)

### Current Auto A11y Model

**Gap**: Only tracks WCAG criteria, no support for other standards

### Proposed Solution

**Add non-WCAG criteria field:**

```python
class Violation:
    # ... existing fields ...

    # WCAG criteria (existing)
    wcag_criteria: List[str] = field(default_factory=list)
    # Format: ["1.3.1", "3.3.2"]

    # NEW: Non-WCAG test criteria
    test_criteria: List[str] = field(default_factory=list)
    # Format: ["6.3.1.3", "6.1", "6.3.5.1"]
    # Reference numbers from EN 301 459 or other standards

    # NEW: Criteria source
    criteria_standard: Optional[str] = None
    # Examples: "WCAG 2.2", "EN 301 459", "Section 508", "AODA"
```

**Drupal mapping:**

```python
# In IssueExporter
if violation.test_criteria:
    # Option 1: Use text field (confirmed to exist)
    attributes['field_txt_relevant_test_criteria'] = ", ".join(violation.test_criteria)

    # Option 2: Look up test_criteria nodes (if relationship field exists)
    # criteria_uuids = self.criteria_manager.lookup_criteria_uuids(violation.test_criteria)
    # if criteria_uuids:
    #     relationships['field_test_criteria'] = {
    #         'data': [{'type': 'node--test_criteria', 'id': uuid} for uuid in criteria_uuids]
    #     }
```

**Implementation priority**: MEDIUM
- Needed for kiosk/ATM testing
- Can use text field fallback initially
- Build proper entity reference later

---

## 7. Recording/Video Integration

### Drupal Fields

**For Manual Issues:**
- `field_video` - Entity reference to `audit_video` (multiple)
- `field_video_timecode` - Timecode strings (multiple)
- `field_transcript` - Formatted text

### Current Auto A11y Model

```python
class Violation:
    recording_id: Optional[str] = None
    timecodes: List[Dict[str, str]] = field(default_factory=list)
    # timecode format: [{"start": "00:00:56.085", "end": "00:01:19.265"}]
```

**Status**: ✅ Good foundation!

**Gap**:
- `recording_id` is Auto A11y internal ID, need Drupal UUID
- No transcript field

### Proposed Solution

**Add Drupal sync fields:**

```python
class Violation:
    # ... existing fields ...

    # Recording reference (local)
    recording_id: Optional[str] = None  # Auto A11y recording ID
    timecodes: List[Dict[str, str]] = field(default_factory=list)

    # NEW: Drupal integration
    drupal_issue_uuid: Optional[str] = None  # Issue node UUID
    drupal_video_uuid: Optional[str] = None  # audit_video UUID (populated on export)
    transcript_text: Optional[str] = None  # Transcript for Drupal field_transcript
```

**Export workflow:**

```python
# 1. Export recording as audit_video first (if not already exported)
if violation.recording_id and not violation.drupal_video_uuid:
    recording = get_recording(violation.recording_id)
    video_result = export_recording_as_audit_video(recording, audit_uuid)
    violation.drupal_video_uuid = video_result['uuid']

# 2. Export violation as issue with video reference
issue_result = export_violation(
    violation,
    audit_uuid,
    page_uuid,
    video_uuid=violation.drupal_video_uuid
)
violation.drupal_issue_uuid = issue_result['uuid']
```

---

## 8. Failure Point Integration

### Drupal Content Type: `failure_point`

**Purpose**: Represents a specific component/location on a page where issues occur

**Fields:**
- `title` - Component name
- `field_failure_point` - Taxonomy term (Header, Footer, Form, etc.)
- `field_url` - Page URL
- `field_parent_audit` - Audit reference
- `field_xpath` - XPath to component

**Relationship**: Issues reference failure_point via `field_parent_failure_point`

### Current Auto A11y Model

**Gap**: No failure point concept

**Current approach**: XPath stored directly on violation

### Proposed Solution

**Option A: Auto-create failure points on export**

```python
def create_failure_point_if_needed(
    client: DrupalJSONAPIClient,
    audit_uuid: str,
    page_uuid: str,
    component_type: str,  # "Forms", "Header", etc.
    xpath: Optional[str] = None
) -> Optional[str]:
    """
    Create or find a failure point for a component

    Returns:
        Failure point UUID or None
    """
    # Generate deterministic title
    title = f"{component_type} on {page_url}"

    # Check if exists (query by title + page)
    existing = query_failure_point(client, title, page_uuid)
    if existing:
        return existing['uuid']

    # Create new
    payload = {
        'data': {
            'type': 'node--failure_point',
            'attributes': {
                'title': title,
                'field_xpath': xpath
            },
            'relationships': {
                'field_parent_audit': {
                    'data': {'type': 'node--audit', 'id': audit_uuid}
                },
                'field_failure_point': {
                    'data': {
                        'type': 'taxonomy_term--failure_point_types',
                        'id': taxonomy_manager.lookup_failure_point_type_uuid(component_type)
                    }
                }
            }
        }
    }

    result = client.post('node/failure_point', payload)
    return result['data']['id']
```

**Option B: Add failure point tracking to model (future)**

```python
@dataclass
class FailurePoint:
    """Represents a specific component/location on page"""
    component_type: str  # "Forms", "Header", etc.
    component_name: Optional[str] = None
    xpath: Optional[str] = None
    page_id: str = None
    drupal_uuid: Optional[str] = None

class Violation:
    # ... existing fields ...
    failure_point_id: Optional[str] = None  # Reference to FailurePoint
```

**Recommendation**: Use Option A initially (auto-create on export)

---

## 9. Model Changes Summary

### Required Changes (HIGH PRIORITY)

```python
# 1. Add lifecycle status
class ViolationStatus(Enum):
    OPEN = "open"
    PENDING = "pending"
    RESOLVED = "resolved"
    WONT_FIX = "wont_fix"
    FALSE_POSITIVE = "false_positive"

class Violation:
    # NEW REQUIRED FIELDS
    status: ViolationStatus = ViolationStatus.OPEN
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

    # NEW REQUIRED FOR EXPORT
    drupal_issue_uuid: Optional[str] = None
    drupal_sync_status: DrupalSyncStatus = DrupalSyncStatus.NOT_SYNCED
    drupal_last_synced: Optional[datetime] = None
    drupal_error_message: Optional[str] = None
```

### Recommended Changes (MEDIUM PRIORITY)

```python
class Violation:
    # Improve WCAG handling
    @classmethod
    def normalize_wcag_criterion(cls, criterion: str) -> Optional[str]:
        """Extract WCAG number from various formats"""
        pass

    # Add issue type
    issue_type: Optional[IssueType] = None

    # Add Drupal video UUID
    drupal_video_uuid: Optional[str] = None

    # Add transcript
    transcript_text: Optional[str] = None
```

### Optional Changes (LOW PRIORITY)

```python
class Violation:
    # Non-WCAG criteria support
    test_criteria: List[str] = field(default_factory=list)
    criteria_standard: Optional[str] = None

    # Failure point support
    failure_point_id: Optional[str] = None
```

---

## 10. Implementation Plan

### Phase 1: Core Issue Export (Week 1-2)

**Goal**: Export automated test violations as Drupal issues

**Tasks:**
1. ✅ Research Issue content type (DONE)
2. Create taxonomy managers (issue_type, issue_category, failure_point_types)
3. Create WCAG chapter manager with caching
4. Implement basic IssueExporter
   - Map violations to issue payloads
   - Handle WCAG criteria lookup
   - Handle taxonomy lookups
   - Map touchpoints to categories
5. Add Drupal sync fields to Violation model
6. Create test script for single violation export
7. Test with various violation types

**Deliverables:**
- `auto_a11y/drupal/issue_taxonomies.py`
- `auto_a11y/drupal/wcag_chapter_manager.py`
- `auto_a11y/drupal/issue_exporter.py`
- `auto_a11y/drupal/mappings.py`
- `test_export_issue.py`
- Updated `Violation` model with sync fields

### Phase 2: Batch Export & Lifecycle (Week 3)

**Goal**: Export all test results for a page/project

**Tasks:**
1. Implement batch export functionality
2. Add violation lifecycle status (ViolationStatus enum)
3. Update test result storage to track sync status
4. Create failure point auto-creation
5. Handle duplicate prevention
6. Add progress tracking and error handling
7. Test with real project data

**Deliverables:**
- `auto_a11y/drupal/failure_point_manager.py`
- Batch export methods in IssueExporter
- Updated Violation model with ViolationStatus
- Integration test with full project

### Phase 3: Manual Issue Export (Week 4)

**Goal**: Export recording issues with video references

**Tasks:**
1. Verify audit_video export works (may already exist)
2. Add video UUID tracking to Violation
3. Handle transcript field
4. Handle timecode arrays
5. Map recording issues to Drupal issue type "Pain Point"
6. Test with Dictaphone import → Drupal export

**Deliverables:**
- Updated IssueExporter for manual issues
- audit_video export integration
- Test with recording data

### Phase 4: Bidirectional Sync (Week 5-6)

**Goal**: Import resolved issues from Drupal

**Tasks:**
1. Create IssueImporter
2. Query issues by audit/page
3. Map Drupal status → ViolationStatus
4. Update local violations with Drupal changes
5. Handle conflict resolution
6. Add last_synced timestamps
7. Create sync orchestrator

**Deliverables:**
- `auto_a11y/drupal/issue_importer.py`
- Bidirectional sync workflow
- Sync command/script

### Phase 5: Advanced Features (Week 7+)

**Goal**: Polish and optimize

**Tasks:**
1. Add non-WCAG criteria support (kiosks)
2. Screenshot upload support
3. Related issues linking
4. Issue templates integration
5. Performance optimization
6. Comprehensive error handling
7. Documentation updates

**Deliverables:**
- Complete Drupal integration documentation
- Performance benchmarks
- Error handling guide

---

## 11. Testing Strategy

### Unit Tests

```python
# test_issue_mapping.py
def test_impact_mapping():
    assert map_impact_to_drupal(ImpactLevel.MEDIUM) == "med"
    assert map_impact_from_drupal("med") == ImpactLevel.MEDIUM

def test_wcag_normalization():
    assert Violation.normalize_wcag_criterion("1.3.1") == "1.3.1"
    assert Violation.normalize_wcag_criterion("SC 1.3.1") == "1.3.1"
    assert Violation.normalize_wcag_criterion("wcag131") == "1.3.1"

def test_touchpoint_to_category():
    assert map_touchpoint_to_categories("Forms") == ["Forms"]
    assert "Links or Buttons" in map_touchpoint_to_categories("Links")
```

### Integration Tests

```python
# test_issue_export_integration.py
def test_export_automated_violation():
    """Test exporting a basic automated violation"""
    violation = create_test_violation(
        id="test-issue",
        impact=ImpactLevel.HIGH,
        touchpoint="Forms",
        wcag_criteria=["1.3.1", "4.1.2"]
    )

    result = issue_exporter.export_violation(
        violation,
        audit_uuid="test-audit-uuid",
        page_uuid="test-page-uuid"
    )

    assert result['success']
    assert result['uuid']

    # Verify in Drupal
    drupal_issue = fetch_issue(result['uuid'])
    assert drupal_issue['attributes']['field_impact'] == "high"
    assert len(drupal_issue['relationships']['field_wcag_chapter']['data']) == 2

def test_export_manual_violation_with_video():
    """Test exporting a manual finding with video reference"""
    pass
```

### End-to-End Tests

```python
# test_full_export_workflow.py
def test_export_full_test_result():
    """
    Test exporting a complete TestResult with multiple violations
    to Drupal, including:
    - Discovered page creation
    - Failure point creation
    - Multiple issues with various types
    """
    pass
```

---

## 12. Migration Considerations

### Existing Data

**Question**: Do we have existing violations in the database?

**If YES**:
1. Add new fields with defaults
2. Run migration script to:
   - Normalize WCAG criteria
   - Set initial status = OPEN
   - Set initial drupal_sync_status = NOT_SYNCED
3. Consider backfilling issue_type from source_type

**Migration script:**

```python
# migrate_violations.py
def migrate_violations():
    """Add new fields to existing violations"""
    db = get_database()

    # Update all test results
    result = db.test_results.update_many(
        {},
        {
            '$set': {
                'violations.$[].status': 'open',
                'violations.$[].drupal_sync_status': 'not_synced',
                'violations.$[].drupal_issue_uuid': None,
                'violations.$[].drupal_last_synced': None,
                'violations.$[].drupal_error_message': None
            }
        }
    )

    print(f"Updated {result.modified_count} test results")

    # Normalize WCAG criteria
    for test_result in db.test_results.find():
        updated = False

        for violation in test_result.get('violations', []):
            if violation.get('wcag_criteria'):
                normalized = [
                    Violation.normalize_wcag_criterion(c)
                    for c in violation['wcag_criteria']
                ]
                normalized = [c for c in normalized if c]

                if normalized != violation['wcag_criteria']:
                    violation['wcag_criteria'] = normalized
                    updated = True

        if updated:
            db.test_results.replace_one(
                {'_id': test_result['_id']},
                test_result
            )
```

---

## 13. Open Questions

### For User/Drupal Admin

1. **Issue relationship field**: Does `field_test_criteria` exist on Issue, or do we use `field_txt_relevant_test_criteria` text field?

2. **Workflow states**: What are all the possible values for `field_ticket_status`? Just fail/pass/pending?

3. **Multiple pages**: When should an issue reference multiple discovered pages? (e.g., sitewide issues)

4. **Failure points**: Do you currently use failure_point nodes? Should we auto-create them?

5. **Issue templates**: Do you use `field_original_issue_template`? Should we reference templates on export?

6. **Non-WCAG standards**: Do you want Auto A11y to test against EN 301 459 kiosk criteria? Or just document them in issues?

7. **Resolution workflow**: When an issue is marked "pass" in Drupal, should we automatically mark it resolved in Auto A11y on next sync?

8. **Duplicate handling**: How should we handle duplicate issues? Match by title? XPath? Create a new issue each test run?

---

## 14. Conclusion

### Summary of Changes Needed

**Model Changes (HIGH):**
- Add ViolationStatus enum and lifecycle fields
- Add Drupal sync fields (uuid, sync_status, last_synced, error)
- Add WCAG normalization method

**Model Changes (MEDIUM):**
- Add IssueType enum or field
- Add drupal_video_uuid
- Add transcript_text

**Model Changes (LOW):**
- Add test_criteria for non-WCAG standards
- Add failure_point_id

**New Components:**
- IssueTaxonomyManager (issue_type, issue_category, failure_point_types)
- WCAGChapterManager (cache WCAG chapters)
- Touchpoint mapping table
- IssueExporter
- IssueImporter (Phase 4)
- FailurePointManager (Phase 2)

**Estimated Effort:**
- Phase 1 (Core Export): 2 weeks
- Phase 2 (Batch + Lifecycle): 1 week
- Phase 3 (Manual Issues): 1 week
- Phase 4 (Bidirectional): 2 weeks
- Phase 5 (Polish): 2+ weeks

**Total**: ~8-10 weeks for complete implementation

### Next Steps

1. Review this analysis with user
2. Answer open questions
3. Get approval for model changes
4. Begin Phase 1 implementation
5. Test with small dataset first
6. Iterate based on feedback

---

**Document Version**: 1.0
**Date**: 2025-01-11
**Author**: Claude Code Analysis
