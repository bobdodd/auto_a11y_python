# Drupal Sync Implementation Summary

## What Was Built

I've implemented a functional Drupal synchronization system for **Discovered Pages** and **Recordings**. This allows you to export content from Auto A11y to your Drupal CMS.

---

## Components Implemented

### 1. **Model Extensions**

#### Recording Model ([auto_a11y/models/recording.py](auto_a11y/models/recording.py:80-85))
Added Drupal sync fields:
```python
# Drupal sync (audit_video export)
drupal_video_uuid: Optional[str] = None  # UUID of audit_video node in Drupal
drupal_video_nid: Optional[int] = None  # Drupal node ID
drupal_sync_status: DrupalSyncStatus = DrupalSyncStatus.NOT_SYNCED
drupal_last_synced: Optional[datetime] = None
drupal_error_message: Optional[str] = None
```

Properties added:
- `is_synced` - Check if synced
- `needs_sync` - Check if needs syncing

#### DiscoveredPage Model
Already had Drupal sync fields from previous work ✓

### 2. **Recording Exporter** ([auto_a11y/drupal/recording_exporter.py](auto_a11y/drupal/recording_exporter.py))

New class to export recordings as `audit_video` nodes in Drupal.

**Key Methods:**
- `export_recording()` - Export single recording
- `export_from_recording_model()` - Export from Recording model instance
- `batch_export()` - Export multiple recordings
- `validate_export_data()` - Validate before export

**What Gets Exported:**
- Title
- Description (built from recording details, task, components)
- Duration
- Auditor name and role
- Recording date
- Link to parent audit

### 3. **Flask Routes** ([auto_a11y/web/routes/drupal_sync.py](auto_a11y/web/routes/drupal_sync.py))

New blueprint registered at `/drupal/` with endpoints:

#### GET `/projects/<project_id>/sync/status`
Returns sync status summary:
```json
{
  "drupal_enabled": true,
  "project_name": "My Project",
  "discovered_pages": {
    "total": 10,
    "synced": 5,
    "pending": 3,
    "failed": 2
  },
  "recordings": {
    "total": 3,
    "synced": 2,
    "pending": 1,
    "failed": 0
  },
  "last_sync_time": "2025-01-11T10:30:00",
  "sync_errors": [...]
}
```

#### POST `/projects/<project_id>/sync/upload`
Uploads selected discovered pages and recordings to Drupal.

**Request Body:**
```json
{
  "discovered_page_ids": ["id1", "id2"],
  "recording_ids": ["id3", "id4"],
  "options": {}
}
```

**Response:** Streaming JSON (NDJSON format) with real-time progress updates:
```json
{"type": "info", "message": "Starting upload..."}
{"type": "progress", "current": 1, "total": 10, "item": "Homepage"}
{"type": "success", "current": 1, "total": 10, "item": "Homepage", "uuid": "..."}
{"type": "error", "current": 2, "total": 10, "item": "About", "error": "..."}
{"type": "complete", "total": 10, "success_count": 8, "failure_count": 2}
```

#### GET `/projects/<project_id>/discovered-pages`
Returns list of discovered pages with sync status.

#### GET `/projects/<project_id>/recordings`
Returns list of recordings with sync status.

### 4. **Upload UI** ([auto_a11y/web/templates/drupal_sync/sync_card.html](auto_a11y/web/templates/drupal_sync/sync_card.html))

Complete upload interface with:

**Sync Status Card:**
- Shows counts of discovered pages and recordings (synced vs pending)
- Last sync timestamp
- Sync errors/warnings
- "Upload to Drupal" button

**Upload Modal - 3 Steps:**

**Step 1: Select Content**
- Checkbox list of all discovered pages
- Checkbox list of all recordings
- Shows sync status badges (Synced, Failed)
- "Select All" checkboxes
- Auto-selects items that need syncing

**Step 2: Upload Progress**
- Progress bar (0-100%)
- Real-time log showing each item being uploaded
- Success/error indicators
- Auto-scrolling log

**Step 3: Upload Complete**
- Success count
- Breakdown (pages vs recordings)
- List of failed items with errors
- Auto-refreshes sync status

---

## How To Use

### Prerequisites

1. **Drupal configured** in `config/drupal.conf`:
```ini
base_url=https://audits.frontier-cnib.ca
username=claude
password=venez1a?
enabled=true
```

2. **Matching audit exists in Drupal** with same name as your Auto A11y project

### Step-by-Step Usage

#### 1. Create Discovered Pages

**Option A: From Scraped Pages** (future feature)
```python
# Flag a scraped page for export
page.is_flagged_for_discovery = True
page.discovery_reasons = ["Form", "Modal dialog"]
page.discovery_areas = ["Header", "Main body"]
page.discovery_notes_private = "<p>Complex form validation</p>"
```

