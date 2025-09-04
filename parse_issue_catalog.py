#!/usr/bin/env python3
"""
Parse ISSUE_CATALOG_TEMPLATE.md and generate Python module with issue data
"""

import re
from pathlib import Path
import json


def parse_issue_catalog(template_path: str) -> dict:
    """Parse the markdown template and extract issue data"""
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match issue blocks
    pattern = r'```\nID: ([^\n]+)\nType: ([^\n]+)\nImpact: ([^\n]+)\nWCAG: ([^\n]+)\nCategory: ([^\n]+)\nDescription: ([^\n]+)\nWhy it matters: ([^\n]+)\nWho it affects: ([^\n]+)\nHow to fix: ([^\n]+)\n```'
    
    issues = {}
    
    for match in re.finditer(pattern, content, re.MULTILINE):
        issue_id = match.group(1).strip()
        
        # Skip template placeholders
        if issue_id in ['[Issue identifier from code]', '[unique_identifier]']:
            continue
        
        # Parse WCAG criteria
        wcag_raw = match.group(4).strip()
        # Extract WCAG numbers (e.g., "1.1.1", "2.4.6")
        wcag_numbers = re.findall(r'\d+\.\d+\.\d+', wcag_raw)
        
        issues[issue_id] = {
            'id': issue_id,
            'type': match.group(2).strip(),
            'impact': match.group(3).strip(),
            'wcag': wcag_numbers,
            'wcag_full': wcag_raw,  # Keep full text with Level indicators
            'category': match.group(5).strip(),
            'description': match.group(6).strip(),
            'why_it_matters': match.group(7).strip(),
            'who_it_affects': match.group(8).strip(), 
            'how_to_fix': match.group(9).strip()
        }
    
    return issues


def generate_python_module(issues: dict, output_path: str):
    """Generate Python module with issue catalog data"""
    
    # Create the module content
    module_content = '''"""
Accessibility Issue Catalog
Generated from ISSUE_CATALOG_TEMPLATE.md
Contains enriched descriptions for all accessibility issues
"""

from typing import Dict, List, Any


class IssueCatalog:
    """Catalog of all accessibility issues with enriched descriptions"""
    
    # Issue data dictionary
    ISSUES: Dict[str, Dict[str, Any]] = {
'''
    
    # Add each issue
    for issue_id, issue_data in issues.items():
        # Escape quotes in strings
        for key in ['description', 'why_it_matters', 'who_it_affects', 'how_to_fix']:
            issue_data[key] = issue_data[key].replace('"', '\\"')
        
        module_content += f'''        "{issue_id}": {{
            "id": "{issue_data['id']}",
            "type": "{issue_data['type']}",
            "impact": "{issue_data['impact']}",
            "wcag": {json.dumps(issue_data['wcag'])},
            "wcag_full": "{issue_data['wcag_full']}",
            "category": "{issue_data['category']}",
            "description": "{issue_data['description']}",
            "why_it_matters": "{issue_data['why_it_matters']}",
            "who_it_affects": "{issue_data['who_it_affects']}",
            "how_to_fix": "{issue_data['how_to_fix']}"
        }},
'''
    
    # Close the dictionary and add methods
    module_content += '''    }
    
    @classmethod
    def get_issue(cls, issue_id: str) -> Dict[str, Any]:
        """
        Get issue details by ID
        
        Args:
            issue_id: The issue identifier
            
        Returns:
            Dictionary with issue details or default if not found
        """
        return cls.ISSUES.get(issue_id, cls._get_default_issue(issue_id))
    
    @classmethod
    def _get_default_issue(cls, issue_id: str) -> Dict[str, Any]:
        """Return default issue data when specific issue not found"""
        return {
            "id": issue_id,
            "type": "Error",
            "impact": "Medium",
            "wcag": [],
            "wcag_full": "WCAG criteria not specified",
            "category": "general",
            "description": f"Accessibility issue: {issue_id}",
            "why_it_matters": "This issue may create barriers for users with disabilities. Specific impact details are not available for this issue type.",
            "who_it_affects": "Users with disabilities who rely on assistive technologies or accessible interfaces",
            "how_to_fix": "Review the specific issue details and apply appropriate accessibility fixes. Consult WCAG guidelines for more information."
        }
    
    @classmethod
    def get_all_issues(cls) -> Dict[str, Dict[str, Any]]:
        """Get all issues in the catalog"""
        return cls.ISSUES
    
    @classmethod
    def get_issues_by_category(cls, category: str) -> List[Dict[str, Any]]:
        """Get all issues in a specific category"""
        return [
            issue for issue in cls.ISSUES.values()
            if issue['category'].lower() == category.lower()
        ]
    
    @classmethod
    def get_issues_by_impact(cls, impact: str) -> List[Dict[str, Any]]:
        """Get all issues with a specific impact level"""
        return [
            issue for issue in cls.ISSUES.values()
            if issue['impact'].lower() == impact.lower()
        ]
    
    @classmethod
    def get_issues_by_wcag(cls, wcag_criterion: str) -> List[Dict[str, Any]]:
        """Get all issues related to a specific WCAG criterion"""
        return [
            issue for issue in cls.ISSUES.values()
            if wcag_criterion in issue['wcag']
        ]
    
    @classmethod
    def enrich_issue(cls, issue_dict: dict) -> dict:
        """
        Enrich a basic issue dictionary with full catalog information
        
        Args:
            issue_dict: Basic issue with at least an 'id' field
            
        Returns:
            Enriched issue dictionary
        """
        issue_id = issue_dict.get('id', issue_dict.get('err', ''))
        catalog_data = cls.get_issue(issue_id)
        
        # Merge catalog data with existing issue data
        enriched = issue_dict.copy()
        
        # Add enriched fields if not present
        if 'description_full' not in enriched:
            enriched['description_full'] = catalog_data['description']
        if 'why_it_matters' not in enriched:
            enriched['why_it_matters'] = catalog_data['why_it_matters']
        if 'who_it_affects' not in enriched:
            enriched['who_it_affects'] = catalog_data['who_it_affects']
        if 'how_to_fix' not in enriched:
            enriched['how_to_fix'] = catalog_data['how_to_fix']
        if 'wcag_full' not in enriched:
            enriched['wcag_full'] = catalog_data['wcag_full']
        if 'impact' not in enriched:
            enriched['impact'] = catalog_data['impact']
            
        return enriched
'''
    
    # Write the module
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(module_content)
    
    print(f"Generated Python module with {len(issues)} issues")


def main():
    template_path = '/Users/bob3/Desktop/auto_a11y_python/ISSUE_CATALOG_TEMPLATE.md'
    output_path = '/Users/bob3/Desktop/auto_a11y_python/auto_a11y/reporting/issue_catalog.py'
    
    # Parse the template
    issues = parse_issue_catalog(template_path)
    print(f"Parsed {len(issues)} issues from template")
    
    # Generate Python module
    generate_python_module(issues, output_path)
    
    # Print summary
    categories = set(issue['category'] for issue in issues.values())
    print(f"\nCategories: {', '.join(sorted(categories))}")
    
    impacts = set(issue['impact'] for issue in issues.values())
    print(f"Impact levels: {', '.join(sorted(impacts))}")
    
    print("\nSample issues:")
    for issue_id in list(issues.keys())[:5]:
        print(f"  - {issue_id}: {issues[issue_id]['description'][:50]}...")


if __name__ == "__main__":
    main()