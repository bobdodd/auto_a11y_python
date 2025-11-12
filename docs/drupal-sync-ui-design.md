# Drupal Sync UI Design

## Overview

This document outlines the user interface design for bidirectional synchronization between Auto A11y and Drupal, supporting:
- **Discovered Pages** (common components and individual pages)
- **Issues** (violations from automated tests and manual audits)
- **Recordings** (audit videos with timecoded issues)
- **Lifecycle management** (tracking resolution status)

---

## Core Concepts

### 1. Common Components as Discovered Pages

**Key Principle**: Common components (header, nav, footer, forms) are treated as **Discovered Pages in Drupal**, not individual failure points.

**Workflow**:
```
Auto A11y Common Component → Drupal Discovered Page
├── Component Name: "Site Header"
├── Example URL: https://example.com/homepage (where it appears)
├── Component Type: "Header"
└── Issues attached to component (appear across all pages)

When header is fixed → All pages with that header benefit
```

**Example**:
```
Common Component: "Main Navigation Menu"
├── Appears on: 45 pages
├── Discovered Page in Drupal: "Main Navigation Menu"
│   └── Example Page URL: https://example.com/homepage
├── Issues (5):
│   ├── 1. Missing skip link
│   ├── 2. Keyboard trap in submenu
│   ├── 3. Insufficient color contrast
│   ├── 4. Missing ARIA labels
│   └── 5. Incorrect heading hierarchy
└── Fix once → Fixes all 45 pages
```

### 2. Sync Scope

**What We Sync**:
- ✅ Discovered Pages (components + individual pages)
- ✅ Issues (automated violations + manual findings)
- ✅ Recordings (as audit_video nodes)
- ✅ Issue lifecycle status (open → resolved)
- ✅ WCAG criteria references
- ✅ Non-WCAG criteria (kiosk standards, POS, etc.)

**What We DON'T Sync**:
- ❌ Projects (manually created in both systems)
- ❌ Raw test results (stay in Auto A11y)
- ❌ Discovery runs (internal to Auto A11y)
- ❌ Page setup scripts (Auto A11y specific)

### 3. Sync Directions

**Upload (Auto A11y → Drupal)**:
1. Export common components as Discovered Pages
2. Export individual pages as Discovered Pages (if flagged)
3. Export issues attached to components/pages
4. Export recordings as audit_video nodes
5. Link issues to recordings via timecodes

**Download (Drupal → Auto A11y)**:
1. Import resolution status changes (fail → pass)
2. Import new manual issues added in Drupal
3. Import notes/annotations added by auditors
4. Sync discovered page metadata changes

---

## UI Components

### 1. Project View - Drupal Sync Section

**Location**: Project view page, new card below "Websites" section

