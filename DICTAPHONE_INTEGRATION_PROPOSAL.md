# Dictaphone Integration Proposal for AutoA11y

## Executive Summary

This proposal outlines the integration of **Dictaphone** (audio-based accessibility audit tool) data into **AutoA11y** (automated accessibility testing platform). Dictaphone analyzes audio/video recordings (MP4 files) from manual audits and lived experience testing sessions, generating structured accessibility issues with timecoded references. AutoA11y will serve as the master portal, combining automated test results with human-validated findings from Dictaphone to provide comprehensive accessibility reporting.

---

## 1. Understanding Dictaphone Data Format

### 1.1 Current Dictaphone JSON Structure

Based on the example file (`example dictaphone issues.json`), Dictaphone generates:

```json
{
  "recording": "NED-A",
  "issues": [
    {
      "title": "Improper use of aside landmark in header region",
      "short_title": "Aside landmark issue",
      "timecodes": [
        {
          "start": "00:00:56.085",
          "end": "00:01:19.265",
          "duration": "00:00:23.180"
        }
      ],
      "what": "Description of the issue...",
      "why": "Impact explanation...",
      "who": "Affected user groups...",
      "remediation": "How to fix...",
      "impact": "medium",
      "wcag": [
        {
          "criteria": "1.3.1",
          "level": "A",
          "versions": ["2.0", "2.1", "2.2"]
        }
      ]
    }
  ]
}
```

### 1.2 Key Differences from AutoA11y Data

| Aspect | AutoA11y (Automated) | Dictaphone (Manual) |
|--------|---------------------|---------------------|
| **Scope** | Page-level | Recording-level (MP4 file) |
| **Reference** | XPath, HTML elements | Timecodes (HH:MM:SS.mmm) |
| **Context** | Single page URL | Audio/video recording session |
| **Issues** | Machine-detected patterns | Human observations |
| **Detail** | Technical (XPath, DOM) | Narrative (what/why/who) |
| **Validation** | Automated rules | Expert judgment + lived experience |
| **Link to Code** | Direct HTML/CSS reference | Descriptive, may span multiple pages |

---

## 2. Proposed Data Model Integration

### 2.1 New Model: Recording

Create a new top-level entity to represent Dictaphone audit sessions:

```python
@dataclass
class Recording:
    """Audio/video recording session from Dictaphone"""

    # Core identifiers
    recording_id: str  # e.g., "NED-A"
    title: str
    description: Optional[str] = None

    # Media information
    media_file_path: Optional[str] = None  # Path to MP4 file
    duration: Optional[str] = None  # Total recording duration
    recorded_date: Optional[datetime] = None

    # Audit context
    auditor_name: Optional[str] = None
    auditor_role: Optional[str] = None  # e.g., "Screen Reader User", "Expert Auditor"
    audit_type: str = "manual"  # "manual", "lived_experience", "expert_review"

    # Relationships
    project_id: Optional[str] = None  # Link to AutoA11y project
    website_ids: List[str] = field(default_factory=list)  # Pages covered
    page_urls: List[str] = field(default_factory=list)  # URLs discussed

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    _id: Optional[ObjectId] = None
```

### 2.2 Enhanced Violation Model

Extend the existing `Violation` model to support both automated and manual findings:

```python
@dataclass
class Violation:
    """Unified violation model for automated and manual findings"""

    # Existing fields...
    id: str
    impact: ImpactLevel
    touchpoint: str
    description: str
    wcag_criteria: List[str]

    # NEW: Source tracking
    source_type: str = "automated"  # "automated", "manual", "hybrid"
    detection_method: Optional[str] = None  # "axe", "pa11y", "dictaphone", "expert"

    # NEW: Manual audit fields (from Dictaphone)
    short_title: Optional[str] = None
    what: Optional[str] = None  # Issue description (more detailed)
    why: Optional[str] = None  # Why it matters
    who: Optional[str] = None  # Affected user groups
    remediation: Optional[str] = None  # How to fix

    # NEW: Recording context (for manual findings)
    recording_id: Optional[str] = None
    timecodes: List[Dict[str, str]] = field(default_factory=list)
    # timecode format: {"start": "00:00:56.085", "end": "00:01:19.265", "duration": "00:00:23.180"}

    # Existing automated test fields (may be None for manual findings)
    xpath: Optional[str] = None
    element: Optional[str] = None
    html: Optional[str] = None
```

