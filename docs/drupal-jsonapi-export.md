# Drupal JSON:API Export Feature

## Overview

This feature enables exporting accessibility test results from Auto A11y to a Drupal 10 site via the JSON:API interface. This allows test results to be consumed by other reporting tools and integrated into broader content management workflows.

## Background

The Drupal site has REST API capabilities but experiences issues with entity reference fields when using the traditional REST API. To work around these issues, we're implementing integration using Drupal's JSON:API module, which provides more reliable handling of entity relationships and follows a standardized specification.

## Configuration Requirements

### Drupal Site Details



**Base URL:**
- Production URL: https://audits.frontier-cnib.ca
- Staging/Test URL: Currently under maintenance
- HTTPS Enabled: Yes 

### Authentication

**Method:** HTTP Basic Authentication

**Credentials:**
- Username: `restuser`
- Password: venez1a?
- Storage method: config file (for now)

### Drupal Content Types

> **Note:** In Drupal terminology, "Audits" = Auto A11y "Projects", and "Issues" = Auto A11y "Test Results/Violations"

#### Content Type: Issue (Test Result/Violation)

**Machine Name:** `issue`

**Bundle Description:** Represents a single accessibility issue/violation found during testing. Maps to our test result violations.

**Available Fields:**

| Field Machine Name | Field Label | Field Type | Required | Description/Notes |
|-------------------|-------------|------------|----------|-------------------|
| `title` | Title | String | Yes | Issue code/name (e.g., "ErrDuplicateLabelForRegionLandmark") |
| `body` | Body | Text (formatted) | No | HTML formatted: What/Why/Who/How to remediate |
| `field_xpath` | XPath | String | No | XPath to the element with the issue |
| `field_ticket_status` | Ticket Status | List (string) | No | Values like "ticket_status_fail" |
| `field_parent_audit` | Parent Audit | Entity Reference | Yes | References the Audit (our Project) |
| `field_discovered_page_issue` | Discovered Page | Entity Reference | Yes | References the Page being tested |
| `field_parent_failure_point` | Parent Failure Point | Entity Reference | No | References a failure point taxonomy/node |
| `field_issue_category` | Issue Category | Entity Reference | No | References issue category taxonomy |
| `field_created_by_automated_testi` | Created By Automated Testing | Boolean | No | TRUE for automated, FALSE for manual |
| `field_transcript` | Transcript | Text (formatted) | No | For manual issues - transcript of observation |
| `field_video_timecode` | Video Timecode | String | No | For manual issues - timecode in video |
| `field_video` | Video | Entity Reference | No | For manual issues - references video entity |
| `field_issue_notes` | Issue Notes | Text | No | Additional notes/screenshots |

#### Content Type: Discovered Page

**Machine Name:** `discovered_page`

**Bundle Description:** Represents a key page/screen flagged for manual inspection or lived experience testing. Typically 20-25 pages per audit are flagged as "interesting" for deeper analysis.

**Purpose:** Discovered pages help auditors and test supervisors identify pages that warrant manual inspection. Pages are interesting if they show accessibility concerns or contain complex UI elements (date pickers, carousels, forms, videos, etc.).

**Available Fields:**

| Field Machine Name | Field Label | Field Type | Required | Description/Notes |
|-------------------|-------------|------------|----------|-------------------|
| `title` | Title | String | Yes | Page name/title |
| `field_include_in_report` | Include in Report | Boolean | Yes | Whether to include in reports (default: true) |
| `field_page_url` | Page URL | Link | Yes | URL of the page tested |
| `field_abbreviation` | Abbreviation | String | No | 4-8 char abbreviation (rarely used) |
| `field_notes_in_discovery` | Discovery Notes | Text (formatted, multiple) | No | Private notes for auditors (HTML) |
| `field_public_note_on_page` | Public Note | Text (formatted) | No | Public notes for audit reports (HTML) |
| `field_interested_because` | Interested Because | Taxonomy Reference (multiple) | No | WHY this page is interesting (75 terms) |
| `field_relevant_page_elements` | Page Elements | Taxonomy Reference (multiple) | No | AREAS of display (16 terms: header, footer, etc.) |
| `field_screenshots_discovery` | Screenshots | File Reference (multiple) | No | Discovery phase screenshots |
| `field_document_links_on_page` | Document Links | Link (multiple) | No | PDFs/documents found on page |
| `field_audited` | Audited | Boolean | No | Has this page been audited? |
| `field_manual_audit` | Manual Audit | Boolean | No | Has this page had manual inspection? |
| `field_parent_audit_discovery` | Parent Audit | Entity Reference | Yes | References the Audit (our Project) |

**Key Taxonomies:**