```html
<!-- Drupal Integration Card -->
<div class="card mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
            <i class="bi bi-cloud-upload"></i> Drupal Sync
        </h5>
        <div>
            <span class="badge bg-info">
                <i class="bi bi-info-circle"></i> Audit: "Project Name" (testA11y)
            </span>
            {% if drupal_audit_uuid %}
            <a href="https://audits.frontier-cnib.ca/node/{{ drupal_audit_nid }}"
               class="btn btn-sm btn-outline-primary" target="_blank">
                <i class="bi bi-box-arrow-up-right"></i> View in Drupal
            </a>
            {% endif %}
        </div>
    </div>
    <div class="card-body">
        {% if drupal_enabled %}
            <!-- Sync Status Summary -->
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="stat-box">
                        <div class="stat-label">Discovered Pages</div>
                        <div class="stat-value">
                            <span class="text-success">{{ sync_stats.pages_synced }}</span> /
                            {{ sync_stats.total_pages }}
                        </div>
                        <small class="text-muted">{{ sync_stats.pages_pending }} pending</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-box">
                        <div class="stat-label">Issues</div>
                        <div class="stat-value">
                            <span class="text-success">{{ sync_stats.issues_synced }}</span> /
                            {{ sync_stats.total_issues }}
                        </div>
                        <small class="text-muted">{{ sync_stats.issues_pending }} pending</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-box">
                        <div class="stat-label">Recordings</div>
                        <div class="stat-value">
                            <span class="text-success">{{ sync_stats.recordings_synced }}</span> /
                            {{ sync_stats.total_recordings }}
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-box">
                        <div class="stat-label">Last Sync</div>
                        <div class="stat-value">
                            {{ last_sync_time.strftime('%Y-%m-%d %H:%M') if last_sync_time else 'Never' }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sync Actions -->
            <div class="btn-toolbar mb-3" role="toolbar">
                <div class="btn-group me-2" role="group">
                    <button type="button" class="btn btn-primary" onclick="openSyncDialog()">
                        <i class="bi bi-arrow-up-circle"></i> Upload to Drupal
                    </button>
                    <button type="button" class="btn btn-outline-primary" onclick="openImportDialog()">
                        <i class="bi bi-arrow-down-circle"></i> Download from Drupal
                    </button>
                </div>
                <div class="btn-group me-2" role="group">
                    <button type="button" class="btn btn-outline-secondary" onclick="viewSyncHistory()">
                        <i class="bi bi-clock-history"></i> Sync History
                    </button>
                    <button type="button" class="btn btn-outline-info" onclick="previewSync()">
                        <i class="bi bi-eye"></i> Preview Changes
                    </button>
                </div>
            </div>

            <!-- Sync Warnings/Errors (if any) -->
            {% if sync_errors %}
            <div class="alert alert-warning" role="alert">
                <strong><i class="bi bi-exclamation-triangle"></i> Sync Issues</strong>
                <ul class="mb-0 mt-2">
                    {% for error in sync_errors %}
                    <li>{{ error }}</li>
                    {% endfor %}
                </ul>
                <button class="btn btn-sm btn-outline-warning mt-2" onclick="viewSyncErrors()">
                    View Details
                </button>
            </div>
            {% endif %}

            <!-- Quick Stats -->
            <div class="row g-2">
                <div class="col-md-6">
                    <div class="alert alert-info mb-0">
                        <strong>Common Components:</strong> {{ common_components_count }}
                        <br><small>These will be exported as Discovered Pages in Drupal</small>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="alert alert-success mb-0">
                        <strong>Resolved Issues:</strong> {{ resolved_issues_count }}
                        <br><small>{{ recently_resolved_count }} resolved in Drupal since last sync</small>
                    </div>
                </div>
            </div>

        {% else %}
            <!-- Drupal Not Configured -->
            <div class="alert alert-warning" role="alert">
                <strong><i class="bi bi-exclamation-triangle"></i> Drupal Integration Not Configured</strong>
                <p class="mb-0">Configure Drupal connection in <code>config/drupal.conf</code> to enable sync.</p>
            </div>
        {% endif %}
    </div>
</div>
```

---

### 2. Upload Dialog (Auto A11y → Drupal)

**Modal Dialog** with multi-step wizard:

#### Step 1: Select What to Upload

