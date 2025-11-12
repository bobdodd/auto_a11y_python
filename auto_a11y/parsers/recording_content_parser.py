"""
HTML Content Parser for Recording Data

Parses HTML fragments containing key takeaways, user painpoints, and user assertions
into structured data for the Recording model.
"""

import re
from typing import List, Dict, Any, Optional
from html.parser import HTMLParser


class RecordingContentHTMLParser(HTMLParser):
    """Base HTML parser for recording content"""

    def __init__(self):
        super().__init__()
        self.current_tag = None
        self.current_text = []
        self.items = []
        self.current_item = {}
        self.in_h4 = False
        self.in_h5 = False
        self.in_p = False
        self.current_h5_label = None
        self.pending_text = []  # Text after h5 but before next tag

    def handle_starttag(self, tag, attrs):
        # Process any pending text from after h5
        if self.pending_text and self.current_h5_label:
            text = ''.join(self.pending_text).strip()
            if text:
                self.process_labeled_content(self.current_h5_label, text)
            self.pending_text = []

        self.current_tag = tag
        if tag == 'h4':
            self.in_h4 = True
            # Start new item
            if self.current_item:
                self.items.append(self.current_item)
            self.current_item = {}
            self.current_text = []
            self.current_h5_label = None
        elif tag == 'h5':
            self.in_h5 = True
            self.current_text = []
        elif tag == 'p':
            self.in_p = True
            self.current_text = []

    def handle_endtag(self, tag):
        if tag == 'h4':
            self.in_h4 = False
            text = ''.join(self.current_text).strip()
            self.process_h4(text)
            self.current_text = []
        elif tag == 'h5':
            self.in_h5 = False
            self.current_h5_label = ''.join(self.current_text).strip()
            self.current_text = []
            self.pending_text = []  # Start collecting text after h5

            # Check if label contains inline content (e.g., "Quote: text" or "Timecode: 00:00:00 - 00:00:00")
            # Only process inline if there's actual content after the colon
            if ':' in self.current_h5_label:
                parts = self.current_h5_label.split(':', 1)
                if len(parts) == 2 and parts[1].strip():
                    # Has content after colon - process inline content immediately
                    self.process_labeled_content(self.current_h5_label, '')
                    self.current_h5_label = None  # Clear label since we processed it
        elif tag == 'p':
            self.in_p = False
            text = ''.join(self.current_text).strip()
            if self.current_h5_label:
                self.process_labeled_content(self.current_h5_label, text)
                self.pending_text = []  # Clear pending since we processed via p tag
            else:
                self.process_paragraph(text)
            self.current_text = []
        self.current_tag = None

    def handle_data(self, data):
        if self.in_h4 or self.in_h5 or self.in_p:
            self.current_text.append(data)
        elif self.current_h5_label and not self.in_h4:
            # Collecting text after h5 ended but before next tag
            self.pending_text.append(data)

    def process_h4(self, text):
        """Override in subclasses"""
        pass

    def process_paragraph(self, text):
        """Override in subclasses"""
        pass

    def process_labeled_content(self, label, text):
        """Override in subclasses"""
        pass

    def get_items(self):
        """Return parsed items"""
        # Process any pending text before finalizing
        if self.pending_text and self.current_h5_label:
            text = ''.join(self.pending_text).strip()
            if text:
                self.process_labeled_content(self.current_h5_label, text)
            self.pending_text = []

        if self.current_item:
            self.items.append(self.current_item)
        return self.items


class KeyTakeawaysParser(RecordingContentHTMLParser):
    """Parse key takeaways HTML"""

    def process_h4(self, text):
        """Process h4 tag - extract number and title"""
        # Extract number and title (e.g., "1. Missing skip to main content link")
        match = re.match(r'(\d+)\.\s*(.*)', text)
        if match:
            self.current_item['number'] = int(match.group(1))
            self.current_item['title'] = match.group(2).strip()
        else:
            self.current_item['title'] = text
            self.current_item['number'] = len(self.items) + 1

    def process_paragraph(self, text):
        """Process paragraph - extract description and timecode"""
        # Extract timecodes from description (format: HH:MM:SS.mmm - HH:MM:SS.mmm)
        timecode_pattern = r'\((\d{2}:\d{2}:\d{2}\.\d{3})\s*-\s*(\d{2}:\d{2}:\d{2}\.\d{3})'
        timecode_matches = list(re.finditer(timecode_pattern, text))

        if timecode_matches:
            # Extract timecodes
            timecodes = []
            for match in timecode_matches:
                timecodes.append({
                    'start': match.group(1),
                    'end': match.group(2)
                })
            self.current_item['timecodes'] = timecodes

            # Remove timecodes from description
            description = re.sub(timecode_pattern + r'[,)]*', '', text).strip()
            self.current_item['description'] = description
        else:
            self.current_item['description'] = text