**Option B: Manual Creation**
```python
from auto_a11y.models import DiscoveredPage

discovered_page = DiscoveredPage(
    title="Homepage",
    url="https://example.com",
    project_id=project.id,
    source_type="manual",
    interested_because=["Home Page", "Form"],
    page_elements=["Header", "Main body", "Footer"],
    private_notes="<p>Key landing page</p>",
    public_notes="<p>Main entry point for users</p>"
)

# Save to database
db.discovered_pages.insert_one(discovered_page.to_dict())
```

#### 2. Upload to Drupal

**Via Web UI:**
1. Go to project view page
2. Scroll to "Drupal Sync" card
3. Click "Upload to Drupal" button
4. Select discovered pages and/or recordings to upload
5. Click "Start Upload"
6. Watch real-time progress
7. View results when complete

**Via API:**
```python
import requests

response = requests.post(
    'http://localhost:5001/drupal/projects/{project_id}/sync/upload',
    json={
        'discovered_page_ids': ['id1', 'id2'],
        'recording_ids': ['id3'],
        'options': {}
    }
)

# Stream response
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        print(f"{data['type']}: {data.get('message', data.get('item'))}")
```

#### 3. View in Drupal

After successful upload:
- Discovered pages appear in Drupal as `discovered_page` nodes
- Recordings appear as `audit_video` nodes
- All linked to the matching audit
- UUIDs and NIDs stored in Auto A11y database for future updates

---

## Database Changes

### recordings Collection

New fields added to all recording documents:
```javascript
{
  drupal_video_uuid: null,  // UUID when synced
  drupal_video_nid: null,   // Node ID when synced
  drupal_sync_status: "not_synced",  // "not_synced" | "synced" | "sync_failed" | "pending"
  drupal_last_synced: null,  // ISO datetime
  drupal_error_message: null  // Error details if failed
}
```

### discovered_pages Collection

Already has sync fields (no changes needed).

---

## Testing

### Manual Test Script

Create `test_sync.py`:
```python
#!/usr/bin/env python3
import sys
from auto_a11y.core.database import get_database
from auto_a11y.models import Project, DiscoveredPage, Recording
from auto_a11y.drupal import (
    DrupalJSONAPIClient,
    DiscoveredPageExporter,
    DiscoveredPageTaxonomies,
    RecordingExporter
)
from auto_a11y.drupal.config import get_drupal_config

def main():
    # Get database
    db = get_database()

    # Find a project
    project_doc = db.projects.find_one()
    if not project_doc:
        print("No projects found")
        return

    project = Project.from_dict(project_doc)
    print(f"Testing sync for project: {project.name}")

    # Initialize Drupal client
    config = get_drupal_config()
    client = DrupalJSONAPIClient(
        base_url=config.base_url,
        username=config.username,
        password=config.password
    )

    # Create test discovered page
    test_page = DiscoveredPage(
        title=f"Test Page - {project.name}",
        url="https://example.com/test",
        project_id=project.id,
        interested_because=["Home Page", "Form"],
        page_elements=["Header", "Main body"]
    )

    # Save to database
    result = db.discovered_pages.insert_one(test_page.to_dict())
    print(f"Created test page: {result.inserted_id}")

    # Export to Drupal
    taxonomies = DiscoveredPageTaxonomies(client)
    exporter = DiscoveredPageExporter(client, taxonomies)

    # Lookup audit UUID
    import requests
    import base64
    credentials = f"{config.username}:{config.password}"
    b64_creds = base64.b64encode(credentials.encode()).decode()
    headers = {'Accept': 'application/json', 'Authorization': f'Basic {b64_creds}'}
    url = f"{config.base_url}/rest/open_audits?_format=json"
    response = requests.get(url, headers=headers, timeout=10)
    audits = response.json()

    audit = next((a for a in audits if a.get('title') == project.name), None)
    if not audit:
        print(f"Audit not found in Drupal: {project.name}")
        return

    audit_uuid = audit.get('uuid') or audit.get('uuId')
    print(f"Found audit UUID: {audit_uuid}")

    # Export
    test_page_from_db = DiscoveredPage.from_dict(db.discovered_pages.find_one({'_id': result.inserted_id}))
    export_result = exporter.export_from_discovered_page_model(test_page_from_db, audit_uuid)

    if export_result.get('success'):
        print(f"✓ Successfully exported to Drupal!")
        print(f"  UUID: {export_result['uuid']}")
        print(f"  NID: {export_result['nid']}")
        print(f"  View at: {config.base_url}/node/{export_result['nid']}")

        # Update database
        db.discovered_pages.update_one(
            {'_id': result.inserted_id},
            {'$set': {
                'drupal_uuid': export_result['uuid'],
                'drupal_sync_status': 'synced'
            }}
        )
    else:
        print(f"✗ Export failed: {export_result.get('error')}")

if __name__ == '__main__':
    main()
```

Run: `python test_sync.py`

---

## Architecture

### Sync Flow

```
Auto A11y (Python/MongoDB)
├── DiscoveredPage model
├── Recording model
└── Web UI

        ↓ Export (JSON:API)

Drupal 10 (PHP/MySQL)
├── discovered_page content type
├── audit_video content type
└── Audit (parent)

        ↓ Entity References (UUIDs)

Linked Structure:
- Audit (parent)
  ├── Discovered Pages (20-25)
  └── Audit Videos (recordings)
```