```html
<div class="modal fade" id="uploadModal" tabindex="-1">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Upload to Drupal</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <!-- Progress Steps -->
                <div class="steps-indicator mb-4">
                    <div class="step active">1. Select</div>
                    <div class="step">2. Review</div>
                    <div class="step">3. Upload</div>
                    <div class="step">4. Complete</div>
                </div>

                <!-- Step 1: Select Content -->
                <div id="step1" class="step-content">
                    <h6>What would you like to upload?</h6>

                    <!-- Common Components Section -->
                    <div class="card mb-3">
                        <div class="card-header">
                            <input type="checkbox" id="selectAllComponents" checked>
                            <strong>Common Components ({{ common_components|length }})</strong>
                            <small class="text-muted">- Will be exported as Discovered Pages</small>
                        </div>
                        <div class="card-body">
                            <div class="component-list">
                                {% for component in common_components %}
                                <div class="form-check">
                                    <input class="form-check-input component-checkbox"
                                           type="checkbox"
                                           id="component_{{ component.id }}"
                                           data-issues="{{ component.issue_count }}"
                                           checked>
                                    <label class="form-check-label" for="component_{{ component.id }}">
                                        <strong>{{ component.name }}</strong>
                                        <span class="badge bg-secondary">{{ component.type }}</span>
                                        <br>
                                        <small class="text-muted">
                                            Found on {{ component.page_count }} pages
                                            • {{ component.issue_count }} issues
                                            {% if component.drupal_uuid %}
                                            • <span class="text-success">Previously synced</span>
                                            {% else %}
                                            • <span class="text-info">New</span>
                                            {% endif %}
                                        </small>
                                    </label>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>

                    <!-- Individual Pages Section -->
                    <div class="card mb-3">
                        <div class="card-header">
                            <input type="checkbox" id="selectAllPages">
                            <strong>Individual Pages ({{ flagged_pages|length }})</strong>
                            <small class="text-muted">- Flagged for manual inspection</small>
                        </div>
                        <div class="card-body">
                            <div class="page-list">
                                {% for page in flagged_pages %}
                                <div class="form-check">
                                    <input class="form-check-input page-checkbox"
                                           type="checkbox"
                                           id="page_{{ page.id }}">
                                    <label class="form-check-label" for="page_{{ page.id }}">
                                        <strong>{{ page.title or page.url }}</strong>
                                        <br>
                                        <small class="text-muted">
                                            {{ page.url }}
                                            • {{ page.issue_count }} issues
                                            {% if page.discovery_reasons %}
                                            • Reason: {{ page.discovery_reasons|join(', ') }}
                                            {% endif %}
                                        </small>
                                    </label>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>

                    <!-- Recordings Section -->
                    <div class="card mb-3">
                        <div class="card-header">
                            <input type="checkbox" id="selectAllRecordings" checked>
                            <strong>Recordings ({{ recordings|length }})</strong>
                            <small class="text-muted">- Manual audit videos</small>
                        </div>
                        <div class="card-body">
                            <div class="recording-list">
                                {% for recording in recordings %}
                                <div class="form-check">
                                    <input class="form-check-input recording-checkbox"
                                           type="checkbox"
                                           id="recording_{{ recording.id }}"
                                           checked>
                                    <label class="form-check-label" for="recording_{{ recording.id }}">
                                        <strong>{{ recording.title }}</strong>
                                        <span class="badge bg-info">{{ recording.recording_type.value }}</span>
                                        <br>
                                        <small class="text-muted">
                                            {{ recording.auditor_name }} • {{ recording.duration }}
                                            • {{ recording.total_issues }} issues
                                            {% if recording.component_names %}
                                            • Components: {{ recording.component_names|join(', ') }}
                                            {% endif %}
                                        </small>
                                    </label>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>

                    <!-- Upload Options -->
                    <div class="card">
                        <div class="card-header">
                            <strong>Upload Options</strong>
                        </div>
                        <div class="card-body">
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="checkbox" id="includeIssues" checked>
                                <label class="form-check-label" for="includeIssues">
                                    Include Issues (violations and warnings)
                                </label>
                            </div>
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="checkbox" id="updateExisting" checked>
                                <label class="form-check-label" for="updateExisting">
                                    Update existing items (rather than skip)
                                </label>
                            </div>
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="checkbox" id="includeScreenshots">
                                <label class="form-check-label" for="includeScreenshots">
                                    Upload screenshots (slower)
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="goToReviewStep()">
                    Next: Review <i class="bi bi-arrow-right"></i>
                </button>
            </div>
        </div>
    </div>
</div>
```

#### Step 2: Review & Confirm

