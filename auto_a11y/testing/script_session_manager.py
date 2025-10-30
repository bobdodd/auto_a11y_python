"""
Script session manager for tracking script execution across test sessions
"""

import logging
import uuid
from typing import Optional
from datetime import datetime

from auto_a11y.models import (
    ScriptExecutionSession, PageSetupScript, ExecutionTrigger, Violation
)
from auto_a11y.core.database import Database

logger = logging.getLogger(__name__)


class ScriptSessionManager:
    """Manages script execution state across test sessions"""

    def __init__(self, db: Database):
        """
        Initialize session manager

        Args:
            db: Database connection
        """
        self.db = db
        self.current_session: Optional[ScriptExecutionSession] = None

    def start_session(self, website_id: str) -> str:
        """
        Start new test session for a website

        Args:
            website_id: Website ID

        Returns:
            Session ID (UUID string)
        """
        session_id = str(uuid.uuid4())
        self.current_session = ScriptExecutionSession(
            session_id=session_id,
            website_id=website_id,
            started_at=datetime.now()
        )

        # Save to database
        self.db.create_script_session(self.current_session)
        logger.info(f"Started script execution session: {session_id} for website {website_id}")

        return session_id

    def end_session(self):
        """End current test session"""
        if self.current_session:
            self.current_session.ended_at = datetime.now()
            self.db.update_script_session(self.current_session)
            logger.info(f"Ended script execution session: {self.current_session.session_id}")
            self.current_session = None

    def has_executed(self, script_id: str) -> bool:
        """
        Check if script has been executed in this session

        Args:
            script_id: Script ID

        Returns:
            True if script has been executed
        """
        if not self.current_session:
            return False

        return self.current_session.has_executed(script_id)

    def mark_executed(
        self,
        script_id: str,
        page_id: str,
        success: bool,
        duration_ms: int
    ):
        """
        Mark script as executed in this session

        Args:
            script_id: Script ID
            page_id: Page ID where script was executed
            success: Whether execution was successful
            duration_ms: Execution duration in milliseconds
        """
        if not self.current_session:
            logger.warning("Attempted to mark script executed without active session")
            return

        # Add execution record to session
        self.current_session.add_execution_record(
            script_id=script_id,
            page_id=page_id,
            success=success,
            duration_ms=duration_ms
        )

        # Update session in database
        self.db.update_script_session(self.current_session)

        logger.debug(f"Marked script {script_id} as executed on page {page_id}")

    def should_execute_script(
        self,
        script: PageSetupScript,
        page_id: str
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if script should execute based on trigger and session state

        Args:
            script: PageSetupScript to check
            page_id: Page ID being tested

        Returns:
            Tuple of (should_execute, skip_reason)
        """
        # Check if enabled
        if not script.enabled:
            return False, "Script disabled"

        # Check trigger conditions
        if script.trigger == ExecutionTrigger.ONCE_PER_SESSION:
            if self.has_executed(script.id):
                return False, "Already executed this session (once_per_session trigger)"

        elif script.trigger == ExecutionTrigger.ONCE_PER_PAGE:
            # Always execute for page-level scripts
            pass

        elif script.trigger == ExecutionTrigger.CONDITIONAL:
            # Will check element existence before execution
            pass

        elif script.trigger == ExecutionTrigger.ALWAYS:
            # Always execute
            pass

        return True, None

    def check_condition_violation(
        self,
        script: PageSetupScript,
        page_id: str,
        condition_met: bool
    ) -> Optional[Violation]:
        """
        Check if condition constitutes a violation

        Args:
            script: PageSetupScript with violation detection config
            page_id: Page ID being tested
            condition_met: Whether the condition selector was found

        Returns:
            Violation object if violation detected, None otherwise
        """
        if not self.current_session:
            return None

        # Record condition check
        self.current_session.add_condition_check(
            script_id=script.id,
            page_id=page_id,
            condition_selector=script.condition_selector,
            condition_met=condition_met,
            violation_reported=False  # Will update if violation created
        )

        # Check if we should report violation
        if condition_met and script.report_violation_if_condition_met:
            # Check if script was already executed (condition should NOT reappear)
            if self.has_executed(script.id):
                logger.warning(
                    f"Condition violation detected: {script.condition_selector} "
                    f"found on page {page_id} after script execution"
                )

                # Update condition check to mark violation reported
                if self.current_session.condition_checks:
                    self.current_session.condition_checks[-1].violation_reported = True

                # Create violation
                violation = Violation(
                    id=script.violation_code or 'WarnScriptConditionPersists',
                    impact='medium',
                    message=script.violation_message or
                            f'Condition persists after script execution: {script.condition_selector}',
                    selector=script.condition_selector,
                    context=f'Script "{script.name}" was executed to handle this condition, '
                            f'but the element reappeared on page {page_id}',
                    help_url='',
                    wcag_criteria=[]
                )

                # Save session with updated condition check
                self.db.update_script_session(self.current_session)

                return violation

        # Save session with condition check
        self.db.update_script_session(self.current_session)

        return None

    def get_session_stats(self) -> dict:
        """
        Get statistics for current session

        Returns:
            Dict with session statistics
        """
        if not self.current_session:
            return {
                'active': False,
                'session_id': None,
                'scripts_executed': 0,
                'conditions_checked': 0,
                'violations_reported': 0
            }

        violations_count = sum(
            1 for check in self.current_session.condition_checks
            if check.violation_reported
        )

        return {
            'active': True,
            'session_id': self.current_session.session_id,
            'website_id': self.current_session.website_id,
            'started_at': self.current_session.started_at,
            'scripts_executed': len(self.current_session.executed_scripts),
            'conditions_checked': len(self.current_session.condition_checks),
            'violations_reported': violations_count
        }
