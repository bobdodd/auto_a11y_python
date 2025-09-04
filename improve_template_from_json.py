#!/usr/bin/env python3
"""
Script to improve ISSUE_CATALOG_TEMPLATE.md using data from predefined_tickets.json
"""

import json
import re
import html
from pathlib import Path
from difflib import SequenceMatcher


def clean_html(text):
    """Remove HTML tags and decode HTML entities"""
    if not text:
        return ""
    # Decode HTML entities
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_json_ticket(ticket):
    """Parse a JSON ticket into structured format"""
    body_clean = clean_html(ticket.get('body', ''))
    
    # Extract sections from body
    sections = {
        'what': '',
        'why': '',
        'who': '',
        'how': '',
        'further': ''
    }
    
    # Try to extract sections
    what_match = re.search(r'What the issue is(.+?)(?:Why this is important|$)', body_clean, re.IGNORECASE | re.DOTALL)
    if what_match:
        sections['what'] = what_match.group(1).strip()
    
    why_match = re.search(r'Why this is important(.+?)(?:Who it affects|$)', body_clean, re.IGNORECASE | re.DOTALL)
    if why_match:
        sections['why'] = why_match.group(1).strip()
    
    who_match = re.search(r'Who it affects(.+?)(?:How to remediate|$)', body_clean, re.IGNORECASE | re.DOTALL)
    if who_match:
        sections['who'] = who_match.group(1).strip()
    
    how_match = re.search(r'How to remediate(.+?)(?:Further|$)', body_clean, re.IGNORECASE | re.DOTALL)
    if how_match:
        sections['how'] = how_match.group(1).strip()
    
    return {
        'title': ticket.get('title', ''),
        'priority': ticket.get('field_priority', ''),
        'wcag': ticket.get('title_1', ''),
        'sections': sections,
        'full_body': body_clean
    }


def load_json_category(category):
    """Load a specific category of JSON tickets"""
    file_path = Path(f'/Users/bob3/Desktop/auto_a11y_python/ticket_categories/tickets_{category}.json')
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [parse_json_ticket(ticket) for ticket in data]
    return []


def find_similar_json_ticket(template_title, json_tickets):
    """Find the most similar JSON ticket to a template issue"""
    best_match = None
    best_score = 0
    
    # Normalize template title for comparison
    template_normalized = template_title.lower().strip()
    
    for ticket in json_tickets:
        json_title = ticket['title'].lower().strip()
        
        # Check for direct substring matches
        if template_normalized in json_title or json_title in template_normalized:
            score = 0.8
        else:
            # Use sequence matcher for fuzzy matching
            score = SequenceMatcher(None, template_normalized, json_title).ratio()
        
        # Boost score for certain keyword matches
        keywords = ['alt', 'label', 'contrast', 'heading', 'landmark', 'focus', 'language']
        for keyword in keywords:
            if keyword in template_normalized and keyword in json_title:
                score += 0.1
        
        if score > best_score:
            best_score = score
            best_match = ticket
    
    # Only return if we have a decent match
    if best_score > 0.3:
        return best_match, best_score
    return None, 0


def extract_template_issues():
    """Extract all issues from the template markdown file"""
    template_path = Path('/Users/bob3/Desktop/auto_a11y_python/ISSUE_CATALOG_TEMPLATE.md')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all issue blocks
    issue_pattern = r'```\nID: ([^\n]+)\nType: ([^\n]+)\nImpact: ([^\n]+)\nWCAG: ([^\n]+)\nCategory: ([^\n]+)\nDescription: ([^\n]+)\nWhy it matters: ([^\n]+)\nWho it affects: ([^\n]+)\nHow to fix: ([^\n]+)\n```'
    
    issues = []
    for match in re.finditer(issue_pattern, content, re.MULTILINE):
        issues.append({
            'id': match.group(1),
            'type': match.group(2),
            'impact': match.group(3),
            'wcag': match.group(4),
            'category': match.group(5),
            'description': match.group(6),
            'why': match.group(7),
            'who': match.group(8),
            'how': match.group(9)
        })
    
    return issues


def create_improvement_report():
    """Create a report showing potential improvements from JSON data"""
    # Load template issues
    template_issues = extract_template_issues()
    print(f"Found {len(template_issues)} issues in template")
    
    # Load all JSON categories
    categories = ['images', 'forms', 'headings', 'landmarks', 'color', 'language', 'focus']
    all_json_tickets = []
    
    for category in categories:
        tickets = load_json_category(category)
        all_json_tickets.extend(tickets)
        print(f"Loaded {len(tickets)} tickets from {category}")
    
    # Find matches and improvements
    improvements = []
    
    for issue in template_issues[:10]:  # Process first 10 for demo
        # Skip example templates
        if issue['id'] == '[Issue identifier from code]' or issue['id'] == '[unique_identifier]':
            continue
            
        match, score = find_similar_json_ticket(issue['description'], all_json_tickets)
        
        if match:
            improvements.append({
                'template_id': issue['id'],
                'template_desc': issue['description'],
                'match_title': match['title'],
                'match_score': score,
                'json_what': match['sections']['what'],
                'json_why': match['sections']['why'],
                'json_who': match['sections']['who'],
                'json_how': match['sections']['how']
            })
    
    # Save improvements to file
    output_path = Path('/Users/bob3/Desktop/auto_a11y_python/template_improvements.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(improvements, f, indent=2, ensure_ascii=False)
    
    print(f"\nFound {len(improvements)} potential improvements")
    print(f"Saved to {output_path}")
    
    # Print a few examples
    for imp in improvements[:3]:
        print(f"\n{'='*60}")
        print(f"Template ID: {imp['template_id']}")
        print(f"Match Score: {imp['match_score']:.2f}")
        print(f"JSON Match: {imp['match_title']}")
        if imp['json_why']:
            print(f"Better 'Why': {imp['json_why'][:200]}...")


if __name__ == "__main__":
    create_improvement_report()