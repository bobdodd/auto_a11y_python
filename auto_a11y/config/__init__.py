"""
Configuration management for Auto A11y
"""

from .test_config import (
    TestConfiguration,
    TouchpointID,
    get_test_config,
    reset_test_config
)

__all__ = [
    'TestConfiguration',
    'TouchpointID',
    'get_test_config',
    'reset_test_config'
]