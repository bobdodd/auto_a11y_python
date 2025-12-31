"""
Test state matrix model for defining which script state combinations to test
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Set
from bson import ObjectId


@dataclass
class ScriptStateDefinition:
    """Defines a script and its possible states (before/after execution)"""

    script_id: str
    script_name: str
    test_before: bool = True   # Include "before execution" as a state
    test_after: bool = True    # Include "after execution" as a state
    execution_order: int = 0   # Order in which script should be executed (0-based)

    def get_state_ids(self) -> List[str]:
        """Get list of state IDs for this script"""
        states = []
        if self.test_before:
            states.append(f"{self.script_id}_before")
        if self.test_after:
            states.append(f"{self.script_id}_after")
        return states

    def get_state_labels(self) -> List[str]:
        """Get human-readable labels for states"""
        labels = []
        if self.test_before:
            labels.append(f"{self.script_name} (Before)")
        if self.test_after:
            labels.append(f"{self.script_name} (After)")
        return labels

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'script_id': self.script_id,
            'script_name': self.script_name,
            'test_before': self.test_before,
            'test_after': self.test_after,
            'execution_order': self.execution_order
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScriptStateDefinition':
        """Create from dictionary"""
        return cls(
            script_id=data['script_id'],
            script_name=data['script_name'],
            test_before=data.get('test_before', True),
            test_after=data.get('test_after', True),
            execution_order=data.get('execution_order', 0)
        )


@dataclass
class StateCombination:
    """Represents a specific combination of script states to test"""

    # Maps script_id to state ("before" or "after")
    script_states: Dict[str, str] = field(default_factory=dict)

    # User-friendly description of this state combination
    description: Optional[str] = None

    # Whether this combination should be tested
    enabled: bool = True

    def get_state_id(self) -> str:
        """Generate a unique ID for this state combination"""
        # Sort by script_id for consistency
        sorted_states = sorted(self.script_states.items())
        parts = [f"{script_id}_{state}" for script_id, state in sorted_states]
        return "_".join(parts)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'script_states': self.script_states,
            'description': self.description,
            'enabled': self.enabled
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StateCombination':
        """Create from dictionary"""
        return cls(
            script_states=data['script_states'],
            description=data.get('description'),
            enabled=data.get('enabled', True)
        )


@dataclass
class TestStateMatrix:
    """
    Defines which script state combinations to test for a page.

    Each combination is a row specifying the state (before/after/none) for each script.
    - "before": Test before script runs (script not executed)
    - "after": Test after script runs (script executed)
    - "none": Script not part of this test

    Example for 2 scripts (Cookie, Dialog):
    combinations = [
        {"cookie_id": "before", "dialog_id": "before"},  # Initial state
        {"cookie_id": "after", "dialog_id": "none"},     # Only cookie dismissed
        {"cookie_id": "after", "dialog_id": "after"},    # Both executed
    ]
    """

    page_id: str
    website_id: str

    scripts: List[ScriptStateDefinition] = field(default_factory=list)

    combinations: List[Dict[str, str]] = field(default_factory=list)

    matrix: Dict[str, Dict[str, bool]] = field(default_factory=dict)

    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None

    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        return str(self._id) if self._id else None

    def initialize_matrix(self):
        """Initialize with default sequential combinations"""
        self.combinations = []

        if not self.scripts:
            return

        scripts_sorted = sorted(self.scripts, key=lambda s: s.execution_order)

        initial = {s.script_id: "before" for s in scripts_sorted}
        self.combinations.append(initial.copy())

        current = initial.copy()
        for script in scripts_sorted:
            if script.test_after:
                current[script.script_id] = "after"
                self.combinations.append(current.copy())

    def get_enabled_combinations(self) -> List[StateCombination]:
        """Get all combinations as StateCombination objects"""
        if self.combinations:
            return [
                StateCombination(script_states={k: v for k, v in combo.items() if v != "none"})
                for combo in self.combinations
            ]

        if self.matrix:
            return self._extract_from_legacy_matrix()

        return []

    def _extract_from_legacy_matrix(self) -> List[StateCombination]:
        """Extract combinations from old matrix format for backwards compatibility"""
        seen: Set[str] = set()
        results: List[StateCombination] = []

        for row_id, row_data in self.matrix.items():
            for col_id, enabled in row_data.items():
                if not enabled:
                    continue

                script_states = {}
                for state_id in [row_id, col_id]:
                    parts = state_id.rsplit('_', 1)
                    if len(parts) == 2:
                        script_id, state = parts
                        script_states[script_id] = state

                combo = StateCombination(script_states=script_states)
                combo_id = combo.get_state_id()
                if combo_id not in seen:
                    seen.add(combo_id)
                    results.append(combo)

        return results

    def to_dict(self) -> dict:
        data = {
            'page_id': self.page_id,
            'website_id': self.website_id,
            'scripts': [script.to_dict() for script in self.scripts],
            'combinations': self.combinations,
            'matrix': self.matrix,
            'created_date': self.created_date,
            'last_modified': self.last_modified,
            'created_by': self.created_by
        }
        if self._id:
            data['_id'] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'TestStateMatrix':
        return cls(
            page_id=data['page_id'],
            website_id=data['website_id'],
            scripts=[ScriptStateDefinition.from_dict(s) for s in data.get('scripts', [])],
            combinations=data.get('combinations', []),
            matrix=data.get('matrix', {}),
            created_date=data.get('created_date', datetime.now()),
            last_modified=data.get('last_modified', datetime.now()),
            created_by=data.get('created_by'),
            _id=data.get('_id')
        )

    def update_timestamp(self):
        self.last_modified = datetime.now()
