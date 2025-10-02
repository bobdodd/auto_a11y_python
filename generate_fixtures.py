#!/usr/bin/env python3
"""
Generate comprehensive test fixtures from ISSUE_CATALOG.md using Claude prompts.
Organizes fixtures by touchpoint and generates multiple test cases per issue.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import json


@dataclass
class IssueDefinition:
    """Issue definition from catalog"""
    id: str
    type: str
    impact: str
    wcag: str
    touchpoint: str
    description: str
    why_it_matters: str
    who_it_affects: str
    how_to_fix: str

    def to_prompt_format(self) -> str:
        """Format for Claude user prompt"""
        return f"""ID: {self.id}
Type: {self.type}
Impact: {self.impact}
WCAG: {self.wcag}
Touchpoint: {self.touchpoint}
Description: {self.description}
Why it matters: {self.why_it_matters}
Who it affects: {self.who_it_affects}
How to fix: {self.how_to_fix}"""


def parse_catalog(catalog_path: Path) -> List[IssueDefinition]:
    """Parse ISSUE_CATALOG.md into issue definitions"""
    content = catalog_path.read_text(encoding='utf-8')

    # Split into individual issue blocks
    blocks = re.split(r'\n---\n', content)

    issues = []
    for block in blocks:
        if not block.strip() or 'ID:' not in block:
            continue

        # Extract fields
        id_match = re.search(r'^ID:\s*(.+)$', block, re.MULTILINE)
        if not id_match:
            continue

        issue = IssueDefinition(
            id=id_match.group(1).strip(),
            type=extract_field(block, 'Type'),
            impact=extract_field(block, 'Impact'),
            wcag=extract_field(block, 'WCAG'),
            touchpoint=extract_field(block, 'Touchpoint'),
            description=extract_field(block, 'Description'),
            why_it_matters=extract_field(block, 'Why it matters'),
            who_it_affects=extract_field(block, 'Who it affects'),
            how_to_fix=extract_field(block, 'How to fix')
        )

        issues.append(issue)

    return issues


def extract_field(block: str, field_name: str) -> str:
    """Extract a field value from issue block"""
    pattern = rf'^{re.escape(field_name)}:\s*(.+?)(?=\n(?:[A-Z][^:]*:|$))'
    match = re.search(pattern, block, re.MULTILINE | re.DOTALL)
    if match:
        return ' '.join(match.group(1).strip().split())
    return 'N/A'


def get_existing_fixtures() -> Dict[str, List[Path]]:
    """Map error codes to their existing fixture files"""
    fixtures_dir = Path('Fixtures')
    existing = {}

    if not fixtures_dir.exists():
        return existing

    for html_file in fixtures_dir.rglob('*.html'):
        # Extract error code from filename (everything before first underscore or end)
        filename = html_file.stem

        # Try to extract error code
        # Format: ErrorCode_001_violations_basic.html
        # or just: ErrorCode.html
        parts = filename.split('_')
        if parts:
            error_code = parts[0]
            if error_code not in existing:
                existing[error_code] = []
            existing[error_code].append(html_file)

    return existing


def generate_fixture_prompts(issues: List[IssueDefinition],
                            existing_fixtures: Dict[str, List[Path]],
                            output_dir: Path):
    """Generate prompt files for Claude to create fixtures"""

    output_dir.mkdir(exist_ok=True)

    # System prompt (same for all)
    system_prompt = """You are a digital accessibility testing fixture generator. Your role is to create comprehensive, passive HTML test fixtures for validating automated accessibility testing tools.

FIXTURE REQUIREMENTS:
1. Each fixture must be a complete, valid HTML5 document
2. Fixtures must be completely passive, except where the JavaScript itself is under test (otherwise no executable JavaScript)
3. Each fixture must contain test metadata in a non-executable JSON format
4. Violations must be marked with data attributes for validation
5. Only ONE h1 element per fixture (accessibility best practice)
6. Test both semantic HTML elements AND their ARIA role equivalents where applicable
7. Include both violation cases AND correct usage cases

METADATA FORMAT:
Include test metadata in the <head> using a script tag with type="application/json":

<script type="application/json" id="test-metadata">
{
    "id": "unique_fixture_id",
    "issueId": "AI_IssueCode",
    "expectedViolationCount": 0,
    "expectedPassCount": 0,
    "description": "Brief description of what this fixture tests",
    "wcag": "X.X.X",
    "impact": "High|Medium|Low"
}
</script>

VIOLATION MARKING:
Mark elements that should trigger violations with data attributes:

<element data-expected-violation="true"
         data-violation-id="AI_IssueCode"
         data-violation-reason="Brief explanation">

Mark elements that should pass validation:

<element data-expected-pass="true"
         data-pass-reason="Brief explanation">

FIXTURE NAMING:
Use this pattern: {IssueId}_{sequence}_{type}_{variant}
Example: AI_ErrSkippedHeading_001_violations_basic

RESPONSE FORMAT:
For each issue, provide:
1. Multiple fixtures covering different scenarios
2. At least one "violations" fixture showing errors
3. At least one "correct" fixture showing proper usage
4. Edge cases and complex scenarios as needed
5. Tests for both semantic HTML and ARIA equivalents