### 2.3 Database Schema Updates

**New Collections:**

1. **`recordings`** - Store Dictaphone audit sessions
   - One recording can relate to multiple pages/websites
   - Contains metadata about the audit session

2. **`recording_issues`** - Store issues from recordings
   - Similar to test_results but recording-centric
   - Links to both `recordings` and `pages` collections

**Modified Collections:**

3. **`projects`** - Add recording_ids list
   ```python
   recording_ids: List[str] = field(default_factory=list)
   ```

---

## 3. Import/Upload Workflow

### 3.1 Upload Interface

Add new section to AutoA11y web interface:

```
Navigation:
- Projects
- Websites
- Pages
- Test Results
- [NEW] Recordings
  - Upload Recording Data
  - View Recordings
  - Recording Issues
```

### 3.2 Upload Process

```
1. User selects project (required)
2. User uploads Dictaphone JSON file
3. System parses JSON and displays preview:
   - Recording ID
   - Number of issues found
   - Impact distribution
   - WCAG criteria coverage
4. User maps recording to website(s) and/or specific page(s) (optional)
5. User adds audit context:
   - Auditor name/role
   - Recording date
   - Audit type
6. System imports data:
   - Creates Recording record
   - Creates RecordingIssue records
   - Links to project/website/pages
7. System updates project summary stats
```

### 3.3 Import API

```python
class DictaphoneImporter:
    """Import Dictaphone JSON data into AutoA11y"""

    def import_recording(
        self,
        json_file_path: str,
        project_id: str,
        website_ids: Optional[List[str]] = None,
        page_urls: Optional[List[str]] = None,
        auditor_info: Optional[Dict] = None
    ) -> Recording:
        """
        Import a Dictaphone JSON file

        Args:
            json_file_path: Path to dictaphone JSON file
            project_id: AutoA11y project to attach to
            website_ids: Optional website IDs this recording covers
            page_urls: Optional specific page URLs discussed
            auditor_info: Optional dict with auditor_name, auditor_role, etc.

        Returns:
            Recording object
        """
        pass

    def parse_dictaphone_json(self, json_data: dict) -> Tuple[Recording, List[Violation]]:
        """Parse Dictaphone JSON into Recording and Violations"""
        pass

    def map_dictaphone_impact(self, impact_str: str) -> ImpactLevel:
        """Map Dictaphone impact levels to AutoA11y ImpactLevel enum"""
        pass
```

---

## 4. Scoring & Reporting Integration

### 4.1 Scoring Approach

**Challenge:** Recordings are not page-specific, so traditional page scoring doesn't apply directly.

**Proposed Solution:**

1. **Recording-Level Score**
   - Calculate score based on issues found in recording
   - Use same ResultProcessor.calculate_score() logic
   - Create synthetic TestResult from recording issues
   - Display as "Manual Audit Score" for the recording

2. **Project-Level Integration**
   - **Combined Score**: Average of automated page scores + recording scores
   - **Automated Score**: Average of all automated test results
   - **Manual Audit Score**: Average of all recording scores
   - **Comprehensive Score**: Weighted combination (e.g., 70% automated, 30% manual)

3. **Page-Level Linking (Optional)**
   - If recording issues can be mapped to specific pages:
     - Show recording issues alongside automated issues on page reports
     - Include in page score calculation (flagged as "manual verification")
     - Link to timecode in recording for context

### 4.2 Scoring Formula

```python
def calculate_recording_score(recording_issues: List[Violation]) -> float:
    """
    Calculate accessibility score for a recording
    Uses same algorithm as automated tests
    """
    # Create synthetic TestResult
    synthetic_result = TestResult(
        violations=[i for i in recording_issues if i.impact == ImpactLevel.HIGH or i.impact == ImpactLevel.MEDIUM],
        warnings=[i for i in recording_issues if i.impact == ImpactLevel.LOW],
        info=[],
        discovery=[],
        passes=[],
        metadata={
            'applicable_checks': len(recording_issues),
            'passed_checks': 0,  # All issues are failures
            'failed_checks': len(recording_issues)
        }
    )

    processor = ResultProcessor()
    return processor.calculate_score(synthetic_result)['score']
```

