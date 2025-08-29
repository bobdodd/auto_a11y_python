"""
Process and transform JavaScript test results into structured data
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from auto_a11y.models import TestResult, Violation, ImpactLevel

logger = logging.getLogger(__name__)


class ResultProcessor:
    """Processes raw JavaScript test results into structured format"""
    
    # Map error codes to WCAG criteria
    WCAG_MAPPING = {
        # Images
        'ErrNoAlt': ['1.1.1'],
        'ErrEmptyAlt': ['1.1.1'],
        'ErrAltTooLong': ['1.1.1'],
        'ErrRedundantAlt': ['1.1.1'],
        
        # Headings
        'ErrEmptyHeading': ['1.3.1', '2.4.6'],
        'ErrSkippedHeadingLevel': ['1.3.1'],
        'ErrMultipleH1': ['1.3.1'],
        'WarnHeadingInsideDisplayNone': ['1.3.1'],
        'WarnHeadingOver60CharsLong': ['2.4.6'],
        
        # Forms
        'ErrNoLabel': ['1.3.1', '3.3.2', '4.1.2'],
        'ErrEmptyLabel': ['3.3.2'],
        'ErrNoFieldset': ['1.3.1'],
        'ErrMissingRequired': ['3.3.2'],
        'ErrPlaceholderAsLabel': ['3.3.2'],
        
        # Landmarks
        'ErrNoMainLandmark': ['1.3.1', '2.4.1'],
        'ErrMultipleBanners': ['1.3.1'],
        'ErrMultipleContentinfo': ['1.3.1'],
        
        # Color
        'ErrInsufficientContrast': ['1.4.3'],
        'ErrLinkContrast': ['1.4.3'],
        
        # Language
        'ErrNoPageLanguage': ['3.1.1'],
        'ErrInvalidLanguageCode': ['3.1.1'],
        
        # Page Title
        'ErrNoPageTitle': ['2.4.2'],
        'ErrEmptyPageTitle': ['2.4.2'],
        
        # Focus
        'ErrNoFocusIndicator': ['2.4.7'],
        'ErrInvalidTabindex': ['2.4.3'],
    }
    
    # Map error codes to impact levels
    IMPACT_MAPPING = {
        # Critical - blocks access completely
        'ErrNoAlt': ImpactLevel.CRITICAL,
        'ErrNoLabel': ImpactLevel.CRITICAL,
        'ErrNoPageTitle': ImpactLevel.CRITICAL,
        'ErrNoPageLanguage': ImpactLevel.CRITICAL,
        
        # Serious - significant barriers
        'ErrEmptyHeading': ImpactLevel.SERIOUS,
        'ErrSkippedHeadingLevel': ImpactLevel.SERIOUS,
        'ErrInsufficientContrast': ImpactLevel.SERIOUS,
        'ErrNoMainLandmark': ImpactLevel.SERIOUS,
        'ErrEmptyLabel': ImpactLevel.SERIOUS,
        
        # Moderate - noticeable issues
        'ErrMultipleH1': ImpactLevel.MODERATE,
        'ErrAltTooLong': ImpactLevel.MODERATE,
        'ErrPlaceholderAsLabel': ImpactLevel.MODERATE,
        'ErrInvalidTabindex': ImpactLevel.MODERATE,
        
        # Minor - small issues
        'WarnHeadingOver60CharsLong': ImpactLevel.MINOR,
        'ErrRedundantAlt': ImpactLevel.MINOR,
        'WarnHeadingInsideDisplayNone': ImpactLevel.MINOR,
    }
    
    def process_test_results(
        self,
        page_id: str,
        raw_results: Dict[str, Dict[str, Any]],
        screenshot_path: Optional[str] = None,
        duration_ms: int = 0
    ) -> TestResult:
        """
        Process raw JavaScript test results into TestResult model
        
        Args:
            page_id: Page ID
            raw_results: Raw results from JavaScript tests
            screenshot_path: Path to screenshot
            duration_ms: Test duration in milliseconds
            
        Returns:
            Processed TestResult
        """
        violations = []  # _Err issues
        warnings = []    # _Warn issues  
        info = []        # _Info issues
        discovery = []   # _Disco issues
        passes = []
        
        # Process each test's results
        for test_name, test_result in raw_results.items():
            if 'error' in test_result and test_result['error']:
                logger.warning(f"Test {test_name} had execution error: {test_result['error']}")
                continue
            
            # Process errors and warnings (they come together from JS tests)
            all_issues = []
            if 'errors' in test_result and test_result['errors']:
                all_issues.extend(test_result['errors'])
            if 'warnings' in test_result and test_result['warnings']:
                all_issues.extend(test_result['warnings'])
            
            # Categorize issues based on their ID pattern
            for issue in all_issues:
                processed = self._process_violation(issue, test_name, 'unknown')
                if processed:
                    # Categorize based on ID pattern
                    if '_Err' in processed.id:
                        violations.append(processed)
                    elif '_Warn' in processed.id:
                        warnings.append(processed)
                    elif '_Info' in processed.id:
                        info.append(processed)
                    elif '_Disco' in processed.id:
                        discovery.append(processed)
                    else:
                        # Default to warnings if pattern not recognized
                        warnings.append(processed)
            
            # Process passes
            if 'passes' in test_result and test_result['passes']:
                passes.extend(test_result['passes'])
        
        # Create test result
        test_result = TestResult(
            page_id=page_id,
            test_date=datetime.now(),
            duration_ms=duration_ms,
            violations=violations,
            warnings=warnings,
            info=info,
            discovery=discovery,
            passes=passes,
            screenshot_path=screenshot_path,
            js_test_results=raw_results,
            metadata={
                'test_count': len(raw_results),
                'tests_run': list(raw_results.keys())
            }
        )
        
        return test_result
    
    def _process_violation(
        self,
        violation_data: Dict[str, Any],
        source_test: str,
        violation_type: str
    ) -> Optional[Violation]:
        """
        Process individual violation into Violation model
        
        Args:
            violation_data: Raw violation data from JavaScript
            source_test: Name of test that found violation
            violation_type: 'error' or 'warning'
            
        Returns:
            Violation object or None
        """
        try:
            error_code = violation_data.get('err', 'UnknownError')
            
            # Determine impact level
            if error_code in self.IMPACT_MAPPING:
                impact = self.IMPACT_MAPPING[error_code]
            elif violation_type == 'warning':
                impact = ImpactLevel.MINOR
            else:
                impact = ImpactLevel.MODERATE
            
            # Get WCAG criteria
            wcag_criteria = self.WCAG_MAPPING.get(error_code, [])
            
            # Create violation
            violation = Violation(
                id=f"{source_test}_{error_code}",
                impact=impact,
                category=violation_data.get('cat', source_test),
                description=self._get_error_description(error_code),
                help_url=self._get_help_url(error_code),
                xpath=violation_data.get('xpath'),
                element=violation_data.get('element'),
                html=violation_data.get('html'),
                failure_summary=self._get_failure_summary(error_code, violation_data),
                wcag_criteria=wcag_criteria
            )
            
            return violation
            
        except Exception as e:
            logger.error(f"Failed to process violation: {e}")
            return None
    
    def _get_error_description(self, error_code: str) -> str:
        """
        Get human-readable description for error code
        
        Args:
            error_code: Error code
            
        Returns:
            Description string
        """
        descriptions = {
            'ErrNoAlt': 'Image is missing alt text',
            'ErrEmptyAlt': 'Image alt text is empty',
            'ErrAltTooLong': 'Image alt text is too long (over 125 characters)',
            'ErrRedundantAlt': 'Image alt text contains redundant words like "image of"',
            'ErrEmptyHeading': 'Heading is empty',
            'ErrSkippedHeadingLevel': 'Heading level is skipped in hierarchy',
            'ErrMultipleH1': 'Multiple H1 elements found on page',
            'ErrNoLabel': 'Form input is missing a label',
            'ErrEmptyLabel': 'Form label is empty',
            'ErrNoFieldset': 'Radio/checkbox group is missing fieldset',
            'ErrNoMainLandmark': 'Page is missing main landmark',
            'ErrInsufficientContrast': 'Text color contrast is insufficient',
            'ErrNoPageLanguage': 'Page is missing language declaration',
            'ErrNoPageTitle': 'Page is missing title element',
            'ErrNoFocusIndicator': 'Element lacks visible focus indicator',
            'ErrInvalidTabindex': 'Invalid tabindex value',
        }
        
        return descriptions.get(error_code, f'Accessibility issue: {error_code}')
    
    def _get_help_url(self, error_code: str) -> str:
        """
        Get help URL for error code
        
        Args:
            error_code: Error code
            
        Returns:
            Help URL
        """
        # Map to WCAG documentation
        wcag_base = "https://www.w3.org/WAI/WCAG21/Understanding/"
        
        wcag_urls = {
            'ErrNoAlt': f"{wcag_base}non-text-content.html",
            'ErrEmptyHeading': f"{wcag_base}headings-and-labels.html",
            'ErrNoLabel': f"{wcag_base}labels-or-instructions.html",
            'ErrInsufficientContrast': f"{wcag_base}contrast-minimum.html",
            'ErrNoPageLanguage': f"{wcag_base}language-of-page.html",
            'ErrNoPageTitle': f"{wcag_base}page-titled.html",
        }
        
        return wcag_urls.get(error_code, "https://www.w3.org/WAI/WCAG21/quickref/")
    
    def _get_failure_summary(self, error_code: str, violation_data: Dict[str, Any]) -> str:
        """
        Get failure summary for violation
        
        Args:
            error_code: Error code
            violation_data: Violation data
            
        Returns:
            Failure summary
        """
        element = violation_data.get('element', 'Element')
        
        summaries = {
            'ErrNoAlt': f'{element} must have an alt attribute',
            'ErrEmptyAlt': f'{element} alt attribute must not be empty for informative images',
            'ErrEmptyHeading': f'{element} must contain text content',
            'ErrNoLabel': f'{element} must have an associated label',
            'ErrInsufficientContrast': 'Text must have sufficient color contrast against background',
            'ErrNoPageLanguage': 'HTML element must have a lang attribute',
            'ErrNoPageTitle': 'Page must have a title element',
        }
        
        return summaries.get(error_code, f'Fix the {error_code} issue')
    
    def calculate_score(self, test_result: TestResult) -> Dict[str, Any]:
        """
        Calculate accessibility score from test results
        
        Args:
            test_result: Test result
            
        Returns:
            Score dictionary
        """
        total_issues = len(test_result.violations) + len(test_result.warnings)
        critical_count = sum(1 for v in test_result.violations if v.impact == ImpactLevel.CRITICAL)
        serious_count = sum(1 for v in test_result.violations if v.impact == ImpactLevel.SERIOUS)
        
        # Simple scoring algorithm
        if critical_count > 0:
            score = 0  # Fail if any critical issues
        elif serious_count > 0:
            score = max(0, 50 - (serious_count * 10))
        elif total_issues > 0:
            score = max(0, 100 - (total_issues * 5))
        else:
            score = 100
        
        return {
            'score': score,
            'grade': self._get_grade(score),
            'critical_issues': critical_count,
            'serious_issues': serious_count,
            'total_issues': total_issues,
            'passes': len(test_result.passes)
        }
    
    def _get_grade(self, score: int) -> str:
        """Get letter grade from score"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'