```html
<div id="step2" class="step-content" style="display:none;">
    <h6>Review Upload</h6>

    <div class="alert alert-info">
        <strong>Summary:</strong>
        <ul class="mb-0">
            <li><span id="reviewComponentCount">0</span> common components</li>
            <li><span id="reviewPageCount">0</span> individual pages</li>
            <li><span id="reviewRecordingCount">0</span> recordings</li>
            <li><span id="reviewIssueCount">0</span> total issues</li>
        </ul>
    </div>

    <!-- Detailed Review -->
    <div class="accordion" id="reviewAccordion">
        <!-- Common Components -->
        <div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button" type="button" data-bs-toggle="collapse"
                        data-bs-target="#reviewComponents">
                    Common Components (<span id="reviewComponentCountInline">0</span>)
                </button>
            </h2>
            <div id="reviewComponents" class="accordion-collapse collapse show">
                <div class="accordion-body">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Component</th>
                                <th>Type</th>
                                <th>Pages</th>
                                <th>Issues</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="reviewComponentsTable">
                            <!-- Populated by JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Issues -->
        <div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                        data-bs-target="#reviewIssues">
                    Issues (<span id="reviewIssueCountInline">0</span>)
                </button>
            </h2>
            <div id="reviewIssues" class="accordion-collapse collapse">
                <div class="accordion-body">
                    <div class="issue-breakdown">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="text-center p-3 border rounded">
                                    <h4 class="text-danger" id="reviewHighCount">0</h4>
                                    <small>High Impact</small>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center p-3 border rounded">
                                    <h4 class="text-warning" id="reviewMediumCount">0</h4>
                                    <small>Medium Impact</small>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center p-3 border rounded">
                                    <h4 class="text-info" id="reviewLowCount">0</h4>
                                    <small>Low Impact</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recordings -->
        <div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                        data-bs-target="#reviewRecordings">
                    Recordings (<span id="reviewRecordingCountInline">0</span>)
                </button>
            </h2>
            <div id="reviewRecordings" class="accordion-collapse collapse">
                <div class="accordion-body">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Auditor</th>
                                <th>Duration</th>
                                <th>Issues</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="reviewRecordingsTable">
                            <!-- Populated by JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Warnings -->
    <div id="reviewWarnings" class="alert alert-warning mt-3" style="display:none;">
        <strong><i class="bi bi-exclamation-triangle"></i> Warnings:</strong>
        <ul id="reviewWarningsList" class="mb-0 mt-2"></ul>
    </div>
</div>

<!-- Step 2 Footer -->
<div class="modal-footer" id="step2Footer" style="display:none;">
    <button type="button" class="btn btn-secondary" onclick="goToSelectStep()">
        <i class="bi bi-arrow-left"></i> Back
    </button>
    <button type="button" class="btn btn-primary" onclick="startUpload()">
        <i class="bi bi-cloud-upload"></i> Start Upload
    </button>
</div>
```

#### Step 3: Upload Progress

```html
<div id="step3" class="step-content" style="display:none;">
    <h6>Uploading to Drupal...</h6>

    <div class="progress mb-3" style="height: 30px;">
        <div id="uploadProgressBar" class="progress-bar progress-bar-striped progress-bar-animated"
             role="progressbar" style="width: 0%">
            <span id="uploadProgressText">0%</span>
        </div>
    </div>

    <div class="upload-status">
        <div id="uploadStatusText" class="mb-3">
            <i class="bi bi-hourglass-split"></i> Preparing upload...
        </div>

        <!-- Real-time Log -->
        <div class="card">
            <div class="card-header">
                <strong>Upload Log</strong>
                <button class="btn btn-sm btn-outline-secondary float-end" onclick="toggleLogDetails()">
                    <i class="bi bi-eye"></i> Show Details
                </button>
            </div>
            <div class="card-body" style="max-height: 300px; overflow-y: auto;">
                <div id="uploadLog" class="font-monospace small">
                    <!-- Log entries appear here -->
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Step 3 Footer -->
<div class="modal-footer" id="step3Footer" style="display:none;">
    <button type="button" class="btn btn-danger" id="cancelUploadBtn" onclick="cancelUpload()">
        <i class="bi bi-x-circle"></i> Cancel Upload
    </button>
</div>
```

#### Step 4: Upload Complete