### 4.3 Compliance Scoring

```python
def calculate_project_compliance(project_id: str) -> Dict:
    """
    Calculate comprehensive compliance including manual audits
    """
    return {
        'automated_compliance': calculate_automated_compliance(project_id),
        'manual_audit_compliance': calculate_recording_compliance(project_id),
        'combined_compliance': weighted_average(...),
        'wcag_coverage': {
            'automated': [...],
            'manual': [...],
            'combined': [...]
        }
    }
```

---

## 5. Reporting Enhancements

### 5.1 Project Dashboard Updates

Add new cards to project overview:

```
┌─────────────────────────┐  ┌─────────────────────────┐
│ Automated Tests         │  │ Manual Audits           │
│ 45 pages tested         │  │ 3 recordings            │
│ Score: 87.3%            │  │ Score: 82.1%            │
└─────────────────────────┘  └─────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ Comprehensive Accessibility Score: 85.7%               │
│ (70% automated + 30% manual audit)                     │
└────────────────────────────────────────────────────────┘
```

### 5.2 New Report Types

**5.2.1 Recording Detail Report**

```html
Recording: NED-A
Auditor: John Smith (Screen Reader User)
Date: 2025-10-31
Duration: 00:51:23

Issues Found: 28
- High Impact: 12
- Medium Impact: 10
- Low Impact: 6

[List of issues with timecodes, expandable accordions]
```

**5.2.2 Comprehensive HTML Report (Enhanced)**

Add new section after automated test results:

```html
<h2>Manual Audit Findings</h2>
<p>Based on 3 audit recordings by accessibility experts and users</p>

<div class="recordings">
  <div class="recording-card">
    <h3>Recording NED-A</h3>
    <p>Screen reader user testing - 28 issues identified</p>
    <a href="#" class="btn">View Issues</a>
    <a href="recordings/NED-A.mp4" class="btn">Watch Recording</a>
  </div>
</div>

<h3>Issues Requiring Manual Verification</h3>
<p>The following issues were identified in manual audits but may not be detected by automated tools:</p>

[List of manual-only issues with links to timecodes]
```

**5.2.3 Excel Report Enhancement**

Add new sheets:

- **"Manual Audit Issues"** - All issues from recordings
  - Columns: Recording ID, Title, Short Title, Impact, Timecodes, What, Why, Who, Remediation, WCAG

- **"Combined Issues (Deduplicated)"** - Merge automated + manual
  - Identify duplicates between automated and manual findings
  - Mark source (Automated/Manual/Both)

### 5.3 Issue Deduplication Strategy

Some issues may be found by BOTH automated tools AND manual audits:

```python
def identify_duplicate_issues(
    automated_issues: List[Violation],
    manual_issues: List[Violation]
) -> List[Tuple[Violation, Violation]]:
    """
    Match automated and manual issues that describe the same problem

    Strategy:
    1. Match by WCAG criteria + impact level
    2. Use fuzzy matching on descriptions
    3. Consider xpath/element matches if available
    4. Tag as "Confirmed by manual audit" if matched
    """
    pass
```

---

## 6. UI/UX Mockups

### 6.1 Navigation Addition

```
┌────────────────────────────────────────────┐
│ AutoA11y - Accessibility Testing Platform  │
├────────────────────────────────────────────┤
│ [Projects] [Websites] [Pages] [Recordings] │  ← NEW
└────────────────────────────────────────────┘
```

### 6.2 Recordings List Page

