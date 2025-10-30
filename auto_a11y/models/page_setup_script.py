"""
Page setup script model for interactive page training
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Set
from enum import Enum
from bson import ObjectId
import uuid


class ScriptScope(Enum):
    """Where the script is configured and executed"""
    WEBSITE = "website"      # Associated with website, runs once per session
    PAGE = "page"            # Associated with specific page, runs every test
    TEST_RUN = "test_run"    # Associated with test batch


class ExecutionTrigger(Enum):
    """When the script should execute"""
    ONCE_PER_SESSION = "once_per_session"     # Run once for entire test session
    ONCE_PER_PAGE = "once_per_page"           # Run every time page is tested
    CONDITIONAL = "conditional"                # Run only if condition selector exists
    ALWAYS = "always"                          # Run unconditionally


class ActionType(Enum):
    """Action types for page setup scripts"""
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    WAIT_FOR_SELECTOR = "wait_for_selector"
    WAIT_FOR_NAVIGATION = "wait_for_navigation"
    WAIT_FOR_NETWORK_IDLE = "wait_for_network_idle"
    SCROLL = "scroll"
    SELECT = "select"
    HOVER = "hover"
    SCREENSHOT = "screenshot"


@dataclass
class ScriptStep:
    """Single step in a page setup script"""

    step_number: int
    action_type: ActionType
    description: str
    selector: Optional[str] = None
    value: Optional[str] = None  # For type, select actions or wait duration
    timeout: int = 5000  # milliseconds
    wait_after: int = 0  # milliseconds to wait after action
    screenshot_after: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'step_number': self.step_number,
            'action_type': self.action_type.value,
            'description': self.description,
            'selector': self.selector,
            'value': self.value,
            'timeout': self.timeout,
            'wait_after': self.wait_after,
            'screenshot_after': self.screenshot_after
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScriptStep':
        """Create from dictionary"""
        return cls(
            step_number=data['step_number'],
            action_type=ActionType(data['action_type']),
            description=data['description'],
            selector=data.get('selector'),
            value=data.get('value'),
            timeout=data.get('timeout', 5000),
            wait_after=data.get('wait_after', 0),
            screenshot_after=data.get('screenshot_after', False)
        )


@dataclass
class ScriptValidation:
    """Validation rules for script execution"""

    success_selector: Optional[str] = None
    success_text: Optional[str] = None
    failure_selectors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'success_selector': self.success_selector,
            'success_text': self.success_text,
            'failure_selectors': self.failure_selectors
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScriptValidation':
        """Create from dictionary"""
        return cls(
            success_selector=data.get('success_selector'),
            success_text=data.get('success_text'),
            failure_selectors=data.get('failure_selectors', [])
        )


@dataclass
class ExecutionStats:
    """Statistics for script execution"""

    last_executed: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    average_duration_ms: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'last_executed': self.last_executed,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'average_duration_ms': self.average_duration_ms
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ExecutionStats':
        """Create from dictionary"""
        return cls(
            last_executed=data.get('last_executed'),
            success_count=data.get('success_count', 0),
            failure_count=data.get('failure_count', 0),
            average_duration_ms=data.get('average_duration_ms', 0)
        )


@dataclass
class PageSetupScript:
    """Page setup script for interactive training"""

    name: str
    description: str

    # NEW: Scope configuration (where script is associated)
    scope: ScriptScope = ScriptScope.PAGE
    website_id: Optional[str] = None      # Required if scope=WEBSITE or TEST_RUN
    page_id: Optional[str] = None         # Required if scope=PAGE
    test_run_id: Optional[str] = None     # Required if scope=TEST_RUN

    # NEW: Execution configuration (when script runs)
    trigger: ExecutionTrigger = ExecutionTrigger.ONCE_PER_PAGE
    condition_selector: Optional[str] = None   # Required if trigger=CONDITIONAL

    # NEW: Violation detection
    report_violation_if_condition_met: bool = False
    violation_message: Optional[str] = None
    violation_code: Optional[str] = None

    # NEW: Multi-state testing configuration
    test_before_execution: bool = False  # Test page BEFORE running script
    test_after_execution: bool = True    # Test page AFTER running script

    # NEW: Expected state changes after execution
    expect_visible_after: List[str] = field(default_factory=list)   # Selectors that should become visible
    expect_hidden_after: List[str] = field(default_factory=list)    # Selectors that should become hidden

    # Existing fields
    enabled: bool = True
    steps: List[ScriptStep] = field(default_factory=list)
    validation: Optional[ScriptValidation] = None
    created_by: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    execution_stats: ExecutionStats = field(default_factory=ExecutionStats)
    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        """Get script ID as string"""
        return str(self._id) if self._id else None

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'name': self.name,
            'description': self.description,
            # Scope configuration
            'scope': self.scope.value,
            'website_id': self.website_id,
            'page_id': self.page_id,
            'test_run_id': self.test_run_id,
            # Execution configuration
            'trigger': self.trigger.value,
            'condition_selector': self.condition_selector,
            # Violation detection
            'report_violation_if_condition_met': self.report_violation_if_condition_met,
            'violation_message': self.violation_message,
            'violation_code': self.violation_code,
            # Multi-state testing
            'test_before_execution': self.test_before_execution,
            'test_after_execution': self.test_after_execution,
            'expect_visible_after': self.expect_visible_after,
            'expect_hidden_after': self.expect_hidden_after,
            # Existing fields
            'enabled': self.enabled,
            'steps': [step.to_dict() for step in self.steps],
            'validation': self.validation.to_dict() if self.validation else None,
            'created_by': self.created_by,
            'created_date': self.created_date,
            'last_modified': self.last_modified,
            'execution_stats': self.execution_stats.to_dict()
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'PageSetupScript':
        """Create from MongoDB document"""
        return cls(
            name=data['name'],
            description=data['description'],
            # Scope configuration (with backward compatibility)
            scope=ScriptScope(data.get('scope', 'page')),
            website_id=data.get('website_id'),
            page_id=data.get('page_id'),
            test_run_id=data.get('test_run_id'),
            # Execution configuration (with backward compatibility)
            trigger=ExecutionTrigger(data.get('trigger', 'once_per_page')),
            condition_selector=data.get('condition_selector'),
            # Violation detection (default False for backward compatibility)
            report_violation_if_condition_met=data.get('report_violation_if_condition_met', False),
            violation_message=data.get('violation_message'),
            violation_code=data.get('violation_code'),
            # Multi-state testing (defaults for backward compatibility)
            test_before_execution=data.get('test_before_execution', False),
            test_after_execution=data.get('test_after_execution', True),
            expect_visible_after=data.get('expect_visible_after', []),
            expect_hidden_after=data.get('expect_hidden_after', []),
            # Existing fields
            enabled=data.get('enabled', True),
            steps=[ScriptStep.from_dict(step) for step in data.get('steps', [])],
            validation=ScriptValidation.from_dict(data['validation']) if data.get('validation') else None,
            created_by=data.get('created_by'),
            created_date=data.get('created_date', datetime.now()),
            last_modified=data.get('last_modified', datetime.now()),
            execution_stats=ExecutionStats.from_dict(data.get('execution_stats', {})),
            _id=data.get('_id')
        )

    def update_timestamp(self):
        """Update the last_modified timestamp"""
        self.last_modified = datetime.now()


@dataclass
class ScriptExecutionRecord:
    """Record of a single script execution"""

    script_id: str
    executed_at: datetime
    page_id: str
    success: bool
    duration_ms: int

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'script_id': self.script_id,
            'executed_at': self.executed_at,
            'page_id': self.page_id,
            'success': self.success,
            'duration_ms': self.duration_ms
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScriptExecutionRecord':
        """Create from dictionary"""
        return cls(
            script_id=data['script_id'],
            executed_at=data['executed_at'],
            page_id=data['page_id'],
            success=data['success'],
            duration_ms=data['duration_ms']
        )


@dataclass
class ConditionCheck:
    """Record of a condition check for violation detection"""

    script_id: str
    page_id: str
    checked_at: datetime
    condition_selector: str
    condition_met: bool
    violation_reported: bool

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'script_id': self.script_id,
            'page_id': self.page_id,
            'checked_at': self.checked_at,
            'condition_selector': self.condition_selector,
            'condition_met': self.condition_met,
            'violation_reported': self.violation_reported
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ConditionCheck':
        """Create from dictionary"""
        return cls(
            script_id=data['script_id'],
            page_id=data['page_id'],
            checked_at=data['checked_at'],
            condition_selector=data['condition_selector'],
            condition_met=data['condition_met'],
            violation_reported=data['violation_reported']
        )


@dataclass
class PageTestState:
    """Represents the state of a page during testing"""

    state_id: str
    description: str

    # Scripts executed to reach this state
    scripts_executed: List[str] = field(default_factory=list)  # Script IDs

    # Buttons/elements clicked to reach this state
    elements_clicked: List[Dict[str, Any]] = field(default_factory=list)  # [{selector, description, timestamp}]

    # Expected conditions
    elements_visible: List[str] = field(default_factory=list)   # Selectors that should be visible
    elements_hidden: List[str] = field(default_factory=list)    # Selectors that should be hidden

    # Timestamp
    captured_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'state_id': self.state_id,
            'description': self.description,
            'scripts_executed': self.scripts_executed,
            'elements_clicked': self.elements_clicked,
            'elements_visible': self.elements_visible,
            'elements_hidden': self.elements_hidden,
            'captured_at': self.captured_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PageTestState':
        """Create from dictionary"""
        return cls(
            state_id=data['state_id'],
            description=data['description'],
            scripts_executed=data.get('scripts_executed', []),
            elements_clicked=data.get('elements_clicked', []),
            elements_visible=data.get('elements_visible', []),
            elements_hidden=data.get('elements_hidden', []),
            captured_at=data.get('captured_at', datetime.now())
        )


@dataclass
class ScriptExecutionSession:
    """Tracks script execution state for a test session"""

    session_id: str
    website_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    executed_scripts: List[ScriptExecutionRecord] = field(default_factory=list)
    condition_checks: List[ConditionCheck] = field(default_factory=list)
    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        """Get session ID as string"""
        return str(self._id) if self._id else None

    def has_executed(self, script_id: str) -> bool:
        """Check if script has been executed in this session"""
        return any(record.script_id == script_id for record in self.executed_scripts)

    def add_execution_record(
        self,
        script_id: str,
        page_id: str,
        success: bool,
        duration_ms: int
    ):
        """Add an execution record"""
        record = ScriptExecutionRecord(
            script_id=script_id,
            executed_at=datetime.now(),
            page_id=page_id,
            success=success,
            duration_ms=duration_ms
        )
        self.executed_scripts.append(record)

    def add_condition_check(
        self,
        script_id: str,
        page_id: str,
        condition_selector: str,
        condition_met: bool,
        violation_reported: bool
    ):
        """Add a condition check record"""
        check = ConditionCheck(
            script_id=script_id,
            page_id=page_id,
            checked_at=datetime.now(),
            condition_selector=condition_selector,
            condition_met=condition_met,
            violation_reported=violation_reported
        )
        self.condition_checks.append(check)

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'session_id': self.session_id,
            'website_id': self.website_id,
            'started_at': self.started_at,
            'ended_at': self.ended_at,
            'executed_scripts': [record.to_dict() for record in self.executed_scripts],
            'condition_checks': [check.to_dict() for check in self.condition_checks]
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'ScriptExecutionSession':
        """Create from MongoDB document"""
        return cls(
            session_id=data['session_id'],
            website_id=data['website_id'],
            started_at=data['started_at'],
            ended_at=data.get('ended_at'),
            executed_scripts=[
                ScriptExecutionRecord.from_dict(record)
                for record in data.get('executed_scripts', [])
            ],
            condition_checks=[
                ConditionCheck.from_dict(check)
                for check in data.get('condition_checks', [])
            ],
            _id=data.get('_id')
        )
