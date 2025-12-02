#!/usr/bin/env python3
"""
Script to add lazy_gettext translation wrappers to issue_descriptions_enhanced.py
Converts placeholder format from {var} to %(var)s for gettext compatibility
"""

import re
import sys

def convert_placeholders(text):
    """Convert {variable} format to %(variable)s format for gettext"""
    # Find all {variable} patterns
    pattern = r'\{([a-zA-Z_][a-zA-Z0-9_\.]*)\}'

    def replacer(match):
        var_name = match.group(1)
        # Convert dot notation to underscore (e.g., {element.tag} -> %(element_tag)s)
        var_name = var_name.replace('.', '_')
        return f'%({var_name})s'

    return re.sub(pattern, replacer, text)

def escape_quotes(text):
    """Escape single quotes in text for Python string"""
    return text.replace("'", "\\'")

def process_file(input_file, output_file):
    """Process the issue_descriptions_enhanced.py file"""

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_lines = []
    in_descriptions_dict = False
    issue_code = None
    field_name = None
    string_value = []
    in_multiline_string = False

    for i, line in enumerate(lines):
        # Check if we're entering the descriptions dictionary
        if 'descriptions = {' in line:
            in_descriptions_dict = True
            # Add import for lazy_gettext at the top of descriptions dict
            output_lines.append(line)
            continue

        # Check if we're exiting the descriptions dictionary
        if in_descriptions_dict and line.strip() == '}' and not in_multiline_string:
            # Check if this is the closing brace of the descriptions dict
            # by looking ahead
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if not next_line.startswith("'") and not next_line.startswith('"'):
                    in_descriptions_dict = False

        if not in_descriptions_dict:
            # Before the first import, add lazy_gettext
            if i == 5 and 'from enum import Enum' in line:
                output_lines.append("from flask_babel import lazy_gettext\n")
            output_lines.append(line)
            continue

        # Inside descriptions dict
        # Detect issue code line
        if re.match(r"^\s+'[A-Z]", line):
            # This is an issue code line like '        'ErrAccordionWithoutARIA': {'
            issue_code_match = re.search(r"'([A-Za-z0-9_]+)':", line)
            if issue_code_match:
                issue_code = issue_code_match.group(1)
            output_lines.append(line)
            continue

        # Detect field lines (title, what, why, who, remediation)
        field_match = re.match(r"^(\s+)'(title|what|why|who|remediation|what_generic)': (.+)", line)

        if field_match and issue_code:
            indent = field_match.group(1)
            field_name = field_match.group(2)
            rest_of_line = field_match.group(3)

            # Check if this is a simple string on one line
            if rest_of_line.strip().endswith(',') or rest_of_line.strip().endswith('}'):
                # Single line string
                # Extract the string value
                string_match = re.search(r'"([^"]*)"', rest_of_line)
                if not string_match:
                    string_match = re.search(r"'([^']*)'", rest_of_line)

                if string_match:
                    original_string = string_match.group(1)
                    # Convert placeholders
                    converted_string = convert_placeholders(original_string)
                    # Escape quotes
                    escaped_string = escape_quotes(converted_string)

                    # Create msgctxt
                    msgctxt = f'issue_{issue_code}_{field_name}'

                    # Write the lazy_gettext wrapped version
                    ending = ',' if rest_of_line.strip().endswith(',') else ''
                    output_lines.append(f"{indent}'{field_name}': lazy_gettext('{msgctxt}', '{escaped_string}'){ending}\n")
                else:
                    # Couldn't parse, keep original
                    output_lines.append(line)
            else:
                # Multiline string - keep original for now (these are rare)
                output_lines.append(line)
        else:
            # Not a translatable field, keep as is
            output_lines.append(line)

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    print(f"Processed {input_file} -> {output_file}")
    print("Note: This is a complex transformation. Please review the output carefully.")

def main():
    input_file = 'auto_a11y/reporting/issue_descriptions_enhanced.py'
    output_file = 'auto_a11y/reporting/issue_descriptions_enhanced_translated.py'

    try:
        process_file(input_file, output_file)
        print("\nSuccess! Review the output file and then:")
        print(f"  mv {output_file} {input_file}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
