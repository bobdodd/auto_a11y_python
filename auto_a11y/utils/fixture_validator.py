"""
Fixture validation utilities
Checks which tests have passing fixtures
"""

import logging
from typing import Dict, Set, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient
from auto_a11y.core.database import Database

logger = logging.getLogger(__name__)


class FixtureValidator:
    """Validates which tests have passing fixture tests"""
    
    def __init__(self, database: Database):
        self.db = database
        self._cache = None
        self._cache_time = None
        self._cache_duration = 300  # Cache for 5 minutes
    
    def get_passing_tests(self, force_refresh: bool = False) -> Set[str]:
        """
        Get set of error codes that have passing fixture tests
        
        Returns:
            Set of error codes that passed their fixture tests
        """
        # Check cache
        if not force_refresh and self._cache is not None:
            if self._cache_time and (datetime.now() - self._cache_time).seconds < self._cache_duration:
                return self._cache
        
        try:
            # Get the most recent test run
            latest_run = self.db.db.fixture_test_runs.find_one(
                {},
                sort=[("completed_at", -1)]
            )
            
            if not latest_run:
                logger.warning("No fixture test runs found in database")
                return set()
            
            # Get all passing tests from this run
            passing_tests = self.db.db.fixture_tests.find({
                "test_run_id": latest_run["_id"],
                "success": True
            })
            
            # Extract error codes
            passing_codes = set()
            for test in passing_tests:
                expected_code = test.get("expected_code", "")
                if expected_code:
                    passing_codes.add(expected_code)
            
            # Cache the results
            self._cache = passing_codes
            self._cache_time = datetime.now()
            
            logger.info(f"Found {len(passing_codes)} passing tests from run {latest_run['_id']}")
            return passing_codes
            
        except Exception as e:
            logger.error(f"Error getting passing tests: {e}")
            return set()
    
    def get_test_status(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """
        Get detailed status for all tests
        
        Returns:
            Dict mapping error codes to their test status
        """
        try:
            # Get the most recent test run
            latest_run = self.db.db.fixture_test_runs.find_one(
                {},
                sort=[("completed_at", -1)]
            )
            
            if not latest_run:
                return {}
            
            # Get all test results from this run
            all_tests = self.db.db.fixture_tests.find({
                "test_run_id": latest_run["_id"]
            })
            
            status_map = {}
            for test in all_tests:
                expected_code = test.get("expected_code", "")
                if expected_code:
                    status_map[expected_code] = {
                        "success": test.get("success", False),
                        "found_codes": test.get("found_codes", []),
                        "notes": test.get("notes", []),
                        "tested_at": test.get("tested_at"),
                        "fixture_path": test.get("fixture_path", "")
                    }
            
            return status_map
            
        except Exception as e:
            logger.error(f"Error getting test status: {e}")
            return {}
    
    def is_test_available(self, error_code: str, debug_mode: bool = False) -> bool:
        """
        Check if a test should be available for use
        
        Args:
            error_code: The error code to check
            debug_mode: If True, all tests are available
            
        Returns:
            True if test should be available
        """
        if debug_mode:
            return True
        
        passing_tests = self.get_passing_tests()
        return error_code in passing_tests
    
    def get_fixture_run_summary(self) -> Optional[Dict]:
        """
        Get summary of the latest fixture test run
        
        Returns:
            Summary dict or None if no runs found
        """
        try:
            latest_run = self.db.db.fixture_test_runs.find_one(
                {},
                sort=[("completed_at", -1)]
            )
            
            if latest_run:
                return {
                    "run_id": latest_run["_id"],
                    "completed_at": latest_run.get("completed_at"),
                    "total": latest_run.get("total_fixtures", 0),
                    "passed": latest_run.get("passed", 0),
                    "failed": latest_run.get("failed", 0),
                    "success_rate": latest_run.get("success_rate", 0)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting fixture run summary: {e}")
            return None