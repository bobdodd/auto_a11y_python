#!/usr/bin/env python3
"""
Add translation markers to reports dashboard modals
"""

import re

def update_file():
    with open('auto_a11y/web/templates/reports/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # List of replacements (old_text, new_text)
    replacements = [
        # Modal titles and common buttons
        ('<h5 class="modal-title">Generate Report</h5>',
         '<h5 class="modal-title">{{ _(\'Generate Report\') }}</h5>'),

        ('<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>',
         '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{{ _(\'Cancel\') }}</button>'),

        # Form labels - simple ones
        ('<label for="reportName" class="form-label">Report Name</label>',
         '<label for="reportName" class="form-label">{{ _(\'Report Name\') }}</label>'),

        ('<label for="reportType" class="form-label">Report Type</label>',
         '<label for="reportType" class="form-label">{{ _(\'Report Type\') }}</label>'),

        ('<label for="projectSelect" class="form-label">Project</label>',
         '<label for="projectSelect" class="form-label">{{ _(\'Project\') }}</label>'),

        ('<label for="websiteSelect" class="form-label">Website</label>',
         '<label for="websiteSelect" class="form-label">{{ _(\'Website\') }}</label>'),

        ('<label class="form-label">Date Range</label>',
         '<label class="form-label">{{ _(\'Date Range\') }}</label>'),

        ('<label class="form-label">Include in Report</label>',
         '<label class="form-label">{{ _(\'Include in Report\') }}</label>'),

        # Select options
        ('<option value="">All Projects</option>',
         '<option value="">{{ _(\'All Projects\') }}</option>'),

        ('<option value="">Select a project first...</option>',
         '<option value="">{{ _(\'Select a project first...\') }}</option>'),

        ('<option value="">All Websites</option>',
         '<option value="">{{ _(\'All Websites\') }}</option>'),

        # Checkbox labels
        ('Accessibility Violations',
         '{{ _(\'Accessibility Violations\') }}'),

        ('AI Analysis Results',
         '{{ _(\'AI Analysis Results\') }}'),

        ('Executive Summary',
         '{{ _(\'Executive Summary\') }}'),
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    with open('auto_a11y/web/templates/reports/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Added translation markers to reports dashboard modals")

if __name__ == '__main__':
    update_file()