```html
<div id="step4" class="step-content" style="display:none;">
    <h6>Upload Complete</h6>

    <div class="alert alert-success">
        <h4><i class="bi bi-check-circle"></i> Upload Successful!</h4>
        <p class="mb-0">
            Successfully uploaded <strong><span id="successCount">0</span></strong> items to Drupal.
        </p>
    </div>

    <!-- Summary -->
    <div class="row mb-3">
        <div class="col-md-4">
            <div class="stat-card text-center p-3 border rounded">
                <h4 id="uploadedComponents">0</h4>
                <small>Components</small>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stat-card text-center p-3 border rounded">
                <h4 id="uploadedIssues">0</h4>
                <small>Issues</small>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stat-card text-center p-3 border rounded">
                <h4 id="uploadedRecordings">0</h4>
                <small>Recordings</small>
            </div>
        </div>
    </div>

    <!-- Errors (if any) -->
    <div id="uploadErrors" class="alert alert-danger" style="display:none;">
        <strong><i class="bi bi-exclamation-triangle"></i> Some items failed to upload:</strong>
        <ul id="uploadErrorsList" class="mb-0 mt-2"></ul>
    </div>

    <!-- View in Drupal -->
    <div class="text-center mt-3">
        <a href="https://audits.frontier-cnib.ca/node/{{ drupal_audit_nid }}"
           class="btn btn-primary" target="_blank">
            <i class="bi bi-box-arrow-up-right"></i> View Audit in Drupal
        </a>
    </div>
</div>

<!-- Step 4 Footer -->
<div class="modal-footer" id="step4Footer" style="display:none;">
    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
    <button type="button" class="btn btn-outline-primary" onclick="downloadUploadReport()">
        <i class="bi bi-download"></i> Download Report
    </button>
</div>
```

---

### 3. Download Dialog (Drupal → Auto A11y)

**Modal Dialog** for importing changes from Drupal:

```html
<div class="modal fade" id="importModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Download from Drupal</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>Import changes from Drupal to Auto A11y:</p>

                <!-- What to Import -->
                <div class="card mb-3">
                    <div class="card-header">
                        <strong>Available Updates</strong>
                    </div>
                    <div class="card-body">
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="importResolutions" checked>
                            <label class="form-check-label" for="importResolutions">
                                <strong>Issue Resolutions</strong>
                                <br>
                                <small class="text-muted">
                                    <span id="resolvedIssueCount">0</span> issues marked as resolved in Drupal
                                </small>
                            </label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="importNewIssues" checked>
                            <label class="form-check-label" for="importNewIssues">
                                <strong>New Manual Issues</strong>
                                <br>
                                <small class="text-muted">
                                    <span id="newIssueCount">0</span> new issues added manually in Drupal
                                </small>
                            </label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="importMetadata" checked>
                            <label class="form-check-label" for="importMetadata">
                                <strong>Metadata Changes</strong>
                                <br>
                                <small class="text-muted">
                                    Notes, annotations, and field updates
                                </small>
                            </label>
                        </div>
                    </div>
                </div>

                <!-- Preview Changes -->
                <div class="card">
                    <div class="card-header">
                        <strong>Changes Preview</strong>
                    </div>
                    <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                        <div id="importPreview">
                            <div class="text-center text-muted py-4">
                                <i class="bi bi-hourglass-split"></i> Loading changes...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="startImport()">
                    <i class="bi bi-arrow-down-circle"></i> Import Changes
                </button>
            </div>
        </div>
    </div>
</div>
```

---

### 4. Common Components Management

**New Section**: Common Components detection and management

**Location**: New tab or section in Project view

