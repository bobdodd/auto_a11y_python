"""
Database connection and repository management
"""

from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from pymongo.collection import Collection
from pymongo.errors import DocumentTooLarge
from bson import ObjectId
from datetime import datetime
import logging

from auto_a11y.models import (
    Project, Website, Page, TestResult,
    ProjectStatus, PageStatus
)
from auto_a11y.utils.document_size_handler import (
    validate_document_size_or_handle,
    create_size_error_result,
    get_document_size,
    format_size,
    DocumentSizeError
)

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection and operations"""
    
    def __init__(self, connection_uri: str, database_name: str):
        """
        Initialize database connection
        
        Args:
            connection_uri: MongoDB connection URI
            database_name: Name of database to use
        """
        self.client = MongoClient(connection_uri)
        self.db: MongoDatabase = self.client[database_name]
        
        # Collections
        self.projects: Collection = self.db.projects
        self.websites: Collection = self.db.websites
        self.pages: Collection = self.db.pages
        self.test_results: Collection = self.db.test_results
        self.document_references: Collection = self.db.document_references
        self.discovery_runs: Collection = self.db.discovery_runs
        
        # Create indexes
        self._create_indexes()
        
        logger.info(f"Connected to MongoDB database: {database_name}")
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        # Projects
        self.projects.create_index("name")
        self.projects.create_index("status")
        
        # Websites
        self.websites.create_index("project_id")
        self.websites.create_index("url")
        
        # Pages
        self.pages.create_index("website_id")
        self.pages.create_index("url")
        self.pages.create_index("status")
        self.pages.create_index([("website_id", 1), ("url", 1)], unique=True)
        
        # Test results
        self.test_results.create_index("page_id")
        self.test_results.create_index("test_date")
        
        # Document references
        self.document_references.create_index("website_id")
        self.document_references.create_index("document_url")
        self.document_references.create_index([("website_id", 1), ("document_url", 1)])
        
        # Discovery runs
        self.discovery_runs.create_index("website_id")
        self.discovery_runs.create_index("started_at")
        self.discovery_runs.create_index("is_latest")
        self.discovery_runs.create_index([("website_id", 1), ("is_latest", 1)])
        
        # Update pages index for discovery run
        self.pages.create_index("discovery_run_id")
        self.pages.create_index("is_in_latest_discovery")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # Ping the database
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def create_indexes(self):
        """Public method to create indexes"""
        self._create_indexes()
    
    def close(self):
        """Close database connection"""
        self.client.close()
        logger.info("Database connection closed")
    
    # Project operations
    
    def create_project(self, project: Project) -> str:
        """Create new project"""
        result = self.projects.insert_one(project.to_dict())
        project._id = result.inserted_id
        logger.info(f"Created project: {project.name} ({project.id})")
        return project.id
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        doc = self.projects.find_one({"_id": ObjectId(project_id)})
        return Project.from_dict(doc) if doc else None
    
    def get_projects(
        self, 
        status: Optional[ProjectStatus] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Project]:
        """Get projects with optional filtering"""
        query = {}
        if status:
            query["status"] = status.value
        
        docs = self.projects.find(query).limit(limit).skip(skip)
        return [Project.from_dict(doc) for doc in docs]
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        docs = self.projects.find()
        return [Project.from_dict(doc) for doc in docs]
    
    def update_project(self, project: Project) -> bool:
        """Update existing project"""
        project.update_timestamp()
        result = self.projects.replace_one(
            {"_id": project._id},
            project.to_dict()
        )
        return result.modified_count > 0
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project and related data"""
        # Delete related data
        websites = self.get_websites(project_id)
        for website in websites:
            self.delete_website(website.id)
        
        # Delete project
        result = self.projects.delete_one({"_id": ObjectId(project_id)})
        logger.info(f"Deleted project: {project_id}")
        return result.deleted_count > 0
    
    # Website operations
    
    def create_website(self, website: Website) -> str:
        """Create new website"""
        result = self.websites.insert_one(website.to_dict())
        website._id = result.inserted_id
        
        # Add to project's website list
        self.projects.update_one(
            {"_id": ObjectId(website.project_id)},
            {"$push": {"website_ids": website.id}}
        )
        
        logger.info(f"Created website: {website.url} ({website.id})")
        return website.id
    
    def get_website(self, website_id: str) -> Optional[Website]:
        """Get website by ID"""
        doc = self.websites.find_one({"_id": ObjectId(website_id)})
        return Website.from_dict(doc) if doc else None
    
    def get_websites(self, project_id: str) -> List[Website]:
        """Get all websites for a project"""
        docs = self.websites.find({"project_id": project_id})
        return [Website.from_dict(doc) for doc in docs]
    
    def update_website(self, website: Website) -> bool:
        """Update existing website"""
        result = self.websites.replace_one(
            {"_id": website._id},
            website.to_dict()
        )
        return result.modified_count > 0
    
    def delete_website(self, website_id: str) -> bool:
        """Delete website and related data"""
        website = self.get_website(website_id)
        if not website:
            return False
        
        # Delete related pages and test results
        pages = self.get_pages(website_id)
        for page in pages:
            self.delete_page(page.id)
        
        # Remove from project's website list
        self.projects.update_one(
            {"_id": ObjectId(website.project_id)},
            {"$pull": {"website_ids": website_id}}
        )
        
        # Delete website
        result = self.websites.delete_one({"_id": ObjectId(website_id)})
        logger.info(f"Deleted website: {website_id}")
        return result.deleted_count > 0
    
    # Page operations
    
    def create_page(self, page: Page) -> str:
        """Create new page"""
        # Check if page already exists
        existing = self.pages.find_one({
            "website_id": page.website_id,
            "url": page.url
        })
        
        if existing:
            page._id = existing["_id"]
            return str(existing["_id"])
        
        result = self.pages.insert_one(page.to_dict())
        page._id = result.inserted_id
        
        # Update website page count
        self.websites.update_one(
            {"_id": ObjectId(page.website_id)},
            {"$inc": {"page_count": 1}}
        )
        
        return page.id
    
    def get_page(self, page_id: str) -> Optional[Page]:
        """Get page by ID"""
        doc = self.pages.find_one({"_id": ObjectId(page_id)})
        return Page.from_dict(doc) if doc else None
    
    def get_page_by_url(self, website_id: str, url: str) -> Optional[Page]:
        """Get page by URL"""
        doc = self.pages.find_one({
            "website_id": website_id,
            "url": url
        })
        return Page.from_dict(doc) if doc else None
    
    def get_pages(
        self,
        website_id: str,
        status: Optional[PageStatus] = None,
        limit: int = 1000,
        skip: int = 0,
        latest_only: bool = True
    ) -> List[Page]:
        """Get pages for a website"""
        query = {"website_id": website_id}
        if status:
            query["status"] = status.value
        
        # By default, only return pages from latest discovery for testing
        if latest_only:
            query["is_in_latest_discovery"] = True
        
        docs = self.pages.find(query).limit(limit).skip(skip)
        return [Page.from_dict(doc) for doc in docs]
    
    def update_page(self, page: Page) -> bool:
        """Update existing page"""
        result = self.pages.replace_one(
            {"_id": page._id},
            page.to_dict()
        )
        return result.modified_count > 0
    
    def delete_page(self, page_id: str) -> bool:
        """Delete page and related test results"""
        # Delete test results
        self.test_results.delete_many({"page_id": page_id})
        
        # Update website page count
        page = self.get_page(page_id)
        if page:
            self.websites.update_one(
                {"_id": ObjectId(page.website_id)},
                {"$inc": {"page_count": -1}}
            )
        
        # Delete page
        result = self.pages.delete_one({"_id": ObjectId(page_id)})
        return result.deleted_count > 0
    
    def bulk_create_pages(self, pages: List[Page]) -> int:
        """Create multiple pages efficiently"""
        if not pages:
            return 0
        
        # Filter out existing pages
        new_pages = []
        for page in pages:
            existing = self.pages.find_one({
                "website_id": page.website_id,
                "url": page.url
            })
            if not existing:
                new_pages.append(page.to_dict())
        
        if not new_pages:
            return 0
        
        insert_result = self.pages.insert_many(new_pages)
        
        # Update website page count
        if new_pages:
            website_id = new_pages[0]["website_id"]
            # website_id is already a string, need to find by string ID
            update_result = self.websites.update_one(
                {"_id": ObjectId(website_id)},
                {"$inc": {"page_count": len(new_pages)}}
            )
            logger.info(f"Updated website {website_id} page count by {len(new_pages)}, modified={update_result.modified_count}")
        
        return len(insert_result.inserted_ids)
    
    # Test result operations
    
    def create_test_result(self, test_result: TestResult) -> str:
        """
        Create new test result with size limit handling

        POLICY: Never truncates violations/warnings/passes data.
        Only removes screenshots if necessary to fit within MongoDB 16MB limit.
        Creates an error report violation if result is still too large.
        """
        test_result_dict = test_result.to_dict()

        # Check and handle document size
        try:
            validated_dict, size_report = validate_document_size_or_handle(
                test_result_dict,
                document_type="test_result"
            )

            if size_report and size_report.get('screenshot_removed'):
                logger.warning(
                    f"Screenshot removed from test result for page {test_result.page_id}: "
                    f"{format_size(size_report['original_size'])} -> "
                    f"{format_size(size_report['final_size'])}"
                )

            # Insert the validated document
            result = self.test_results.insert_one(validated_dict)
            test_result._id = result.inserted_id

        except DocumentSizeError as e:
            logger.error(
                f"Test result too large even after removing screenshot for page {test_result.page_id}: "
                f"{format_size(e.size)} - Creating error report"
            )

            # Create an error result with the size limit violation
            error_result = create_size_error_result(
                page_id=test_result.page_id,
                test_date=test_result.test_date,
                duration_ms=test_result.duration_ms,
                error_details={
                    'size': e.size,
                    'size_formatted': format_size(e.size),
                    'counts': {
                        'violations': test_result.violation_count,
                        'warnings': test_result.warning_count,
                        'info': test_result.info_count,
                        'discovery': test_result.discovery_count,
                        'passes': test_result.pass_count
                    }
                }
            )

            result = self.test_results.insert_one(error_result)
            test_result._id = result.inserted_id

        except DocumentTooLarge as e:
            # MongoDB rejected the document - this shouldn't happen after our validation
            logger.error(f"MongoDB rejected document (should not happen after validation): {e}")

            # Create size error result
            error_result = create_size_error_result(
                page_id=test_result.page_id,
                test_date=test_result.test_date,
                duration_ms=test_result.duration_ms,
                error_details={
                    'size': get_document_size(test_result_dict),
                    'size_formatted': format_size(get_document_size(test_result_dict)),
                    'mongodb_error': str(e),
                    'counts': {
                        'violations': test_result.violation_count,
                        'warnings': test_result.warning_count,
                        'info': test_result.info_count,
                        'discovery': test_result.discovery_count,
                        'passes': test_result.pass_count
                    }
                }
            )

            result = self.test_results.insert_one(error_result)
            test_result._id = result.inserted_id

        # Update page with latest test info
        page = self.get_page(test_result.page_id)
        if page:
            page.last_tested = test_result.test_date
            page.status = PageStatus.TESTED
            page.violation_count = test_result.violation_count
            page.warning_count = test_result.warning_count
            page.info_count = test_result.info_count
            page.discovery_count = test_result.discovery_count
            page.pass_count = test_result.pass_count
            page.test_duration_ms = test_result.duration_ms
            self.update_page(page)

        logger.info(f"Created test result for page: {test_result.page_id}")
        return test_result.id
    
    def get_test_result(self, result_id: str) -> Optional[TestResult]:
        """Get test result by ID"""
        doc = self.test_results.find_one({"_id": ObjectId(result_id)})
        return TestResult.from_dict(doc) if doc else None
    
    def get_latest_test_result(self, page_id: str) -> Optional[TestResult]:
        """Get most recent test result for a page"""
        doc = self.test_results.find_one(
            {"page_id": page_id},
            sort=[("test_date", -1)]
        )
        return TestResult.from_dict(doc) if doc else None
    
    def get_test_results(
        self,
        page_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[TestResult]:
        """Get test results with optional filtering"""
        query = {}
        if page_id:
            query["page_id"] = page_id
        if start_date or end_date:
            query["test_date"] = {}
            if start_date:
                query["test_date"]["$gte"] = start_date
            if end_date:
                query["test_date"]["$lte"] = end_date
        
        docs = self.test_results.find(query).limit(limit).skip(skip).sort("test_date", -1)
        return [TestResult.from_dict(doc) for doc in docs]
    
    def delete_test_result(self, result_id: str) -> bool:
        """Delete test result"""
        result = self.test_results.delete_one({"_id": ObjectId(result_id)})
        return result.deleted_count > 0
    
    # Statistics
    
    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get statistics for a project"""
        websites = self.get_websites(project_id)
        
        total_pages = 0
        tested_pages = 0
        total_violations = 0
        total_warnings = 0
        
        for website in websites:
            pages = self.get_pages(website.id)
            total_pages += len(pages)
            
            for page in pages:
                if page.status == PageStatus.TESTED:
                    tested_pages += 1
                    total_violations += page.violation_count
                    total_warnings += page.warning_count
        
        return {
            "website_count": len(websites),
            "total_pages": total_pages,
            "tested_pages": tested_pages,
            "untested_pages": total_pages - tested_pages,
            "total_violations": total_violations,
            "total_warnings": total_warnings,
            "test_coverage": (tested_pages / total_pages * 100) if total_pages > 0 else 0
        }
    
    # Document Reference methods
    def add_document_reference(self, doc_ref: 'DocumentReference') -> str:
        """Add or update a document reference"""
        from auto_a11y.models import DocumentReference
        
        # Check if this document already exists for this website
        existing = self.document_references.find_one({
            'website_id': doc_ref.website_id,
            'document_url': doc_ref.document_url
        })
        
        if existing:
            # Update existing reference
            self.document_references.update_one(
                {'_id': existing['_id']},
                {
                    '$set': {
                        'last_seen': doc_ref.last_seen,
                        'via_redirect': doc_ref.via_redirect or existing.get('via_redirect', False)
                    },
                    '$inc': {'seen_count': 1},
                    '$addToSet': {'referring_pages': doc_ref.referring_page_url}
                }
            )
            return str(existing['_id'])
        else:
            # Add new reference
            doc_data = doc_ref.to_dict()
            doc_data['referring_pages'] = [doc_ref.referring_page_url]
            result = self.document_references.insert_one(doc_data)
            return str(result.inserted_id)
    
    def get_document_references(self, website_id: str, internal_only: bool = None) -> List['DocumentReference']:
        """Get document references for a website"""
        from auto_a11y.models import DocumentReference
        
        query = {'website_id': website_id}
        if internal_only is not None:
            query['is_internal'] = internal_only
        
        docs = self.document_references.find(query)
        return [DocumentReference.from_dict(doc) for doc in docs]
    
    def get_all_document_references(self, project_id: str = None) -> List['DocumentReference']:
        """Get all document references, optionally filtered by project"""
        from auto_a11y.models import DocumentReference
        
        if project_id:
            # Get all websites for the project first
            websites = self.get_websites(project_id)
            website_ids = [w.id for w in websites]
            docs = self.document_references.find({'website_id': {'$in': website_ids}})
        else:
            docs = self.document_references.find({})
        
        return [DocumentReference.from_dict(doc) for doc in docs]
    
    def delete_document_references(self, website_id: str) -> bool:
        """Delete all document references for a website"""
        result = self.document_references.delete_many({'website_id': website_id})
        return result.deleted_count > 0
    
    # Discovery Run methods
    def create_discovery_run(self, discovery_run: 'DiscoveryRun') -> str:
        """Create a new discovery run"""
        from auto_a11y.models import DiscoveryRun
        
        # Mark all previous runs for this website as not latest
        self.discovery_runs.update_many(
            {'website_id': discovery_run.website_id},
            {'$set': {'is_latest': False}}
        )
        
        # Insert new discovery run
        result = self.discovery_runs.insert_one(discovery_run.to_dict())
        discovery_run._id = result.inserted_id
        logger.info(f"Created discovery run {discovery_run.id} for website {discovery_run.website_id}")
        return discovery_run.id
    
    def get_discovery_run(self, discovery_run_id: str) -> Optional['DiscoveryRun']:
        """Get a discovery run by ID"""
        from auto_a11y.models import DiscoveryRun
        
        doc = self.discovery_runs.find_one({'_id': ObjectId(discovery_run_id)})
        return DiscoveryRun.from_dict(doc) if doc else None
    
    def get_latest_discovery_run(self, website_id: str) -> Optional['DiscoveryRun']:
        """Get the latest discovery run for a website"""
        from auto_a11y.models import DiscoveryRun
        
        doc = self.discovery_runs.find_one({
            'website_id': website_id,
            'is_latest': True
        })
        return DiscoveryRun.from_dict(doc) if doc else None
    
    def get_discovery_runs(self, website_id: str) -> List['DiscoveryRun']:
        """Get all discovery runs for a website, ordered by date descending"""
        from auto_a11y.models import DiscoveryRun
        
        docs = self.discovery_runs.find({'website_id': website_id}).sort('started_at', -1)
        return [DiscoveryRun.from_dict(doc) for doc in docs]
    
    def update_discovery_run(self, discovery_run: 'DiscoveryRun') -> bool:
        """Update a discovery run"""
        result = self.discovery_runs.update_one(
            {'_id': discovery_run._id},
            {'$set': discovery_run.to_dict()}
        )
        return result.modified_count > 0
    
    def bulk_create_pages_with_discovery(self, pages: List[Page], discovery_run_id: str) -> int:
        """Create multiple pages with discovery run tracking"""
        if not pages:
            return 0
        
        # Get existing pages for this website
        website_id = pages[0].website_id
        existing_urls = set()
        for doc in self.pages.find({'website_id': website_id}, {'url': 1}):
            existing_urls.add(doc['url'])
        
        # Mark all existing pages as not in latest discovery
        self.pages.update_many(
            {'website_id': website_id},
            {'$set': {'is_in_latest_discovery': False}}
        )
        
        # Process new and existing pages
        new_pages = []
        updated_count = 0
        
        for page in pages:
            page.discovery_run_id = discovery_run_id
            page.is_in_latest_discovery = True
            
            if page.url in existing_urls:
                # Update existing page
                self.pages.update_one(
                    {'website_id': website_id, 'url': page.url},
                    {'$set': {
                        'discovery_run_id': discovery_run_id,
                        'is_in_latest_discovery': True,
                        'discovered_at': page.discovered_at,
                        'title': page.title,
                        'depth': page.depth,
                        'status': page.status.value if hasattr(page.status, 'value') else page.status,
                        'error_reason': page.error_reason
                    }}
                )
                updated_count += 1
            else:
                # New page
                new_pages.append(page.to_dict())
        
        # Insert new pages
        if new_pages:
            insert_result = self.pages.insert_many(new_pages)
            
            # Update website page count
            self.websites.update_one(
                {"_id": ObjectId(website_id)},
                {"$inc": {"page_count": len(new_pages)}}
            )
            logger.info(f"Added {len(new_pages)} new pages, updated {updated_count} existing pages")
            
            return len(insert_result.inserted_ids) + updated_count
        
        return updated_count
    
    def get_pages_for_testing(self, website_id: str, status: Optional[PageStatus] = None) -> List[Page]:
        """Get pages for testing (only from latest discovery)"""
        query = {
            'website_id': website_id,
            'is_in_latest_discovery': True
        }
        
        if status:
            query['status'] = status.value
        
        docs = self.pages.find(query)
        return [Page.from_dict(doc) for doc in docs]
    
    def compare_discoveries(self, website_id: str, old_run_id: str, new_run_id: str) -> Dict[str, Any]:
        """Compare two discovery runs to find added/removed pages"""
        
        # Get pages from old discovery
        old_pages = set()
        for doc in self.pages.find({'website_id': website_id, 'discovery_run_id': old_run_id}, {'url': 1}):
            old_pages.add(doc['url'])
        
        # Get pages from new discovery
        new_pages = set()
        for doc in self.pages.find({'website_id': website_id, 'discovery_run_id': new_run_id}, {'url': 1}):
            new_pages.add(doc['url'])
        
        # Calculate differences
        pages_added = new_pages - old_pages
        pages_removed = old_pages - new_pages
        pages_unchanged = old_pages & new_pages
        
        return {
            'pages_added': list(pages_added),
            'pages_removed': list(pages_removed),
            'pages_unchanged': list(pages_unchanged),
            'added_count': len(pages_added),
            'removed_count': len(pages_removed),
            'unchanged_count': len(pages_unchanged)
        }