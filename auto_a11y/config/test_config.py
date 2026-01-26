"""
Test configuration for enabling/disabling touchpoints and individual tests
"""

from typing import Dict, List, Any, Set
from enum import Enum
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TouchpointID(Enum):
    """Touchpoint identifiers matching the 23 touchpoints"""
    ACCESSIBLE_NAMES = "accessible_names"
    ANIMATION = "animation"
    ARIA = "aria"
    BUTTONS = "buttons"
    COLORS_CONTRAST = "colors_contrast"
    DIALOGS = "dialogs"
    DOCUMENTS = "documents"
    EVENT_HANDLING = "event_handling"
    FOCUS_MANAGEMENT = "focus_management"
    FORMS = "forms"
    HEADINGS = "headings"
    IFRAMES = "iframes"
    IMAGES = "images"
    KEYBOARD_NAVIGATION = "keyboard_navigation"
    LANDMARKS = "landmarks"
    LANGUAGE = "language"
    LINKS = "links"
    LISTS = "lists"
    MAPS = "maps"
    MEDIA = "media"
    NAVIGATION = "navigation"
    READING_ORDER = "reading_order"
    SEMANTIC_STRUCTURE = "semantic_structure"
    TABLES = "tables"
    TIMING = "timing"
    FONTS = "fonts"
    TOUCH_MOBILE = "touch_mobile"


