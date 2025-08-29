"""
Database connection and repository management
"""

from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from pymongo.collection import Collection
from bson import ObjectId
from datetime import datetime
import logging

from auto_a11y.models import (
    Project, Website, Page, TestResult,
    ProjectStatus, PageStatus
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
        skip: int = 0
    ) -> List[Page]:
        """Get pages for a website"""
        query = {"website_id": website_id}
        if status:
            query["status"] = status.value
        
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
        """Create new test result"""
        result = self.test_results.insert_one(test_result.to_dict())
        test_result._id = result.inserted_id
        
        # Update page with latest test info
        page = self.get_page(test_result.page_id)
        if page:
            page.last_tested = test_result.test_date
            page.status = PageStatus.TESTED
            page.violation_count = test_result.violation_count
            page.warning_count = test_result.warning_count
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