```html
<!-- Common Components Tab -->
<div class="card mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
            <i class="bi bi-grid-3x3"></i> Common Components
        </h5>
        <button class="btn btn-sm btn-primary" onclick="detectComponents()">
            <i class="bi bi-search"></i> Detect Components
        </button>
    </div>
    <div class="card-body">
        {% if common_components %}
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th>Type</th>
                        <th>Pages</th>
                        <th>Issues</th>
                        <th>Drupal Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for component in common_components %}
                    <tr>
                        <td>
                            <strong>{{ component.name }}</strong>
                            <br>
                            <small class="text-muted">
                                Example: <a href="{{ component.example_url }}" target="_blank">
                                    {{ component.example_url|truncate(50) }}
                                </a>
                            </small>
                        </td>
                        <td>
                            <span class="badge bg-secondary">{{ component.type }}</span>
                        </td>
                        <td>{{ component.page_count }}</td>
                        <td>
                            {% if component.issue_count > 0 %}
                            <span class="badge bg-danger">{{ component.issue_count }}</span>
                            <br>
                            <small class="text-danger">{{ component.high_count }} high</small>
                            {% else %}
                            <span class="text-success">✓ No issues</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if component.drupal_uuid %}
                            <span class="badge bg-success">Synced</span>
                            <br>
                            <small class="text-muted">
                                {{ component.drupal_last_synced.strftime('%Y-%m-%d') }}
                            </small>
                            {% else %}
                            <span class="badge bg-warning">Not synced</span>
                            {% endif %}
                        </td>
                        <td>
                            <div class="btn-group" role="group">
                                <button class="btn btn-sm btn-primary" onclick="viewComponent('{{ component.id }}')">
                                    <i class="bi bi-eye"></i>
                                </button>
                                {% if component.drupal_uuid %}
                                <a href="https://audits.frontier-cnib.ca/node/{{ component.drupal_nid }}"
                                   class="btn btn-sm btn-outline-primary" target="_blank">
                                    <i class="bi bi-box-arrow-up-right"></i>
                                </a>
                                {% else %}
                                <button class="btn btn-sm btn-success" onclick="exportComponent('{{ component.id }}')">
                                    <i class="bi bi-cloud-upload"></i>
                                </button>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="text-center text-muted py-4">
            <i class="bi bi-grid-3x3"></i>
            <p>No common components detected yet.</p>
            <button class="btn btn-primary" onclick="detectComponents()">
                <i class="bi bi-search"></i> Detect Components
            </button>
        </div>
        {% endif %}
    </div>
</div>
```

---

### 5. Issue Lifecycle Visualization

**In test results view**, show issue status with Drupal sync state:

```html
<!-- Issue Card with Lifecycle -->
<div class="issue-card" data-issue-id="{{ issue.id }}">
    <div class="issue-header">
        <div class="issue-title">
            <span class="issue-id">{{ issue.id }}</span>
            <span class="badge bg-{{ {'high': 'danger', 'medium': 'warning', 'low': 'info'}[issue.impact.value] }}">
                {{ issue.impact.value }}
            </span>
        </div>
        <div class="issue-lifecycle">
            <!-- Status Badge -->
            {% if issue.status.value == 'resolved' %}
            <span class="badge bg-success">
                <i class="bi bi-check-circle"></i> Resolved
            </span>
            {% elif issue.status.value == 'pending' %}
            <span class="badge bg-warning">
                <i class="bi bi-hourglass-split"></i> Pending
            </span>
            {% else %}
            <span class="badge bg-danger">
                <i class="bi bi-exclamation-circle"></i> Open
            </span>
            {% endif %}

            <!-- Drupal Sync Status -->
            {% if issue.drupal_issue_uuid %}
            <a href="https://audits.frontier-cnib.ca/node/{{ issue.drupal_nid }}"
               class="btn btn-sm btn-outline-primary" target="_blank" title="View in Drupal">
                <i class="bi bi-cloud-check"></i>
            </a>
            {% elif issue.drupal_sync_status.value == 'pending' %}
            <span class="badge bg-info">
                <i class="bi bi-clock"></i> Pending upload
            </span>
            {% elif issue.drupal_sync_status.value == 'sync_failed' %}
            <span class="badge bg-danger" title="{{ issue.drupal_error_message }}">
                <i class="bi bi-exclamation-triangle"></i> Sync failed
            </span>
            {% endif %}
        </div>
    </div>
    <div class="issue-body">
        <p>{{ issue.description }}</p>
        <!-- ... rest of issue details ... -->
    </div>
</div>
```

---

## API Endpoints

### Backend Routes (Flask)

