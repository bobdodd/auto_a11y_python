# Latest Test Results UI - Complete Technical Documentation

## Overview

The Latest Test Results section on the page detail view (`/pages/{page_id}`) displays accessibility issues found during testing in a structured, hierarchical accordion format with comprehensive metadata and remediation guidance.

**Primary Template:** [auto_a11y/web/templates/pages/view.html](../auto_a11y/web/templates/pages/view.html)
**Route Handler:** [auto_a11y/web/routes/pages.py](../auto_a11y/web/routes/pages.py)
**Data Enrichment:** IssueCatalog system

---

## Display Structure Hierarchy

### Level 1: Issue Type Grouping (Fixed Order)

Issues are displayed in four sections with fixed ordering:

#### 1. Errors (Violations)
- **Color theme:** Red (`#dc3545`)
- **Icon:** `bi-x-circle`
- **Type:** Critical accessibility violations
- **Accordion ID:** `violationsAccordion`

#### 2. Warnings
- **Color theme:** Yellow (`#ffc107`)
- **Icon:** `bi-exclamation-triangle`
- **Type:** Potential issues requiring review
- **Accordion ID:** `warningsAccordion`

#### 3. Info Notes
- **Color theme:** Blue (`#0dcaf0`)
- **Icon:** `bi-info-circle`
- **Type:** Informational findings
- **Accordion ID:** `infoAccordion`

#### 4. Discovery Items
- **Color theme:** Purple (`#6f42c1`)
- **Icon:** `bi-search`
- **Type:** Detected patterns/elements
- **Accordion ID:** `discoveryAccordion`

### Level 2: Touchpoint Grouping (Alphabetical)

Within each issue type, issues are grouped by **Touchpoint** in **alphabetical order**.

**Visual styling:**
```html
<div class="touchpoint-header mt-3 mb-2 ps-2"
     style="background-color: #f8f9fa; padding: 8px; border-left: 4px solid {type-color};">
    <strong>{{ touchpoint|replace('_', ' ')|title }}</strong>
</div>
```

**Jinja2 grouping:**
```jinja2
{% for touchpoint, touchpoint_violations in latest_result.violations|groupby('touchpoint') %}
```

**Example touchpoints:**
- Accessible Names
- Animation
- Buttons
- Colors
- Dialogs
- Floating Content
- Focus Management
- Forms
- Headings
- Images
- Landmarks
- Language
- Links
- Lists
- Maps
- Navigation
- Page
- Read More Links
- Styles
- Tabindex
- Tables
- Title Attributes
- Timers
- Videos

### Level 3: Error Code Grouping (Outer Accordion)

Within each touchpoint, all instances of the same **error code** are grouped together.

**Jinja2 grouping:**
```jinja2
{% for error_code, description_group in touchpoint_violations|groupby('id') %}
    {% set group_list = description_group|list %}
```

#### Outer Accordion Button Components:

**1. Count Badge** (multiple instances only):
```html
<span class="badge bg-{impact-color}">{{ group_list|length }}</span>
```

**2. Impact Badge:**
```html
<span class="badge bg-{impact-color} me-2 impact-badge">
    {{ violation.impact.value|upper }}
</span>
```
- **Impact mapping:** `high`→`danger`, `medium`→`warning`, `low`→`info`

**3. AI Detection Badge** (if applicable):
```html
<span class="badge bg-info me-2" title="Detected by AI analysis">
    <i class="bi bi-robot"></i> AI
</span>
```

**4. Error Code:**
```html
<code class="me-2">{{ error_code|error_code_only }}</code>
```
- **Filter:** Extracts code from full ID (e.g., `headings_ErrEmptyHeading` → `ErrEmptyHeading`)

**5. Generic Description** (for grouped issues):
```jinja2
{% if group_list|length > 1 %}
    {# For grouped issues, use generic description from catalog #}
    {{ first_violation.metadata.what_generic if first_violation.metadata.what_generic
       else first_violation.metadata.what
       else error_code|error_code_only }}
{% else %}
    {# For single issues, show full specific description #}
    {{ first_violation.metadata.title or first_violation.metadata.what or first_violation.description }}
{% endif %}
```

**Key principle:** Never uses specific values (like element names, xpaths) when multiple instances exist

**6. XPath Suffix** (single issues only):
```html
<span class="text-muted ms-2" style="font-size: 0.9em;">
    • {{ violation.xpath }}
</span>
```

### Level 4: Individual Issue Instances (Inner Accordion)

Each specific occurrence of an error code gets its own nested accordion.

**Inner Accordion Button Format:**
```html
<button class="accordion-button collapsed" type="button"
        data-bs-toggle="collapse"
        data-bs-target="#viol-instance-{{ instance_id }}">
    <strong>Instance {{ loop.index }}:</strong>
    {% if violation.xpath %}
    <code class="ms-2">{{ violation.xpath }}</code>
    {% endif %}
</button>
```

