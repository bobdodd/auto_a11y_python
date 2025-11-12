"""
WCAG 2.2 Parser and Query Module

This module provides utilities to parse and query the official W3C WCAG 2.2 JSON data.

Attribution and License:
========================
The WCAG data used by this module is sourced from the World Wide Web Consortium (W3C):
- Web Content Accessibility Guidelines (WCAG) 2.2: https://www.w3.org/TR/WCAG22/
- Techniques for WCAG 2.2: https://www.w3.org/WAI/WCAG22/Techniques/
- WCAG 2.2 JSON Data: https://www.w3.org/WAI/WCAG22/wcag.json

Copyright (c) 2008-2023 World Wide Web Consortium.
The WCAG content is used with attribution as permitted by W3C.
The content has not been modified from its original form.

W3C Document License: https://www.w3.org/Consortium/Legal/2015/doc-license

All additional code, analysis, and features provided by Auto A11y are clearly
distinguished from the original W3C WCAG content.
"""

import json
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SuccessCriterion:
    """Represents a WCAG Success Criterion"""
    id: str
    num: str
    handle: str
    title: str
    level: str  # A, AA, or AAA
    versions: List[str]
    content: str

    def __str__(self):
        return f"{self.num} {self.handle} (Level {self.level})"


class WCAGParser:
    """Parser for WCAG 2.2 JSON data"""

    def __init__(self):
        """Load WCAG 2.2 JSON data"""
        data_file = Path(__file__).parent / 'data' / 'wcag' / 'wcag22.json'
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # Cache all success criteria
        self._criteria_cache: Dict[str, SuccessCriterion] = {}
        self._load_criteria()

    def _load_criteria(self):
        """Load all success criteria into cache"""
        for principle in self.data.get('principles', []):
            for guideline in principle.get('guidelines', []):
                for sc in guideline.get('successcriteria', []):
                    criterion = SuccessCriterion(
                        id=sc['id'],
                        num=sc['num'],
                        handle=sc['handle'],
                        title=sc['title'],
                        level=sc['level'],
                        versions=sc['versions'],
                        content=sc.get('content', '')
                    )
                    self._criteria_cache[sc['id']] = criterion

    def get_all_criteria(self, level: Optional[str] = None, version: str = '2.2') -> List[SuccessCriterion]:
        """
        Get all success criteria, optionally filtered by level

        Args:
            level: Filter by level ('A', 'AA', 'AAA'). If None, returns all levels.
            version: WCAG version to filter by (default '2.2')

        Returns:
            List of SuccessCriterion objects
        """
        criteria = [
            sc for sc in self._criteria_cache.values()
            if version in sc.versions
        ]

        if level:
            criteria = [sc for sc in criteria if sc.level == level]

        return sorted(criteria, key=lambda x: x.num)

    def get_criterion_by_id(self, criterion_id: str) -> Optional[SuccessCriterion]:
        """Get a specific success criterion by ID"""
        return self._criteria_cache.get(criterion_id)

    def get_criterion_by_num(self, num: str) -> Optional[SuccessCriterion]:
        """Get a specific success criterion by number (e.g., '1.1.1')"""
        for sc in self._criteria_cache.values():
            if sc.num == num:
                return sc
        return None

    def get_criteria_for_level(self, target_level: str) -> List[SuccessCriterion]:
        """
        Get all criteria up to and including the specified level

        Args:
            target_level: 'A', 'AA', or 'AAA'

        Returns:
            List of all criteria at levels A, AA (if target is AA or AAA), and AAA (if target is AAA)
        """
        level_hierarchy = ['A', 'AA', 'AAA']
        target_idx = level_hierarchy.index(target_level)
        included_levels = level_hierarchy[:target_idx + 1]

        criteria = [
            sc for sc in self._criteria_cache.values()
            if sc.level in included_levels and '2.2' in sc.versions
        ]

        return sorted(criteria, key=lambda x: x.num)


