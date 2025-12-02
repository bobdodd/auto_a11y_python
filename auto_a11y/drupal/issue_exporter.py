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

    def __init__(self, client, taxonomy_cache=None, wcag_cache=None):
        """
        Initialize issue exporter.

        Args:
            client: DrupalJSONAPIClient instance
            taxonomy_cache: Optional TaxonomyCache instance for taxonomy lookups
            wcag_cache: Optional WCAGChapterCache instance for WCAG chapter lookups
        """
        self.client = client
        self.taxonomy_cache = taxonomy_cache
        self.wcag_cache = wcag_cache

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
        existing_uuid: Optional[str] = None,
        video_uuid: Optional[str] = None,
        discovered_page_uuid: Optional[str] = None
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
            video_uuid: Optional Drupal audit_video UUID to link to
            discovered_page_uuid: Optional Drupal discovered_page UUID to link to

        Returns:
            Dict with 'success', 'uuid', 'nid', and optional 'error' keys
        """
        # Log what export_issue receives
        logger.warning(f"📥 EXPORT_ISSUE RECEIVED for '{title}':")
        logger.warning(f"   description parameter length: {len(description)} chars")
        logger.warning(f"   description parameter preview (first 200 chars): {description[:200]}")

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
                existing_uuid=existing_uuid,
                video_uuid=video_uuid,
                discovered_page_uuid=discovered_page_uuid
            )

            # Log the payload body field for debugging
            body_in_payload = payload.get('data', {}).get('attributes', {}).get('body')
            if body_in_payload:
                body_value = body_in_payload.get('value', '')
                logger.warning(f"🔍 PAYLOAD CHECK for '{title}': body field IS PRESENT in payload, value length={len(body_value)}, format={body_in_payload.get('format')}")
                logger.warning(f"📄 PAYLOAD BODY PREVIEW (first 500 chars):\n{body_value[:500]}")
            else:
                logger.warning(f"🔍 PAYLOAD CHECK for '{title}': body field is MISSING from payload!")

            # Create or update
            if existing_uuid:
                # Verify the entity exists before attempting PATCH
                try:
                    logger.info(f"Checking if issue exists (UUID: {existing_uuid})")
                    self.client.get(f"node/issue/{existing_uuid}")
                    logger.warning(f"🔧 Using PATCH to UPDATE issue '{title}' (UUID: {existing_uuid})")
                    response = self.client.patch("node/issue", existing_uuid, payload)
                except Exception as e:
                    # Entity doesn't exist, create new instead
                    logger.warning(f"issue UUID {existing_uuid} not found in Drupal, creating new: {e}")
                    logger.warning(f"🔧 Using POST to CREATE issue '{title}' (fallback from failed PATCH)")
                    response = self.client.post("node/issue", payload)
            else:
                logger.warning(f"🔧 Using POST to CREATE new issue '{title}'")
                response = self.client.post("node/issue", payload)

            # Extract result
            data = response.get('data', {})
            uuid = data.get('id')
            nid = data.get('attributes', {}).get('drupal_internal__nid')

            # Check if body field came back in the response
            response_body = data.get('attributes', {}).get('body')
            if response_body:
                logger.warning(f"🔍 RESPONSE CHECK for '{title}': body field IS PRESENT in Drupal response, value length={len(response_body.get('value', ''))}")
            else:
                logger.warning(f"🔍 RESPONSE CHECK for '{title}': body field is MISSING from Drupal response!")

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
        import html

        # Map impact enum to Drupal format
        impact_mapping = {
            'low': 'low',
            'medium': 'med',
            'high': 'high'
        }
        impact = impact_mapping.get(issue.impact.value, 'med')

        # Try to get enhanced descriptions if issue_code is available
        description = issue.description
        used_enhanced = False

        if hasattr(issue, 'issue_code') and issue.issue_code:
            try:
                from auto_a11y.reporting.issue_descriptions_translated import get_detailed_issue_description

                # Build metadata for contextual substitution
                metadata = {}
                if hasattr(issue, 'element') and issue.element:
                    metadata['element_text'] = issue.element
                if hasattr(issue, 'html') and issue.html:
                    # Try to extract tag name from HTML
                    import re
                    tag_match = re.match(r'<(\w+)', issue.html)
                    if tag_match:
                        metadata['element_tag'] = tag_match.group(1)

                enhanced = get_detailed_issue_description(issue.issue_code, metadata)

                if enhanced:
                    # Build enhanced description HTML
                    description_parts = []
                    if enhanced.get('what'):
                        description_parts.append(f"<h3>What the issue is</h3>\n<p>{html.escape(enhanced['what'])}</p>")
                    if enhanced.get('why'):
                        description_parts.append(f"<h3>Why it is important</h3>\n<p>{html.escape(enhanced['why'])}</p>")
                    if enhanced.get('who'):
                        description_parts.append(f"<h3>Who it affects</h3>\n<p>{html.escape(enhanced['who'])}</p>")
                    if enhanced.get('remediation'):
                        description_parts.append(f"<h3>How to remediate</h3>\n<p>{html.escape(enhanced['remediation'])}</p>")

                    if description_parts:
                        description = "\n".join(description_parts)
                        used_enhanced = True
                        logger.info(f"Using enhanced description for issue code: {issue.issue_code}")
            except Exception as e:
                logger.warning(f"Failed to get enhanced description for {issue.issue_code}: {e}")

        return self.export_issue(
            title=issue.title,
            description=description,
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

        # For RecordingIssues, ALWAYS use the detailed descriptions from the recording itself
        # These come from manual audits and lived experience testing with expert-crafted content
        description_parts = []

        logger.warning(f"🔍 RECORDING ISSUE '{recording_issue.title}': Checking fields...")
        logger.warning(f"   what: {'✓ Present' if recording_issue.what else '✗ Missing'} ({len(recording_issue.what) if recording_issue.what else 0} chars)")
        logger.warning(f"   why: {'✓ Present' if recording_issue.why else '✗ Missing'} ({len(recording_issue.why) if recording_issue.why else 0} chars)")
        logger.warning(f"   who: {'✓ Present' if recording_issue.who else '✗ Missing'} ({len(recording_issue.who) if recording_issue.who else 0} chars)")
        logger.warning(f"   remediation: {'✓ Present' if recording_issue.remediation else '✗ Missing'} ({len(recording_issue.remediation) if recording_issue.remediation else 0} chars)")

        if recording_issue.what:
            description_parts.append(f"<h3>What the issue is</h3>\n<p>{html.escape(recording_issue.what)}</p>")
        if recording_issue.why:
            description_parts.append(f"<h3>Why it is important</h3>\n<p>{html.escape(recording_issue.why)}</p>")
        if recording_issue.who:
            description_parts.append(f"<h3>Who it affects</h3>\n<p>{html.escape(recording_issue.who)}</p>")
        if recording_issue.remediation:
            description_parts.append(f"<h3>How to remediate</h3>\n<p>{html.escape(recording_issue.remediation)}</p>")

        description = "\n".join(description_parts) if description_parts else recording_issue.what or ""

        # Debug logging at WARNING level so it appears in Flask logs
        logger.warning(f"📦 Built description_parts list with {len(description_parts)} parts")
        if description:
            logger.warning(f"✓ RecordingIssue '{recording_issue.title}': Final description has {len(description)} chars")
            logger.warning(f"📄 DESCRIPTION CONTENT PREVIEW (first 500 chars):\n{description[:500]}")
        else:
            logger.warning(f"✗ RecordingIssue '{recording_issue.title}': Description is EMPTY!")

        # Convert timecodes to video_timecode string
        video_timecode = None
        if recording_issue.timecodes:
            timecode_strs = [f"{tc.start} - {tc.end}" for tc in recording_issue.timecodes]
            video_timecode = "; ".join(timecode_strs)

        # Extract WCAG criteria strings
        wcag_criteria = [w.criteria for w in recording_issue.wcag]

        # Get first page URL if available
        url = recording_issue.page_urls[0] if recording_issue.page_urls else None

        # Log the exact value being passed to export_issue
        logger.warning(f"🚀 CALLING export_issue() for '{recording_issue.title}':")
        logger.warning(f"   description parameter length: {len(description)} chars")
        logger.warning(f"   description parameter preview (first 200 chars): {description[:200]}")

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
            existing_uuid=recording_issue.drupal_uuid,  # Use existing UUID for updates
            video_uuid=video_uuid
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
        existing_uuid: Optional[str] = None,
        video_uuid: Optional[str] = None,
        discovered_page_uuid: Optional[str] = None
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
            'status': True  # Publish the issue by default
        }
        # Note: field_ticket_status omitted - all existing issues have null for this field

        # Add impact as simple string field (not a taxonomy reference)
        # Map internal values to Drupal values: "medium" → "med"
        if impact:
            impact_mapping = {
                'low': 'low',
                'medium': 'med',  # Drupal uses "med" not "medium"
                'high': 'high',
                'critical': 'critical'
            }
            drupal_impact = impact_mapping.get(impact.lower(), 'med')
            attributes['field_impact'] = drupal_impact
        else:
            attributes['field_impact'] = 'med'  # Default to medium

        # Add description/body (only include if present - body field accepts null but format is required)
        if description:
            attributes['body'] = {
                'value': description,
                'format': 'unfiltered'  # Use unfiltered format to allow HTML
            }
            logger.warning(f"✓ Issue '{title}': Setting body field with {len(description)} characters (format=unfiltered)")
        else:
            logger.warning(f"✗ Issue '{title}': NO DESCRIPTION - body field will be omitted!")

        # Add issue type text field - "WCAG" if WCAG criteria present, "NOT WCAG" otherwise
        if wcag_criteria:
            attributes['field_txt_issue_type'] = 'WCAG'
        else:
            attributes['field_txt_issue_type'] = 'NOT WCAG'

        # Add relevant test criteria text field (always include, may be empty)
        if wcag_criteria:
            attributes['field_txt_relevant_test_criteria'] = ', '.join(wcag_criteria)
        else:
            attributes['field_txt_relevant_test_criteria'] = None

        # Add issue category text field from issue_type (touchpoint) (always include)
        if issue_type:
            attributes['field_txt_issue_category'] = issue_type
        else:
            attributes['field_txt_issue_category'] = None

        # Add optional fields (always include for updates to clear removed values)
        # Simple text fields can be set to None to clear them
        attributes['field_xpath'] = xpath if xpath else None

        # URL field has special structure - only include if present, or set to None to clear
        if url:
            attributes['field_url'] = {
                'uri': url
            }
        else:
            # Set to None to clear the field on updates
            attributes['field_url'] = None

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
        else:
            attributes['field_video_timecode'] = None

        # field_id is required if present, so only add if we have a value
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

        # Add video relationship (always include for updates to clear if removed)
        if video_uuid:
            relationships['field_video'] = {
                'data': {
                    'type': 'node--audit_video',
                    'id': video_uuid
                }
            }
        else:
            relationships['field_video'] = {'data': None}

        # Add Issue Type taxonomy relationship (WCAG vs NOT WCAG)
        if self.taxonomy_cache:
            # Determine issue type based on WCAG criteria
            if wcag_criteria:
                issue_type_term = 'WCAG'
            else:
                # Default to 'Note' for non-WCAG issues
                issue_type_term = 'Note'

            issue_type_uuid = self.taxonomy_cache.get_uuid_by_name('issue_type', issue_type_term)
            if issue_type_uuid:
                relationships['field_issue_type'] = {
                    'data': {
                        'type': 'taxonomy_term--issue_type',
                        'id': issue_type_uuid
                    }
                }
            else:
                logger.warning(f"Could not find issue_type term '{issue_type_term}'")
                relationships['field_issue_type'] = {'data': None}
        else:
            relationships['field_issue_type'] = {'data': None}

        # Add Issue Category taxonomy relationship (from touchpoint/issue_type)
        if self.taxonomy_cache and issue_type:
            # Map touchpoint names to Drupal issue_category term names
            touchpoint_to_category = {
                'color contrast': 'Colour or Contrast',
                'colors': 'Colour or Contrast',  # Manual recording touchpoint
                'colour': 'Colour or Contrast',
                'landmarks': 'Page Regions',
                'navigation': 'Navigation or Multiple Ways',
                'forms': 'Forms',
                'headings': 'Headings or Titles',
                'links': 'Links or Buttons',
                'images': 'Images or Non-Text Content',
                'tables': 'Tables',
                'aria': 'ARIA',
                'focus': 'Focus or Keyboard',
                'keyboard': 'Focus or Keyboard',
                'search': 'Search or Filters',
                'text': 'Text or Font',
                'font': 'Text or Font',
                'typography': 'Text or Font',  # Manual recording touchpoint
                'html': 'HTML or Attribute',
                'language': 'Language',
                'labels': 'Label or Name',
                'accessible_names': 'Label or Name',
                'sequence': 'Sequence or Order',
                'modal': 'Modal Dialog',
                'status messages': 'Status Messages, Errors or Instructions',
                'errors': 'Status Messages, Errors or Instructions',
                'context': 'Change of Context',
                'pagination': 'Pagination',
                'tabs': 'Tabs',
                'lists': 'Lists',
                'timing': 'Timing',
                'menus': 'Menus',
                'iframes': 'IFrames',
                'breadcrumbs': 'Breadcrumbs',
                'accordions': 'Accordions',
                'carousels': 'Carousels',
                'motion': 'Motion or Animation',
                'animation': 'Motion or Animation',
                'magnifiers': 'Magnifiers',
                'audio': 'Audio',
                'skip links': 'Skip links',
                'reflow': 'Reflow, Resize or Text Spacing',
                'resize': 'Reflow, Resize or Text Spacing'
            }

            # Try to map touchpoint to category term name
            category_name = touchpoint_to_category.get(issue_type.lower(), issue_type)

            category_uuid = self.taxonomy_cache.get_uuid_by_name('issue_category', category_name)
            if category_uuid:
                relationships['field_issue_category'] = {
                    'data': {
                        'type': 'taxonomy_term--issue_category',
                        'id': category_uuid
                    }
                }
            else:
                logger.warning(f"Could not find issue_category term for touchpoint '{issue_type}' (tried '{category_name}')")
                relationships['field_issue_category'] = {'data': None}
        else:
            relationships['field_issue_category'] = {'data': None}

        # Add WCAG chapter relationships (field_wcag_chapter - multi-value reference to WCAG chapter nodes)
        if wcag_criteria:
            # Check if wcag_criteria are already UUIDs or need conversion
            # UUIDs are 36 chars with 4 dashes (e.g., "6d1519a5-730a-478d-99cf-97692df1d0bc")
            # WCAG criteria numbers are like "1.3.1", "2.4.6"
            if wcag_criteria and len(wcag_criteria[0]) == 36 and wcag_criteria[0].count('-') == 4:
                # Already UUIDs, use directly
                chapter_uuids = wcag_criteria
                logger.info(f"Using provided WCAG chapter UUIDs: {len(chapter_uuids)} chapters")
                relationships['field_wcag_chapter'] = {
                    'data': [
                        {'type': 'node--wcag_chapter', 'id': uuid}
                        for uuid in chapter_uuids
                    ]
                }
            elif self.wcag_cache:
                # WCAG criteria numbers, need to convert to UUIDs
                # Filter out non-standard criteria like "best practice"
                valid_criteria = [c for c in wcag_criteria if c and c[0].isdigit()]

                if valid_criteria:
                    chapter_uuids = self.wcag_cache.lookup_uuids(valid_criteria)
                    if chapter_uuids:
                        # Build multi-value relationship
                        relationships['field_wcag_chapter'] = {
                            'data': [
                                {'type': 'node--wcag_chapter', 'id': uuid}
                                for uuid in chapter_uuids
                            ]
                        }
                        logger.info(f"Linked {len(chapter_uuids)} WCAG chapters: {', '.join(valid_criteria)}")
                    else:
                        logger.warning(f"No WCAG chapter UUIDs found for criteria: {valid_criteria}")
                        relationships['field_wcag_chapter'] = {'data': []}
                else:
                    relationships['field_wcag_chapter'] = {'data': []}
            else:
                relationships['field_wcag_chapter'] = {'data': []}
        else:
            relationships['field_wcag_chapter'] = {'data': []}

        # Add Discovered Page relationship (for linking issues to discovered pages/components)
        if discovered_page_uuid:
            relationships['field_discovered_page_issue'] = {
                'data': {
                    'type': 'node--discovered_page',
                    'id': discovered_page_uuid
                }
            }
        else:
            relationships['field_discovered_page_issue'] = {'data': None}

        # Note: field_ticket_status has been removed from the staging Issue content type
        # (test-audits.pantheonsite.io) to allow issue creation via JSON:API.
        # The production site (audits.frontier-cnib.ca) still has the workflow field requirement.
        #
        # TODO: If workflow states are needed in the future:
        # - Investigate Drupal Workflow module's JSON:API integration
        # - Determine correct SID value format for field_ticket_status
        # - Add workflow state handling as optional parameter

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