**Special formatting for specific error types:**

- **ErrDuplicateNavNames:** Shows duplicate name
  ```html
  <span class="ms-2">{{ violation.metadata.duplicateName }}</span>
  ```

- **DiscoFontFound:** Shows font name and sizes
  ```html
  <span class="ms-2">Font '{{ violation.metadata.fontName }}' at {{ violation.metadata.sizeCount }} size(s)</span>
  ```

- **Default:** Shows XPath when available

---

## Issue Detail Content Structure

### 1. Main Heading / Alert Box

**Enhanced metadata format:**
```html
<div class="alert alert-{type} mb-3">
    <h6 class="alert-heading">{{ violation.description }}</h6>
</div>
```

**Alert colors:**
- Errors: `alert-danger`
- Warnings: `alert-warning`
- Info: `alert-info`

### 2. About This Issue Section

Four standardized subsections with consistent structure:

#### a) What the issue is:
```html
<div class="mb-3">
    <strong>What the issue is:</strong>
    <p>{{ violation.metadata.what|default(violation.description) }}</p>
</div>
```

**Special handling:**
- `ErrLinkAccessibleNameMismatch`: Uses `violation.description` directly
- Others: Uses `metadata.what` field

#### b) Why this is important:
```html
<div class="mb-3">
    <strong>Why this is important:</strong>
    <p>{{ violation.metadata.why }}</p>
</div>
```

#### c) Who it affects:
```html
<div class="mb-3">
    <strong>Who it affects:</strong>
    <p>{{ violation.metadata.who }}</p>
</div>
```

#### d) How to remediate:
```html
<div class="mb-3">
    <strong>How to remediate:</strong>
    <div class="bg-light p-3 rounded"
         style="white-space: pre-wrap; word-wrap: break-word; font-family: monospace;">
        {{ violation.metadata.full_remediation|default(violation.failure_summary) }}
    </div>
</div>
```

### 3. Relevant Test Criteria Section

Lists applicable WCAG success criteria:

```html
<h6 class="text-{type} mb-2 mt-4">Relevant test criteria:</h6>
<div class="mb-3">
    <strong>WCAG Success Criteria:</strong>
    <ul>
        {% for criterion in violation.metadata.wcag_full %}
        <li>{{ criterion|safe }}</li>
        {% endfor %}
    </ul>
</div>
```

### 4. Two-Column Layout

#### Left Column:
```html
<div class="col-md-6">
    <p><strong>Touchpoint:</strong> {{ violation.touchpoint|default('General') }}</p>
    <p><strong>Impact:</strong>
        <span class="badge bg-{impact-color} impact-badge">
            {{ violation.impact.value|upper }}
        </span>
    </p>
</div>
```

#### Right Column - WCAG Details:

For each WCAG criterion:
```html
<div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-left: 3px solid #0066cc;">
    <p style="margin: 0 0 8px 0; font-weight: bold;">
        WCAG {{ criterion|safe }}
    </p>

    <p style="margin: 0 0 5px 0;">
        <a href="{{ criterion.split()[0] | wcag_understanding_url }}" target="_blank">
            More about {{ criterion | wcag_name }} <i class="bi bi-box-arrow-up-right"></i>
        </a>
    </p>
    <p style="margin: 0;">
        <a href="{{ criterion.split()[0] | wcag_quickref_url }}" target="_blank">
            Ways to meet {{ criterion | wcag_name }} <i class="bi bi-box-arrow-up-right"></i>
        </a>
    </p>
</div>
```

**WCAG Link Generation:**
- Uses custom Jinja filters from `app.py`
- `wcag_understanding_url`: Links to WCAG 2.2 Understanding documents
- `wcag_quickref_url`: Links to WCAG 2.2 How to Meet quick reference
- `wcag_name`: Extracts criterion name from full string

**Special case - WCAG 5.2.4:**
- Treated as "Accessibility Supported" success criterion
- Both links point to Accessibility Supported definition in WCAG 2.2

### 5. Location Section

**XPath Display with Copy Button:**
```html
<p>
    <strong>Location:</strong>
    <code>{{ violation.selector|default(violation.xpath) }}</code>
    <button class="btn btn-sm btn-link p-0 ms-2"
            onclick="copyXpathToClipboard('{{ violation.selector|default(violation.xpath)|e }}', this)"
            title="Copy XPath to clipboard">
        <i class="bi bi-clipboard"></i>
    </button>
</p>
```

**Exceptions:**
- Not displayed for `ErrDuplicateNavNames` (shows all instances instead)

### 6. Code Snippet Section

#### Standard Format:
```html
<h6 class="mt-3">Code Snippet</h6>
<pre class="bg-dark text-light p-3 rounded">
    <code>{{ violation.html|e }}</code>
</pre>
```

#### Special Handling for Complex Error Types:

##### ErrSkippedHeadingLevel
Shows both previous and current headings:
```html
<p class="mb-2"><strong>Previous heading (h{{ violation.metadata.skippedFrom }}):</strong></p>
<pre class="bg-dark text-light p-3 rounded mb-3">
    <code>{{ violation.metadata.previousHeadingHtml|e }}</code>
</pre>

<p class="mb-2"><strong>Current heading (h{{ violation.metadata.skippedTo }}) - skipped h{{ violation.metadata.expectedLevel }}:</strong></p>
<pre class="bg-dark text-light p-3 rounded">
    <code>{{ violation.html|e }}</code>
</pre>
```

##### ErrContentObscuring
Shows obscuring element + all obscured elements:
```html
<p class="mb-2"><strong>Obscuring element (dialog/overlay):</strong></p>
<pre class="bg-dark text-light p-3 rounded mb-3">
    <code>{{ violation.html|e }}</code>
</pre>

<h6 class="mt-4">{{ violation.metadata.obscuredCount }} Interactive element(s) being obscured:</h6>
{% for element in violation.metadata.obscuredElements %}
<div class="mb-3 border-start border-warning border-3 ps-3">
    <p class="mb-1"><strong>&lt;{{ element.element }}&gt;:</strong> "{{ element.text }}"</p>
    <p class="mb-1 small text-muted">
        Location: <code>{{element.xpath}}</code>
        <button class="btn btn-sm btn-link p-0 ms-1"
                onclick="copyXpathToClipboard('{{element.xpath|e}}', this)"
                title="Copy XPath to clipboard">
            <i class="bi bi-clipboard"></i>
        </button>
    </p>
</div>
{% endfor %}
```

##### ErrMultipleH1
Shows all H1 elements found:
```html
<h6 class="mt-3">All {{ violation.metadata.count }} H1 elements found on page:</h6>
{% for h1 in violation.metadata.allH1s %}
<div class="mb-3">
    <p class="mb-1"><strong>H1 #{{ h1.index }}:</strong> {{ h1.text }}</p>
    <p class="mb-1 small text-muted">
        Location: <code>{{h1.xpath}}</code>
        <button onclick="copyXpathToClipboard('{{h1.xpath|e}}', this)">
            <i class="bi bi-clipboard"></i>
        </button>
    </p>
    <pre class="bg-dark text-light p-2 rounded">
        <code>{{ h1.html|e }}</code>
    </pre>
</div>
{% endfor %}
```

##### ErrFakeListImplementation
Shows detected pattern and sample items:
```html
<p class="mb-2"><strong>Detected pattern:</strong> {{ violation.metadata.pattern }}</p>
<p class="mb-2"><strong>Number of items found:</strong> {{ violation.metadata.itemCount }}</p>

<h6 class="mt-4">Sample list items detected:</h6>
{% for item in violation.metadata.sampleItems %}
<div class="mb-2 border-start border-info border-3 ps-3">
    <p class="mb-0"><strong>Item {{ item.index }}:</strong> {{ item.text }}</p>
</div>
{% endfor %}

<p class="mb-2 mt-3"><strong>Container element:</strong></p>
<pre class="bg-dark text-light p-3 rounded">
    <code>{{ violation.html|e }}</code>
</pre>
```

##### ErrDuplicateLandmarkWithoutName
Shows all landmark instances:
```html
<p class="mb-2"><strong>This instance (missing accessible name):</strong></p>
<pre class="bg-dark text-light p-3 rounded mb-3">
    <code>{{ violation.html|e }}</code>
</pre>

<h6 class="mt-4">All {{ violation.metadata.totalCount }} {{ violation.metadata.role }} landmarks on page:</h6>
{% for instance in violation.metadata.allInstances %}
<div class="mb-3">
    <p class="mb-1"><strong>Instance {{ instance.index }}:</strong> {{ instance.name }}</p>
    <p class="mb-1 small text-muted">
        Location: <code>{{instance.xpath}}</code>
        <button onclick="copyXpathToClipboard('{{instance.xpath|e}}', this)">
            <i class="bi bi-clipboard"></i>
        </button>
    </p>
    <pre class="bg-dark text-light p-2 rounded">
        <code>{{ instance.html|e }}</code>
    </pre>
</div>
{% endfor %}
```

##### ErrDuplicateNavNames
Shows all navigation elements with duplicate names:
```html
<h6 class="mt-3">All {{ violation.metadata.totalCount }} navigation elements with the name "{{ violation.metadata.duplicateName }}":</h6>
{% for instance in violation.metadata.allInstances %}
<div class="mb-3">
    <p class="mb-1"><strong>Navigation {{ instance.index }}:</strong></p>
    <p class="mb-1 small text-muted">
        Location: <code>{{instance.xpath}}</code>
        <button onclick="copyXpathToClipboard('{{instance.xpath|e}}', this)">
            <i class="bi bi-clipboard"></i>
        </button>
    </p>
    <pre class="bg-dark text-light p-2 rounded">
        <code>{{ instance.html|e }}</code>
    </pre>
</div>
{% endfor %}
```

