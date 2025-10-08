"""
MongoDB Document Size Handler

Handles MongoDB's 16MB document size limit gracefully by:
1. Reducing screenshot quality (already done at 80%)
2. Removing screenshots if necessary
3. Generating error reports if still too large

POLICY: NEVER truncate actual test results (violations, warnings, passes, etc.).
Only optimize/remove screenshots and generate clear error reports for oversized results.
"""

import json
import logging
from typing import Dict, Any, Tuple, Optional
from bson import encode

logger = logging.getLogger(__name__)

# MongoDB limits
MONGODB_MAX_DOCUMENT_SIZE = 16 * 1024 * 1024  # 16 MB in bytes
SAFE_DOCUMENT_SIZE = int(MONGODB_MAX_DOCUMENT_SIZE * 0.9)  # 90% of max for safety buffer


class DocumentSizeError(Exception):
    """Raised when a document exceeds MongoDB size limits even after screenshot removal"""
    def __init__(self, message: str, size: int, page_id: str = None):
        super().__init__(message)
        self.size = size
        self.page_id = page_id


def get_document_size(document: Dict[str, Any]) -> int:
    """
    Calculate the BSON size of a document

    Args:
        document: Dictionary to measure

    Returns:
        Size in bytes
    """
    try:
        # Encode to BSON to get actual MongoDB storage size
        bson_data = encode(document)
        return len(bson_data)
    except Exception as e:
        logger.error(f"Error calculating document size: {e}")
        # Fallback to JSON size estimate (usually close enough)
        try:
            return len(json.dumps(document, default=str).encode('utf-8'))
        except:
            return 0


def check_document_size(document: Dict[str, Any],
                       max_size: int = SAFE_DOCUMENT_SIZE) -> Tuple[bool, int]:
    """
    Check if document size is within limits

    Args:
        document: Document to check
        max_size: Maximum allowed size in bytes

    Returns:
        Tuple of (is_within_limit, actual_size)
    """
    size = get_document_size(document)
    return (size <= max_size, size)


def format_size(size_bytes: int) -> str:
    """
    Format byte size as human-readable string

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "2.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def handle_oversized_test_result(test_result_dict: Dict[str, Any],
                                 max_size: int = SAFE_DOCUMENT_SIZE) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle oversized test results by removing screenshots if necessary.
    NEVER truncates actual test data (violations, warnings, passes).

    Strategy:
    1. Check current size
    2. If over limit, remove screenshot path (screenshots stored separately anyway)
    3. If still over limit, create error report document

    Args:
        test_result_dict: Test result dictionary
        max_size: Maximum allowed size in bytes

    Returns:
        Tuple of (processed_result, size_report or None)
    """
    result = test_result_dict.copy()
    size_report = {
        'original_size': get_document_size(result),
        'final_size': 0,
        'actions_taken': [],
        'screenshot_removed': False,
        'size_error': False
    }

    current_size = size_report['original_size']

    # If within limits, no action needed
    if current_size <= max_size:
        size_report['final_size'] = current_size
        return result, None

    logger.warning(f"Test result exceeds size limit: {format_size(current_size)} > {format_size(max_size)}")

    # Step 1: Remove screenshot_path (screenshot file is saved separately anyway)
    if 'screenshot_path' in result and result['screenshot_path']:
        original_path = result['screenshot_path']
        result['screenshot_path'] = None
        size_report['screenshot_removed'] = True
        size_report['actions_taken'].append({
            'action': 'removed_screenshot_path',
            'original_path': original_path,
            'reason': 'Document too large'
        })
        current_size = get_document_size(result)
        logger.info(f"After removing screenshot path: {format_size(current_size)}")

    size_report['final_size'] = current_size

    # If still over limit after removing screenshot, we have a problem
    if current_size > max_size:
        violation_count = len(result.get('violations', []))
        warning_count = len(result.get('warnings', []))
        info_count = len(result.get('info', []))
        discovery_count = len(result.get('discovery', []))
        pass_count = len(result.get('passes', []))

        logger.error(
            f"Test result still too large after screenshot removal: {format_size(current_size)}. "
            f"Violations: {violation_count}, Warnings: {warning_count}, "
            f"Info: {info_count}, Discovery: {discovery_count}, Passes: {pass_count}"
        )

        size_report['size_error'] = True
        size_report['actions_taken'].append({
            'action': 'size_limit_exceeded',
            'size_after_optimization': current_size,
            'counts': {
                'violations': violation_count,
                'warnings': warning_count,
                'info': info_count,
                'discovery': discovery_count,
                'passes': pass_count
            }
        })

        # We can't store the full result, so we'll raise an error with the report
        raise DocumentSizeError(
            f"Test result too large even after removing screenshot: {format_size(current_size)} > {format_size(max_size)}",
            size=current_size,
            page_id=result.get('page_id')
        )

    # Add size metadata to result if screenshot was removed
    if size_report['screenshot_removed']:
        result['_size_handling'] = {
            'screenshot_removed': True,
            'original_size': size_report['original_size'],
            'final_size': size_report['final_size'],
            'message': 'Screenshot path removed to fit MongoDB size limits'
        }

    return result, size_report