```
┌──────────────────────────────────────────────────────────┐
│ Recordings                                   [+ Upload]   │
├──────────────────────────────────────────────────────────┤
│                                                            │
│ Filter: [All Projects ▼] [All Auditors ▼] [Date Range]   │
│                                                            │
│ ┌────────────────────────────────────────────────────┐   │
│ │ NED-A                                   Score: 82% │   │
│ │ Main Website Audit                                 │   │
│ │ 📹 00:51:23 | 👤 John Smith | 📅 2025-10-31       │   │
│ │ 28 issues • 12 high • 10 medium • 6 low            │   │
│ │ [View Details] [Watch Recording] [Download JSON]    │   │
│ └────────────────────────────────────────────────────┘   │
│                                                            │
│ ┌────────────────────────────────────────────────────┐   │
│ │ NED-B                                   Score: 89% │   │
│ │ Homepage Deep Dive                                 │   │
│ │ 📹 00:32:15 | 👤 Jane Doe | 📅 2025-10-28         │   │
│ │ 15 issues • 3 high • 8 medium • 4 low              │   │
│ │ [View Details] [Watch Recording] [Download JSON]    │   │
│ └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 6.3 Recording Detail Page

```
┌──────────────────────────────────────────────────────────┐
│ ← Back to Recordings                                      │
├──────────────────────────────────────────────────────────┤
│ Recording: NED-A                                          │
│ Main Website Screen Reader Audit                          │
│                                                            │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐            │
│ │ Score      │ │ Issues     │ │ Duration   │            │
│ │ 82.3%      │ │ 28         │ │ 00:51:23   │            │
│ └────────────┘ └────────────┘ └────────────┘            │
│                                                            │
│ Auditor: John Smith (Screen Reader User)                  │
│ Date: October 31, 2025                                    │
│ Project: Main Website Redesign                            │
│ Pages: /home, /about, /contact, /services                 │
│                                                            │
│ ┌────────────────────────────────────────────────────┐   │
│ │ 🎬 Video Player                                     │   │
│ │ [====================|-------------------------]    │   │
│ │ 00:12:34 / 00:51:23                                │   │
│ │ [◀◀] [▶] [▶▶] 🔊 [Jump to Issue Timecode ▼]      │   │
│ └────────────────────────────────────────────────────┘   │
│                                                            │
│ Issues (28) [High(12)] [Medium(10)] [Low(6)]              │
│                                                            │
│ ┌────────────────────────────────────────────────────┐   │
│ │ ⚠️ HIGH • Multiple navigation regions lack labels  │   │
│ │ Timecodes: 00:01:26 - 00:01:33, 00:34:35 - 00:34:39 │ │
│ │ WCAG: 1.3.1 (A), 5.2.4 (AA)                       │   │
│ │                                                     │   │
│ │ What: The page contains multiple navigation...     │   │
│ │ Why: Screen reader users rely on landmark...       │   │
│ │ Who: Screen reader users, keyboard users           │   │
│ │ How to Fix: Add unique labels to each nav...       │   │
│ │                                                     │   │
│ │ [🎬 Jump to 00:01:26] [📄 View Full Details]      │   │
│ └────────────────────────────────────────────────────┘   │
│                                                            │
│ [Show more issues...]                                     │
└──────────────────────────────────────────────────────────┘
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] Create `Recording` and `RecordingIssue` models
- [ ] Extend `Violation` model with manual audit fields
- [ ] Set up database collections and indexes
- [ ] Create `DictaphoneImporter` class
- [ ] Write unit tests for JSON parsing

### Phase 2: Import Workflow (Weeks 3-4)
- [ ] Build upload interface
- [ ] Implement JSON validation and preview
- [ ] Create recording-project linking
- [ ] Add recording list page
- [ ] Add recording detail page

### Phase 3: Scoring Integration (Weeks 5-6)
- [ ] Implement recording score calculation
- [ ] Update project dashboard with manual audit stats
- [ ] Add combined scoring logic
- [ ] Create score comparison views

### Phase 4: Reporting (Weeks 7-8)
- [ ] Add recordings section to HTML reports
- [ ] Enhance Excel exports with manual audit data
- [ ] Implement issue deduplication logic
- [ ] Add recording detail report template

### Phase 5: Advanced Features (Weeks 9-10)
- [ ] Video player integration (optional)
- [ ] Timecode navigation
- [ ] Issue matching/deduplication UI
- [ ] Bulk upload capability
- [ ] Export combined reports

---

## 8. Technical Considerations

### 8.1 Data Storage

**Size Considerations:**
- Dictaphone JSON files: ~50-200 KB per recording
- MP4 video files: 500 MB - 2 GB per recording