##### ErrSmallText
Shows all text elements smaller than 16px:
```html
<h6 class="mt-3">{{ violation.metadata.allInstances|length }} element(s) with text smaller than 16px:</h6>
{% for instance in violation.metadata.allInstances %}
<div class="mb-3">
    <p class="mb-1">
        <strong>Instance {{ instance.index }}:</strong>
        &lt;{{ instance.element }}&gt; element -
        Text size: <span class="badge bg-warning">{{ instance.fontSize }}px</span>
    </p>
    <p class="mb-1 small">Text preview: "{{ instance.text }}"</p>
    <p class="mb-1 small text-muted">
        Location: <code>{{instance.xpath}}</code>
        <button onclick="copyXpathToClipboard('{{instance.xpath|e}}', this)">
            <i class="bi bi-clipboard"></i>
        </button>
    </p>
    <pre class="bg-dark text-light p-2 rounded">
        <code>{{ instance.html|e }}</code>
    </pre>
</div>
{% endfor %}
```

##### ErrAnchorTargetTabindex
Shows link target and all anchor links pointing to it:
```html
<h6 class="mt-3">Link target (needs tabindex="-1"):</h6>
<p class="mb-2">
    <strong>Target element:</strong>
    &lt;{{ violation.element }}&gt; with id="{{ violation.metadata.targetId }}"
</p>
<pre class="bg-dark text-light p-3 rounded mb-3">
    <code>{{ violation.html|e }}</code>
</pre>

<h6 class="mt-4">{{ violation.metadata.anchorLinksCount }} anchor link(s) pointing to this target:</h6>
{% for anchor in violation.metadata.anchorLinks %}
<div class="mb-3">
    <p class="mb-1"><strong>Link {{ anchor.index }}:</strong> "{{ anchor.text }}"</p>
    <p class="mb-1 small text-muted">
        Location: <code>{{anchor.xpath}}</code>
        <button onclick="copyXpathToClipboard('{{anchor.xpath|e}}', this)">
            <i class="bi bi-clipboard"></i>
        </button>
    </p>
    <pre class="bg-dark text-light p-2 rounded">
        <code>{{ anchor.html|e }}</code>
    </pre>
</div>
{% endfor %}
```

##### ErrTabOrderViolation
Shows both elements in visual position order:
```html
<p class="mb-2"><strong>This element (comes later in tab order but appears visually left):</strong></p>
<pre class="bg-dark text-light p-3 rounded mb-3">
    <code>{{ violation.html|e }}</code>
</pre>

<p class="mb-2"><strong>Previous element in tab order (visually to the right):</strong></p>
<pre class="bg-dark text-light p-3 rounded mb-3">
    <code>{{ violation.metadata.previousElement.html|e }}</code>
</pre>

<div class="alert alert-info">
    <p class="mb-1"><strong>Visual positions:</strong></p>
    <p class="mb-1">
        • This element: x={{ violation.metadata.currentElement.position.x }},
                       y={{ violation.metadata.currentElement.position.y }}
                       (tab stop #{{ violation.metadata.currentElement.tabIndex }})
    </p>
    <p class="mb-0">
        • Previous element: x={{ violation.metadata.previousElement.position.x }},
                           y={{ violation.metadata.previousElement.position.y }}
                           (tab stop #{{ violation.metadata.previousElement.tabIndex }})
    </p>
</div>
```

### 7. Page Thumbnail Section

```html
<h6 class="mt-4">Page Thumbnail (at time of test)</h6>
<a href="#" onclick="showScreenshot('{{ url_for('serve_screenshot', filename=screenshot_filename) }}', '{{ page.url }}'); return false;">
    <img src="{{ url_for('serve_screenshot', filename=screenshot_filename) }}"
         alt="Thumbnail of {{ page.url }}"
         class="img-thumbnail"
         style="max-width: 300px; height: auto; cursor: pointer;"
         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
    <span style="display: none; font-size: 0.9em; color: #999;">Thumbnail not available</span>
</a>
<p class="text-muted small mt-1">Click to view full size</p>
```

### 8. AI Detection Note (if applicable)

```html
{% if violation.metadata.ai_detected %}
<div class="alert alert-info mt-3">
    <i class="bi bi-robot"></i> <strong>AI Detection Note:</strong>
    <p class="mb-0">This issue was detected through visual analysis.</p>
    {% if violation.metadata.ai_confidence %}
    <p><strong>Confidence:</strong> {{ (violation.metadata.ai_confidence * 100)|round }}%</p>
    {% endif %}
</div>
{% endif %}
```

---

## Data Flow & Processing

### 1. Route Handler

**File:** `auto_a11y/web/routes/pages.py:188-211`

