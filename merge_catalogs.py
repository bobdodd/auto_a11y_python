#!/usr/bin/env python3
"""
Merge and consolidate issue catalog files into a single authoritative source.
Handles terminology change from 'category' to 'touchpoint'.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class IssueEntry:
    """Represents a single accessibility issue"""

    def __init__(self):
        self.id: Optional[str] = None
        self.type: Optional[str] = None
        self.impact: Optional[str] = None
        self.wcag: Optional[str] = None
        self.touchpoint: Optional[str] = None  # Was 'category', now 'touchpoint'
        self.description: Optional[str] = None
        self.why_it_matters: Optional[str] = None
        self.who_it_affects: Optional[str] = None
        self.how_to_fix: Optional[str] = None
        self.source_file: Optional[str] = None

    def __repr__(self):
        return f"IssueEntry(id={self.id}, type={self.type}, touchpoint={self.touchpoint})"

    def merge_with(self, other: 'IssueEntry', prefer_other: bool = False):
        """Merge another issue entry, preferring non-empty values"""
        if prefer_other:
            # Prefer other's values, but keep ours if other is empty
            self.type = other.type or self.type
            self.impact = other.impact or self.impact
            self.wcag = other.wcag or self.wcag
            self.touchpoint = other.touchpoint or self.touchpoint
            self.description = other.description or self.description
            self.why_it_matters = other.why_it_matters or self.why_it_matters
            self.who_it_affects = other.who_it_affects or self.who_it_affects
            self.how_to_fix = other.how_to_fix or self.how_to_fix
        else:
            # Keep our values, only fill in if we're missing them
            self.type = self.type or other.type
            self.impact = self.impact or other.impact
            self.wcag = self.wcag or other.wcag
            self.touchpoint = self.touchpoint or other.touchpoint
            self.description = self.description or other.description
            self.why_it_matters = self.why_it_matters or other.why_it_matters
            self.who_it_affects = self.who_it_affects or other.who_it_affects
            self.how_to_fix = self.how_to_fix or other.how_to_fix

    def is_complete(self) -> bool:
        """Check if all required fields are present"""
        return all([
            self.id,
            self.type,
            self.touchpoint,
            self.description
        ])

    def to_markdown(self) -> str:
        """Convert to markdown format"""
        lines = [
            f"ID: {self.id}",
            f"Type: {self.type or 'N/A'}",
            f"Impact: {self.impact or 'N/A'}",
            f"WCAG: {self.wcag or 'N/A'}",
            f"Touchpoint: {self.touchpoint or 'N/A'}",
            f"Description: {self.description or 'N/A'}",
            f"Why it matters: {self.why_it_matters or 'N/A'}",
            f"Who it affects: {self.who_it_affects or 'N/A'}",
            f"How to fix: {self.how_to_fix or 'N/A'}",
            ""
        ]
        return "\n".join(lines)


def parse_issue_block(block: str, source_file: str) -> Optional[IssueEntry]:
    """Parse a single issue block from text"""
    issue = IssueEntry()
    issue.source_file = source_file

    # Extract ID
    id_match = re.search(r'^ID:\s*(.+)$', block, re.MULTILINE)
    if not id_match:
        return None
    issue.id = id_match.group(1).strip()

    # Extract other fields
    type_match = re.search(r'^Type:\s*(.+)$', block, re.MULTILINE)
    if type_match:
        issue.type = type_match.group(1).strip()

    impact_match = re.search(r'^Impact:\s*(.+)$', block, re.MULTILINE)
    if impact_match:
        issue.impact = impact_match.group(1).strip()

    wcag_match = re.search(r'^WCAG:\s*(.+)$', block, re.MULTILINE)
    if wcag_match:
        issue.wcag = wcag_match.group(1).strip()

    # Handle both 'Category' and 'Touchpoint' field names
    touchpoint_match = re.search(r'^(?:Category|Touchpoint):\s*(.+)$', block, re.MULTILINE)
    if touchpoint_match:
        issue.touchpoint = touchpoint_match.group(1).strip()

    desc_match = re.search(r'^Description:\s*(.+?)(?=\n(?:Why it matters|Who it affects|How to fix|ID:|Type:|$))',
                           block, re.MULTILINE | re.DOTALL)
    if desc_match:
        issue.description = ' '.join(desc_match.group(1).strip().split())

    why_match = re.search(r'^Why it matters:\s*(.+?)(?=\n(?:Who it affects|How to fix|ID:|Type:|$))',
                          block, re.MULTILINE | re.DOTALL)
    if why_match:
        issue.why_it_matters = ' '.join(why_match.group(1).strip().split())

    who_match = re.search(r'^Who it affects:\s*(.+?)(?=\n(?:How to fix|ID:|Type:|$))',
                          block, re.MULTILINE | re.DOTALL)
    if who_match:
        issue.who_it_affects = ' '.join(who_match.group(1).strip().split())

    how_match = re.search(r'^How to fix:\s*(.+?)(?=\n(?:ID:|Type:|```|$))',
                          block, re.MULTILINE | re.DOTALL)
    if how_match:
        issue.how_to_fix = ' '.join(how_match.group(1).strip().split())

    return issue


def parse_file(file_path: Path) -> List[IssueEntry]:
    """Parse an entire catalog file"""
    print(f"Parsing {file_path.name}...")

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  Error reading file: {e}")
        return []

    # Split on ID: markers to get issue blocks
    blocks = re.split(r'\n(?=ID:\s*\w)', content)

    issues = []
    for block in blocks:
        if not block.strip():
            continue

        issue = parse_issue_block(block, file_path.name)
        if issue and issue.id:
            issues.append(issue)

    print(f"  Found {len(issues)} issues")
    return issues


def merge_issues(all_issues: Dict[str, List[IssueEntry]]) -> Dict[str, IssueEntry]:
    """Merge issues from multiple sources, prioritizing by source quality"""
    merged = {}

    # Priority order: NEW TICKETS > TOUCHPOINT > TEMPLATE
    priority_order = ['NEW TICKETS', 'ISSUE_CATALOG_BY_TOUCHPOINT.md', 'ISSUE_CATALOG_TEMPLATE.md']

    # Group issues by ID
    by_id = defaultdict(list)
    for source, issues in all_issues.items():
        for issue in issues:
            by_id[issue.id].append((source, issue))

    # Merge each ID
    for issue_id, source_issues in by_id.items():
        # Sort by priority
        sorted_issues = sorted(source_issues,
                              key=lambda x: priority_order.index(x[0])
                                            if x[0] in priority_order else 999)

        # Start with highest priority
        merged_issue = IssueEntry()
        merged_issue.id = issue_id

        # Merge in priority order
        for source, issue in sorted_issues:
            if merged_issue.id is None:
                # First issue
                merged_issue = issue
            else:
                # Merge, keeping existing values unless new one is better
                merged_issue.merge_with(issue, prefer_other=False)

        merged[issue_id] = merged_issue

    return merged


def generate_consolidated_catalog(merged_issues: Dict[str, IssueEntry], output_path: Path):
    """Generate the consolidated catalog file"""
    print(f"\nGenerating consolidated catalog: {output_path}")

    # Sort by ID
    sorted_ids = sorted(merged_issues.keys())

    # Group by touchpoint for organization
    by_touchpoint = defaultdict(list)
    for issue_id in sorted_ids:
        issue = merged_issues[issue_id]
        touchpoint = issue.touchpoint or "Unknown"
        by_touchpoint[touchpoint].append(issue)

    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Accessibility Issue Catalog - Consolidated\n\n")
        f.write("This is the authoritative catalog of all accessibility issues detected by auto_a11y_python.\n")
        f.write("Generated by merging NEW TICKETS, ISSUE_CATALOG_TEMPLATE.md, and ISSUE_CATALOG_BY_TOUCHPOINT.md.\n\n")
        f.write("## Format\n\n")
        f.write("Each issue entry contains:\n")
        f.write("- **ID**: Unique identifier used in code\n")
        f.write("- **Type**: Error, Warning, Info, or Discovery\n")
        f.write("- **Impact**: High, Medium, Low, or N/A\n")
        f.write("- **WCAG**: Related WCAG success criteria\n")
        f.write("- **Touchpoint**: Accessibility testing category\n")
        f.write("- **Description**: What the issue is\n")
        f.write("- **Why it matters**: Importance for accessibility\n")
        f.write("- **Who it affects**: User groups impacted\n")
        f.write("- **How to fix**: Remediation guidance\n\n")
        f.write("---\n\n")

        # Write all issues alphabetically
        f.write("## All Issues (Alphabetical)\n\n")
        for issue_id in sorted_ids:
            issue = merged_issues[issue_id]
            f.write(issue.to_markdown())
            f.write("\n---\n\n")

        # Write organized by touchpoint
        f.write("\n## Issues by Touchpoint\n\n")
        for touchpoint in sorted(by_touchpoint.keys()):
            f.write(f"### {touchpoint}\n\n")
            for issue in by_touchpoint[touchpoint]:
                f.write(issue.to_markdown())
                f.write("\n")
            f.write("---\n\n")

    print(f"  Wrote {len(merged_issues)} issues to {output_path}")

    # Print statistics by touchpoint
    print("\n## Issues by Touchpoint:")
    for touchpoint in sorted(by_touchpoint.keys()):
        count = len(by_touchpoint[touchpoint])
        print(f"  {touchpoint}: {count}")


def main():
    """Main entry point"""
    base_path = Path(__file__).parent

    # Define source files
    sources = {
        'NEW TICKETS': base_path / 'NEW TICKETS',
        'ISSUE_CATALOG_TEMPLATE.md': base_path / 'ISSUE_CATALOG_TEMPLATE.md',
        'ISSUE_CATALOG_BY_TOUCHPOINT.md': base_path / 'ISSUE_CATALOG_BY_TOUCHPOINT.md'
    }

    # Parse all files
    all_issues = {}
    for name, path in sources.items():
        if path.exists():
            issues = parse_file(path)
            all_issues[name] = issues
        else:
            print(f"Warning: {path} not found")

    # Count totals
    total_from_all_files = sum(len(issues) for issues in all_issues.values())
    print(f"\n## Total issues parsed from all files: {total_from_all_files}")

    # Merge
    print("\n## Merging issues (prioritizing NEW TICKETS > TOUCHPOINT > TEMPLATE)...")
    merged_issues = merge_issues(all_issues)
    print(f"  Unique IDs after merge: {len(merged_issues)}")

    # Check completeness
    complete = sum(1 for issue in merged_issues.values() if issue.is_complete())
    incomplete = len(merged_issues) - complete
    print(f"  Complete entries: {complete}")
    print(f"  Incomplete entries: {incomplete}")

    if incomplete > 0:
        print(f"\n  Incomplete IDs:")
        for issue_id, issue in merged_issues.items():
            if not issue.is_complete():
                missing = []
                if not issue.id: missing.append("ID")
                if not issue.type: missing.append("Type")
                if not issue.touchpoint: missing.append("Touchpoint")
                if not issue.description: missing.append("Description")
                print(f"    {issue_id}: missing {', '.join(missing)}")

    # Generate output
    output_path = base_path / 'ISSUE_CATALOG.md'
    generate_consolidated_catalog(merged_issues, output_path)

    print(f"\n✅ Successfully created consolidated catalog: {output_path}")
    print(f"   Total unique issues: {len(merged_issues)}")

    return 0


if __name__ == '__main__':
    exit(main())
