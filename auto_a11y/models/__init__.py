"""
Database models for Auto A11y Python
"""

from .project import Project, ProjectStatus
from .website import Website, ScrapingConfig
from .page import Page, PageStatus
from .test_result import TestResult, Violation, AIFinding, ImpactLevel
from .document_reference import DocumentReference, DocumentType
from .discovery_run import DiscoveryRun, DiscoveryStatus
from .page_setup_script import (
    PageSetupScript, ScriptStep, ScriptValidation, ExecutionStats,
    ActionType, ScriptScope, ExecutionTrigger,
    ScriptExecutionSession, ScriptExecutionRecord, ConditionCheck,
    PageTestState
)
from .website_user import WebsiteUser, LoginConfig, AuthenticationMethod

__all__ = [
    'Project', 'ProjectStatus',
    'Website', 'ScrapingConfig',
    'Page', 'PageStatus',
    'TestResult', 'Violation', 'AIFinding', 'ImpactLevel',
    'DocumentReference', 'DocumentType',
    'DiscoveryRun', 'DiscoveryStatus',
    'PageSetupScript', 'ScriptStep', 'ScriptValidation', 'ExecutionStats',
    'ActionType', 'ScriptScope', 'ExecutionTrigger',
    'ScriptExecutionSession', 'ScriptExecutionRecord', 'ConditionCheck',
    'PageTestState',
    'WebsiteUser', 'LoginConfig', 'AuthenticationMethod'
]