```python
@pages_bp.route('/<page_id>')
def view_page(page_id):
    """View page details and test results"""

    # Fetch core data
    page = current_app.db.get_page(page_id)
    website = current_app.db.get_website(page.website_id)
    project = current_app.db.get_project(website.project_id)

    # Get latest test result from database
    test_result = current_app.db.get_latest_test_result(page_id)

    # Enrich with catalog metadata
    test_result = enrich_test_result_with_catalog(test_result)

    # Get test history
    test_history = current_app.db.get_test_results(page_id=page_id, limit=10)

    # Render template
    return render_template('pages/view.html',
                         page=page,
                         website=website,
                         project=project,
                         latest_result=test_result,
                         test_history=test_history)
```

### 2. Result Processing & Metadata Enrichment

**Primary enrichment happens during test result processing.**

**File:** `auto_a11y/testing/result_processor.py:440-488`

```python
def _process_violation(self, violation_data, source_test, violation_type):
    """Process individual violation into Violation model"""

    error_code = violation_data.get('err', 'UnknownError')
    violation_id = f"{source_test}_{error_code}"

    # Get enhanced description with actual metadata (placeholders replaced)
    enhanced_desc = get_detailed_issue_description(violation_id, violation_data)

    if enhanced_desc:
        # CRITICAL: Get generic description WITHOUT placeholder replacement
        # This is used for grouped accordion headers
        generic_desc = get_detailed_issue_description(violation_id, {})

        # Store THREE types of descriptions:
        metadata = {
            # Instance-specific (with placeholder values replaced)
            'title': enhanced_desc.get('title', ''),
            'what': enhanced_desc.get('what', ''),

            # Generic catalog description (NO placeholder replacement)
            # Used for grouped accordion headers
            'what_generic': generic_desc.get('what', ''),

            # Other metadata
            'why': enhanced_desc.get('why', ''),
            'who': enhanced_desc.get('who', ''),
            'wcag_full': wcag_full,
            'full_remediation': enhanced_desc.get('remediation', ''),
            **violation_data  # Include all original metadata from JS tests
        }
```

**Key Implementation Detail:**

The function calls `get_detailed_issue_description()` **twice**:

1. **With metadata** (`violation_data`) - Replaces placeholders like `{totalCount}`, `{role}`, `{element}` with actual values
   - Used for `title` and `what` fields
   - Example: "Found 2 &lt;header&gt; elements with role="banner"..."

2. **Without metadata** (empty dict `{}`) - Returns catalog description, preferring `what_generic` field if it exists
   - Used for `what_generic` field
   - **Preferred:** Uses catalog's `what_generic` field (properly written generic text)
     - Example: "Multiple landmarks of the same type exist, but this instance lacks a unique accessible name..."
   - **Fallback:** Uses catalog's `what` field without placeholder replacement (if `what_generic` not defined)
     - Example: "Found {totalCount} {role} landmarks, but this one lacks..."

**Why the two-tier approach:**
- Some catalog entries have a dedicated `what_generic` field with properly written generic text (no placeholders)
- Older catalog entries only have `what` with placeholders, which get displayed literally when not replaced
- The code prefers `what_generic` but falls back to `what` for backward compatibility

This ensures:
- **Grouped accordions** show properly generic descriptions (no specific values, no unreplaced placeholders)
- **Individual instances** show specific descriptions (with actual values)
- **Maintains UI principle:** Grouped headers never contain instance-specific information or unreplaced placeholders

### 3. Catalog Enrichment (Fallback)

**File:** `auto_a11y/web/routes/pages.py:15-67`

```python
def enrich_test_result_with_catalog(test_result):
    """Enrich test result issues with catalog metadata"""

    if not test_result:
        return test_result

    # Enrich violations (and warnings, info, discovery - same logic)
    for violation in test_result.violations:
        if not hasattr(violation, 'metadata') or not violation.metadata:
            violation.metadata = {}

        # Extract error code from violation ID
        # IDs can be in formats like:
        # - testname_ErrorCode (e.g., headings_ErrEmptyHeading)
        # - testname_subtest_ErrorCode (e.g., more_links_ErrInvalidGenericLinkName)
        issue_id = violation.id if hasattr(violation, 'id') else ''

        # Find the actual error code (starts with Err, Warn, Info, Disco, or AI)
        error_code = issue_id
        if '_' in issue_id:
            parts = issue_id.split('_')
            for i, part in enumerate(parts):
                if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                    # Found the error code, join from here to end
                    error_code = '_'.join(parts[i:])
                    break

        # Skip if already has enhanced metadata with 'what' field
        # This preserves the metadata replacement done in result_processor.py
        if violation.metadata.get('what'):
            continue

        # Get catalog info for this issue as fallback
        catalog_info = IssueCatalog.get_issue(error_code)

        # Only update if we got meaningful enriched data
        if catalog_info and catalog_info.get('description') != f"Issue {error_code} needs documentation":
            # Add enriched metadata
            violation.metadata['title'] = catalog_info.get('type', '')
            violation.metadata['what'] = catalog_info['description']
            violation.metadata['what_generic'] = catalog_info['description']  # Always store generic for grouped headers
            violation.metadata['why'] = catalog_info['why_it_matters']
            violation.metadata['who'] = catalog_info['who_it_affects']
            violation.metadata['how'] = catalog_info['how_to_fix']

            # Handle WCAG criteria properly
            wcag = catalog_info.get('wcag', [])
            if isinstance(wcag, list) and wcag:
                violation.metadata['wcag_full'] = wcag
            elif isinstance(wcag, str) and wcag != 'N/A':
                violation.metadata['wcag_full'] = [wcag]

    return test_result
```

