"""
Drupal Issue Exporter

Handles exporting issues from Auto A11y to Drupal via JSON:API.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class IssueExporter:
    """
    Export issues to Drupal.

    Handles creating and updating issue nodes in Drupal from Auto A11y Issue objects.
    """

    def __init__(self, client):
        """
        Initialize issue exporter.

        Args:
            client: DrupalJSONAPIClient instance
        """
        self.client = client

    def export_issue(
        self,
        title: str,
        description: str,
        audit_uuid: str,
        impact: str = "med",
        issue_type: Optional[str] = None,
        location_on_page: Optional[str] = None,
        wcag_criteria: Optional[List[str]] = None,
        xpath: Optional[str] = None,
        url: Optional[str] = None,
        video_timecode: Optional[str] = None,
        issue_id: Optional[int] = None,
        existing_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export an issue to Drupal.

        Args:
            title: Issue title
            description: Issue description (HTML)
            audit_uuid: Parent audit UUID
            impact: Impact level ("low", "med", "high")
            issue_type: Issue type taxonomy term name
            location_on_page: Location taxonomy term name
            wcag_criteria: List of WCAG criteria (e.g., ["1.3.1", "2.4.6"])
            xpath: XPath selector
            url: Related URL
            video_timecode: Video timecode string
            issue_id: Numeric issue ID (field_id)
            existing_uuid: If provided, UPDATE existing issue instead of creating new

        Returns:
            Dict with 'success', 'uuid', 'nid', and optional 'error' keys
        """
        try:
            # Build the JSON:API payload
            payload = self._build_payload(
                title=title,
                description=description,
                audit_uuid=audit_uuid,
                impact=impact,
                issue_type=issue_type,
                location_on_page=location_on_page,
                wcag_criteria=wcag_criteria or [],
                xpath=xpath,
                url=url,
                video_timecode=video_timecode,
                issue_id=issue_id,
                existing_uuid=existing_uuid
            )

            # Create or update
            if existing_uuid:
                # Verify the entity exists before attempting PATCH
                try:
                    logger.info(f"Checking if issue exists (UUID: {existing_uuid})")
                    self.client.get(f"node/issue/{existing_uuid}")
                    logger.info(f"Updating issue '{title}' (UUID: {existing_uuid})")
                    response = self.client.patch("node/issue", existing_uuid, payload)
                except Exception as e:
                    # Entity doesn't exist, create new instead
                    logger.warning(f"issue UUID {existing_uuid} not found in Drupal, creating new: {e}")
                    response = self.client.post("node/issue", payload)
            else:
                logger.info(f"Creating issue '{title}'")
                response = self.client.post("node/issue", payload)

            # Extract result
            data = response.get('data', {})
            uuid = data.get('id')
            nid = data.get('attributes', {}).get('drupal_internal__nid')

            logger.info(f"Successfully exported issue: UUID={uuid}, NID={nid}")

            return {
                'success': True,
                'uuid': uuid,
                'nid': nid,
                'response': data
            }

        except Exception as e:
            logger.error(f"Failed to export issue '{title}': {e}")

            # Try to get detailed error from response
            error_detail = str(e)
            if hasattr(e, 'response'):
                try:
                    error_data = e.response.json()
                    if 'errors' in error_data:
                        error_messages = [err.get('detail', err.get('title', '')) for err in error_data['errors']]
                        error_detail = '; '.join(error_messages)
                except:
                    pass

            return {
                'success': False,
                'error': error_detail
            }

    def export_from_issue_model(self, issue, audit_uuid: str) -> Dict[str, Any]:
        """
        Export an issue from an Issue model instance.

        Args:
            issue: Issue model instance
            audit_uuid: Drupal audit UUID to link to

        Returns:
            Dict with 'success', 'uuid', and optional 'error' keys
        """
        # Map impact enum to Drupal format
        impact_mapping = {
            'low': 'low',
            'medium': 'med',
            'high': 'high'
        }
        impact = impact_mapping.get(issue.impact.value, 'med')

        return self.export_issue(
            title=issue.title,
            description=issue.description,
            audit_uuid=audit_uuid,
            impact=impact,
            issue_type=issue.issue_type,
            location_on_page=issue.location_on_page,
            wcag_criteria=issue.wcag_criteria,
            xpath=issue.xpath,
            url=issue.url,
            video_timecode=issue.video_timecode,
            issue_id=issue.drupal_issue_id,
            existing_uuid=issue.drupal_uuid
        )

    def _build_payload(
        self,
        title: str,
        description: str,
        audit_uuid: str,
        impact: str,
        issue_type: Optional[str],
        location_on_page: Optional[str],
        wcag_criteria: List[str],
        xpath: Optional[str],
        url: Optional[str],
        video_timecode: Optional[str],
        issue_id: Optional[int],
        existing_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build JSON:API payload for issue.

        Args:
            title: Issue title
            description: Issue description
            audit_uuid: Parent audit UUID
            impact: Impact level
            issue_type: Issue type term name
            location_on_page: Location term name
            wcag_criteria: List of WCAG criteria
            xpath: XPath
            url: URL
            video_timecode: Timecode
            issue_id: Numeric ID
            existing_uuid: UUID if updating

        Returns:
            JSON:API payload dict
        """
        # Build attributes
        attributes = {
            'title': title,
            'field_impact': impact
        }

        # Add description/body if provided
        if description:
            attributes['body'] = {
                'value': description,
                'format': 'formatted_text'
            }

        # Add optional fields
        if xpath:
            attributes['field_xpath'] = xpath

        if url:
            attributes['field_url'] = {
                'uri': url
            }

        if video_timecode:
            attributes['field_video_timecode'] = video_timecode

        if issue_id is not None:
            attributes['field_id'] = issue_id

        # Build relationships
        relationships = {
            'field_parent_audit': {
                'data': {
                    'type': 'node--audit',
                    'id': audit_uuid
                }
            }
        }

        # TODO: Add taxonomy term relationships for issue_type and location_on_page
        # This would require looking up taxonomy term UUIDs by name
        # For now, we'll skip these and they can be added later

        # TODO: Add WCAG chapter relationships
        # This would require looking up WCAG node UUIDs by criteria
        # For now, we'll skip these and they can be added later

        # Build data section
        data = {
            'type': 'node--issue',
            'attributes': attributes,
            'relationships': relationships
        }

        # For PATCH requests, must include the ID in the data section
        if existing_uuid:
            data['id'] = existing_uuid

        # Build final payload
        payload = {
            'data': data
        }

        return payload

    def batch_export(
        self,
        issues: List[Any],
        audit_uuid: str,
        continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Export multiple issues in batch.

        Args:
            issues: List of Issue model instances
            audit_uuid: Drupal audit UUID to link to
            continue_on_error: Whether to continue if individual exports fail

        Returns:
            Dict with 'total', 'success_count', 'failure_count', 'results' keys
        """
        results = []
        success_count = 0
        failure_count = 0

        for i, issue in enumerate(issues):
            logger.info(f"Exporting issue {i+1}/{len(issues)}: {issue.title}")

            try:
                result = self.export_from_issue_model(issue, audit_uuid)
                results.append(result)

                if result.get('success'):
                    success_count += 1
                else:
                    failure_count += 1

            except Exception as e:
                logger.error(f"Unexpected error exporting issue: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'issue_title': issue.title
                })
                failure_count += 1

                if not continue_on_error:
                    break

        return {
            'total': len(issues),
            'success_count': success_count,
            'failure_count': failure_count,
            'results': results
        }

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        import html
        return html.escape(text)
