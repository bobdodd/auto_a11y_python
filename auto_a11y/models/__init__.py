"""
Database models for Auto A11y Python
"""

from .project import Project, ProjectStatus
from .website import Website, ScrapingConfig
from .page import Page, PageStatus
from .test_result import TestResult, Violation, AIFinding, ImpactLevel
from .document_reference import DocumentReference, DocumentType
from .discovery_run import DiscoveryRun, DiscoveryStatus

__all__ = [
    'Project', 'ProjectStatus',
    'Website', 'ScrapingConfig',
    'Page', 'PageStatus',
    'TestResult', 'Violation', 'AIFinding', 'ImpactLevel',
    'DocumentReference', 'DocumentType',
    'DiscoveryRun', 'DiscoveryStatus'
]