class UserPainpointsParser(RecordingContentHTMLParser):
    """Parse user painpoints HTML"""

    def process_h4(self, text):
        """Process h4 tag - the title of the painpoint"""
        self.current_item['title'] = text
        self.current_item['locations'] = []

    def process_labeled_content(self, label, text):
        """Process labeled content (User Statement, User Quote, Location, etc.)"""
        label_lower = label.lower()

        # Check if label contains inline data with actual content after colon
        if ':' in label:
            # Split on first colon to separate label from content
            parts = label.split(':', 1)
            if len(parts) == 2:
                actual_label = parts[0].strip().lower()
                inline_content = parts[1].strip()

                # Only process inline if there's actual content after the colon
                if inline_content and ('user statement' in actual_label or 'user quote' in actual_label):
                    inline_content = inline_content.strip('"\'')
                    self.current_item['user_statement'] = inline_content
                    return

        # Handle traditional format with text in separate p tags or after h5
        if 'user statement' in label_lower or 'user quote' in label_lower:
            # Remove surrounding quotes if present
            text = text.strip('"\'')
            self.current_item['user_statement'] = text
        elif 'location' in label_lower:
            # Parse location data
            # Could be "Location", "Location 1", "Location 2", etc.
            if 'locations' not in self.current_item:
                self.current_item['locations'] = []
            # Location data will be in subsequent text lines
            # Parse inline format: "Start: HH:MM:SS End: HH:MM:SS Duration: HH:MM:SS"
            location = {}
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('Start:'):
                    location['start'] = line.replace('Start:', '').strip()
                elif line.startswith('End:'):
                    location['end'] = line.replace('End:', '').strip()
                elif line.startswith('Duration:'):
                    location['duration'] = line.replace('Duration:', '').strip()

            if location:
                self.current_item['locations'].append(location)
        elif 'start time' in label_lower or 'start' in label_lower:
            # Parse start time - create location with single timecode
            if 'locations' not in self.current_item:
                self.current_item['locations'] = []
            self.current_item.setdefault('_temp_location', {})['start'] = text.strip()
        elif 'end time' in label_lower or 'end' in label_lower:
            # Parse end time
            self.current_item.setdefault('_temp_location', {})['end'] = text.strip()
        elif 'duration' in label_lower:
            # Parse duration and complete the location
            location = self.current_item.get('_temp_location', {})
            location['duration'] = text.strip()
            if location:
                if 'locations' not in self.current_item:
                    self.current_item['locations'] = []
                self.current_item['locations'].append(location)
                self.current_item['_temp_location'] = {}

    def get_items(self):
        """Clean up temporary fields and return items"""
        if self.current_item:
            # Clean up temporary location if exists
            if '_temp_location' in self.current_item:
                loc = self.current_item.pop('_temp_location')
                if loc:
                    self.current_item.setdefault('locations', []).append(loc)
            self.items.append(self.current_item)

        # Clean up any remaining temp fields
        for item in self.items:
            item.pop('_temp_location', None)

        return self.items


class UserAssertionsParser(RecordingContentHTMLParser):
    """Parse user assertions HTML"""

    def process_h4(self, text):
        """Process h4 tag - extract number and title"""
        # Extract number and title (e.g., "1. Aside region incorrectly placed")
        match = re.match(r'(\d+)\.\s*(.*)', text)
        if match:
            self.current_item['number'] = int(match.group(1))
            self.current_item['title'] = match.group(2).strip()
        else:
            self.current_item['title'] = text
            self.current_item['number'] = len(self.items) + 1

    def process_labeled_content(self, label, text):
        """Process labeled content (Text Spoken, Quote, User Statement, Start Time, etc.)"""
        label_lower = label.lower()

        # Check if label contains inline data (e.g., "Quote: text here" or "Timecode: 00:00:00 - 00:00:00")
        if ':' in label:
            # Split on first colon to separate label from content
            parts = label.split(':', 1)
            if len(parts) == 2:
                actual_label = parts[0].strip().lower()
                inline_content = parts[1].strip()

                # Process based on the actual label
                if 'quote' in actual_label or 'user statement' in actual_label or 'text spoken' in actual_label:
                    inline_content = inline_content.strip('"\'')
                    self.current_item['text_spoken'] = inline_content
                    return
                elif 'timecode' in actual_label or 'time code' in actual_label:
                    # Parse inline timecode
                    time_pattern = r'(\d{1,2}:\d{2}:\d{2}(?:\.\d{3})?)'
                    times = re.findall(time_pattern, inline_content)

                    if len(times) >= 2:
                        self.current_item['start_time'] = times[0]
                        self.current_item['end_time'] = times[1]
                        if len(times) >= 3:
                            self.current_item['duration'] = times[2]
                    return

        # Handle traditional format with text in separate p tags
        if 'text spoken' in label_lower or 'quote' in label_lower or 'user statement' in label_lower:
            # Remove surrounding quotes if present
            text = text.strip('"\'')
            self.current_item['text_spoken'] = text
        elif 'start time' in label_lower or ('start' in label_lower and 'time' not in label_lower):
            self.current_item['start_time'] = text.strip()
        elif 'end time' in label_lower or ('end' in label_lower and 'time' not in label_lower):
            self.current_item['end_time'] = text.strip()
        elif 'duration' in label_lower:
            self.current_item['duration'] = text.strip()
        elif 'timecode' in label_lower or 'time code' in label_lower:
            # Parse timecode format: "HH:MM:SS - HH:MM:SS (Duration: HH:MM:SS)"
            # or "Start: HH:MM:SS, End: HH:MM:SS, Duration: HH:MM:SS"
            # or just "HH:MM:SS - HH:MM:SS"

            # Try to extract start, end, duration
            # First try to find all time patterns in the text
            time_pattern = r'(\d{1,2}:\d{2}:\d{2}(?:\.\d{3})?)'
            times = re.findall(time_pattern, text)

            if len(times) >= 2:
                # First time is start, second is end
                self.current_item['start_time'] = times[0]
                self.current_item['end_time'] = times[1]
                if len(times) >= 3:
                    # Third time is duration
                    self.current_item['duration'] = times[2]
            elif len(times) == 1:
                # Just one time, could be start or duration
                if 'duration' in text.lower():
                    self.current_item['duration'] = times[0]
                else:
                    self.current_item['start_time'] = times[0]