Use markdown headers to organize fixtures clearly:
## Fixture {number}: {Description}"""

    # Write system prompt
    (output_dir / 'SYSTEM_PROMPT.md').write_text(system_prompt)

    # Group issues by touchpoint and existing fixture status
    by_touchpoint = {}
    needs_fixtures = []
    has_old_fixtures = []

    for issue in issues:
        touchpoint = issue.touchpoint
        if touchpoint not in by_touchpoint:
            by_touchpoint[touchpoint] = []
        by_touchpoint[touchpoint].append(issue)

        if issue.id in existing_fixtures:
            has_old_fixtures.append(issue)
        else:
            needs_fixtures.append(issue)

    # Generate summary
    summary = {
        'total_issues': len(issues),
        'needs_new_fixtures': len(needs_fixtures),
        'has_existing_fixtures': len(has_old_fixtures),
        'by_touchpoint': {tp: len(iss) for tp, iss in by_touchpoint.items()},
        'touchpoints': list(by_touchpoint.keys())
    }

    (output_dir / 'generation_summary.json').write_text(
        json.dumps(summary, indent=2)
    )

    # Generate prompt file for issues needing fixtures
    if needs_fixtures:
        prompt_file = output_dir / 'issues_needing_fixtures.txt'
        with open(prompt_file, 'w') as f:
            f.write("# Issues Needing Fixtures\n\n")
            f.write(f"Total: {len(needs_fixtures)} issues\n\n")
            f.write("="*80 + "\n\n")

            for issue in needs_fixtures:
                f.write(f"## {issue.id}\n\n")
                f.write(issue.to_prompt_format())
                f.write("\n\n" + "="*80 + "\n\n")

    # Generate prompt file for issues with old fixtures to replace
    if has_old_fixtures:
        prompt_file = output_dir / 'issues_to_replace_fixtures.txt'
        with open(prompt_file, 'w') as f:
            f.write("# Issues with Old Fixtures to Replace\n\n")
            f.write(f"Total: {len(has_old_fixtures)} issues\n\n")
            f.write("Note: These have simple old-style fixtures that need enhancement\n\n")
            f.write("="*80 + "\n\n")

            for issue in has_old_fixtures:
                f.write(f"## {issue.id}\n\n")
                f.write(f"Existing fixtures:\n")
                for fixture_path in existing_fixtures[issue.id]:
                    f.write(f"  - {fixture_path}\n")
                f.write("\n")
                f.write(issue.to_prompt_format())
                f.write("\n\n" + "="*80 + "\n\n")

    # Generate per-touchpoint prompt files
    touchpoint_dir = output_dir / 'by_touchpoint'
    touchpoint_dir.mkdir(exist_ok=True)

    for touchpoint, touchpoint_issues in sorted(by_touchpoint.items()):
        if touchpoint in ['N/A', 'Unknown']:
            continue

        prompt_file = touchpoint_dir / f'{touchpoint}.txt'
        with open(prompt_file, 'w') as f:
            f.write(f"# {touchpoint.upper()} Touchpoint\n\n")
            f.write(f"Total issues: {len(touchpoint_issues)}\n\n")
            f.write("="*80 + "\n\n")

            for issue in touchpoint_issues:
                f.write(f"## {issue.id}\n\n")
                if issue.id in existing_fixtures:
                    f.write(f"⚠️  Has old fixtures to replace:\n")
                    for fixture_path in existing_fixtures[issue.id]:
                        f.write(f"  - {fixture_path}\n")
                    f.write("\n")
                else:
                    f.write("✨ New fixtures needed\n\n")

                f.write(issue.to_prompt_format())
                f.write("\n\n" + "="*80 + "\n\n")

    print(f"\n✅ Generated fixture generation prompts in {output_dir}/")
    print(f"\n📊 Summary:")
    print(f"   Total issues: {len(issues)}")
    print(f"   Need new fixtures: {len(needs_fixtures)}")
    print(f"   Have old fixtures: {len(has_old_fixtures)}")
    print(f"\n📁 Files created:")
    print(f"   - SYSTEM_PROMPT.md (use this as system prompt)")
    print(f"   - generation_summary.json (statistics)")
    print(f"   - issues_needing_fixtures.txt ({len(needs_fixtures)} issues)")
    print(f"   - issues_to_replace_fixtures.txt ({len(has_old_fixtures)} issues)")
    print(f"   - by_touchpoint/*.txt ({len(by_touchpoint)} touchpoint files)")

    return summary


def main():
    """Main entry point"""
    catalog_path = Path('ISSUE_CATALOG.md')
    output_dir = Path('fixture_generation')

    if not catalog_path.exists():
        print(f"Error: {catalog_path} not found")
        return 1

    print("📖 Parsing ISSUE_CATALOG.md...")
    issues = parse_catalog(catalog_path)
    print(f"   Found {len(issues)} unique issues")

    print("\n🔍 Checking existing fixtures...")
    existing_fixtures = get_existing_fixtures()
    print(f"   Found fixtures for {len(existing_fixtures)} error codes")

    print("\n📝 Generating prompts for Claude...")
    summary = generate_fixture_prompts(issues, existing_fixtures, output_dir)

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("\n1. Use the SYSTEM_PROMPT.md as your Claude system prompt")
    print("\n2. For systematic generation by touchpoint:")
    print("   - Open fixture_generation/by_touchpoint/[touchpoint].txt")
    print("   - Use content as Claude user prompt")
    print("   - Save fixtures to Fixtures/[Touchpoint]/")
    print("\n3. Or generate in batches:")
    print("   - Use issues_needing_fixtures.txt for all new issues")
    print("   - Use issues_to_replace_fixtures.txt to enhance old fixtures")
    print("\n4. Test fixtures with:")
    print("   ./test_fixtures.py --fixture [Touchpoint]/[fixture_name].html")

    return 0


if __name__ == '__main__':
    exit(main())