class TestConfiguration:
    """Manages test configuration for touchpoints and individual tests"""
    
    def __init__(self, config_file: str = None, database = None, debug_mode: bool = False):
        """
        Initialize test configuration
        
        Args:
            config_file: Path to JSON configuration file
            database: Database connection for fixture validation
            debug_mode: If True, all tests are available regardless of fixture status
        """
        self.config_file = Path(config_file) if config_file else Path('test_config.json')
        self.config = self._load_config()
        self.database = database
        self.debug_mode = debug_mode
        self.fixture_validator = None
        
        # Initialize fixture validator if database is provided
        if database:
            from auto_a11y.utils.fixture_validator import FixtureValidator
            self.fixture_validator = FixtureValidator(database)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded test configuration from {self.config_file}")
                return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return self._get_default_config()
        else:
            logger.info("No config file found, using default configuration")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration with all tests enabled"""
        return {
            "global": {
                "enabled": True,
                "run_ai_tests": True,
                "run_javascript_tests": True,
                "run_python_tests": True
            },
            "touchpoints": {
                touchpoint.value: {
                    "enabled": True,
                    "tests": {}  # Individual test overrides
                }
                for touchpoint in TouchpointID
            },
            "ai_tests": {
                "enabled": True,
                "analyses": {
                    "headings": True,
                    "reading_order": True,
                    "modals": True,
                    "language": True,
                    "animations": True,
                    "interactive": True
                }
            },
            "individual_tests": {}  # Override specific test IDs
        }
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved test configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def is_touchpoint_enabled(self, touchpoint: str) -> bool:
        """
        Check if a touchpoint is enabled
        
        Args:
            touchpoint: Touchpoint ID or name
            
        Returns:
            True if enabled, False otherwise
        """
        if not self.config.get("global", {}).get("enabled", True):
            return False
            
        touchpoint_config = self.config.get("touchpoints", {}).get(touchpoint, {})
        return touchpoint_config.get("enabled", True)
    
    def is_test_available_by_fixture(self, error_code: str) -> bool:
        """
        Check if a test is available based on fixture validation
        
        Args:
            error_code: The error code to check
            
        Returns:
            True if test passed fixtures or debug mode is on
        """
        if self.debug_mode:
            return True
            
        if not self.fixture_validator:
            # No database connection, assume all tests available
            return True
            
        return self.fixture_validator.is_test_available(error_code, self.debug_mode)
    
    def get_test_fixture_status(self, error_code: str) -> Dict[str, Any]:
        """
        Get fixture test status for an error code
        
        Args:
            error_code: The error code to check
            
        Returns:
            Status dictionary with success, notes, etc.
        """
        if not self.fixture_validator:
            return {"available": True, "reason": "No fixture validation"}
            
        status = self.fixture_validator.get_test_status().get(error_code, {})
        if not status:
            return {
                "available": self.debug_mode,
                "reason": "No fixture test found",
                "debug_override": self.debug_mode
            }
            
        return {
            "available": status.get("success", False) or self.debug_mode,
            "passed_fixture": status.get("success", False),
            "fixture_path": status.get("fixture_path", ""),
            "tested_at": status.get("tested_at"),
            "debug_override": self.debug_mode and not status.get("success", False)
        }
    
    def get_all_test_statuses(self) -> Dict[str, Dict]:
        """Get fixture status for all tests"""
        if not self.fixture_validator:
            return {}
        
        return self.fixture_validator.get_test_status()
    
    def is_test_enabled(self, test_id: str, touchpoint: str = None) -> bool:
        """
        Check if a specific test is enabled
        
        Args:
            test_id: Test identifier
            touchpoint: Optional touchpoint for the test
            
        Returns:
            True if enabled, False otherwise
        """
        # Check global enable
        if not self.config.get("global", {}).get("enabled", True):
            return False
        
        # Check individual test override in global settings
        individual_override = self.config.get("individual_tests", {}).get(test_id)
        if individual_override is not None:
            return individual_override
        
        # Check touchpoint enable
        if touchpoint:
            touchpoint_config = self.config.get("touchpoints", {}).get(touchpoint, {})
            
            # If touchpoint is disabled, all its tests are disabled
            if not touchpoint_config.get("enabled", True):
                return False
            
            # Check test-specific setting within touchpoint
            test_override = touchpoint_config.get("tests", {}).get(test_id)
            if test_override is not None:
                return test_override
        
        # Default to enabled if no specific setting found
        return True
    
    def is_ai_test_enabled(self, analysis_type: str) -> bool:
        """
        Check if an AI analysis type is enabled
        
        Args:
            analysis_type: Type of AI analysis (e.g., 'headings', 'reading_order')
            
        Returns:
            True if enabled, False otherwise
        """
        if not self.config.get("global", {}).get("enabled", True):
            return False
            
        if not self.config.get("global", {}).get("run_ai_tests", True):
            return False
            
        ai_config = self.config.get("ai_tests", {})
        if not ai_config.get("enabled", True):
            return False
            
        return ai_config.get("analyses", {}).get(analysis_type, True)
    
    def set_touchpoint_enabled(self, touchpoint: str, enabled: bool):
        """
        Enable or disable a touchpoint
        
        Args:
            touchpoint: Touchpoint ID
            enabled: Whether to enable or disable
        """
        if "touchpoints" not in self.config:
            self.config["touchpoints"] = {}
        if touchpoint not in self.config["touchpoints"]:
            self.config["touchpoints"][touchpoint] = {}
        
        self.config["touchpoints"][touchpoint]["enabled"] = enabled
        logger.info(f"Set touchpoint {touchpoint} enabled={enabled}")
    
    def set_test_enabled(self, test_id: str, enabled: bool, touchpoint: str = None):
        """
        Enable or disable a specific test
        
        Args:
            test_id: Test identifier
            enabled: Whether to enable or disable
            touchpoint: Optional touchpoint for the test
        """
        if touchpoint:
            # Set within touchpoint config
            if "touchpoints" not in self.config:
                self.config["touchpoints"] = {}
            if touchpoint not in self.config["touchpoints"]:
                self.config["touchpoints"][touchpoint] = {"tests": {}}
            if "tests" not in self.config["touchpoints"][touchpoint]:
                self.config["touchpoints"][touchpoint]["tests"] = {}
                
            self.config["touchpoints"][touchpoint]["tests"][test_id] = enabled
            logger.info(f"Set test {test_id} in touchpoint {touchpoint} enabled={enabled}")
        else:
            # Set as individual override
            if "individual_tests" not in self.config:
                self.config["individual_tests"] = {}
                
            self.config["individual_tests"][test_id] = enabled
            logger.info(f"Set individual test {test_id} enabled={enabled}")
    
    def set_ai_test_enabled(self, analysis_type: str, enabled: bool):
        """
        Enable or disable an AI analysis type
        
        Args:
            analysis_type: Type of AI analysis
            enabled: Whether to enable or disable
        """
        if "ai_tests" not in self.config:
            self.config["ai_tests"] = {"enabled": True, "analyses": {}}
        if "analyses" not in self.config["ai_tests"]:
            self.config["ai_tests"]["analyses"] = {}
            
        self.config["ai_tests"]["analyses"][analysis_type] = enabled
        logger.info(f"Set AI analysis {analysis_type} enabled={enabled}")
    
    def get_enabled_touchpoints(self) -> List[str]:
        """Get list of enabled touchpoints"""
        if not self.config.get("global", {}).get("enabled", True):
            return []
            
        enabled = []
        for touchpoint in TouchpointID:
            if self.is_touchpoint_enabled(touchpoint.value):
                enabled.append(touchpoint.value)
        
        return enabled
    
    def get_enabled_tests_for_touchpoint(self, touchpoint: str) -> Set[str]:
        """
        Get enabled tests for a specific touchpoint
        
        Args:
            touchpoint: Touchpoint ID
            
        Returns:
            Set of enabled test IDs
        """
        if not self.is_touchpoint_enabled(touchpoint):
            return set()
        
        # Get all tests for touchpoint from test registry
        # Filter based on configuration
        # This would integrate with the actual test loading mechanism
        
        return set()  # Placeholder
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        enabled_touchpoints = self.get_enabled_touchpoints()
        
        ai_analyses = []
        if self.config.get("global", {}).get("run_ai_tests", True):
            ai_config = self.config.get("ai_tests", {})
            for analysis, enabled in ai_config.get("analyses", {}).items():
                if enabled:
                    ai_analyses.append(analysis)
        
        return {
            "global_enabled": self.config.get("global", {}).get("enabled", True),
            "total_touchpoints": len(TouchpointID),
            "enabled_touchpoints": len(enabled_touchpoints),
            "touchpoint_list": enabled_touchpoints,
            "ai_tests_enabled": self.config.get("global", {}).get("run_ai_tests", True),
            "ai_analyses": ai_analyses,
            "javascript_tests_enabled": self.config.get("global", {}).get("run_javascript_tests", True),
            "python_tests_enabled": self.config.get("global", {}).get("run_python_tests", True)
        }


# Global instance
_test_config = None

def get_test_config(config_file: str = None, database = None, debug_mode: bool = False) -> TestConfiguration:
    """
    Get or create the global test configuration instance
    
    Args:
        config_file: Path to configuration file
        database: Database connection for fixture validation
        debug_mode: If True, all tests are available
    """
    global _test_config
    if _test_config is None:
        _test_config = TestConfiguration(config_file, database, debug_mode)
    elif database and not _test_config.database:
        # Update with database if not previously set
        _test_config.database = database
        _test_config.debug_mode = debug_mode
        if database:
            from auto_a11y.utils.fixture_validator import FixtureValidator
            _test_config.fixture_validator = FixtureValidator(database)
    return _test_config


def reset_test_config():
    """Reset the global test configuration"""
    global _test_config
    _test_config = None