def parse_key_takeaways_html(html_content: str) -> List[Dict[str, Any]]:
    """
    Parse key takeaways HTML into structured data.

    Args:
        html_content: HTML string containing key takeaways

    Returns:
        List of dicts with keys: number, title, description, timecodes
    """
    parser = KeyTakeawaysParser()
    parser.feed(html_content)
    return parser.get_items()


def parse_user_painpoints_html(html_content: str) -> List[Dict[str, Any]]:
    """
    Parse user painpoints HTML into structured data.

    Args:
        html_content: HTML string containing user painpoints

    Returns:
        List of dicts with keys: title, user_statement, locations
    """
    parser = UserPainpointsParser()
    parser.feed(html_content)
    return parser.get_items()


def parse_user_assertions_html(html_content: str) -> List[Dict[str, Any]]:
    """
    Parse user assertions HTML into structured data.

    Args:
        html_content: HTML string containing user assertions

    Returns:
        List of dicts with keys: number, title, text_spoken, start_time, end_time, duration
    """
    parser = UserAssertionsParser()
    parser.feed(html_content)
    return parser.get_items()


# JSON Parsing Functions

def parse_key_takeaways_json(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse key takeaways JSON into structured data.

    Expected JSON format:
    {
        "recording": "Recording Name",
        "takeaways": [
            {
                "number": 1,
                "topic": "Topic Title",
                "description": "Detailed description..."
            }
        ]
    }

    Args:
        json_data: Dictionary containing key takeaways data

    Returns:
        List of dicts with keys: number, topic, description
    """
    import json

    # If json_data is a string, parse it
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    takeaways = json_data.get('takeaways', [])

    # Keep the original JSON structure
    result = []
    for item in takeaways:
        result.append({
            'number': item.get('number', 0),
            'topic': item.get('topic', ''),
            'description': item.get('description', '')
        })

    return result


def parse_user_painpoints_json(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse user painpoints JSON into structured data.

    Expected JSON format:
    {
        "recording": "Recording Name",
        "pain_points": [
            {
                "title": "Pain Point Title",
                "timecodes": [
                    {
                        "start": "00:00:22.285",
                        "end": "00:01:34.520",
                        "duration": "00:01:12.235"
                    }
                ],
                "user_quote": "Detailed quote...",
                "impact": "high"
            }
        ]
    }

    Args:
        json_data: Dictionary containing user painpoints data

    Returns:
        List of dicts with keys: title, user_statement, locations
    """
    import json

    # If json_data is a string, parse it
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    # Support both "pain_points" and "painpoints" keys
    painpoints = json_data.get('pain_points', json_data.get('painpoints', []))

    # Keep the original JSON structure
    result = []
    for item in painpoints:
        result.append({
            'title': item.get('title', ''),
            'user_quote': item.get('user_quote', ''),
            'timecodes': item.get('timecodes', []),
            'impact': item.get('impact', '')
        })

    return result


def parse_user_assertions_json(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse user assertions JSON into structured data.

    Expected JSON format:
    {
        "recording": "Recording Name",
        "assertions": [
            {
                "number": 1,
                "assertion": "Assertion Title",
                "timecodes": [
                    {
                        "start": "00:00:22:765",
                        "end": "00:00:25:805",
                        "duration": "00:00:03:040"
                    }
                ],
                "user_quote": "Quote or observation...",
                "context": "Additional context..."
            }
        ]
    }

    Args:
        json_data: Dictionary containing user assertions data

    Returns:
        List of dicts with keys: number, title, text_spoken, start_time, end_time, duration, context
    """
    import json

    # If json_data is a string, parse it
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    assertions = json_data.get('assertions', [])

    # Keep the original JSON structure
    result = []
    for item in assertions:
        result.append({
            'number': item.get('number', 0),
            'assertion': item.get('assertion', item.get('title', '')),
            'user_quote': item.get('user_quote', ''),
            'timecodes': item.get('timecodes', []),
            'context': item.get('context', '')
        })

    return result