**Key points:**
- Extracts error code from compound IDs
- Only enriches if metadata not already set by result_processor
- Stores both `what` (specific) and `what_generic` (generic) descriptions
- Handles WCAG criteria as list or string
- **Note:** This is fallback enrichment. Primary enrichment happens in result_processor.py

### 4. Template Rendering

**File:** `auto_a11y/web/templates/pages/view.html`

**Overall structure:**
```jinja2
{# Level 1: Issue types (fixed order) #}
{% if latest_result.violations %}
    <h6 class="text-danger mb-3">Errors ({{ latest_result.violations|length }})</h6>
    <div class="accordion mb-4" id="violationsAccordion">

        {# Level 2: Touchpoints (alphabetical) #}
        {% for touchpoint, touchpoint_violations in latest_result.violations|groupby('touchpoint') %}
            <div class="touchpoint-header">{{ touchpoint|title }}</div>

            {# Level 3: Error codes #}
            {% for error_code, description_group in touchpoint_violations|groupby('id') %}
                {% set group_list = description_group|list %}

                {% if group_list|length > 1 %}
                    {# Multiple instances - show outer accordion #}
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button data-bs-target="#viol-group-{{ counter }}">
                                {# Generic description for grouped issues #}
                                {{ first_violation.metadata.what_generic }}
                            </button>
                        </h2>
                        <div id="viol-group-{{ counter }}" class="accordion-collapse collapse">
                            <div class="accordion-body">

                                {# Level 4: Individual instances in inner accordion #}
                                <div class="accordion" id="viol-group-instances-{{ counter }}">
                                    {% for violation in group_list %}
                                        <div class="accordion-item">
                                            <button data-bs-target="#viol-instance-{{ counter }}-{{ loop.index }}">
                                                Instance {{ loop.index }}: {{ violation.xpath }}
                                            </button>
                                            <div id="viol-instance-{{ counter }}-{{ loop.index }}">
                                                {# Full issue details #}
                                            </div>
                                        </div>
                                    {% endfor %}
                                </div>

                            </div>
                        </div>
                    </div>
                {% else %}
                    {# Single instance - show directly #}
                    <div class="accordion-item">
                        <button data-bs-target="#viol-single-{{ counter }}">
                            {# Specific description for single issues #}
                            {{ violation.metadata.title }}
                        </button>
                        <div id="viol-single-{{ counter }}">
                            {# Full issue details #}
                        </div>
                    </div>
                {% endif %}

            {% endfor %}
        {% endfor %}
    </div>
{% endif %}

{# Repeat same pattern for warnings, info, discovery #}
```

---

## Jinja2 Custom Filters

**File:** `auto_a11y/web/app.py:69-103`

### error_code_only

Extracts the error code from a compound violation ID.

```python
@app.template_filter('error_code_only')
def error_code_only(violation_id):
    """
    Extract just the error code from full violation ID

    Examples:
        'event_handlers_WarnTabindexDefaultFocus' -> 'WarnTabindexDefaultFocus'
        'headings_ErrEmptyHeading' -> 'ErrEmptyHeading'
        'more_links_ErrInvalidGenericLinkName' -> 'ErrInvalidGenericLinkName'
    """
    if not violation_id or '_' not in violation_id:
        return violation_id

    # Split by underscore and find the part that starts with Err/Warn/Info/Disco/AI
    parts = violation_id.split('_')
    for i, part in enumerate(parts):
        if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
            return '_'.join(parts[i:])

    # If no match, return original
    return violation_id
```

### wcag_understanding_url

Generates WCAG 2.2 Understanding document URL.

```python
@app.template_filter('wcag_understanding_url')
def wcag_understanding_url(criterion):
    """
    Generate WCAG 2.2 Understanding URL for a criterion

    Example:
        '2.4.8' -> 'https://www.w3.org/WAI/WCAG22/Understanding/location'
    """
    from auto_a11y.reporting.wcag_mapper import format_wcag_link
    return format_wcag_link(criterion, 'understanding')
```

### wcag_quickref_url

Generates WCAG 2.2 Quick Reference URL.

