"""
Drupal JSON:API integration module.

This module provides connectivity to Drupal 10 sites via the JSON:API interface,
enabling export of accessibility test results and recording issues.
"""

from .client import DrupalJSONAPIClient
from .formatters import format_recording_body, format_issue_body
from .taxonomy import TaxonomyCache, DiscoveredPageTaxonomies
from .discovered_page_exporter import DiscoveredPageExporter
from .discovered_page_importer import DiscoveredPageImporter
from .recording_exporter import RecordingExporter
from .issue_importer import IssueImporter
from .issue_exporter import IssueExporter

__all__ = [
    'DrupalJSONAPIClient',
    'format_recording_body',
    'format_issue_body',
    'TaxonomyCache',
    'DiscoveredPageTaxonomies',
    'DiscoveredPageExporter',
    'DiscoveredPageImporter',
    'RecordingExporter',
    'IssueImporter',
    'IssueExporter'
]