```python
# auto_a11y/web/routes/drupal_sync.py

@drupal_sync_bp.route('/projects/<project_id>/sync/status')
def sync_status(project_id):
    """Get sync status for a project"""
    # Returns:
    # - Total pages/issues/recordings
    # - Synced counts
    # - Pending counts
    # - Last sync time
    # - Errors

@drupal_sync_bp.route('/projects/<project_id>/sync/preview', methods=['POST'])
def preview_sync(project_id):
    """Preview what would be uploaded without actually uploading"""
    # Request body: selected items
    # Returns:
    # - List of items to upload
    # - List of items to update
    # - Warnings (e.g., missing fields)

@drupal_sync_bp.route('/projects/<project_id>/sync/upload', methods=['POST'])
def upload_to_drupal(project_id):
    """Upload selected content to Drupal"""
    # Request body:
    # - component_ids: [...]
    # - page_ids: [...]
    # - recording_ids: [...]
    # - options: {include_issues, update_existing, include_screenshots}
    #
    # Returns streaming JSON response with progress updates

@drupal_sync_bp.route('/projects/<project_id>/sync/import', methods=['POST'])
def import_from_drupal(project_id):
    """Import changes from Drupal"""
    # Request body:
    # - import_resolutions: bool
    # - import_new_issues: bool
    # - import_metadata: bool
    #
    # Returns:
    # - imported_count
    # - updated_issues
    # - errors

@drupal_sync_bp.route('/projects/<project_id>/sync/history')
def sync_history(project_id):
    """Get sync history/log"""
    # Returns list of sync operations with:
    # - timestamp
    # - direction (upload/download)
    # - items_count
    # - success/failure
    # - errors

@drupal_sync_bp.route('/projects/<project_id>/components')
def list_components(project_id):
    """List common components for a project"""
    # Returns:
    # - component_id
    # - name
    # - type
    # - page_count
    # - issue_count
    # - drupal_uuid
    # - drupal_sync_status

@drupal_sync_bp.route('/projects/<project_id>/components/detect', methods=['POST'])
def detect_components(project_id):
    """Detect common components across pages"""
    # Uses AI/heuristics to identify:
    # - Headers
    # - Footers
    # - Navigation menus
    # - Forms
    # - Sidebars
    # - etc.
```

---

## Implementation Phases

### Phase 1: Basic Upload (Week 1-2)
- ✅ Discovered page export (DONE)
- ⬜ Issue export infrastructure
- ⬜ Simple upload UI (select all → upload)
- ⬜ Progress tracking
- ⬜ Success/error reporting

### Phase 2: Component Detection (Week 3)
- ⬜ Common component detection algorithm
- ⬜ Component management UI
- ⬜ Component → Discovered Page mapping
- ⬜ Component-based issue export

### Phase 3: Selective Upload (Week 4)
- ⬜ Multi-step upload wizard
- ⬜ Selection UI (checkboxes)
- ⬜ Preview/review step
- ⬜ Batch processing with detailed logs

### Phase 4: Download/Import (Week 5)
- ⬜ Import dialog UI
- ⬜ Resolution status sync
- ⬜ New manual issue import
- ⬜ Metadata sync

### Phase 5: Lifecycle Management (Week 6)
- ⬜ Issue status tracking UI
- ⬜ Status change workflow
- ⬜ Resolution notes
- ⬜ Sync history viewer

### Phase 6: Polish (Week 7+)
- ⬜ Real-time sync indicators
- ⬜ Conflict resolution UI
- ⬜ Bulk operations
- ⬜ Export/import reports
- ⬜ Sync scheduling

---

## User Workflows

### Workflow 1: Initial Project Export

```
1. User creates project in Auto A11y
2. User runs tests (automated + manual)
3. User detects common components
4. User clicks "Upload to Drupal"
5. System shows:
   - 3 common components (Header, Nav, Footer)
   - 45 individual pages
   - 2 recordings
   - 156 issues total
6. User selects:
   ✓ All common components
   ✓ 5 key pages for manual inspection
   ✓ Both recordings
   ✓ Include issues
7. System exports:
   - 3 discovered pages for components
   - 5 discovered pages for individual pages
   - 2 audit_video nodes
   - 156 issue nodes linked to components/pages
8. Success! User views in Drupal
```

### Workflow 2: Ongoing Sync

```
1. Auditor in Drupal marks 12 issues as "pass"
2. User in Auto A11y clicks "Download from Drupal"
3. System shows:
   - 12 issues marked resolved
   - 3 new manual issues added by auditor
4. User clicks "Import Changes"
5. System updates:
   - 12 issues → status = RESOLVED
   - Creates 3 new Violation objects from Drupal issues
6. User sees resolved issues with green checkmarks
```

### Workflow 3: Re-test & Update