```python
@app.template_filter('wcag_quickref_url')
def wcag_quickref_url(criterion):
    """
    Generate WCAG 2.2 Quick Reference URL for a criterion

    Example:
        '2.4.8' -> 'https://www.w3.org/WAI/WCAG22/quickref/#location'
    """
    from auto_a11y.reporting.wcag_mapper import format_wcag_link
    return format_wcag_link(criterion, 'quickref')
```

### wcag_name

Extracts the criterion name from a full WCAG string.

```python
@app.template_filter('wcag_name')
def wcag_name(criterion):
    """
    Extract just the name from a WCAG criterion string

    Examples:
        '2.4.8 Location (Level AAA)' -> 'Location'
        '1.4.3 Contrast (Minimum) (Level AA)' -> 'Contrast (Minimum)'
    """
    if not criterion:
        return criterion

    # Handle format "2.4.8 Location (Level AAA)"
    if ' (' in criterion:
        # Extract text between number and (Level
        name_part = criterion.split(' (')[0]  # "2.4.8 Location"
        return name_part.split(' ', 1)[1] if ' ' in name_part else name_part

    return criterion
```

---

## Accordion ID Patterns

### Counter Management

Each issue type maintains its own counter using Jinja2 namespaces:

```jinja2
{# Initialize counter for violations #}
{% set viol_counter = namespace(value=0) %}

{# Increment counter for each error code group #}
{% set viol_counter.value = viol_counter.value + 1 %}
```

### ID Naming Convention

**Outer accordions (error code groups):**
- Violations: `viol-group-{counter}`
- Warnings: `warn-group-{counter}`
- Info: `info-group-{counter}`
- Discovery: `disc-group-{counter}`

**Inner accordions (individual instances):**
- Violations: `viol-instance-{counter}-{loop.index}`
- Warnings: `warn-instance-{counter}-{loop.index}`
- Info: `info-instance-{counter}-{loop.index}`
- Discovery: `disc-instance-{counter}-{loop.index}`

**Single items (no grouping):**
- Violations: `viol-single-{counter}`
- Warnings: `warn-single-{counter}`
- Info: `info-single-{counter}`
- Discovery: `disc-single-{counter}`

### Parent Relationships

```html
<!-- Inner accordion has parent relationship -->
<div id="viol-instance-{{ instance_id }}"
     class="accordion-collapse collapse"
     data-bs-parent="#viol-group-instances-{{ counter }}">
```

This ensures proper Bootstrap accordion behavior where opening one instance closes others.

---

## CSS Customizations

**File:** `auto_a11y/web/templates/pages/view.html` (inline styles)

```css
/* Move accordion indicators to the left for accessibility */
.accordion-button {
    padding-left: 2.5rem;
    padding-right: 1.25rem;
}

.accordion-button::after {
    position: absolute;
    left: 1rem;
    right: auto;
    transition: transform 0.2s ease-in-out;
}

.accordion-button:not(.collapsed)::after {
    transform: rotate(0deg);
}

/* Ensure proper spacing for content */
.accordion-button > * {
    margin-left: 0.5rem;
}

.accordion-button > *:first-child {
    margin-left: 0;
}
```

**Rationale:**
- Positions expand/collapse indicator on the left side
- Improves accessibility by making indicator visible first
- Follows common accessibility UI patterns

---

## JavaScript Functions

### copyXpathToClipboard

```javascript
function copyXpathToClipboard(xpath, button) {
    navigator.clipboard.writeText(xpath).then(function() {
        // Change icon temporarily to show success
        const icon = button.querySelector('i');
        const originalClass = icon.className;
        icon.className = 'bi bi-check';

        setTimeout(function() {
            icon.className = originalClass;
        }, 2000);
    });
}
```

### showScreenshot

```javascript
function showScreenshot(imageUrl, pageUrl) {
    // Opens modal or new window to display full-size screenshot
    // Implementation depends on modal library used
}
```

---

## Bootstrap Accordion Configuration

### Collapse Behavior

**Default state:** All accordions start collapsed
```html
<button class="accordion-button collapsed" ...>
<div class="accordion-collapse collapse" ...>
```

**Toggle mechanism:**
```html
<button ...
    data-bs-toggle="collapse"
    data-bs-target="#accordion-id">
```

**Parent relationship:**
```html
<div ...
    data-bs-parent="#parentAccordionId">
```

This ensures only one child accordion can be open at a time within a parent.

---

## Issue Catalog Integration

### IssueCatalog Structure

**File:** `auto_a11y/reporting/issue_catalog.py`

The Issue Catalog provides standardized metadata for all error codes:

```python
{
    'ErrEmptyHeading': {
        'type': 'Error',
        'description': 'Heading element contains no text content',
        'why_it_matters': 'Screen readers announce empty headings...',
        'who_it_affects': 'Users who rely on screen readers...',
        'how_to_fix': 'Add descriptive text to the heading or remove it...',
        'wcag': ['1.3.1 Info and Relationships (Level A)', '2.4.6 Headings and Labels (Level AA)']
    }
}
```

