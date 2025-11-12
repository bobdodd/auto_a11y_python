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

    def __init__(self, client, taxonomy_cache=None):
        """
        Initialize issue exporter.

        Args:
            client: DrupalJSONAPIClient instance
            taxonomy_cache: Optional TaxonomyCache instance for taxonomy lookups
        """
        self.client = client
        self.taxonomy_cache = taxonomy_cache

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

    def export_from_recording_issue(self, recording_issue, audit_uuid: str, video_uuid: Optional[str] = None) -> Dict[str, Any]:
        """
        Export an issue from a RecordingIssue model instance.

        Args:
            recording_issue: RecordingIssue model instance
            audit_uuid: Drupal audit UUID to link to
            video_uuid: Optional Drupal audit_video UUID to link to

        Returns:
            Dict with 'success', 'uuid', and optional 'error' keys
        """
        import html

        # Map impact enum to Drupal format
        impact_mapping = {
            'low': 'low',
            'medium': 'med',
            'high': 'high'
        }
        impact = impact_mapping.get(recording_issue.impact.value, 'med')

        # Build description HTML from what/why/who/remediation
        description_parts = []
        if recording_issue.what:
            description_parts.append(f"<h3>What</h3><p>{html.escape(recording_issue.what)}</p>")
        if recording_issue.why:
            description_parts.append(f"<h3>Why</h3><p>{html.escape(recording_issue.why)}</p>")
        if recording_issue.who:
            description_parts.append(f"<h3>Who</h3><p>{html.escape(recording_issue.who)}</p>")
        if recording_issue.remediation:
            description_parts.append(f"<h3>Remediation</h3><p>{html.escape(recording_issue.remediation)}</p>")

        description = "\n".join(description_parts) if description_parts else recording_issue.what or ""

        # Convert timecodes to video_timecode string
        video_timecode = None
        if recording_issue.timecodes:
            timecode_strs = [f"{tc.start} - {tc.end}" for tc in recording_issue.timecodes]
            video_timecode = "; ".join(timecode_strs)

        # Extract WCAG criteria strings
        wcag_criteria = [w.criteria for w in recording_issue.wcag]

        # Get first page URL if available
        url = recording_issue.page_urls[0] if recording_issue.page_urls else None

        return self.export_issue(
            title=recording_issue.title,
            description=description,
            audit_uuid=audit_uuid,
            impact=impact,
            issue_type=recording_issue.touchpoint,
            location_on_page=None,  # RecordingIssue doesn't have this field
            wcag_criteria=wcag_criteria,
            xpath=recording_issue.xpath,
            url=url,
            video_timecode=video_timecode,
            issue_id=None,
            existing_uuid=None  # RecordingIssues don't track Drupal UUIDs currently
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

        # field_video_timecode has 8-char limit, so extract just start time in MM:SS format
        if video_timecode:
            # Extract first timecode (format: "HH:MM:SS.mmm - HH:MM:SS.mmm")
            # Convert to MM:SS format (max 8 chars with colon)
            try:
                start_time = video_timecode.split(' - ')[0]  # Get start time
                # Parse HH:MM:SS.mmm
                parts = start_time.split(':')
                if len(parts) >= 3:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = int(parts[2].split('.')[0])
                    # Convert to total minutes:seconds
                    total_minutes = hours * 60 + minutes
                    formatted_time = f"{total_minutes}:{seconds:02d}"
                    # Truncate to 8 chars if needed
                    attributes['field_video_timecode'] = formatted_time[:8]
                else:
                    # Fallback: just take first 8 chars
                    attributes['field_video_timecode'] = video_timecode[:8]
            except Exception as e:
                logger.warning(f"Failed to parse video_timecode '{video_timecode}': {e}")
                # Fallback: take first 8 chars
                attributes['field_video_timecode'] = video_timecode[:8]

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

        # Add ticket_status taxonomy term (required field)
        if self.taxonomy_cache:
            try:
                status_uuid = self.taxonomy_cache.get_uuid_by_name('ticket_status', 'open')
                if status_uuid:
                    relationships['field_ticket_status'] = {
                        'data': {
                            'type': 'taxonomy_term--ticket_status',
                            'id': status_uuid
                        }
                    }
                else:
                    logger.warning("Could not find 'open' term in ticket_status vocabulary")
            except Exception as e:
                logger.error(f"Error looking up ticket_status taxonomy: {e}")

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
