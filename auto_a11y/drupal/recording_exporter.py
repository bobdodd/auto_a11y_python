"""
Recording Exporter

Handles exporting Audio/Video recordings from Auto A11y to Drupal as audit_video nodes.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class RecordingExporter:
    """
    Export recordings to Drupal as audit_video nodes.

    Handles creating and updating audit_video content in Drupal,
    including file references and metadata.
    """

    def __init__(self, client):
        """
        Initialize exporter.

        Args:
            client: DrupalJSONAPIClient instance
        """
        self.client = client

    def export_recording(
        self,
        title: str,
        description: Optional[str],
        audit_uuid: str,
        media_url: Optional[str] = None,
        duration: Optional[str] = None,
        auditor_name: Optional[str] = None,
        auditor_role: Optional[str] = None,
        recording_date: Optional[datetime] = None,
        existing_uuid: Optional[str] = None,
        discovered_page_uuids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Export a recording to Drupal as audit_video.

        Args:
            title: Video title
            description: Video description
            audit_uuid: UUID of parent audit in Drupal
            media_url: URL to video file (if publicly accessible)
            duration: Video duration (HH:MM:SS format)
            auditor_name: Name of auditor
            auditor_role: Role of auditor (e.g., "Screen Reader User")
            recording_date: Date recording was made
            existing_uuid: If provided, UPDATE existing video instead of creating new
            discovered_page_uuids: List of discovered page Drupal UUIDs to link

        Returns:
            Dict with 'success', 'uuid', 'nid', and optional 'error' keys

        Raises:
            Exception: If export fails
        """
        try:
            # Build the JSON:API payload
            payload = self._build_payload(
                title=title,
                description=description,
                audit_uuid=audit_uuid,
                media_url=media_url,
                duration=duration,
                auditor_name=auditor_name,
                auditor_role=auditor_role,
                recording_date=recording_date,
                existing_uuid=existing_uuid,
                discovered_page_uuids=discovered_page_uuids
            )

            # Create or update
            if existing_uuid:
                # Verify the entity exists before attempting PATCH
                try:
                    logger.info(f"Checking if audit_video exists (UUID: {existing_uuid})")
                    self.client.get(f"node/audit_video/{existing_uuid}")
                    logger.info(f"Updating audit_video '{title}' (UUID: {existing_uuid})")
                    response = self.client.patch("node/audit_video", existing_uuid, payload)
                except Exception as e:
                    # Entity doesn't exist, create new instead
                    logger.warning(f"audit_video UUID {existing_uuid} not found in Drupal, creating new: {e}")
                    response = self.client.post("node/audit_video", payload)
            else:
                logger.info(f"Creating audit_video '{title}'")
                response = self.client.post("node/audit_video", payload)

            # Extract result
            data = response.get('data', {})
            uuid = data.get('id')
            nid = data.get('attributes', {}).get('drupal_internal__nid')

            logger.info(f"Successfully exported audit_video: UUID={uuid}, NID={nid}")

            return {
                'success': True,
                'uuid': uuid,
                'nid': nid,
                'response': data
            }

        except Exception as e:
            logger.error(f"Failed to export audit_video '{title}': {e}")

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

    def export_from_recording_model(self, recording, audit_uuid: str, discovered_page_uuids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export an audit_video from a Recording model instance.

        Args:
            recording: Recording model instance
            audit_uuid: Drupal audit UUID to link to
            discovered_page_uuids: Optional list of discovered page Drupal UUIDs to link (if not provided, will not link any discovered pages)

        Returns:
            Dict with 'success', 'uuid', and optional 'error' keys
        """
        # Build description HTML from recording details
        html_parts = []

        # Basic description
        if recording.description:
            html_parts.append(f"<p>{self._escape_html(recording.description)}</p>")

        # Task and component info
        if recording.task_description:
            html_parts.append(f"<p><strong>Task:</strong> {self._escape_html(recording.task_description)}</p>")

        if recording.component_names:
            html_parts.append(f"<p><strong>Components:</strong> {self._escape_html(', '.join(recording.component_names))}</p>")

        if recording.page_urls:
            html_parts.append(f"<p><strong>Pages tested:</strong> {len(recording.page_urls)}</p>")

        # Auditor metadata (since we can't use separate fields)
        metadata_parts = []
        if recording.auditor_name:
            metadata_parts.append(f"<strong>Auditor:</strong> {self._escape_html(recording.auditor_name)}")
        if recording.auditor_role:
            metadata_parts.append(f"<strong>Role:</strong> {self._escape_html(recording.auditor_role)}")
        if recording.duration:
            metadata_parts.append(f"<strong>Duration:</strong> {self._escape_html(recording.duration)}")
        if recording.recorded_date:
            metadata_parts.append(f"<strong>Date:</strong> {recording.recorded_date.strftime('%Y-%m-%d')}")

        if metadata_parts:
            html_parts.append(f"<p>{' | '.join(metadata_parts)}</p>")

        # Add key takeaways, painpoints, and assertions as HTML sections (English only)
        # Note: French translations exist in the database but are not uploaded to Drupal
        # See docs/DRUPAL_MULTILINGUAL_TRANSLATION_RESEARCH.md for details
        key_takeaways_en = recording.get_key_takeaways('en')
        user_painpoints_en = recording.get_user_painpoints('en')
        user_assertions_en = recording.get_user_assertions('en')

        logger.info(f"Recording has {len(key_takeaways_en)} key takeaways, {len(user_painpoints_en)} painpoints, {len(user_assertions_en)} assertions (uploading English only)")

        # Generate English sections only
        key_takeaways_html = self._generate_key_takeaways_html(key_takeaways_en, language='en')
        if key_takeaways_html:
            logger.info(f"Generated key takeaways HTML: {len(key_takeaways_html)} chars")
            html_parts.append(key_takeaways_html)

        painpoints_html = self._generate_user_painpoints_html(user_painpoints_en, language='en')
        if painpoints_html:
            logger.info(f"Generated painpoints HTML: {len(painpoints_html)} chars")
            html_parts.append(painpoints_html)

        assertions_html = self._generate_user_assertions_html(user_assertions_en, language='en')
        if assertions_html:
            logger.info(f"Generated assertions HTML: {len(assertions_html)} chars")
            html_parts.append(assertions_html)

        description = "\n".join(html_parts) if html_parts else None

        return self.export_recording(
            title=recording.title,
            description=description,
            audit_uuid=audit_uuid,
            duration=recording.duration,
            auditor_name=recording.auditor_name,
            auditor_role=recording.auditor_role,
            recording_date=recording.recorded_date,
            existing_uuid=recording.drupal_video_uuid,
            discovered_page_uuids=discovered_page_uuids
        )

    def batch_export(
        self,
        recordings: List[Any],
        audit_uuid: str,
        continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Export multiple recordings in batch.

        Args:
            recordings: List of Recording model instances
            audit_uuid: Drupal audit UUID to link to
            continue_on_error: Whether to continue if individual exports fail

        Returns:
            Dict with 'total', 'success_count', 'failure_count', 'results' keys
        """
        results = []
        success_count = 0
        failure_count = 0

        for i, recording in enumerate(recordings):
            logger.info(f"Exporting recording {i+1}/{len(recordings)}: {recording.title}")

            try:
                result = self.export_from_recording_model(recording, audit_uuid)
                results.append(result)

                if result.get('success'):
                    success_count += 1
                else:
                    failure_count += 1

            except Exception as e:
                logger.error(f"Unexpected error exporting recording: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'recording_title': recording.title
                })
                failure_count += 1

                if not continue_on_error:
                    break

        return {
            'total': len(recordings),
            'success_count': success_count,
            'failure_count': failure_count,
            'results': results
        }

    def _build_payload(
        self,
        title: str,
        description: Optional[str],
        audit_uuid: str,
        media_url: Optional[str],
        duration: Optional[str],
        auditor_name: Optional[str],
        auditor_role: Optional[str],
        recording_date: Optional[datetime],
        existing_uuid: Optional[str] = None,
        discovered_page_uuids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Build JSON:API payload for audit_video.

        Args:
            title: Video title
            description: Video description
            audit_uuid: Parent audit UUID
            media_url: Video file URL
            duration: Duration string
            auditor_name: Auditor name
            auditor_role: Auditor role
            recording_date: Recording date
            existing_uuid: UUID if updating existing entity
            discovered_page_uuids: List of discovered page Drupal UUIDs to link

        Returns:
            JSON:API payload dict
        """
        # Build attributes
        attributes = {
            'title': title
        }

        # Add description/body if provided
        # Note: description is expected to already be HTML from export_from_recording_model
        if description:
            attributes['body'] = {
                'value': description,
                'format': 'unfiltered'
            }

        # Note: The following fields are NOT in the current Drupal audit_video schema:
        # - field_video_duration
        # - field_auditor_name
        # - field_auditor_role
        # - field_recording_date
        # TODO: Add these fields to Drupal or store this metadata elsewhere (e.g., in body/description)
        #
        # If needed, auditor info and recording date can be included in the description/body field above

        # Build relationships
        # Note: The relationship field is 'field_audit', not 'field_parent_audit'
        relationships = {
            'field_audit': {
                'data': {
                    'type': 'node--audit',
                    'id': audit_uuid
                }
            }
        }

        # Add discovered pages relationship if provided
        if discovered_page_uuids:
            relationships['field_discovered_pages'] = {
                'data': [
                    {
                        'type': 'node--discovered_page',
                        'id': page_uuid
                    }
                    for page_uuid in discovered_page_uuids
                ]
            }

        # Build data section
        data = {
            'type': 'node--audit_video',
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

    def validate_export_data(
        self,
        title: str,
        audit_uuid: str
    ) -> Dict[str, Any]:
        """
        Validate data before export.

        Args:
            title: Video title
            audit_uuid: Audit UUID

        Returns:
            Dict with 'valid', 'errors', 'warnings' keys
        """
        errors = []
        warnings = []

        # Check required fields
        if not title:
            errors.append("Title is required")

        if not audit_uuid:
            errors.append("Audit UUID is required")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        import html
        return html.escape(text)

    def _generate_key_takeaways_html(self, key_takeaways: list, language: str = 'en') -> str:
        """
        Generate HTML for key takeaways.

        Args:
            key_takeaways: List of dicts with 'number', 'topic', 'description'
            language: Language code (currently only 'en' is used)

        Returns:
            HTML string
        """
        if not key_takeaways:
            return ""

        html_parts = [f"<h3>Key Takeaways</h3>"]

        for item in key_takeaways:
            number = item.get('number', '')
            topic = self._escape_html(item.get('topic', ''))
            description = self._escape_html(item.get('description', ''))

            html_parts.append(f"<h4>{number}. {topic}</h4>")
            html_parts.append(f"<p>{description}</p>")

        return "\n".join(html_parts)

    def _generate_user_painpoints_html(self, painpoints: list, language: str = 'en') -> str:
        """
        Generate HTML for user painpoints.

        Args:
            painpoints: List of dicts with 'title', 'user_quote', 'timecodes'
            language: Language code (currently only 'en' is used)

        Returns:
            HTML string
        """
        if not painpoints:
            return ""

        html_parts = [f"<h3>User Painpoints</h3>"]

        for item in painpoints:
            title = self._escape_html(item.get('title', ''))
            user_quote = self._escape_html(item.get('user_quote', ''))
            timecodes = item.get('timecodes', [])

            html_parts.append(f"<h4>{title}</h4>")
            html_parts.append(f"<h5>User Statement</h5>")
            html_parts.append(f'<p>"{user_quote}"</p>')

            # Add timecode locations
            if timecodes:
                if len(timecodes) == 1:
                    tc = timecodes[0]
                    html_parts.append(f"<h5>Location</h5>")
                    html_parts.append(f"<p>Start: {tc.get('start', '')}<br>")
                    html_parts.append(f"End: {tc.get('end', '')}<br>")
                    html_parts.append(f"Duration: {tc.get('duration', '')}</p>")
                else:
                    for i, tc in enumerate(timecodes, 1):
                        html_parts.append(f"<h5>Location {i}</h5>")
                        html_parts.append(f"<p>Start: {tc.get('start', '')}<br>")
                        html_parts.append(f"End: {tc.get('end', '')}<br>")
                        html_parts.append(f"Duration: {tc.get('duration', '')}</p>")

        return "\n".join(html_parts)

    def _generate_user_assertions_html(self, assertions: list, language: str = 'en') -> str:
        """
        Generate HTML for user assertions.

        Args:
            assertions: List of dicts with 'number', 'assertion', 'user_quote', 'timecodes', 'context'
            language: Language code (currently only 'en' is used)

        Returns:
            HTML string
        """
        if not assertions:
            return ""

        html_parts = [f"<h3>User Assertions</h3>"]

        for item in assertions:
            number = item.get('number', '')
            assertion = self._escape_html(item.get('assertion', ''))
            user_quote = self._escape_html(item.get('user_quote', ''))
            timecodes = item.get('timecodes', [])

            html_parts.append(f"<h4>{number}. {assertion}</h4>")
            html_parts.append(f"<h5>Text Spoken</h5>")
            html_parts.append(f'<p>"{user_quote}"</p>')

            # Add timecode information
            if timecodes:
                tc = timecodes[0] if timecodes else {}
                html_parts.append(f"<h5>Start Time</h5>")
                html_parts.append(f"<p>{tc.get('start', '')}</p>")
                html_parts.append(f"<h5>End Time</h5>")
                html_parts.append(f"<p>{tc.get('end', '')}</p>")
                html_parts.append(f"<h5>Duration</h5>")
                html_parts.append(f"<p>{tc.get('duration', '')}</p>")

        return "\n".join(html_parts)