```
1. Developer fixes header issues
2. User re-runs tests
3. Header component now has 0 issues
4. User clicks "Upload to Drupal"
5. System detects:
   - Header component changed
   - 5 issues resolved (no longer appear)
6. User selects "Update existing"
7. System:
   - Updates header discovered page
   - Marks 5 issues as resolved in Drupal
8. Drupal now shows header with 0 issues
```

---

## Technical Considerations

### 1. Common Component Detection

**Approach**: Use combination of:
- **XPath similarity** (same structure across pages)
- **HTML similarity** (similar content)
- **Semantic markers** (`<header>`, `<nav>`, `<footer>`, `role="navigation"`)
- **AI/ML** (optional: Claude vision to identify visual similarity)

**Algorithm**:
```python
def detect_common_components(project_id):
    """Detect components appearing on multiple pages"""
    pages = get_all_pages(project_id)

    # Extract candidate components
    candidates = []
    for page in pages:
        headers = page.extract_elements('//header | //*[@role="banner"]')
        navs = page.extract_elements('//nav | //*[@role="navigation"]')
        footers = page.extract_elements('//footer | //*[@role="contentinfo"]')
        # ... etc

        candidates.extend([
            {'type': 'header', 'html': h, 'page_id': page.id} for h in headers
        ])
        # ... etc

    # Group by similarity
    components = group_by_similarity(candidates, threshold=0.8)

    # Filter: must appear on at least 3 pages
    components = [c for c in components if len(c['pages']) >= 3]

    return components
```

### 2. Issue Deduplication

**Challenge**: Same component issue appears on multiple pages

**Solution**: Attach issue to component (discovered page), reference multiple example pages

```python
# When exporting issue:
if issue.component_id:
    # Attach to component discovered page
    page_uuid = component.drupal_discovered_page_uuid
else:
    # Attach to individual page
    page_uuid = page.drupal_discovered_page_uuid
```

### 3. Sync Conflict Resolution

**Scenarios**:
1. Issue resolved in Drupal, but re-appears in new test
2. Issue manually edited in Drupal (changed description)
3. Page deleted in Auto A11y but still in Drupal

**Resolution Strategy**:
```python
class SyncConflictResolution(Enum):
    DRUPAL_WINS = "drupal"  # Drupal is source of truth
    AUTO_A11Y_WINS = "auto_a11y"  # Auto A11y is source of truth
    MERGE = "merge"  # Attempt to merge (e.g., append notes)
    ASK_USER = "ask"  # Prompt user to resolve

# Default rules:
# - Resolution status: DRUPAL_WINS (auditor decision)
# - Issue description: AUTO_A11Y_WINS (automated data)
# - Notes/annotations: MERGE (append both)
```

### 4. Performance Optimization

**Batch Operations**:
- Upload 10-50 items at a time (configurable)
- Use connection pooling
- Cache taxonomy/WCAG lookups
- Parallelize independent uploads

**Progress Tracking**:
```python
@app.route('/projects/<project_id>/sync/upload', methods=['POST'])
def upload_to_drupal(project_id):
    """Upload with streaming progress"""

    def generate():
        total = len(selected_items)

        for i, item in enumerate(selected_items):
            try:
                result = export_item(item)
                yield json.dumps({
                    'type': 'progress',
                    'current': i + 1,
                    'total': total,
                    'item': item.name,
                    'status': 'success',
                    'uuid': result['uuid']
                }) + '\n'
            except Exception as e:
                yield json.dumps({
                    'type': 'error',
                    'current': i + 1,
                    'total': total,
                    'item': item.name,
                    'error': str(e)
                }) + '\n'

        yield json.dumps({'type': 'complete'}) + '\n'

    return Response(generate(), mimetype='application/x-ndjson')
```

---

## Next Steps

1. **Review this UI design** with user
2. **Implement Phase 1**: Basic upload functionality
3. **Create component detection** algorithm
4. **Build upload wizard UI**
5. **Add download/import** functionality
6. **Implement lifecycle tracking**
7. **Polish and optimize**

**Estimated Timeline**: 6-8 weeks for full implementation

---

**Document Version**: 1.0
**Date**: 2025-01-11
**Author**: Claude Code Design
