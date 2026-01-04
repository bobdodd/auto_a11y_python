"""
Database models for Auto A11y Python
"""

from .project import Project, ProjectStatus, ProjectType, LivedExperienceTester, TestSupervisor
from .website import Website, ScrapingConfig
from .page import Page, PageStatus, DrupalSyncStatus
from .test_result import TestResult, Violation, AIFinding, ImpactLevel
from .document_reference import DocumentReference, DocumentType
from .discovery_run import DiscoveryRun, DiscoveryStatus
from .page_setup_script import (
    PageSetupScript, ScriptStep, ScriptValidation, ExecutionStats,
    ActionType, ScriptScope, ExecutionTrigger,
    ScriptExecutionSession, ScriptExecutionRecord, ConditionCheck,
    PageTestState
)
from .test_state_matrix import (
    TestStateMatrix, ScriptStateDefinition, StateCombination
)
from .website_user import WebsiteUser, LoginConfig, AuthenticationMethod
from .project_user import ProjectUser
from .recording import Recording, RecordingType, Timecode, WCAGReference
from .recording_issue import RecordingIssue
from .discovered_page import DiscoveredPage
from .issue import Issue
from .app_user import AppUser, UserRole

__all__ = [
    'Project', 'ProjectStatus', 'ProjectType', 'LivedExperienceTester', 'TestSupervisor',
    'Website', 'ScrapingConfig',
    'Page', 'PageStatus', 'DrupalSyncStatus',
    'TestResult', 'Violation', 'AIFinding', 'ImpactLevel',
    'DocumentReference', 'DocumentType',
    'DiscoveryRun', 'DiscoveryStatus',
    'PageSetupScript', 'ScriptStep', 'ScriptValidation', 'ExecutionStats',
    'ActionType', 'ScriptScope', 'ExecutionTrigger',
    'ScriptExecutionSession', 'ScriptExecutionRecord', 'ConditionCheck',
    'PageTestState',
    'TestStateMatrix', 'ScriptStateDefinition', 'StateCombination',
    'WebsiteUser', 'LoginConfig', 'AuthenticationMethod',
    'ProjectUser',
    'Recording', 'RecordingType', 'Timecode', 'WCAGReference',
    'RecordingIssue',
    'DiscoveredPage',
    'Issue',
    'AppUser', 'UserRole'
]