class TestingScopeMapper:
    """Maps testing scope categories to applicable WCAG Success Criteria"""

    # Mapping of testing scope categories to WCAG Success Criteria IDs
    # ONLY includes criteria that are EXCLUSIVELY about that specific content type
    # General criteria (like 1.1.1, 1.3.1, keyboard access, etc.) are NOT included
    # as they apply broadly regardless of specific content types tested
    SCOPE_TO_CRITERIA = {
        'forms': [
            'identify-input-purpose',  # 1.3.5 - Autocomplete (forms-specific)
            'error-identification',  # 3.3.1 - Error identification (forms-specific)
            'labels-or-instructions',  # 3.3.2 - Labels or instructions (forms-specific)
            'error-suggestion',  # 3.3.3 - Error suggestion (forms-specific)
            'error-prevention-legal-financial-data',  # 3.3.4 - Error prevention (forms-specific)
            'redundant-entry',  # 3.3.7 - Redundant entry (forms-specific)
            'accessible-authentication-minimum',  # 3.3.8 - Accessible authentication (forms-specific)
            'accessible-authentication-enhanced',  # 3.3.9 - Accessible authentication (forms-specific)
        ],
        'video': [
            # All time-based media criteria (1.2.x series) - exclusively about video/audio
            'audio-only-and-video-only-prerecorded',  # 1.2.1
            'captions-prerecorded',  # 1.2.2
            'audio-description-or-media-alternative-prerecorded',  # 1.2.3
            'captions-live',  # 1.2.4
            'audio-description-prerecorded',  # 1.2.5
            'sign-language-prerecorded',  # 1.2.6
            'extended-audio-description-prerecorded',  # 1.2.7
            'media-alternative-prerecorded',  # 1.2.8
            'audio-only-live',  # 1.2.9
        ],
        'live_multimedia': [
            'captions-live',  # 1.2.4 - Live captions
            'audio-only-live',  # 1.2.9 - Audio-only live
        ],
        'multilingual': [
            # Note: 3.1.1 (Language of page) is required for ALL pages
            # Only 3.1.2 is specific to multilingual content
            'language-of-parts',  # 3.1.2 - Language of parts (multilingual-specific)
        ],
        'orientation': [
            'orientation',  # 1.3.4 - Orientation (specific to orientation changes)
        ],
        'zoom': [
            'resize-text',  # 1.4.4 - Resize text (zoom-specific)
            'reflow',  # 1.4.10 - Reflow (zoom-specific)
            'text-spacing',  # 1.4.12 - Text spacing (zoom-specific)
        ],
        'timeouts': [
            # Only criteria specifically about session timeouts and re-authentication
            # Note: 2.2.1 and 2.2.2 apply broadly (carousels, auto-updating content, etc.)
            're-authenticating',  # 2.2.5 - Re-authenticating (session-specific)
            'timeouts',  # 2.2.6 - Timeouts (session-specific)
        ],
        'motion_actuation': [
            'motion-actuation',  # 2.5.4 - Motion actuation (motion-specific)
        ],
        'drag_drop': [
            'dragging-movements',  # 2.5.7 - Dragging movements (drag/drop-specific)
        ],
    }

    def __init__(self, wcag_parser: WCAGParser):
        """
        Initialize with a WCAG parser instance

        Args:
            wcag_parser: WCAGParser instance for looking up criteria
        """
        self.parser = wcag_parser

    def get_applicable_criteria(self, testing_scope: Dict[str, bool],
                                target_level: str = 'AA') -> List[SuccessCriterion]:
        """
        Get all applicable WCAG Success Criteria based on testing scope.

        Uses subtractive approach: starts with ALL criteria for the target level,
        then removes criteria that are ONLY associated with content types that were NOT tested.

        Args:
            testing_scope: Dictionary mapping scope categories to boolean values
                          (e.g., {"forms": True, "video": False, ...})
            target_level: Target conformance level ('A', 'AA', or 'AAA')

        Returns:
            List of applicable SuccessCriterion objects (what was actually tested)
        """
        # Start with ALL criteria for the target level
        all_criteria = self.parser.get_criteria_for_level(target_level)
        applicable_ids: Set[str] = set(c.id for c in all_criteria)

        # Build sets of criteria to potentially remove (from untested scopes)
        # and criteria to keep (from tested scopes)
        criteria_to_remove: Set[str] = set()
        criteria_to_keep: Set[str] = set()

        for scope_key, is_tested in testing_scope.items():
            if scope_key in self.SCOPE_TO_CRITERIA:
                if is_tested:
                    # These criteria must be kept - they're being tested
                    criteria_to_keep.update(self.SCOPE_TO_CRITERIA[scope_key])
                else:
                    # These criteria are candidates for removal
                    criteria_to_remove.update(self.SCOPE_TO_CRITERIA[scope_key])

        # Only remove criteria that are NOT in the "keep" set
        # (i.e., only remove if they're exclusively associated with untested content)
        criteria_to_actually_remove = criteria_to_remove - criteria_to_keep
        applicable_ids.difference_update(criteria_to_actually_remove)

        # Get the actual criterion objects for remaining IDs
        criteria = []
        for criterion_id in applicable_ids:
            sc = self.parser.get_criterion_by_id(criterion_id)
            if sc:
                criteria.append(sc)

        return sorted(criteria, key=lambda x: x.num)

    def _is_within_level(self, criterion_level: str, target_level: str) -> bool:
        """Check if criterion level is within target level"""
        level_hierarchy = ['A', 'AA', 'AAA']
        # Handle empty or invalid criterion levels
        if not criterion_level or criterion_level not in level_hierarchy:
            return False
        criterion_idx = level_hierarchy.index(criterion_level)
        target_idx = level_hierarchy.index(target_level)
        return criterion_idx <= target_idx

    def get_scope_categories(self) -> List[str]:
        """Get all available testing scope categories"""
        return sorted(self.SCOPE_TO_CRITERIA.keys())

    def get_criteria_for_scope(self, scope_key: str) -> List[SuccessCriterion]:
        """
        Get all criteria associated with a specific scope category

        Args:
            scope_key: Scope category key (e.g., 'forms', 'video')

        Returns:
            List of SuccessCriterion objects for that scope
        """
        if scope_key not in self.SCOPE_TO_CRITERIA:
            return []

        criteria = []
        for criterion_id in self.SCOPE_TO_CRITERIA[scope_key]:
            sc = self.parser.get_criterion_by_id(criterion_id)
            if sc:
                criteria.append(sc)

        return sorted(criteria, key=lambda x: x.num)


# Singleton instances for easy access
_wcag_parser_instance = None
_scope_mapper_instance = None


def get_wcag_parser() -> WCAGParser:
    """Get singleton WCAG parser instance"""
    global _wcag_parser_instance
    if _wcag_parser_instance is None:
        _wcag_parser_instance = WCAGParser()
    return _wcag_parser_instance


def get_scope_mapper() -> TestingScopeMapper:
    """Get singleton testing scope mapper instance"""
    global _scope_mapper_instance
    if _scope_mapper_instance is None:
        parser = get_wcag_parser()
        _scope_mapper_instance = TestingScopeMapper(parser)
    return _scope_mapper_instance
