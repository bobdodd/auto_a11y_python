"""
Manual Accessibility Scoring Module

Calculates accessibility and compliance scores for manual testing recordings based on
issues found and testing scope.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from auto_a11y.models import Recording, RecordingIssue
from auto_a11y.wcag_parser import get_wcag_parser, get_scope_mapper


@dataclass
class ManualScores:
    """Container for manual testing scores"""
    accessibility_score: float  # 0-100, deductive based on issues
    compliance_score: Optional[float]  # 0-100, based on applicable criteria
    total_applicable_criteria: int  # Total WCAG criteria applicable based on testing scope
    failed_criteria: int  # Number of criteria with issues
    passed_criteria: int  # Assumed passed (applicable - failed)
    total_issues: int
    high_impact_issues: int
    medium_impact_issues: int
    low_impact_issues: int


class ManualAccessibilityScorer:
    """
    Calculate accessibility scores for manual testing recordings.

    Two scoring approaches:
    1. Accessibility Score: Deductive model starting at 100%, subtracting penalties for issues
    2. Compliance Score: Percentage of applicable WCAG criteria that passed
    """

    # Severity penalties (points deducted per issue)
    SEVERITY_PENALTIES = {
        'critical': 10.0,
        'high': 5.0,
        'medium': 2.0,
        'low': 0.5
    }

    # Frequency multipliers
    FREQUENCY_MULTIPLIERS = {
        'widespread': 3.0,
        'localized': 2.0,
        'isolated': 1.0
    }

    def __init__(self):
        """Initialize scorer with WCAG parser and scope mapper"""
        self.wcag_parser = get_wcag_parser()
        self.scope_mapper = get_scope_mapper()

    def calculate_scores(
        self,
        recording: Recording,
        issues: List[RecordingIssue],
        target_level: str = 'AA'
    ) -> ManualScores:
        """
        Calculate both accessibility and compliance scores for a recording.

        Args:
            recording: Recording object with testing_scope
            issues: List of RecordingIssue objects
            target_level: WCAG conformance level ('A', 'AA', or 'AAA')

        Returns:
            ManualScores object with calculated scores
        """
        # Calculate accessibility score (deductive model)
        accessibility_score = self._calculate_accessibility_score(issues)

        # Calculate compliance score (only if testing scope is defined)
        compliance_score = None
        total_applicable = 0
        failed_criteria = 0
        passed_criteria = 0

        if recording.testing_scope:
            compliance_score, total_applicable, failed_criteria, passed_criteria = \
                self._calculate_compliance_score(recording.testing_scope, issues, target_level)

        # Count issues by severity
        high_count = sum(1 for issue in issues if self._normalize_impact(issue.impact) in ['critical', 'high'])
        medium_count = sum(1 for issue in issues if self._normalize_impact(issue.impact) == 'medium')
        low_count = sum(1 for issue in issues if self._normalize_impact(issue.impact) == 'low')

        return ManualScores(
            accessibility_score=accessibility_score,
            compliance_score=compliance_score,
            total_applicable_criteria=total_applicable,
            failed_criteria=failed_criteria,
            passed_criteria=passed_criteria,
            total_issues=len(issues),
            high_impact_issues=high_count,
            medium_impact_issues=medium_count,
            low_impact_issues=low_count
        )

    def _calculate_accessibility_score(self, issues: List[RecordingIssue]) -> float:
        """
        Calculate accessibility score using deductive model.

        Starts at 100 and subtracts penalties based on issue severity and frequency.
        Formula: 100 - Σ(Severity Penalty × Frequency Multiplier)

        Args:
            issues: List of issues found

        Returns:
            Score between 0 and 100
        """
        score = 100.0

        for issue in issues:
            # Normalize impact level
            severity = self._normalize_impact(issue.impact)
            penalty = self.SEVERITY_PENALTIES.get(severity, self.SEVERITY_PENALTIES['medium'])

            # For now, assume isolated frequency
            # In future, could infer from issue description or add frequency field
            frequency_multiplier = self.FREQUENCY_MULTIPLIERS['isolated']

            # Deduct penalty
            score -= (penalty * frequency_multiplier)

        # Ensure score doesn't go below 0
        return max(0.0, score)

    def _calculate_compliance_score(
        self,
        testing_scope: Dict[str, bool],
        issues: List[RecordingIssue],
        target_level: str
    ) -> Tuple[float, int, int, int]:
        """
        Calculate compliance score based on applicable WCAG criteria.

        Formula: (Passed Criteria / Total Applicable Criteria) × 100
        Where Passed = Applicable - Failed

        Args:
            testing_scope: Dict of content types tested
            issues: List of issues found
            target_level: WCAG conformance level

        Returns:
            Tuple of (compliance_score, total_applicable, failed_criteria, passed_criteria)
        """
        # Get applicable criteria based on testing scope
        applicable_criteria = self.scope_mapper.get_applicable_criteria(
            testing_scope,
            target_level
        )

        total_applicable = len(applicable_criteria)

        if total_applicable == 0:
            # No applicable criteria, cannot calculate compliance score
            return None, 0, 0, 0

        # Determine which criteria failed based on issues
        failed_criterion_ids = set()

        for issue in issues:
            # Extract WCAG criteria from issue
            if issue.wcag:
                for wcag_ref in issue.wcag:
                    # wcag_ref.criteria is like "1.1.1" or "1.1.1 Non-text Content"
                    criterion_num = self._extract_criterion_number(wcag_ref.criteria)
                    if criterion_num:
                        # Find the criterion in applicable criteria
                        criterion = self.wcag_parser.get_criterion_by_num(criterion_num)
                        if criterion and criterion.id in [c.id for c in applicable_criteria]:
                            failed_criterion_ids.add(criterion.id)

        failed_criteria = len(failed_criterion_ids)
        passed_criteria = total_applicable - failed_criteria

        # Calculate compliance score
        compliance_score = (passed_criteria / total_applicable) * 100.0

        return compliance_score, total_applicable, failed_criteria, passed_criteria

    def _normalize_impact(self, impact) -> str:
        """
        Normalize impact level to standard categories.

        Args:
            impact: Impact level (can be ImpactLevel enum or string like "high", "High", "CRITICAL", etc.)

        Returns:
            Normalized impact: 'critical', 'high', 'medium', or 'low'
        """
        if not impact:
            return 'medium'

        # Handle ImpactLevel enum
        from auto_a11y.models import ImpactLevel
        if isinstance(impact, ImpactLevel):
            impact_str = impact.value
        else:
            impact_str = str(impact)

        impact_lower = impact_str.lower().strip()

        # Map variations to standard levels
        if impact_lower in ['critical', 'blocker', 'severe']:
            return 'critical'
        elif impact_lower in ['high', 'major']:
            return 'high'
        elif impact_lower in ['medium', 'moderate', 'normal']:
            return 'medium'
        elif impact_lower in ['low', 'minor', 'trivial']:
            return 'low'
        else:
            # Default to medium if unknown
            return 'medium'

    def _extract_criterion_number(self, criterion_str: str) -> Optional[str]:
        """
        Extract criterion number from various formats.

        Examples:
            "1.1.1" -> "1.1.1"
            "1.1.1 Non-text Content" -> "1.1.1"
            "WCAG 2.1.1" -> "2.1.1"

        Args:
            criterion_str: WCAG criterion string

        Returns:
            Criterion number (e.g., "1.1.1") or None if not found
        """
        if not criterion_str:
            return None

        import re
        # Look for pattern like X.X.X where X is a digit
        match = re.search(r'\b(\d+\.\d+\.\d+)\b', criterion_str)
        if match:
            return match.group(1)

        return None


def calculate_project_manual_scores(
    recordings: List[Recording],
    all_issues: Dict[str, List[RecordingIssue]],
    target_level: str = 'AA'
) -> ManualScores:
    """
    Calculate aggregate manual scores across multiple recordings for a project.

    Args:
        recordings: List of Recording objects
        all_issues: Dict mapping recording_id to list of RecordingIssue objects
        target_level: WCAG conformance level

    Returns:
        Aggregate ManualScores object
    """
    if not recordings:
        return ManualScores(
            accessibility_score=100.0,
            compliance_score=None,
            total_applicable_criteria=0,
            failed_criteria=0,
            passed_criteria=0,
            total_issues=0,
            high_impact_issues=0,
            medium_impact_issues=0,
            low_impact_issues=0
        )

    scorer = ManualAccessibilityScorer()

    # Calculate scores for each recording
    all_scores = []
    for recording in recordings:
        issues = all_issues.get(recording.recording_id, [])
        scores = scorer.calculate_scores(recording, issues, target_level)
        all_scores.append(scores)

    # Aggregate scores
    # Accessibility score: average across recordings
    avg_accessibility = sum(s.accessibility_score for s in all_scores) / len(all_scores)

    # Compliance score: aggregate criteria
    total_applicable_set = set()
    failed_criteria_set = set()

    for recording in recordings:
        if recording.testing_scope:
            issues = all_issues.get(recording.recording_id, [])
            _, total_app, failed, _ = scorer._calculate_compliance_score(
                recording.testing_scope,
                issues,
                target_level
            )

            # Get applicable criteria for this recording
            applicable = scorer.scope_mapper.get_applicable_criteria(
                recording.testing_scope,
                target_level
            )
            total_applicable_set.update(c.id for c in applicable)

            # Get failed criteria
            for issue in issues:
                if issue.wcag:
                    for wcag_ref in issue.wcag:
                        criterion_num = scorer._extract_criterion_number(wcag_ref.criteria)
                        if criterion_num:
                            criterion = scorer.wcag_parser.get_criterion_by_num(criterion_num)
                            if criterion:
                                failed_criteria_set.add(criterion.id)

    total_applicable = len(total_applicable_set)
    failed_criteria = len(failed_criteria_set)
    passed_criteria = total_applicable - failed_criteria

    compliance_score = None
    if total_applicable > 0:
        compliance_score = (passed_criteria / total_applicable) * 100.0

    # Total issue counts
    total_issues = sum(s.total_issues for s in all_scores)
    high_issues = sum(s.high_impact_issues for s in all_scores)
    medium_issues = sum(s.medium_impact_issues for s in all_scores)
    low_issues = sum(s.low_impact_issues for s in all_scores)

    return ManualScores(
        accessibility_score=avg_accessibility,
        compliance_score=compliance_score,
        total_applicable_criteria=total_applicable,
        failed_criteria=failed_criteria,
        passed_criteria=passed_criteria,
        total_issues=total_issues,
        high_impact_issues=high_issues,
        medium_impact_issues=medium_issues,
        low_impact_issues=low_issues
    )
