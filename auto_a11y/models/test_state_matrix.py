"""
Test state matrix model for defining which script state combinations to test
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Set, Tuple
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
    Matrix defining which script state combinations should be tested

    This is a 2D matrix where:
    - Rows represent script states (e.g., "Cookie Before", "Cookie After")
    - Columns represent script states (e.g., "Modal Before", "Modal After")
    - Cells marked True indicate that combination should be tested

    Example for 2 scripts (Cookie, Modal):
                    Cookie_Before  Cookie_After  Modal_Before  Modal_After
    Cookie_Before        X              -             -            -
    Cookie_After         -              X             X            X
    Modal_Before         -              X             X            -
    Modal_After          -              X             -            X

    This creates 4 test states:
    1. Cookie=Before, Modal=Before (initial state)
    2. Cookie=After, Modal=Before
    3. Cookie=After, Modal=After
    4. Cookie=Before, Modal=After (modal without cookie dismissed)
    """

    page_id: str
    website_id: str

    # Scripts included in this matrix
    scripts: List[ScriptStateDefinition] = field(default_factory=list)

    # Matrix data: dict[row_state_id, dict[col_state_id, bool]]
    # Example: {"cookie_before": {"modal_before": True, "modal_after": False}, ...}
    matrix: Dict[str, Dict[str, bool]] = field(default_factory=dict)

    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None

    # MongoDB ID
    _id: Optional[ObjectId] = None

    @property
    def id(self) -> str:
        """Get matrix ID as string"""
        return str(self._id) if self._id else None

    def initialize_matrix(self):
        """
        Initialize matrix with default values

        By default, we enable:
        1. Initial state (all scripts "before")
        2. Final state (all scripts "after")
        3. Sequential execution states (execute scripts one by one)
        """
        # Get all state IDs
        all_state_ids = []
        for script in self.scripts:
            all_state_ids.extend(script.get_state_ids())

        # Initialize empty matrix
        self.matrix = {}
        for row_state in all_state_ids:
            self.matrix[row_state] = {}
            for col_state in all_state_ids:
                self.matrix[row_state][col_state] = False

        # Enable default combinations
        # 1. Initial state (all "before")
        initial_states = [f"{script.script_id}_before" for script in self.scripts if script.test_before]
        for state in initial_states:
            if state in self.matrix:
                self.matrix[state][state] = True

        # 2. Sequential execution states
        scripts_sorted = sorted(self.scripts, key=lambda s: s.execution_order)
        current_states = {script.script_id: "before" for script in scripts_sorted if script.test_before}

        for script in scripts_sorted:
            if script.test_after:
                # Mark this transition
                current_states[script.script_id] = "after"

                # Create state IDs for current combination
                for row_script_id, row_state in current_states.items():
                    row_state_id = f"{row_script_id}_{row_state}"
                    if row_state_id in self.matrix:
                        for col_script_id, col_state in current_states.items():
                            col_state_id = f"{col_script_id}_{col_state}"
                            if col_state_id in self.matrix[row_state_id]:
                                self.matrix[row_state_id][col_state_id] = True

    def get_enabled_combinations(self) -> List[StateCombination]:
        """
        Extract all enabled state combinations from the matrix

        Returns:
            List of StateCombination objects representing unique test states
        """
        # Use a set to track unique combinations
        seen_combinations: Set[str] = set()
        combinations: List[StateCombination] = []

        # Scan matrix for enabled cells
        for row_state_id, row_data in self.matrix.items():
            for col_state_id, enabled in row_data.items():
                if enabled:
                    # Parse state IDs
                    row_script_id, row_state = row_state_id.rsplit('_', 1)
                    col_script_id, col_state = col_state_id.rsplit('_', 1)

                    # Create combination
                    script_states = {
                        row_script_id: row_state,
                        col_script_id: col_state
                    }

                    # Generate combination ID for deduplication
                    combo = StateCombination(script_states=script_states)
                    combo_id = combo.get_state_id()

                    if combo_id not in seen_combinations:
                        seen_combinations.add(combo_id)
                        combinations.append(combo)

        return combinations

    def set_combination_enabled(self, row_state_id: str, col_state_id: str, enabled: bool):
        """Enable or disable a specific state combination"""
        if row_state_id in self.matrix and col_state_id in self.matrix[row_state_id]:
            self.matrix[row_state_id][col_state_id] = enabled
            self.last_modified = datetime.now()

    def is_combination_enabled(self, row_state_id: str, col_state_id: str) -> bool:
        """Check if a combination is enabled"""
        return self.matrix.get(row_state_id, {}).get(col_state_id, False)

    def get_matrix_dimensions(self) -> Tuple[List[str], List[str]]:
        """
        Get row and column headers for the matrix

        Returns:
            Tuple of (row_headers, col_headers) as lists of state IDs
        """
        all_state_ids = []
        for script in self.scripts:
            all_state_ids.extend(script.get_state_ids())
        return (all_state_ids, all_state_ids)

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'page_id': self.page_id,
            'website_id': self.website_id,
            'scripts': [script.to_dict() for script in self.scripts],
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
        """Create from MongoDB document"""
        return cls(
            page_id=data['page_id'],
            website_id=data['website_id'],
            scripts=[ScriptStateDefinition.from_dict(s) for s in data.get('scripts', [])],
            matrix=data.get('matrix', {}),
            created_date=data.get('created_date', datetime.now()),
            last_modified=data.get('last_modified', datetime.now()),
            created_by=data.get('created_by'),
            _id=data.get('_id')
        )

    def update_timestamp(self):
        """Update the last_modified timestamp"""
        self.last_modified = datetime.now()