### Metadata Fields

| Field | Purpose | Used In |
|-------|---------|---------|
| `type` | Issue severity (Error, Warning, Info, Discovery) | `metadata.title` |
| `description` | Generic description of the issue | `metadata.what` and `metadata.what_generic` |
| `why_it_matters` | Explanation of impact | `metadata.why` |
| `who_it_affects` | User groups affected | `metadata.who` |
| `how_to_fix` | Remediation guidance | `metadata.how` / `metadata.full_remediation` |
| `wcag` | Related WCAG success criteria | `metadata.wcag_full` |

---

## Special Cases & Edge Cases

### No Metadata Available

If no catalog entry exists or metadata is incomplete:

```jinja2
{% if violation.metadata and violation.metadata.title %}
    {{ violation.metadata.title }}
{% elif violation.metadata and violation.metadata.what %}
    {{ violation.metadata.what }}
{% else %}
    {{ violation.description }}
{% endif %}
```

Falls back to `violation.description` from test result.

### Font Discovery Items

Special formatting for discovered fonts:

```html
Font '{{ violation.metadata.fontName }}' at {{ violation.metadata.sizeCount }} size{{ 's' if violation.metadata.sizeCount != 1 else '' }}: {{ violation.metadata.fontSizes|join(', ') }}
```

Example: `Font 'Arial' at 3 sizes: 12px, 14px, 16px`

### XPath Not Available

Some issues don't have element-level XPaths:
- Page-level issues (e.g., `ErrNoH1`)
- Pattern-based issues (e.g., `ErrFakeListImplementation`)

In these cases, location section shows alternate information or is omitted.

---

## Performance Considerations

### Grouping Operations

Jinja2's `groupby` filter performs sorting and grouping:

```jinja2
{% for touchpoint, touchpoint_violations in latest_result.violations|groupby('touchpoint') %}
```

- **Time complexity:** O(n log n) for sorting
- **Optimization:** Pre-sort data in Python route handler if grouping becomes slow

### Accordion Rendering

- **DOM size:** Nested accordions create substantial DOM
- **Mitigation:** All accordions start collapsed, reducing initial render
- **Future optimization:** Lazy load inner accordion content on expand

### Screenshot Loading

```html
<img ... onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
<span style="display: none;">Thumbnail not available</span>
```

Gracefully handles missing screenshots without breaking layout.

---

## Testing Considerations

### Manual Testing Checklist

- [ ] Single violations display correctly
- [ ] Multiple violations group properly
- [ ] Generic descriptions used for groups
- [ ] Specific descriptions for instances
- [ ] XPath copy buttons work
- [ ] WCAG links navigate correctly
- [ ] Screenshots load or fail gracefully
- [ ] Accordions expand/collapse properly
- [ ] Special error types render correctly
- [ ] All four issue types (Errors, Warnings, Info, Discovery) display
- [ ] Touchpoints sort alphabetically
- [ ] Issue type sections maintain fixed order

### Automated Testing

Potential test scenarios:
```python
def test_view_page_with_violations():
    """Test page view renders violations correctly"""
    # Create test page with violations
    # Check template renders without errors
    # Verify grouping logic

def test_enrich_test_result():
    """Test catalog enrichment"""
    # Create mock test result
    # Call enrich function
    # Verify metadata populated correctly
```

---

## Future Enhancements

### Potential Improvements

1. **Filtering/Sorting:**
   - Filter by impact level
   - Filter by touchpoint
   - Sort by different criteria

2. **Bulk Actions:**
   - Mark issues as false positives
   - Add notes to specific violations
   - Create remediation tasks

3. **Comparison View:**
   - Compare current results with previous test
   - Show newly introduced issues
   - Show fixed issues

4. **Export Options:**
   - Export filtered results
   - Generate remediation tickets
   - Create developer-friendly reports

5. **Visual Enhancements:**
   - Highlight affected elements in screenshot
   - Show element position in page thumbnail
   - Add visual indicators for issue density

6. **Progressive Loading:**
   - Lazy load accordion content
   - Infinite scroll for many issues
   - Virtual scrolling for performance

---

## Summary

The Latest Test Results UI provides a comprehensive, hierarchical display system with:

1. **Four-level hierarchy** for logical organization
2. **Smart grouping** that prevents duplication
3. **Generic vs. specific descriptions** based on context
4. **Rich metadata** from centralized Issue Catalog
5. **Direct WCAG mapping** with documentation links
6. **Visual aids** (code snippets, screenshots, XPaths)
7. **Special handling** for complex error types
8. **Accessibility-first design** (left-side indicators, semantic HTML)
9. **Progressive disclosure** via nested accordions
10. **Actionable guidance** for developers

This design balances comprehensiveness with usability, providing developers with all information needed to understand and remediate accessibility issues efficiently.
