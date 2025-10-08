"""
Utility modules for Auto A11y
"""

from auto_a11y.utils.document_size_handler import (
    get_document_size,
    check_document_size,
    format_size,
    handle_oversized_test_result,
    create_size_error_result,
    validate_document_size_or_handle,
    DocumentSizeError,
    MONGODB_MAX_DOCUMENT_SIZE,
    SAFE_DOCUMENT_SIZE
)

__all__ = [
    'get_document_size',
    'check_document_size',
    'format_size',
    'handle_oversized_test_result',
    'create_size_error_result',
    'validate_document_size_or_handle',
    'DocumentSizeError',
    'MONGODB_MAX_DOCUMENT_SIZE',
    'SAFE_DOCUMENT_SIZE'
]
