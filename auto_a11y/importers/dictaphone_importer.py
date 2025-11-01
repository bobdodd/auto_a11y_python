"""
Dictaphone JSON importer for AutoA11y

Imports manual accessibility audit data from Dictaphone format into AutoA11y's
recording and issue tracking system.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from auto_a11y.models import (
    Recording, RecordingIssue, RecordingType,
    Timecode, WCAGReference, ImpactLevel
)

logger = logging.getLogger(__name__)


class DictaphoneImporter:
    """
    Import Dictaphone JSON data into AutoA11y.

    Dictaphone generates accessibility findings from audio/video recordings
    of manual audits and lived experience testing. This importer converts
    that data into AutoA11y's Recording and RecordingIssue models.
    """

    def __init__(self):
        """Initialize the importer"""
        pass

    def import_from_file(
        self,
        json_file_path: str,
        project_id: str,
        website_ids: Optional[List[str]] = None,
        page_urls: Optional[List[str]] = None,
        auditor_info: Optional[Dict[str, Any]] = None,
        recording_type: str = "audit"
    ) -> Tuple[Recording, List[RecordingIssue]]:
        """
        Import a Dictaphone JSON file.

        Args:
            json_file_path: Path to dictaphone JSON file
            project_id: AutoA11y project ID to attach to
            website_ids: Optional website IDs this recording covers
            page_urls: Optional specific page URLs discussed in recording
            auditor_info: Optional dict with auditor_name, auditor_role, etc.
            recording_type: Type of recording (audit, lived_experience_website, etc.)

        Returns:
            Tuple of (Recording object, List of RecordingIssue objects)

        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValueError: If JSON is invalid or missing required fields
            json.JSONDecodeError: If file is not valid JSON
        """
        # Read and parse JSON file
        file_path = Path(json_file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Dictaphone JSON file not found: {json_file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Parsing Dictaphone JSON from {json_file_path}")

        # Parse the data
        recording, issues = self.parse_dictaphone_json(
            data,
            project_id=project_id,
            website_ids=website_ids or [],
            page_urls=page_urls or [],
            auditor_info=auditor_info or {},
            recording_type=recording_type
        )

        logger.info(f"Successfully parsed recording '{recording.recording_id}' with {len(issues)} issues")

        return recording, issues

    def parse_dictaphone_json(
        self,
        data: dict,
        project_id: str,
        website_ids: List[str],
        page_urls: List[str],
        auditor_info: Dict[str, Any],
        recording_type: str
    ) -> Tuple[Recording, List[RecordingIssue]]:
        """
        Parse Dictaphone JSON structure into Recording and RecordingIssue objects.

        Args:
            data: Parsed JSON dict from Dictaphone
            project_id: Project ID to link to
            website_ids: Website IDs
            page_urls: Page URLs
            auditor_info: Auditor information
            recording_type: Type of recording

        Returns:
            Tuple of (Recording, List[RecordingIssue])

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        if 'recording' not in data:
            raise ValueError("Missing required field: 'recording'")
        if 'issues' not in data:
            raise ValueError("Missing required field: 'issues'")

        recording_id = data['recording']
        issues_data = data['issues']

        # Parse recording type
        try:
            recording_type_enum = RecordingType(recording_type)
        except ValueError:
            logger.warning(f"Invalid recording_type '{recording_type}', defaulting to 'audit'")
            recording_type_enum = RecordingType.AUDIT

        # Count issues by impact
        high_count = sum(1 for issue in issues_data if issue.get('impact', '').lower() in ['high', 'critical'])
        medium_count = sum(1 for issue in issues_data if issue.get('impact', '').lower() in ['medium', 'moderate'])
        low_count = sum(1 for issue in issues_data if issue.get('impact', '').lower() == 'low')

        # Calculate total duration if we can extract it from timecodes
        total_duration = self._calculate_total_duration(issues_data)

        # Create Recording object
        recording = Recording(
            recording_id=recording_id,
            title=auditor_info.get('title', f"Recording {recording_id}"),
            description=auditor_info.get('description'),
            media_file_path=auditor_info.get('media_file_path'),
            duration=total_duration,
            recorded_date=auditor_info.get('recorded_date'),
            auditor_name=auditor_info.get('auditor_name'),
            auditor_role=auditor_info.get('auditor_role'),
            recording_type=recording_type_enum,
            project_id=project_id,
            website_ids=website_ids,
            page_urls=page_urls,
            total_issues=len(issues_data),
            high_impact_count=high_count,
            medium_impact_count=medium_count,
            low_impact_count=low_count,
            tags=auditor_info.get('tags', []),
            notes=auditor_info.get('notes')
        )

        # Parse issues
        issues = []
        for issue_data in issues_data:
            try:
                issue = RecordingIssue.from_dictaphone_issue(
                    issue_data,
                    recording_id=recording_id,
                    project_id=project_id
                )
                # Add page_urls and website_ids from recording
                issue.page_urls = page_urls
                issue.website_ids = website_ids

                # Infer touchpoint from WCAG criteria if not present
                if not issue.touchpoint:
                    issue.touchpoint = self._infer_touchpoint(issue_data)

                issues.append(issue)
            except Exception as e:
                logger.error(f"Error parsing issue '{issue_data.get('title', 'unknown')}': {e}")
                # Continue with other issues

        return recording, issues

    def _calculate_total_duration(self, issues_data: List[Dict]) -> Optional[str]:
        """
        Calculate total recording duration from issue timecodes.
        Returns the maximum end time found across all timecodes.

        Args:
            issues_data: List of issue dicts from Dictaphone JSON

        Returns:
            Duration string in HH:MM:SS format, or None if cannot determine
        """
        max_seconds = 0.0

        for issue in issues_data:
            timecodes = issue.get('timecodes', [])
            for tc in timecodes:
                try:
                    # Create Timecode object to parse time
                    timecode = Timecode(
                        start=tc.get('start', '00:00:00'),
                        end=tc.get('end', '00:00:00'),
                        duration=tc.get('duration', '00:00:00')
                    )
                    end_seconds = timecode.end_seconds
                    if end_seconds > max_seconds:
                        max_seconds = end_seconds
                except Exception as e:
                    logger.debug(f"Could not parse timecode: {e}")
                    continue

        if max_seconds > 0:
            # Convert back to HH:MM:SS format
            hours = int(max_seconds // 3600)
            minutes = int((max_seconds % 3600) // 60)
            seconds = int(max_seconds % 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        return None

    def _infer_touchpoint(self, issue_data: Dict) -> str:
        """
        Infer accessibility touchpoint/category from issue details.

        Args:
            issue_data: Issue dict from Dictaphone JSON

        Returns:
            Touchpoint string (e.g., "Landmarks", "Navigation", "Forms")
        """
        title = issue_data.get('title', '').lower()
        short_title = issue_data.get('short_title', '').lower()

        # Mapping of keywords to touchpoints
        keyword_mapping = {
            'landmark': 'Landmarks',
            'aside': 'Landmarks',
            'navigation': 'Navigation',
            'nav': 'Navigation',
            'menu': 'Navigation',
            'dropdown': 'Navigation',
            'search': 'Forms',
            'input': 'Forms',
            'form': 'Forms',
            'field': 'Forms',
            'label': 'Forms',
            'button': 'Forms',
            'contrast': 'Color Contrast',
            'color': 'Color Contrast',
            'focus': 'Focus Management',
            'heading': 'Headings',
            'h1': 'Headings',
            'h2': 'Headings',
            'h3': 'Headings',
            'image': 'Images',
            'img': 'Images',
            'svg': 'Images',
            'logo': 'Images',
            'alt': 'Images',
            'link': 'Links',
            'aria': 'ARIA',
            'role': 'ARIA',
            'list': 'Lists',
            'table': 'Tables',
            'font': 'Typography',
            'text': 'Typography',
            'skip': 'Page Structure',
            'title': 'Page Structure'
        }

        # Check title and short_title for keywords
        search_text = f"{title} {short_title}"
        for keyword, touchpoint in keyword_mapping.items():
            if keyword in search_text:
                return touchpoint

        # Check WCAG criteria for hints
        wcag_list = issue_data.get('wcag', [])
        if wcag_list:
            first_criteria = wcag_list[0].get('criteria', '')
            if first_criteria.startswith('1.1'):
                return 'Images'
            elif first_criteria.startswith('1.3'):
                return 'Page Structure'
            elif first_criteria.startswith('1.4'):
                return 'Color Contrast'
            elif first_criteria.startswith('2.1'):
                return 'Keyboard'
            elif first_criteria.startswith('2.4'):
                return 'Navigation'
            elif first_criteria.startswith('3.3'):
                return 'Forms'
            elif first_criteria.startswith('4.1'):
                return 'ARIA'

        # Default fallback
        return 'General'

    def map_dictaphone_impact(self, impact_str: str) -> ImpactLevel:
        """
        Map Dictaphone impact levels to AutoA11y ImpactLevel enum.

        Args:
            impact_str: Impact string from Dictaphone (e.g., "high", "medium", "low")

        Returns:
            ImpactLevel enum value
        """
        impact_lower = impact_str.lower() if impact_str else 'medium'

        mapping = {
            'low': ImpactLevel.LOW,
            'minor': ImpactLevel.LOW,
            'medium': ImpactLevel.MEDIUM,
            'moderate': ImpactLevel.MEDIUM,
            'high': ImpactLevel.HIGH,
            'critical': ImpactLevel.HIGH,
            'serious': ImpactLevel.HIGH
        }

        return mapping.get(impact_lower, ImpactLevel.MEDIUM)

    def validate_dictaphone_json(self, data: dict) -> Tuple[bool, Optional[str]]:
        """
        Validate Dictaphone JSON structure.

        Args:
            data: Parsed JSON dict

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required top-level fields
        if 'recording' not in data:
            return False, "Missing required field: 'recording'"

        if 'issues' not in data:
            return False, "Missing required field: 'issues'"

        if not isinstance(data['issues'], list):
            return False, "'issues' must be an array"

        # Validate each issue has required fields
        for i, issue in enumerate(data['issues']):
            if 'title' not in issue:
                return False, f"Issue {i} missing required field: 'title'"

            if 'impact' not in issue:
                return False, f"Issue {i} missing required field: 'impact'"

            if 'timecodes' in issue and not isinstance(issue['timecodes'], list):
                return False, f"Issue {i}: 'timecodes' must be an array"

            if 'wcag' in issue and not isinstance(issue['wcag'], list):
                return False, f"Issue {i}: 'wcag' must be an array"

        return True, None
