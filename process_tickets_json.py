#!/usr/bin/env python3
"""
Script to process the large predefined_tickets.json file and extract relevant information
for improving the ISSUE_CATALOG_TEMPLATE.md
"""

import json
import html
import re
from pathlib import Path


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


def extract_ticket_info(ticket):
    """Extract relevant information from a ticket"""
    return {
        'title': ticket.get('title', ''),
        'body_clean': clean_html(ticket.get('body', '')),
        'priority': ticket.get('field_priority', ''),
        'wcag': ticket.get('title_1', '')
    }


def categorize_tickets(tickets):
    """Categorize tickets by their titles"""
    categories = {
        'images': [],
        'forms': [],
        'headings': [],
        'landmarks': [],
        'color': [],
        'language': [],
        'focus': [],
        'buttons': [],
        'links': [],
        'tables': [],
        'aria': [],
        'page': [],
        'video': [],
        'audio': [],
        'other': []
    }
    
    for ticket in tickets:
        title_lower = ticket['title'].lower()
        categorized = False
        
        # Categorize based on title content
        if 'image' in title_lower or 'img' in title_lower or 'alt' in title_lower:
            categories['images'].append(ticket)
            categorized = True
        elif 'form' in title_lower or 'input' in title_lower or 'field' in title_lower or 'label' in title_lower:
            categories['forms'].append(ticket)
            categorized = True
        elif 'heading' in title_lower or 'h1' in title_lower or 'h2' in title_lower:
            categories['headings'].append(ticket)
            categorized = True
        elif 'landmark' in title_lower or 'main' in title_lower or 'nav' in title_lower or 'banner' in title_lower:
            categories['landmarks'].append(ticket)
            categorized = True
        elif 'color' in title_lower or 'contrast' in title_lower:
            categories['color'].append(ticket)
            categorized = True
        elif 'lang' in title_lower or 'language' in title_lower:
            categories['language'].append(ticket)
            categorized = True
        elif 'focus' in title_lower or 'tab' in title_lower or 'keyboard' in title_lower:
            categories['focus'].append(ticket)
            categorized = True
        elif 'button' in title_lower:
            categories['buttons'].append(ticket)
            categorized = True
        elif 'link' in title_lower or 'anchor' in title_lower:
            categories['links'].append(ticket)
            categorized = True
        elif 'table' in title_lower:
            categories['tables'].append(ticket)
            categorized = True
        elif 'aria' in title_lower or 'role' in title_lower:
            categories['aria'].append(ticket)
            categorized = True
        elif 'page' in title_lower or 'title' in title_lower:
            categories['page'].append(ticket)
            categorized = True
        elif 'video' in title_lower or 'media' in title_lower:
            categories['video'].append(ticket)
            categorized = True
        elif 'audio' in title_lower:
            categories['audio'].append(ticket)
            categorized = True
        
        if not categorized:
            categories['other'].append(ticket)
    
    return categories


def save_category_files(categories, output_dir):
    """Save each category to a separate file"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for category, tickets in categories.items():
        if tickets:  # Only save non-empty categories
            filename = output_path / f"tickets_{category}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tickets, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(tickets)} tickets to {filename}")


def create_summary(categories):
    """Create a summary of all categories"""
    summary = []
    summary.append("# Predefined Tickets Summary\n")
    summary.append(f"Total categories: {len(categories)}\n")
    
    for category, tickets in categories.items():
        if tickets:
            summary.append(f"\n## {category.upper()} ({len(tickets)} tickets)\n")
            # Show first 5 titles as examples
            for ticket in tickets[:5]:
                summary.append(f"- {ticket['title']}\n")
            if len(tickets) > 5:
                summary.append(f"... and {len(tickets) - 5} more\n")
    
    return ''.join(summary)


def main():
    # Load the JSON file
    json_file = Path('/Users/bob3/Desktop/auto_a11y_python/predefined_tickets.json')
    
    print(f"Loading {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} tickets")
    
    # Extract relevant info from each ticket
    print("Extracting ticket information...")
    tickets = [extract_ticket_info(ticket) for ticket in data]
    
    # Remove duplicates based on title
    unique_tickets = {}
    for ticket in tickets:
        if ticket['title'] not in unique_tickets:
            unique_tickets[ticket['title']] = ticket
    
    tickets = list(unique_tickets.values())
    print(f"Found {len(tickets)} unique tickets")
    
    # Categorize tickets
    print("Categorizing tickets...")
    categories = categorize_tickets(tickets)
    
    # Save categorized tickets to separate files
    output_dir = '/Users/bob3/Desktop/auto_a11y_python/ticket_categories'
    print(f"Saving categorized tickets to {output_dir}...")
    save_category_files(categories, output_dir)
    
    # Create and save summary
    summary = create_summary(categories)
    summary_file = Path(output_dir) / 'SUMMARY.md'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Saved summary to {summary_file}")
    
    print("\nDone! Check the ticket_categories folder for the processed files.")
    
    # Print statistics
    print("\n=== Statistics ===")
    total = 0
    for category, tickets in categories.items():
        if tickets:
            print(f"{category}: {len(tickets)} tickets")
            total += len(tickets)
    print(f"Total categorized: {total}")


if __name__ == "__main__":
    main()