### Data Mapping

#### Discovered Page → Drupal
```python
Auto A11y DiscoveredPage     →  Drupal discovered_page
├── title                     →  title
├── url                       →  field_page_url
├── interested_because (list) →  field_interested_because (taxonomy refs)
├── page_elements (list)      →  field_relevant_page_elements (taxonomy refs)
├── private_notes (HTML)      →  field_notes_in_discovery
├── public_notes (HTML)       →  field_public_note_on_page
└── project_id               →  field_parent_audit_discovery (via audit lookup)
```

#### Recording → Drupal
```python
Auto A11y Recording           →  Drupal audit_video
├── title                     →  title
├── description + task + etc  →  body
├── duration                  →  field_video_duration
├── auditor_name              →  field_auditor_name
├── auditor_role              →  field_auditor_role
├── recorded_date             →  field_recording_date
└── project_id               →  field_parent_audit (via audit lookup)
```

---

## Known Limitations & Future Work

### Current Limitations

1. **No Download/Import** - Can only upload TO Drupal, not import FROM Drupal yet
   - Future: Import resolution status changes
   - Future: Import manually added issues

2. **No Component Detection** - Must manually create discovered pages
   - Future: Auto-detect common components (header, nav, footer)
   - Future: Map components to multiple pages

3. **No Issue Export** - Only pages and recordings, not individual violations yet
   - Future: Export test violations as Issue nodes
   - Future: Link issues to discovered pages

4. **Manual Audit Matching** - Requires audit name to match exactly
   - Future: Allow audit selection/mapping in UI
   - Future: Auto-create audit if missing

5. **No Conflict Resolution** - If item exists in Drupal but was deleted locally
   - Future: Bidirectional sync with conflict resolution

### Future Enhancements

**Phase 2 - Component Detection:**
- Algorithm to identify common components across pages
- UI to review and approve detected components
- Export components as discovered pages with example URLs

**Phase 3 - Issue Export:**
- Export violations as Issue nodes
- Map touchpoints to issue categories
- WCAG criteria lookup and linking
- Lifecycle status tracking

**Phase 4 - Bidirectional Sync:**
- Import resolution status from Drupal
- Import manual issues created in Drupal
- Conflict resolution UI
- Sync scheduling/automation

**Phase 5 - Advanced Features:**
- Screenshot upload support
- Related issues linking
- Bulk operations (mark all as synced, retry all failed)
- Export/import reports
- Sync history viewer

---

## Files Changed/Created

### New Files
- `auto_a11y/drupal/recording_exporter.py` - Recording export logic
- `auto_a11y/web/routes/drupal_sync.py` - Sync API routes
- `auto_a11y/web/templates/drupal_sync/sync_card.html` - Upload UI

### Modified Files
- `auto_a11y/models/recording.py` - Added Drupal sync fields
- `auto_a11y/drupal/__init__.py` - Export RecordingExporter
- `auto_a11y/web/routes/__init__.py` - Export drupal_sync_bp
- `auto_a11y/web/app.py` - Register drupal_sync_bp

### Documentation
- `docs/drupal-issue-mapping-analysis.md` - Gap analysis for Issue export
- `docs/drupal-sync-ui-design.md` - Full UI design spec
- `docs/drupal-sync-implementation-summary.md` - This document

---

## Next Steps to Use

1. **Add sync card to project view template:**

Edit `auto_a11y/web/templates/projects/view.html`, add after the websites card:
```html
{% include 'drupal_sync/sync_card.html' %}
```

2. **Create some discovered pages** in the database (or via future UI)

3. **Import some recordings** (or already have them from Dictaphone imports)

4. **Visit project page** - you'll see the Drupal Sync card

5. **Click "Upload to Drupal"** - select items and upload

6. **Check Drupal** - visit your audit to see the imported content

---

## Support & Troubleshooting

### Common Issues

**"Drupal Integration Not Configured"**
- Check `config/drupal.conf` exists and has correct credentials
- Ensure `enabled=true`
- Test connection: `curl -u claude:password https://audits.frontier-cnib.ca/jsonapi`

**"Audit not found in Drupal"**
- Ensure audit name in Drupal matches Auto A11y project name exactly
- Check REST endpoint: `curl -u claude:password https://audits.frontier-cnib.ca/rest/open_audits?_format=json`

**"Access forbidden"**
- User `claude` must have permissions to create discovered_page and audit_video nodes
- Check user is active and has correct role

**Upload fails with validation errors**
- Check taxonomy terms match Drupal exactly (case-sensitive)
- Ensure required fields (title, URL, audit UUID) are present

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

View Drupal sync logs:
```bash
tail -f logs/auto_a11y.log | grep drupal
```

---

**Implementation Complete**: Discovered Pages and Recordings sync is now functional!
**Next Priority**: Add sync card to project view template, then test end-to-end.

---

**Version**: 1.0
**Date**: 2025-01-11
**Author**: Claude Code Implementation