**Storage Strategy:**
- Store JSON in MongoDB (small size)
- Store MP4 files in filesystem or cloud storage (S3, Azure Blob)
- Store file path reference in database

### 8.2 Performance

- Index recordings by project_id, recording_id, recorded_date
- Cache score calculations
- Paginate issue lists for large recordings

### 8.3 Security

- Validate uploaded JSON schema
- Sanitize file uploads
- Access control: only project members can view recordings
- Audit log for imports and deletions

### 8.4 Backward Compatibility

- All existing automated test functionality remains unchanged
- New fields are optional with sensible defaults
- Reports gracefully handle projects with no recordings

---

## 9. Benefits & Value Proposition

### 9.1 For Accessibility Teams

✅ **Single source of truth** - All accessibility data in one platform
✅ **Comprehensive coverage** - Automated + human validation
✅ **Better insights** - Combine quantitative metrics with qualitative feedback
✅ **Audit trail** - Track findings from both tools and testers
✅ **Efficiency** - No need to maintain separate reporting systems

### 9.2 For Stakeholders

✅ **Complete picture** - Scores reflect both automated and expert testing
✅ **User perspective** - Lived experience findings complement automated tests
✅ **Prioritization** - Issues confirmed by multiple sources bubble up
✅ **Confidence** - Manual validation increases trust in results

### 9.3 For Development Teams

✅ **Context** - Timecoded recordings show real user impact
✅ **Clarity** - "What/Why/Who/How" fields aid understanding
✅ **Remediation** - Clear fix instructions from experts
✅ **Verification** - Can watch recording to understand issue

---

## 10. Open Questions & Decisions Needed

### 10.1 Scoring Weights

**Question:** How should automated vs manual scores be weighted in combined score?

**Options:**
- A: Equal weight (50/50)
- B: Higher weight for manual (30/70) - expert judgment valued more
- C: Higher weight for automated (70/30) - broader coverage
- **D: Configurable per project** ✅ RECOMMENDED

### 10.2 Issue Matching

**Question:** Should we automatically match/deduplicate issues found by both methods?

**Options:**
- A: Fully automatic (may have false positives)
- B: Semi-automatic with manual review ✅ RECOMMENDED
- C: Manual only (more work but accurate)

### 10.3 Video Hosting

**Question:** How to handle video files?

**Options:**
- A: Store locally in AutoA11y filesystem
- B: Upload to cloud storage (S3/Azure/GCS)
- **C: Store path reference only** - video stays in Dictaphone system ✅ RECOMMENDED
- D: Embed video player in AutoA11y

### 10.4 Multiple Recordings Per Page

**Question:** Can multiple recordings reference the same page?

**Answer:** Yes - different auditors may test same page at different times. Show chronologically with "Latest", "Previous" markers.

---

## 11. Future Enhancements

### Post-MVP Features

1. **Bidirectional Sync** - Update Dictaphone when AutoA11y finds new issues
2. **Issue Assignment** - Assign recording issues to developers
3. **Remediation Tracking** - Mark recording issues as fixed, retest
4. **Annotation Tool** - Add comments/notes to specific timecodes
5. **AI Analysis** - Transcribe audio, extract additional insights
6. **Real-time Upload** - Dictaphone pushes to AutoA11y via API
7. **Comparison Reports** - Before/after recordings show improvements
8. **Trend Analysis** - Track issue types over multiple recordings

---

## 12. Conclusion

This integration will position **AutoA11y as the central hub** for all accessibility data - both automated and human-validated. By combining Dictaphone's rich, narrative, expert-driven findings with AutoA11y's comprehensive automated testing, teams gain unprecedented visibility into their accessibility posture.

The phased approach allows for iterative development and early value delivery, while the extensible data model ensures future tools can be integrated seamlessly.

**Next Steps:**
1. Review and approve this proposal
2. Prioritize Phase 1 tasks
3. Create detailed technical specifications
4. Begin implementation of data models and import workflow

---

**Document Version:** 1.0
**Author:** Claude (AI Assistant)
**Date:** 2025-11-01
**Status:** DRAFT - Awaiting Review
