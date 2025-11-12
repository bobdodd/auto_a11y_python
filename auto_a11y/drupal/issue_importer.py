"""
Drupal Issue Importer

Handles importing issues from Drupal to Auto A11y via JSON:API.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from auto_a11y.models import Issue, ImpactLevel
from auto_a11y.models.page import DrupalSyncStatus

logger = logging.getLogger(__name__)


class IssueImporter:
    """
    Import issues from Drupal.

    Handles fetching issue nodes from Drupal and converting them
    to Auto A11y Issue objects.
    """

    def __init__(self, client):
        """
        Initialize issue importer.

        Args:
            client: DrupalJSONAPIClient instance
        """
        self.client = client

    def fetch_issues_for_audit(self, audit_uuid: str) -> List[Dict[str, Any]]:
        """
        Fetch all issues for a given audit from Drupal.

        Args:
            audit_uuid: Drupal audit UUID

        Returns:
            List of issue dictionaries with parsed data
        """
        logger.info(f"Fetching issues for audit {audit_uuid}")

        all_issues = []
        page_limit = 50
        offset = 0

        while True:
            # Fetch issues with parent_audit filter
            response = self.client.get(
                'node/issue',
                params={
                    'filter[field_parent_audit.id]': audit_uuid,
                    'page[limit]': page_limit,
                    'page[offset]': offset,
                    'include': 'field_issue_type,field_location_on_page,field_wcag_chapter'
                }
            )

            issues = response.get('data', [])
            if not issues:
                break

            # Parse each issue
            for issue_node in issues:
                try:
                    parsed_issue = self._parse_issue_node(issue_node, response.get('included', []))
                    all_issues.append(parsed_issue)
                except Exception as e:
                    logger.error(f"Error parsing issue node: {e}")
                    continue

            offset += page_limit

            # If we got fewer than page_limit, we're done
            if len(issues) < page_limit:
                break

        logger.info(f"Fetched {len(all_issues)} issues for audit {audit_uuid}")
        return all_issues

    def _parse_issue_node(self, node: Dict[str, Any], included: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse a Drupal issue node into a dictionary.

        Args:
            node: JSON:API node data
            included: Included relationship data

        Returns:
            Dictionary with parsed issue data
        """
        uuid = node.get('id')
        attributes = node.get('attributes', {})
        relationships = node.get('relationships', {})

        # Extract basic fields
        title = attributes.get('title', 'Untitled Issue')

        # Body/description
        body_field = attributes.get('body')
        description = ''
        if body_field and isinstance(body_field, dict):
            description = body_field.get('value', '')
        elif body_field and isinstance(body_field, list) and len(body_field) > 0:
            description = body_field[0].get('value', '')

        # Impact
        impact_value = attributes.get('field_impact', 'med').lower()
        impact_mapping = {
            'low': 'low',
            'med': 'medium',
            'medium': 'medium',
            'high': 'high'
        }
        impact = impact_mapping.get(impact_value, 'medium')

        # Issue type (taxonomy term)
        issue_type = self._extract_taxonomy_term(
            relationships.get('field_issue_type'),
            included
        )

        # Location on page (taxonomy term)
        location_on_page = self._extract_taxonomy_term(
            relationships.get('field_location_on_page'),
            included
        )

        # WCAG chapters (may be multiple)
        wcag_criteria = self._extract_wcag_references(
            relationships.get('field_wcag_chapter'),
            included
        )

        # Technical fields
        xpath = attributes.get('field_xpath')
        url_field = attributes.get('field_url')
        url = None
        if url_field and isinstance(url_field, dict):
            url = url_field.get('uri')
        elif url_field and isinstance(url_field, list) and len(url_field) > 0:
            url = url_field[0].get('uri')

        video_timecode = attributes.get('field_video_timecode')

        # Drupal IDs
        drupal_issue_id = attributes.get('field_id')
        drupal_nid = attributes.get('drupal_internal__nid')

        # Timestamps
        created = attributes.get('created')
        changed = attributes.get('changed')

        return {
            'uuid': uuid,
            'title': title,
            'description': description,
            'impact': impact,
            'issue_type': issue_type,
            'location_on_page': location_on_page,
            'wcag_criteria': wcag_criteria,
            'xpath': xpath,
            'url': url,
            'video_timecode': video_timecode,
            'drupal_issue_id': drupal_issue_id,
            'drupal_nid': drupal_nid,
            'created_timestamp': created,
            'changed_timestamp': changed
        }

    def _extract_taxonomy_term(
        self,
        relationship: Optional[Dict[str, Any]],
        included: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Extract taxonomy term name from relationship.

        Args:
            relationship: Relationship object
            included: Included resources

        Returns:
            Term name or None
        """
        if not relationship:
            return None

        rel_data = relationship.get('data')
        if not rel_data:
            return None

        # Handle single relationship
        if isinstance(rel_data, dict):
            term_id = rel_data.get('id')
        # Handle multiple (take first)
        elif isinstance(rel_data, list) and len(rel_data) > 0:
            term_id = rel_data[0].get('id')
        else:
            return None

        # Find term in included
        for resource in included:
            if resource.get('id') == term_id:
                return resource.get('attributes', {}).get('name')

        return None

    def _extract_wcag_references(
        self,
        relationship: Optional[Dict[str, Any]],
        included: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract WCAG criteria from relationship.

        Args:
            relationship: Relationship object
            included: Included resources

        Returns:
            List of WCAG criteria strings (e.g., ["1.3.1", "2.4.6"])
        """
        if not relationship:
            return []

        rel_data = relationship.get('data')
        if not rel_data:
            return []

        # Ensure it's a list
        if isinstance(rel_data, dict):
            rel_data = [rel_data]

        criteria = []
        for item in rel_data:
            wcag_id = item.get('id')

            # Find WCAG node in included
            for resource in included:
                if resource.get('id') == wcag_id:
                    # Extract WCAG number from title
                    title = resource.get('attributes', {}).get('title', '')
                    # Title might be like "1.3.1 Info and Relationships"
                    # Extract just the number
                    parts = title.split()
                    if parts and parts[0].replace('.', '').isdigit():
                        criteria.append(parts[0])
                    break

        return criteria

    def convert_to_issue_model(
        self,
        drupal_issue: Dict[str, Any],
        project_id: str
    ) -> Issue:
        """
        Convert Drupal issue dict to Issue model instance.

        Args:
            drupal_issue: Parsed Drupal issue dict
            project_id: Project ID to associate with

        Returns:
            Issue model instance
        """
        # Convert timestamp to datetime
        created_at = datetime.fromtimestamp(drupal_issue['created_timestamp']) if drupal_issue.get('created_timestamp') else datetime.now()
        updated_at = datetime.fromtimestamp(drupal_issue['changed_timestamp']) if drupal_issue.get('changed_timestamp') else datetime.now()

        # Map impact
        impact_str = drupal_issue['impact']
        impact = ImpactLevel.MEDIUM
        if impact_str == 'low':
            impact = ImpactLevel.LOW
        elif impact_str == 'high':
            impact = ImpactLevel.HIGH

        return Issue(
            title=drupal_issue['title'],
            description=drupal_issue['description'],
            impact=impact,
            issue_type=drupal_issue.get('issue_type'),
            location_on_page=drupal_issue.get('location_on_page'),
            wcag_criteria=drupal_issue.get('wcag_criteria', []),
            xpath=drupal_issue.get('xpath'),
            url=drupal_issue.get('url'),
            video_timecode=drupal_issue.get('video_timecode'),
            project_id=project_id,
            source_type="manual",
            detection_method="drupal_import",
            created_at=created_at,
            updated_at=updated_at,
            drupal_issue_id=drupal_issue.get('drupal_issue_id'),
            drupal_uuid=drupal_issue['uuid'],
            drupal_nid=drupal_issue.get('drupal_nid'),
            drupal_sync_status=DrupalSyncStatus.SYNCED,
            drupal_last_synced=datetime.now()
        )

    def to_database_dict(self, drupal_issue: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Convert Drupal issue to database-ready dictionary.

        Args:
            drupal_issue: Parsed Drupal issue dict
            project_id: Project ID to associate with

        Returns:
            Dictionary ready for MongoDB insertion
        """
        issue = self.convert_to_issue_model(drupal_issue, project_id)
        return issue.to_dict()