def create_size_error_result(page_id: str, test_date, duration_ms: int,
                            error_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a minimal error result when test results are too large to store

    Args:
        page_id: Page ID
        test_date: Test date
        duration_ms: Test duration
        error_details: Details about the size error

    Returns:
        Minimal error result document
    """
    return {
        'page_id': page_id,
        'test_date': test_date,
        'duration_ms': duration_ms,
        'violations': [{
            'id': 'ErrSizeLimitExceeded',
            'impact': 'high',
            'touchpoint': 'system',
            'description': (
                f"This page generated test results that exceed MongoDB's size limit "
                f"({error_details.get('size_formatted', 'unknown')}). "
                f"The page has {error_details.get('counts', {}).get('violations', 0)} violations, "
                f"{error_details.get('counts', {}).get('warnings', 0)} warnings, "
                f"and {error_details.get('counts', {}).get('passes', 0)} passes. "
                f"This indicates severe accessibility issues requiring immediate attention."
            ),
            'xpath': '/',
            'element': 'DOCUMENT',
            'wcag_criteria': [],
            'metadata': error_details
        }],
        'warnings': [],
        'info': [],
        'discovery': [],
        'passes': [],
        'ai_findings': [],
        'screenshot_path': None,
        'error': f"Size limit exceeded: {error_details.get('size_formatted', 'unknown')}",
        '_size_error': True,
        '_size_error_details': error_details
    }


def validate_document_size_or_handle(document: Dict[str, Any],
                                    document_type: str = "document",
                                    max_size: int = SAFE_DOCUMENT_SIZE) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Validate document size and handle if necessary (screenshot removal only)

    Args:
        document: Document to validate
        document_type: Type of document (for logging)
        max_size: Maximum allowed size

    Returns:
        Tuple of (validated_document, size_report or None)

    Raises:
        DocumentSizeError: If document is too large even after screenshot removal
    """
    is_valid, size = check_document_size(document, max_size)

    if is_valid:
        logger.debug(f"{document_type} size OK: {format_size(size)}")
        return document, None

    logger.warning(f"{document_type} size exceeds limit: {format_size(size)} > {format_size(max_size)}")

    # Attempt to handle if it's a test result
    if 'violations' in document or 'test_date' in document:
        try:
            handled, report = handle_oversized_test_result(document, max_size)
            if report:
                logger.info(f"Successfully handled oversized {document_type}: {format_size(report['original_size'])} -> {format_size(report['final_size'])}")
            return handled, report
        except DocumentSizeError:
            # Re-raise - caller will handle creating error result
            raise
    else:
        # For non-test-result documents, we can't auto-handle
        raise DocumentSizeError(
            f"{document_type} exceeds size limit: {format_size(size)} > {format_size(max_size)}",
            size=size
        )