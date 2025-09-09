"""
Document Reference model for tracking electronic documents found during scraping
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
from bson import ObjectId


class DocumentType(Enum):
    """Common document types"""
    PDF = "application/pdf"
    WORD = "application/msword"
    WORDX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    EXCEL = "application/vnd.ms-excel"
    EXCELX = "application/vnd.openxmlformats-officedocument.spreadsheetml.document"
    POWERPOINT = "application/vnd.ms-powerpoint"
    POWERPOINTX = "application/vnd.openxmlformats-officedocument.presentationml.document"
    RTF = "application/rtf"
    TEXT = "text/plain"
    CSV = "text/csv"
    ZIP = "application/zip"
    UNKNOWN = "application/octet-stream"
    
    @classmethod
    def from_extension(cls, ext: str) -> 'DocumentType':
        """Get document type from file extension"""
        ext = ext.lower().lstrip('.')
        extension_map = {
            'pdf': cls.PDF,
            'doc': cls.WORD,
            'docx': cls.WORDX,
            'xls': cls.EXCEL,
            'xlsx': cls.EXCELX,
            'ppt': cls.POWERPOINT,
            'pptx': cls.POWERPOINTX,
            'rtf': cls.RTF,
            'txt': cls.TEXT,
            'csv': cls.CSV,
            'zip': cls.ZIP,
            'rar': cls.ZIP,
            '7z': cls.ZIP
        }
        return extension_map.get(ext, cls.UNKNOWN)


@dataclass
class DocumentReference:
    """Model for document references found on websites"""
    
    website_id: str
    document_url: str
    referring_page_url: str
    mime_type: str
    is_internal: bool  # True if document is within the base URL domain
    link_text: Optional[str] = None  # The text of the link pointing to the document
    file_extension: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    seen_count: int = 1  # Track how many times this document is referenced
    via_redirect: bool = False  # True if found through address rewriting/redirect
    _id: Optional[ObjectId] = None
    
    @property
    def id(self) -> str:
        """Get document reference ID as string"""
        return str(self._id) if self._id else None
    
    @property
    def document_type_display(self) -> str:
        """Get human-friendly document type"""
        type_map = {
            DocumentType.PDF.value: "PDF",
            DocumentType.WORD.value: "Word Document",
            DocumentType.WORDX.value: "Word Document",
            DocumentType.EXCEL.value: "Excel Spreadsheet",
            DocumentType.EXCELX.value: "Excel Spreadsheet",
            DocumentType.POWERPOINT.value: "PowerPoint Presentation",
            DocumentType.POWERPOINTX.value: "PowerPoint Presentation",
            DocumentType.RTF.value: "Rich Text Document",
            DocumentType.TEXT.value: "Text File",
            DocumentType.CSV.value: "CSV File",
            DocumentType.ZIP.value: "Archive",
        }
        return type_map.get(self.mime_type, "Document")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        data = {
            'website_id': self.website_id,
            'document_url': self.document_url,
            'referring_page_url': self.referring_page_url,
            'mime_type': self.mime_type,
            'is_internal': self.is_internal,
            'link_text': self.link_text,
            'file_extension': self.file_extension,
            'discovered_at': self.discovered_at,
            'last_seen': self.last_seen,
            'seen_count': self.seen_count,
            'via_redirect': self.via_redirect
        }
        if self._id:
            data['_id'] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentReference':
        """Create from MongoDB document"""
        return cls(
            website_id=data['website_id'],
            document_url=data['document_url'],
            referring_page_url=data['referring_page_url'],
            mime_type=data['mime_type'],
            is_internal=data['is_internal'],
            link_text=data.get('link_text'),
            file_extension=data.get('file_extension'),
            discovered_at=data.get('discovered_at', datetime.now()),
            last_seen=data.get('last_seen', datetime.now()),
            seen_count=data.get('seen_count', 1),
            via_redirect=data.get('via_redirect', False),
            _id=data.get('_id')
        )