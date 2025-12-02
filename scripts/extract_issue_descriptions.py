#!/usr/bin/env python3
"""
Extract translatable strings from issue_descriptions_enhanced.py

This script:
1. Parses the descriptions dictionary from issue_descriptions_enhanced.py
2. Extracts all translatable string fields (title, what, why, who, remediation, what_generic)
3. Converts placeholders from {var} to %(var)s format
4. Generates msgctxt/msgid pairs
5. Outputs structured JSON for translation

Usage:
    python scripts/extract_issue_descriptions.py > extracted_strings.json
"""

import ast
import json
import re
import sys
from pathlib import Path


def convert_placeholders(text):
    """Convert {variable} format to %(variable)s format for gettext"""
    if not text or not isinstance(text, str):
        return text

    # Find all {variable} patterns
    pattern = r'\{([a-zA-Z_][a-zA-Z0-9_\.]*)\}'

    def replacer(match):
        var_name = match.group(1)
        # Convert dot notation to underscore (e.g., {element.tag} -> %(element_tag)s)
        var_name = var_name.replace('.', '_')
        return f'%({var_name})s'

    return re.sub(pattern, replacer, text)


def extract_strings_from_ast(file_path):
    """
    Parse the Python file and extract the descriptions dictionary using AST
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    # Parse the Python file
    tree = ast.parse(source)

    # Find the get_detailed_issue_description function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'get_detailed_issue_description':
            # Find the descriptions dictionary assignment
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id == 'descriptions':
                            # This is the descriptions dictionary
                            return extract_dict_from_ast(stmt.value)

    return {}


def extract_dict_from_ast(node):
    """
    Recursively extract dictionary values from AST node
    """
    if isinstance(node, ast.Dict):
        result = {}
        for key_node, value_node in zip(node.keys, node.values):
            if isinstance(key_node, ast.Constant):
                key = key_node.value
            elif isinstance(key_node, ast.Str):  # Python 3.7 compatibility
                key = key_node.s
            else:
                continue

            if isinstance(value_node, ast.Dict):
                result[key] = extract_dict_from_ast(value_node)
            elif isinstance(value_node, ast.Constant):
                result[key] = value_node.value
            elif isinstance(value_node, ast.Str):  # Python 3.7 compatibility
                result[key] = value_node.s
            elif isinstance(value_node, ast.List):
                result[key] = [item.value if isinstance(item, (ast.Constant, ast.Str)) else None
                               for item in value_node.elts]
            elif isinstance(value_node, ast.Attribute):
                # Handle ImpactScale.HIGH.value type attributes
                result[key] = 'ENUM_VALUE'  # Placeholder, not translatable

        return result

    return None


def extract_strings_with_regex(file_path):
    """
    Fallback: Extract strings using regex parsing (more robust for complex Python)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the descriptions dictionary
    desc_match = re.search(r'descriptions = \{(.*?)\n    \}', content, re.DOTALL)
    if not desc_match:
        return {}

    descriptions_text = desc_match.group(1)

    # Parse individual issue blocks
    issue_pattern = r"'([A-Za-z0-9_]+)':\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}"
    issues = {}

    for match in re.finditer(issue_pattern, descriptions_text):
        issue_code = match.group(1)
        issue_content = match.group(2)

        issue_data = {}

        # Extract string fields
        field_pattern = r"'(title|what|why|who|remediation|what_generic)':\s*[\"']([^\"']*(?:[^\"'\\]|\\.[^\"']*)*)['\"']"

        for field_match in re.finditer(field_pattern, issue_content):
            field_name = field_match.group(1)
            field_value = field_match.group(2)
            # Unescape quotes
            field_value = field_value.replace("\\'", "'").replace('\\"', '"')
            issue_data[field_name] = field_value

        if issue_data:
            issues[issue_code] = issue_data

    return issues


def main():
    # Path to the issue descriptions file
    file_path = Path(__file__).parent.parent / 'auto_a11y' / 'reporting' / 'issue_descriptions_enhanced.py'

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    print(f"Extracting strings from {file_path}", file=sys.stderr)

    # Try AST parsing first
    try:
        descriptions = extract_strings_from_ast(file_path)
        if not descriptions:
            print("AST parsing returned empty, trying regex fallback...", file=sys.stderr)
            descriptions = extract_strings_with_regex(file_path)
    except Exception as e:
        print(f"AST parsing failed: {e}", file=sys.stderr)
        print("Falling back to regex parsing...", file=sys.stderr)
        descriptions = extract_strings_with_regex(file_path)

    if not descriptions:
        print("Error: Could not extract descriptions", file=sys.stderr)
        return 1

    print(f"Extracted {len(descriptions)} issue descriptions", file=sys.stderr)

    # Convert to translatable format
    translatable_strings = []
    string_count = 0

    for issue_code, issue_data in sorted(descriptions.items()):
        for field in ['title', 'what', 'why', 'who', 'remediation', 'what_generic']:
            if field in issue_data and isinstance(issue_data[field], str):
                original_text = issue_data[field]
                converted_text = convert_placeholders(original_text)

                translatable_strings.append({
                    'msgctxt': f'issue_{issue_code}_{field}',
                    'msgid': converted_text,
                    'original': original_text,
                    'issue_code': issue_code,
                    'field': field
                })
                string_count += 1

    print(f"Extracted {string_count} translatable strings", file=sys.stderr)

    # Output JSON
    output = {
        'metadata': {
            'total_issues': len(descriptions),
            'total_strings': string_count,
            'file': str(file_path.name)
        },
        'strings': translatable_strings
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))

    return 0


if __name__ == '__main__':
    sys.exit(main())