1. **interested_in_because** (75 terms) - Why pages are flagged:
   - Form, Date Picker or Calendar, Carousel or Image Gallery
   - Modal dialog, Video, Interactive map or widget
   - Keyboard Inaccessible, Focus Order, ARIA use
   - Tables, Accordions, Tabbed Pane, etc.
   - See [Full Term List](#interested-because-taxonomy)

2. **page_elements** (16 terms) - Areas of display:
   - Header, Footer, Main body
   - Left Sidebar, Right sidebar
   - Search region, Hamburger menu, Modal dialog
   - Hero image, Language Selector, etc.
   - See [Full Term List](#page-elements-taxonomy)

#### Content Type: Audit (Project)

**Machine Name:** `audit`

**Key Info:**
- Retrieved via REST endpoint: `/rest/open_audits`
- Has fields: `title`, `nid`, `uuId`, `field_abbreviation`
- Audits must already exist in Drupal - we reference them, don't create them

#### Content Type: Audit Video (Recording)

**Machine Name:** `audit_video`

**Bundle Description:** Represents a recording/video of a user session during testing. Maps to our Recording model.

**Available Fields:**

| Field Machine Name | Field Label | Field Type | Required | Description/Notes |
|-------------------|-------------|------------|----------|-------------------|
| `title` | Title | String | Yes | Recording name/title |
| `body` | Body | Text (formatted) | No | Description/notes about the recording |
| `field_video_url` | Video URL | Link | No | External URL where video is hosted (Screencast.com, etc.) |
| `field_video_host` | Video Host | String | No | Identifier for video hosting platform |
| `field_play_sequence` | Play Sequence | Integer | No | Order/sequence number for this video |
| `field_audit` | Parent Audit | Entity Reference | Yes | References the Audit (our Project) |
| `field_discovered_pages` | Discovered Pages | Entity Reference (multiple) | No | Links to pages visited in recording |
| `field_exploratory_test_subtasks` | Exploratory Test Subtasks | Entity Reference (multiple) | No | Links to exploratory test tasks |
| `field_scripted_lived_test_runs` | Scripted/Lived Test Runs | Entity Reference (multiple) | No | Links to scripted test runs |

**Key Points:**
- 50 existing audit_video entries in production Drupal
- Videos are stored externally (not uploaded to Drupal)
- Proper entity reference to parent audit (no text field workaround needed!)
- Can link to multiple discovered pages
- Supports both exploratory and scripted testing workflows

#### Supporting Content Types

**Failure Point:**
- **Machine Name:** `failure_point`
- **Purpose:** Groups issues by component/location (Header, Footer, Navigation, etc.)
- **Fields:** `title`, `field_fp_temp_id`, `field_xpath`, `field_parent_audit`, `field_parent_discovered_page`, `field_failure_point` (taxonomy term)

**Issue Categories:**
- Taxonomy terms retrieved via `/rest/issue_categories`
- Used to categorize issues by type

**Failure Point Types:**
- Taxonomy terms retrieved via `/rest/failure_point_types`
- Examples: Header, Footer, Banner, ContentInfo, Navigation, etc.

### Data Mapping

#### From Auto A11y to Drupal

**Workflow:**
1. Look up Audit (Project) by title to get UUID
2. Create/find Discovered Page for the page being tested
3. Create Failure Point for component (if needed)
4. Create Issue for each violation

**Automated Test Results (Violations):**

| Auto A11y Field | Maps to Drupal Field | Drupal Content Type | Transformation Needed |
|----------------|---------------------|---------------------|----------------------|
| `page.url` | `field_page_url` | `discovered_page` | Format as link field |
| `page.name` | `title` | `discovered_page` | Page title |
| `violation.id` | `title` | `issue` | Issue code (e.g., "ErrDuplicateLabelForRegionLandmark") |
| `violation.description` | `body` (What section) | `issue` | Format as HTML |
| `violation.impact` | `field_ticket_status` | `issue` | Map: high→"ticket_status_fail", etc. |
| `violation.xpath` | `field_xpath` | `issue` | Direct mapping |
| `violation.html` | `field_issue_notes` | `issue` | Include as note/context |
| `violation.touchpoint` | `field_issue_category` | `issue` | Lookup taxonomy term ID |
| `project.id` | `field_parent_audit` | `issue` | Lookup Audit UUID by project name |
| `project.id` | `field_parent_audit_discovery` | `discovered_page` | Lookup Audit UUID by project name |
| N/A | `field_created_by_automated_testi` | `issue` | Set to TRUE |
| N/A | `field_include_in_report` | `discovered_page` | Set to TRUE |
| N/A | `field_abbreviation` | `discovered_page` | Generate 4-8 char abbreviation |

**Recordings (Audit Videos):**

| Auto A11y Field | Maps to Drupal Field | Drupal Content Type | Transformation Needed |
|----------------|---------------------|---------------------|----------------------|
| `recording.filename` | `title` | `audit_video` | Recording name/identifier |
| `recording.description` | `body` (intro) | `audit_video` | HTML formatted description |
| `recording.key_takeaways` | `body` (section) | `audit_video` | HTML formatted as `<h3>Key Takeaways</h3><ol>...</ol>` |
| `recording.user_painpoints` | `body` (section) | `audit_video` | HTML formatted as `<h3>User Painpoints</h3><h4>...</h4>` with quotes |
| `recording.user_assertions` | `body` (section) | `audit_video` | HTML formatted as `<h3>User Assertions</h3><ol>...</ol>` with quotes |
| `recording.auditor_name` + `auditor_role` | `body` (intro) | `audit_video` | Include auditor info in HTML |
| `recording.video_url` | `field_video_url` | `audit_video` | External video URL (if stored externally) |
| `recording.session_date` | `created` | `audit_video` | Recording date |
| `recording.project_id` | `field_audit` | `audit_video` | Lookup Audit UUID by project name |
| `recording.pages_visited` | `field_discovered_pages` | `audit_video` | Array of page UUIDs |
| N/A | `field_play_sequence` | `audit_video` | Auto-increment or set explicitly |

**Note:** The `body` field contains HTML-formatted content combining description, key takeaways, painpoints, and assertions. Issues are NOT included in the body - they are created as separate `issue` entities and linked via the `field_video` relationship.

**Manual Recording Issues (from Dictaphone):**

| Auto A11y Field | Maps to Drupal Field | Drupal Content Type | Transformation Needed |
|----------------|---------------------|---------------------|----------------------|
| `recording.recording_id` | `title` | `issue` | Use as issue title |
| `issue.title` | `body` (What section) | `issue` | Format as HTML |
| `issue.what` | `body` (What section) | `issue` | Format as HTML |
| `issue.why` | `body` (Why section) | `issue` | Format as HTML |
| `issue.who` | `body` (Who section) | `issue` | Format as HTML |
| `issue.remediation` | `body` (How section) | `issue` | Format as HTML |
| `issue.impact` | `field_ticket_status` | `issue` | Map: high→"ticket_status_fail" |
| `issue.touchpoint` | `field_issue_category` | `issue` | Lookup taxonomy term ID |
| `issue.timecodes[0]` | `field_video_timecode` | `issue` | Format timecode string |
| `recording.project_id` | `field_parent_audit` | `issue` | Lookup Audit UUID |
| `recording.video_id` | `field_video` | `issue` | Reference to audit_video entity UUID |
| N/A | `field_created_by_automated_testi` | `issue` | Set to FALSE |
| N/A | `field_transcript` | `issue` | Format HTML with transcript |

**Component/Failure Point Mapping:**

| Auto A11y Touchpoint | Drupal Failure Point Type | Notes |
|---------------------|---------------------------|-------|
| Banner | Header | Mapped in connector |
| ContentInfo | Footer | Mapped in connector |
| Navigation | Navigation | Direct mapping |
| Main | Main | Direct mapping |
| Forms | Form | Direct mapping |
| Color Contrast | Color Contrast | Direct mapping |
| Images | Images | Direct mapping |
| (others) | (lookup in taxonomy) | Retrieve from `/rest/failure_point_types` |

### Referenced Entities

#### Audits (Auto A11y Projects)

**Do Projects exist in Drupal?** YES

**Details:**
- Content Type/Bundle: Unknown (not specified in connector, but exists)
- Retrieved via: `GET /rest/open_audits`
- Match strategy: **By title (exact match)**
- Fields available: `title`, `nid`, `uuId`, `field_abbreviation`
- **We do NOT create Audits** - they must already exist in Drupal
- **Lookup process:**
  1. Fetch all open audits from `/rest/open_audits`
  2. Match Auto A11y project name to Drupal audit title
  3. Cache the UUID for use in entity references

#### Pages (Discovered Pages)

**Do Pages exist in Drupal?** SOMETIMES - created on demand

**Details:**
- Content Type/Bundle: `discovered_page`
- Match strategy: **By URL AND title**
- **We DO create pages** if they don't exist
- Before creating, check if page exists with same `field_page_url` and `title`
- Required fields for creation:
  - `title` (page name)
  - `field_page_url` (URL)
  - `field_abbreviation` (generated 4-8 char code)
  - `field_parent_audit_discovery` (reference to audit)
  - `field_include_in_report` (boolean, default TRUE)

#### Failure Points

**Do Failure Points exist in Drupal?** NO - created for each page component

**Details:**
- Content Type/Bundle: `failure_point`
- Purpose: Groups issues by page component/location
- Created automatically when issues are exported
- One failure point per touchpoint per page
- Required fields:
  - `title` (generated: AuditAbbrev-PageAbbrev-Component-RandomCode)
  - `field_parent_audit` (reference to audit)
  - `field_parent_discovered_page` (reference to page)
  - `field_failure_point` (taxonomy term for type)
  - `field_xpath` (XPath if applicable)
  - `field_fp_temp_id` (temporary ID for tracking)

#### Issue Categories (Taxonomy)

**Pre-existing in Drupal:** YES

**Details:**
- Taxonomy vocabulary for categorizing issues
- Retrieved via: `GET /rest/issue_categories`
- Must map Auto A11y touchpoints to Drupal taxonomy term IDs
- **Cache strategy:** Fetch once at connection init, cache locally

#### Failure Point Types (Taxonomy)

**Pre-existing in Drupal:** YES

**Details:**
- Taxonomy vocabulary for component types
- Retrieved via: `GET /rest/failure_point_types`
- Examples: Header, Footer, Navigation, Main, Form, etc.
- **Special mappings:** Banner→Header, ContentInfo→Footer
- **Cache strategy:** Fetch once at connection init, cache locally

## Export Workflow

### Trigger Options

**When should export happen?**

- [ ] Manual trigger (button in UI)
- [ ] Automatic after each test run
- [ ] Scheduled batch export (e.g., nightly)
- [ ] API endpoint for external triggers
- [ ] Other: ___________

**What data should be exported?**

- [ ] Individual page test results (automated tests)
- [ ] Recording issues (manual audits)
- [ ] Project summaries/reports
- [ ] Website-level aggregated data
- [ ] All of the above

**Export behavior:**

- [ ] Only export new results (not previously exported)
- [ ] Re-export all results on each run
- [ ] Update existing Drupal content if it exists
- [ ] Always create new Drupal content

### Error Handling

**What should happen if export fails?**

- [ ] Log error and continue with other items
- [ ] Stop entire export process
- [ ] Retry automatically (how many times? _______)
- [ ] Queue for manual review
- [ ] Send notification (email/slack/other)

**What should happen if entity references can't be resolved?**

- [ ] Skip the item and log error
- [ ] Create the content without the reference
- [ ] Attempt to create the referenced entity first
- [ ] Fail and report to user

## HTML Body Format for Recordings

The `body` field of `audit_video` content type contains HTML-formatted content with the following structure:

```html
<!-- Description and auditor info -->
<p>Recording description goes here</p>
<p><em>Tested by: Auditor Name, Role</em></p>

<!-- Key Takeaways Section -->
<h3>Key Takeaways</h3>
<ol>
  <li><strong>Topic Title</strong> &ndash; Description of the takeaway</li>
  <li><strong>Another Topic</strong> &ndash; Description text</li>
</ol>

<!-- User Painpoints Section -->
<h3>User Painpoints</h3>
<h4><span class="badge badge-high">HIGH</span> Painpoint Title</h4>
<blockquote>
  <p><em>"User quote describing the painpoint"</em></p>
</blockquote>
<p><strong>Timecodes:</strong> 00:05:23 &ndash; 00:06:45</p>

<!-- User Assertions Section -->
<h3>User Assertions</h3>
<ol>
  <li>
    <p><strong>Assertion statement</strong></p>
    <blockquote>
      <p><em>"User quote supporting the assertion"</em></p>
    </blockquote>
    <p><em>Context:</em> Additional context information</p>
    <p><strong>Timecodes:</strong> 00:02:15 &ndash; 00:03:30</p>
  </li>
</ol>
```

**Notes:**
- Uses standard HTML heading levels (h3 for major sections, h4 for painpoint titles)
- Impact badges use CSS classes (badge-high, badge-medium, badge-low)
- User quotes are in `<blockquote>` tags with `<em>` for italic styling
- Timecodes use &ndash; (en dash) between start and end times
- All text is HTML-escaped for security
- Structure is flexible - sections are omitted if data is not available

## Data Format Examples

### Sample JSON:API Request Body for Audit Video

```json
{
  "data": {
    "type": "node--audit_video",
    "attributes": {
      "title": "User Testing Session - Checkout Flow",
      "body": {
        "value": "<p>Usability testing...</p><h3>Key Takeaways</h3>...",
        "format": "formatted_text"
      },
      "field_video_url": {
        "uri": "https://screencast.com/t/abc123",
        "title": ""
      },
      "field_play_sequence": 1
    },
    "relationships": {
      "field_audit": {
        "data": {
          "type": "node--audit",
          "id": "e9e9dffa-e707-4fb0-9c03-368a09a8dc6e"
        }
      },
      "field_discovered_pages": {
        "data": [
          {
            "type": "node--discovered_page",
            "id": "page-uuid-1"
          },
          {
            "type": "node--discovered_page",
            "id": "page-uuid-2"
          }
        ]
      }
    }
  }
}
```

### Sample JSON:API Request Body for Issue

```json
{
  "data": {
    "type": "node--issue",
    "attributes": {
      "title": "Missing Form Label",
      "body": {
        "value": "<h4>What</h4><p>Email field lacks proper label...</p>",
        "format": "formatted_text"
      },
      "field_xpath": "//input[@type='email']",
      "field_ticket_status": "ticket_status_fail",
      "field_created_by_automated_testi": false,
      "field_video_timecode": "00:05:23",
      "field_transcript": {
        "value": "<p>User attempted to locate email field...</p>",
        "format": "formatted_text"
      }
    },
    "relationships": {
      "field_parent_audit": {
        "data": {
          "type": "node--audit",
          "id": "audit-uuid"
        }
      },
      "field_discovered_page_issue": {
        "data": {
          "type": "node--discovered_page",
          "id": "page-uuid"
        }
      },
      "field_video": {
        "data": {
          "type": "node--audit_video",
          "id": "video-uuid"
        }
      },
      "field_issue_category": {
        "data": {
          "type": "taxonomy_term--issue_category",
          "id": "category-uuid"
        }
      }
    }
  }
}
```

## Implementation Notes

### JSON:API Endpoint Structure

- List content: `GET /jsonapi/node/{bundle}`
- Create content: `POST /jsonapi/node/{bundle}`
- Update content: `PATCH /jsonapi/node/{bundle}/{uuid}`
- Get single item: `GET /jsonapi/node/{bundle}/{uuid}`

### Required Headers

```
Content-Type: application/vnd.api+json
Accept: application/vnd.api+json
Authorization: Basic {base64-encoded-credentials}
```

### UUID Management

**Strategy for tracking Drupal UUIDs:**

- [ ] Store in Auto A11y database (add field to track Drupal UUID)
- [ ] Query Drupal before each export to get UUID
- [ ] Cache UUIDs locally with expiration
- [ ] Other: ___________

## Testing Plan

### Test Scenarios

1. **Export single test result**
   - Verify all fields map correctly
   - Verify entity references resolve
   - Verify content appears in Drupal

2. **Export batch of results**
   - Verify performance with multiple items
   - Verify error handling for partial failures

3. **Handle missing references**
   - Test when project doesn't exist in Drupal
   - Test when website doesn't exist in Drupal

4. **Authentication failure**
   - Test with invalid credentials
   - Test with expired credentials

5. **Network failure**
   - Test timeout handling
   - Test retry mechanism

### Test Environment

- Drupal Test Site URL: ___________
- Test restuser credentials: ___________
- Test project/website to use: ___________

## Questions to Answer

1. What is the exact machine name of the Drupal content type that should receive test results?

2. What fields exist on that content type, and which are required?

3. Are there any taxonomy terms or other reference entities we need to be aware of?

4. Should we create projects/websites/pages in Drupal if they don't exist, or only reference existing ones?

5. How should we identify/match entities between Auto A11y and Drupal? (by URL, by name, by external ID field?)

6. What should the export workflow be? Manual button, automatic, or both?

7. Where should the export feature be accessible in the UI? (per-project, per-page, per-test result, global export all?)

8. Should we track export history (when was each item last exported)?

9. Are there any Drupal field validation rules or constraints we need to handle?

10. What's the expected volume? (hundreds, thousands, millions of test results?)

## Summary of Findings from alabsConnector.js

Based on the Node.js connector, here's what we learned:

### Architecture Pattern

The old connector uses **REST API with CSRF tokens**, but we'll migrate to **JSON:API** which is more reliable.

**Old Flow (REST):**
1. POST `/user/login?_format=json` to get CSRF token
2. GET `/rest/open_audits` to fetch audits
3. GET `/rest/discovered_pages?audit={nid}` to fetch pages
4. GET `/rest/issues?audit={nid}` to fetch issues
5. POST `/node?_format=json` to create content

**New Flow (JSON:API):**
1. Use Basic Auth (no CSRF needed)
2. GET `/jsonapi/node/audit` to fetch audits with filtering
3. POST `/jsonapi/node/discovered_page` to create pages
4. POST `/jsonapi/node/failure_point` to create failure points
5. POST `/jsonapi/node/issue` to create issues

### Key Differences

| Aspect | Old REST Connector | New JSON:API Implementation |
|--------|-------------------|----------------------------|
| Auth | CSRF Token | Basic Auth (simpler) |
| Entity References | Numeric ID (`target_id`) | UUID (`id` in relationships) |
| Endpoints | `/rest/*` custom views | `/jsonapi/node/*` standardized |
| Field Format | Arrays with values | Attributes + Relationships |
| Error Handling | Custom parsing | Standardized JSON:API errors |

### Export Workflow Design

**For Automated Test Results:**
```
1. User runs accessibility test on a page
2. Test completes with violations
3. User clicks "Export to Drupal" button
4. System:
   a. Looks up Audit (Project) by name → get UUID
   b. Creates/finds Discovered Page → get UUID
   c. For each violation touchpoint:
      - Create Failure Point (if not exists) → get UUID
   d. For each violation:
      - Create Issue with all references
5. Show success/failure summary
```

**For Recordings (Audit Videos):**
```
1. User imports recording
2. User clicks "Export Recording to Drupal" button
3. System:
   a. Looks up Audit (Project) by name → get UUID
   b. Creates/finds Discovered Pages for all pages visited → get UUIDs
   c. Creates Audit Video entity:
      - Link to parent audit
      - Link to discovered pages
      - Set video URL (if stored externally)
      - Set title and description
   d. Get audit_video UUID for linking issues
4. Show success message with link to Drupal
```

**For Manual Recording Issues:**
```
1. User imports recording with issues (or after recording is exported)
2. User clicks "Export Issues to Drupal" button
3. System:
   a. Looks up Audit (Project) by name → get UUID
   b. Looks up or creates Audit Video → get UUID
   c. Creates/finds Discovered Page → get UUID
   d. For each recording issue:
      - Create Failure Point (if not exists) → get UUID
      - Create Issue with:
        * Link to audit_video (field_video)
        * Video timecode (field_video_timecode)
        * Transcript (field_transcript)
        * All standard issue fields
4. Show success/failure summary
```

## Next Steps

### Phase 1: Foundation (Week 1)
1. [x] Document Drupal content structure from alabsConnector.js
2. [x] Create Python JSON:API client module (`auto_a11y/drupal/client.py`)
   - [x] Connection management
   - [x] Basic auth handling
   - [x] GET/POST/PATCH methods with proper headers
   - [x] Error handling and logging
3. [x] Add Drupal configuration to config file
   - [x] Store: base_url, username, password in `config/drupal.conf`
   - [x] Configuration loader (`auto_a11y/drupal/config.py`)
   - [ ] Audit name mapping to projects (deferred to Phase 2)
4. [x] Test basic connection and authentication
   - [x] Created `test_drupal_connection.py` script
   - [x] Successfully connected to https://audits.frontier-cnib.ca
   - [x] Verified 200+ JSON:API resources available
   - [x] Confirmed 30 open audits accessible
5. [x] Investigate audit_video content type
   - [x] Created `investigate_audit_video.py` script
   - [x] Found 50 existing audit_video entries
   - [x] Documented all fields and relationships
   - [x] Confirmed proper entity references (no text field workarounds)

### Phase 2: Entity Management (Week 2)
5. [ ] Implement audit lookup functionality
   - Cache audit list on connection
   - Match by title to get UUID
6. [ ] Implement discovered page creation/lookup
   - Check if page exists by URL+title
   - Create if doesn't exist
   - Generate page abbreviations
7. [ ] Implement taxonomy lookups
   - Fetch and cache issue categories
   - Fetch and cache failure point types
   - Map Auto A11y touchpoints to Drupal terms
8. [ ] Implement failure point creation
   - Generate names with abbreviations
   - Link to audit, page, and taxonomy

### Phase 3: Issue Export (Week 3)
9. [ ] Implement automated issue export
   - Transform violations to Drupal format
   - Format body field as HTML (What/Why/Who/How)
   - Handle XPath and element HTML
   - Set created_by_automated_testing flag
10. [ ] Implement manual issue export
    - Transform recording issues to Drupal format
    - Handle transcript and timecode fields
    - Format rich text properly
11. [ ] Add export tracking
    - Track which items have been exported
    - Prevent duplicate exports
    - Allow re-export if needed

### Phase 4: UI Integration (Week 4)
12. [ ] Add export buttons to UI
    - Project level: Export all test results
    - Page level: Export results for this page
    - Recording level: Export this recording's issues
13. [ ] Create export status display
    - Show progress during export
    - Display success/failure counts
    - Link to Drupal items if possible
14. [ ] Add configuration UI
    - Drupal connection settings
    - Audit name mapping
    - Enable/disable auto-export

### Phase 5: Testing & Deployment
15. [ ] Test with production Drupal site (https://audits.frontier-cnib.ca)
16. [ ] Handle edge cases and error scenarios
17. [ ] Performance testing with large datasets
18. [ ] Documentation for users
19. [ ] Deploy to production

## Open Questions to Answer

1. **Should export be automatic or manual?**
   - Manual trigger gives user control
   - Automatic ensures nothing is missed
   - Recommendation: Manual with option for auto

2. **How to handle export failures?**
   - Recommendation: Log error, continue with others, show summary at end

3. **Should we store Drupal UUIDs in our database?**
   - Recommendation: Yes, add optional fields to track Drupal entity UUIDs for pages and issues

4. **What about updates to existing Drupal content?**
   - Recommendation: Initial version only creates, doesn't update. Add update capability later if needed.

5. **How to handle project name mismatches?**
   - Recommendation: Show dropdown to map Auto A11y project to Drupal audit on first export

## Discovered Pages Taxonomies

### Interested Because Taxonomy

**Vocabulary Machine Name:** `interested_in_because`  
**Total Terms:** 75  
**Purpose:** Tag WHY pages are interesting for manual inspection

**Complete Term List:**

1. Accordions
2. Language selector
3. Animation or motion
4. ARIA use
5. Autocomplete
6. Block capitalized / Italicized text
7. Breadcrumbs
8. Bug
9. Captcha
10. Carousel or Image Gallery
11. Charts or graphs
12. Colour Contrast Issue
13. Colour Picker
14. Colour Use Issue
15. Contains PDFs
16. Contains spreadsheets
17. Contains Word documents
18. Date Picker or Calendar
19. FAQ
20. Floating Controls and Buttons
21. Focus Order
22. Focus Outline
23. Font Issue
24. Form
25. Hamburger menu
26. Heading Misuse
27. Hero Image
28. Home Page
29. Hover or focus content
30. Image annotation issues
31. Infinite Scroll
32. Interactive map or widget
33. Jaws Issue
34. Keyboard Inaccessible
35. Keyboard Trap
36. Language issues
37. Link issues
38. Link/button confusion
39. Lists
40. Load More
41. Magnifier Issues
42. Masonry Tiles
43. Media Player
44. Menu bar
45. Mobile (hamburger) menu
46. Modal dialog
47. Multipage or Multistep Form
48. No Interest
49. Other
50. Page layout
51. Page title issue
52. Pagination
53. Part of an SPA
54. Placeholder text
55. Read More
56. Region issues
57. Representative Layout
58. Responsive Breakpoint Issue
59. Search or search filters
60. Skip links
61. Tabbed Pane
62. Tabindex Use
63. Tables
64. Tables Used for Layout
65. Images of text
66. Text on Noisy Backgrounds
67. Time Picker
68. Title attribute
69. Unique Layout
70. Unlabeled Regions
71. Video
72. Visually hidden gunk
73. VoiceOver Issue
74. WCAG violation
75. Whitespace Issue

**Usage Statistics:**
- Average tags per page: 5.9
- Range: 0-14 tags per page
- 94% of pages have at least one tag

### Page Elements Taxonomy

**Vocabulary Machine Name:** `page_elements`  
**Total Terms:** 16  
**Purpose:** Tag AREAS of display/page sections

**Complete Term List:**

1. Accessibility features
2. Header
3. Footer
4. Main body
5. Search region
6. Hamburger menu
7. Breadcrumb trail
8. Main menu
9. Secondary menu
10. Left Sidebar
11. Right sidebar
12. Interactive element
13. Autocomplete
14. Hero image
15. Modal dialog
16. Language Selector

**Usage Statistics:**
- Average tags per page: 2.9
- Range: 0-7 tags per page
- 86% of pages have at least one tag

## Discovered Pages Integration

### Overview

The Discovered Pages feature allows bidirectional synchronization between Auto A11y and Drupal:

1. **Push:** Export flagged pages from Auto A11y to Drupal
2. **Pull:** Import discovered pages from Drupal to Auto A11y
3. **Sync:** Keep both systems aligned

### Auto A11y Implementation

#### New Models

**Page Model Extensions:**
- `is_flagged_for_discovery` - Boolean flag
- `discovery_reasons` - List of "interested_because" term names
- `discovery_areas` - List of "page_elements" term names
- `discovery_notes_private` - Private notes HTML
- `discovery_notes_public` - Public notes HTML
- `drupal_discovered_page_uuid` - Drupal UUID
- `drupal_sync_status` - Enum: not_synced, synced, sync_failed, pending
- `drupal_last_synced` - Timestamp
- `drupal_error_message` - Error details if sync failed

**DiscoveredPage Model:**
- Separate model for manually created discovered pages
- Fields: title, url, project_id, source_type, taxonomies, notes
- Can be created from scraped pages or manually
- Maintains link to source page if applicable

#### Drupal Integration Modules

**TaxonomyCache** (`auto_a11y/drupal/taxonomy.py`):
- Caches taxonomy terms for 24 hours
- Provides fast name → UUID lookup
- Provides fast UUID → name lookup
- Validates term names
- Suggests terms based on partial names

**DiscoveredPageTaxonomies** (`auto_a11y/drupal/taxonomy.py`):
- High-level interface for discovered page taxonomies
- Methods for "interested_because" and "page_elements"
- Batch lookup operations
- Term validation

**DiscoveredPageExporter** (`auto_a11y/drupal/discovered_page_exporter.py`):
- Export discovered pages to Drupal
- Create new or update existing
- Validate data before export
- Batch export with error handling
- Returns success/failure status

**DiscoveredPageImporter** (`auto_a11y/drupal/discovered_page_importer.py`):
- Import discovered pages from Drupal
- Fetch by audit UUID
- Convert Drupal format to Auto A11y models
- Match with existing scraped pages by URL
- Sync bidirectionally

### Workflows

#### Workflow 1: Flag and Export Scraped Pages

1. User runs website scraping in Auto A11y
2. System discovers 100+ pages
3. User reviews pages in Pages list
4. User flags 20-25 interesting pages:
   - Clicks "Flag for Discovery" checkbox
   - Opens discovery dialog for each
   - Selects "interested_because" tags
   - Selects "page_elements" tags
   - Adds notes (private and/or public)
5. User clicks "Export Flagged to Drupal"
6. System:
   - Validates data
   - Looks up audit UUID by project name
   - Looks up taxonomy term UUIDs
   - Creates discovered_page entries in Drupal
   - Stores Drupal UUIDs in Page models
   - Updates sync status
7. User can view synced pages in Drupal

#### Workflow 2: Manual Discovery Page Creation

1. User navigates to "Discovered Pages" section
2. User clicks "Add Discovered Page"
3. User fills form:
   - Page title
   - Page URL (can be app screen, device display, etc.)
   - Source type: manual, app screen, device display
   - "Interested because" tags
   - "Page elements" tags
   - Notes
4. User clicks "Save and Export to Drupal"
5. System creates DiscoveredPage model and exports to Drupal

#### Workflow 3: Pull from Drupal

1. User opens project in Auto A11y
2. User clicks "Import Discovered Pages from Drupal"
3. System:
   - Looks up audit UUID by project name
   - Fetches all discovered pages for audit
   - Matches pages with existing scraped pages by URL
   - For matches: Updates Page models with Drupal data
   - For unmatched: Creates new DiscoveredPage models
4. User sees imported pages in Discovered Pages list
5. Sync status shows "Synced from Drupal"

#### Workflow 4: Bidirectional Sync

1. Changes made in Auto A11y → Push to Drupal
2. Changes made in Drupal → Pull to Auto A11y
3. Conflict resolution: Latest timestamp wins
4. Sync status tracking prevents duplicates

### API Examples

#### Example 1: Create Discovered Page

```python
from auto_a11y.drupal import DrupalJSONAPIClient, DiscoveredPageTaxonomies, DiscoveredPageExporter
from auto_a11y.drupal.config import get_drupal_config

# Initialize
config = get_drupal_config()
client = DrupalJSONAPIClient(config.base_url, config.username, config.password)
taxonomies = DiscoveredPageTaxonomies(client)
exporter = DiscoveredPageExporter(client, taxonomies)

# Export a discovered page
result = exporter.export_discovered_page(
    title="Checkout Form",
    url="https://example.com/checkout",
    audit_uuid="audit-uuid-here",
    interested_because=["Form", "Date Picker or Calendar", "Multipage or Multistep Form"],
    page_elements=["Header", "Main body", "Footer"],
    private_notes="<p>Date picker not keyboard accessible</p>",
    public_notes="<p>Complex form requiring accessibility improvements</p>",
    include_in_report=True
)

if result['success']:
    print(f"Created discovered page: {result['uuid']}")
else:
    print(f"Error: {result['error']}")
```

#### Example 2: Import Discovered Pages

```python
from auto_a11y.drupal import DrupalJSONAPIClient, DiscoveredPageTaxonomies, DiscoveredPageImporter
from auto_a11y.drupal.config import get_drupal_config

# Initialize
config = get_drupal_config()
client = DrupalJSONAPIClient(config.base_url, config.username, config.password)
taxonomies = DiscoveredPageTaxonomies(client)
importer = DiscoveredPageImporter(client, taxonomies)

# Fetch discovered pages for an audit
pages = importer.fetch_discovered_pages_for_audit("audit-uuid-here")

for page in pages:
    print(f"Page: {page['title']}")
    print(f"URL: {page['url']}")
    print(f"Reasons: {page['interested_because']}")
    print(f"Areas: {page['page_elements']}")
    print()
```

#### Example 3: Taxonomy Lookup

```python
from auto_a11y.drupal import DrupalJSONAPIClient, DiscoveredPageTaxonomies
from auto_a11y.drupal.config import get_drupal_config

# Initialize
config = get_drupal_config()
client = DrupalJSONAPIClient(config.base_url, config.username, config.password)
taxonomies = DiscoveredPageTaxonomies(client)

# Get all terms
interested_terms = taxonomies.get_interested_because_terms()
print(f"Total 'interested because' terms: {len(interested_terms)}")

# Lookup UUIDs by names
term_names = ["Form", "Modal dialog", "Video"]
uuids = taxonomies.lookup_interested_because_uuids(term_names)
print(f"UUIDs: {uuids}")

# Lookup names by UUIDs
names = taxonomies.lookup_interested_because_names(uuids)
print(f"Names: {names}")

# Validate terms
valid, invalid = taxonomies.validate_term_names(
    taxonomies.INTERESTED_BECAUSE,
    ["Form", "Invalid Term", "Video"]
)
print(f"Valid: {valid}")
print(f"Invalid: {invalid}")

# Get suggestions
suggestions = taxonomies.get_term_suggestions(
    taxonomies.INTERESTED_BECAUSE,
    "menu",
    limit=5
)
for term in suggestions:
    print(f"  - {term['name']}")
```

### Testing

**Test Scripts:**
- `test_taxonomy_manager.py` - Test taxonomy caching and lookup
- `test_discovered_page_export.py` - Test exporting pages to Drupal
- `test_discovered_page_import.py` - Test importing pages from Drupal

**Run Tests:**
```bash
# Test taxonomy manager
python test_taxonomy_manager.py

# Test export (TODO: create this)
python test_discovered_page_export.py

# Test import (TODO: create this)
python test_discovered_page_import.py
```

### Next Steps for UI Implementation

1. **Pages List Enhancements:**
   - Add "Flag for Discovery" checkbox column
   - Add sync status indicator (✓/⚠/✗/○)
   - Add bulk actions for flagging
   - Add "Export Flagged to Drupal" button

2. **Discovery Dialog:**
   - Multi-select for taxonomy terms (with search)
   - Rich text editors for notes
   - Document link input
   - Preview before export

3. **Discovered Pages Section:**
   - New navigation item
   - List all discovered pages (manual + flagged)
   - CRUD operations
   - Bulk export/import
   - Sync status display

4. **Project-Level Actions:**
   - "Import from Drupal" button
   - "Export All Flagged" button
   - Sync conflict resolution UI

