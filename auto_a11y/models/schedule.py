"""
TestSchedule model for scheduling automated accessibility tests
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from enum import Enum


class ScheduleType(Enum):
    """Types of schedule configurations"""
    ONE_TIME = "one_time"      # Run once at a specific date/time
    CRON = "cron"              # Full cron expression
    DAILY = "daily"            # Run daily at a specific time
    WEEKLY = "weekly"          # Run weekly on a specific day/time
    MONTHLY = "monthly"        # Run monthly on a specific day/time


class AITestMode(Enum):
    """Modes for AI testing on pages"""
    ALL = "all"                # Run AI tests on all pages
    SELECTED = "selected"      # Run AI tests only on selected pages
    NONE = "none"              # Do not run AI tests


class ScheduleRunStatus(Enum):
    """Status of a schedule run"""
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RUNNING = "running"


@dataclass
class PresetConfig:
    """Configuration for preset schedule types (daily, weekly, monthly)"""
    time: str = "02:00"                    # Time of day (HH:MM) in 24-hour format
    day_of_week: int = 0                   # For weekly: 0=Monday, 6=Sunday
    day_of_month: int = 1                  # For monthly: 1-31
    timezone: str = "America/Toronto"      # Timezone for scheduling

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'time': self.time,
            'day_of_week': self.day_of_week,
            'day_of_month': self.day_of_month,
            'timezone': self.timezone
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PresetConfig':
        """Create from dictionary"""
        if not data:
            return cls()

        return cls(
            time=data.get('time', '02:00'),
            day_of_week=data.get('day_of_week', 0),
            day_of_month=data.get('day_of_month', 1),
            timezone=data.get('timezone', 'America/Toronto')
        )


@dataclass
class ScheduleTestConfig:
    """Test configuration for a schedule"""
    # Which test types to run
    run_ai_tests: bool = True
    run_javascript_tests: bool = True
    run_python_tests: bool = True

    # Touchpoint configuration
    enabled_touchpoints: List[str] = field(default_factory=list)  # Empty = all touchpoints

    # AI-specific page selection (for cost control)
    ai_pages_mode: AITestMode = AITestMode.ALL
    ai_page_ids: List[str] = field(default_factory=list)  # Page IDs when mode=SELECTED

    # Screenshot settings
    take_screenshots: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'run_ai_tests': self.run_ai_tests,
            'run_javascript_tests': self.run_javascript_tests,
            'run_python_tests': self.run_python_tests,
            'enabled_touchpoints': self.enabled_touchpoints,
            'ai_pages_mode': self.ai_pages_mode.value if isinstance(self.ai_pages_mode, AITestMode) else self.ai_pages_mode,
            'ai_page_ids': self.ai_page_ids,
            'take_screenshots': self.take_screenshots
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScheduleTestConfig':
        """Create from dictionary"""
        if not data:
            return cls()

        ai_mode = data.get('ai_pages_mode', 'all')
        if isinstance(ai_mode, str):
            ai_mode = AITestMode(ai_mode)

        return cls(
            run_ai_tests=data.get('run_ai_tests', True),
            run_javascript_tests=data.get('run_javascript_tests', True),
            run_python_tests=data.get('run_python_tests', True),
            enabled_touchpoints=data.get('enabled_touchpoints', []),
            ai_pages_mode=ai_mode,
            ai_page_ids=data.get('ai_page_ids', []),
            take_screenshots=data.get('take_screenshots', True)
        )


@dataclass
class TestSchedule:
    """Scheduled test configuration for a website"""

    # Core identity
    website_id: str
    name: str
    description: Optional[str] = None

    # Schedule timing
    schedule_type: ScheduleType = ScheduleType.DAILY
    scheduled_datetime: Optional[datetime] = None  # For one_time schedules
    cron_expression: Optional[str] = None          # For cron schedules (e.g., "0 2 * * *")
    preset_config: PresetConfig = field(default_factory=PresetConfig)

    # Test configuration
    test_config: ScheduleTestConfig = field(default_factory=ScheduleTestConfig)

    # Authentication - which project users to test with
    project_user_ids: List[str] = field(default_factory=list)  # Empty = guest only

    # Status
    enabled: bool = True
    created_by: Optional[str] = None  # App user ID who created this

    # Execution tracking
    last_run_at: Optional[datetime] = None
    last_run_job_id: Optional[str] = None
    last_run_status: Optional[ScheduleRunStatus] = None
    next_run_at: Optional[datetime] = None
    run_count: int = 0

    # APScheduler integration
    apscheduler_job_id: Optional[str] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        """Get schedule ID as string"""
        return str(self._id) if self._id else None

    @property
    def type_display(self) -> str:
        """Get human-readable schedule type"""
        type_names = {
            ScheduleType.ONE_TIME: "One-time",
            ScheduleType.CRON: "Custom (Cron)",
            ScheduleType.DAILY: "Daily",
            ScheduleType.WEEKLY: "Weekly",
            ScheduleType.MONTHLY: "Monthly"
        }
        return type_names.get(self.schedule_type, str(self.schedule_type.value))

    @property
    def schedule_summary(self) -> str:
        """Get human-readable schedule summary"""
        if self.schedule_type == ScheduleType.ONE_TIME:
            if self.scheduled_datetime:
                return f"Once at {self.scheduled_datetime.strftime('%Y-%m-%d %H:%M')}"
            return "One-time (no date set)"

        if self.schedule_type == ScheduleType.CRON:
            return f"Cron: {self.cron_expression or 'Not set'}"

        if self.schedule_type == ScheduleType.DAILY:
            return f"Daily at {self.preset_config.time}"

        if self.schedule_type == ScheduleType.WEEKLY:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_name = days[self.preset_config.day_of_week] if 0 <= self.preset_config.day_of_week <= 6 else 'Unknown'
            return f"Weekly on {day_name} at {self.preset_config.time}"

        if self.schedule_type == ScheduleType.MONTHLY:
            return f"Monthly on day {self.preset_config.day_of_month} at {self.preset_config.time}"

        return "Unknown schedule"

    @property
    def status_display(self) -> str:
        """Get status for display"""
        if not self.enabled:
            return "Disabled"
        if self.last_run_status == ScheduleRunStatus.RUNNING:
            return "Running"
        return "Enabled"

    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now()

    def mark_run_started(self, job_id: str):
        """Mark that a scheduled run has started"""
        self.last_run_at = datetime.now()
        self.last_run_job_id = job_id
        self.last_run_status = ScheduleRunStatus.RUNNING
        self.run_count += 1
        self.update_timestamp()

    def mark_run_completed(self, success: bool):
        """Mark that a scheduled run has completed"""
        self.last_run_status = ScheduleRunStatus.SUCCESS if success else ScheduleRunStatus.FAILED
        self.update_timestamp()

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'website_id': self.website_id,
            'name': self.name,
            'description': self.description,
            'schedule_type': self.schedule_type.value if isinstance(self.schedule_type, ScheduleType) else self.schedule_type,
            'scheduled_datetime': self.scheduled_datetime,
            'cron_expression': self.cron_expression,
            'preset_config': self.preset_config.to_dict(),
            'test_config': self.test_config.to_dict(),
            'project_user_ids': self.project_user_ids,
            'enabled': self.enabled,
            'created_by': self.created_by,
            'last_run_at': self.last_run_at,
            'last_run_job_id': self.last_run_job_id,
            'last_run_status': self.last_run_status.value if isinstance(self.last_run_status, ScheduleRunStatus) else self.last_run_status,
            'next_run_at': self.next_run_at,
            'run_count': self.run_count,
            'apscheduler_job_id': self.apscheduler_job_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'TestSchedule':
        """Create from MongoDB document"""
        schedule_type = data.get('schedule_type', 'daily')
        if isinstance(schedule_type, str):
            schedule_type = ScheduleType(schedule_type)

        last_run_status = data.get('last_run_status')
        if isinstance(last_run_status, str):
            last_run_status = ScheduleRunStatus(last_run_status)

        return cls(
            website_id=data['website_id'],
            name=data['name'],
            description=data.get('description'),
            schedule_type=schedule_type,
            scheduled_datetime=data.get('scheduled_datetime'),
            cron_expression=data.get('cron_expression'),
            preset_config=PresetConfig.from_dict(data.get('preset_config', {})),
            test_config=ScheduleTestConfig.from_dict(data.get('test_config', {})),
            project_user_ids=data.get('project_user_ids', []),
            enabled=data.get('enabled', True),
            created_by=data.get('created_by'),
            last_run_at=data.get('last_run_at'),
            last_run_job_id=data.get('last_run_job_id'),
            last_run_status=last_run_status,
            next_run_at=data.get('next_run_at'),
            run_count=data.get('run_count', 0),
            apscheduler_job_id=data.get('apscheduler_job_id'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            _id=data.get('_id')
        )
