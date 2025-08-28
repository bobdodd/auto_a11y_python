"""
Project management business logic
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from auto_a11y.models import Project, ProjectStatus, Website
from auto_a11y.core.database import Database

logger = logging.getLogger(__name__)


class ProjectManager:
    """Manages project operations"""
    
    def __init__(self, database: Database):
        """
        Initialize project manager
        
        Args:
            database: Database connection
        """
        self.db = database
    
    def create_project(
        self,
        name: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None
    ) -> Project:
        """
        Create a new project
        
        Args:
            name: Project name
            description: Project description
            config: Project configuration
            
        Returns:
            Created project
        """
        # Check if name exists
        existing = self.db.projects.find_one({'name': name})
        if existing:
            raise ValueError(f"Project '{name}' already exists")
        
        # Create project
        project = Project(
            name=name,
            description=description,
            status=ProjectStatus.ACTIVE,
            config=config or {}
        )
        
        project_id = self.db.create_project(project)
        project._id = project_id
        
        logger.info(f"Created project: {name} ({project_id})")
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """
        Get project by ID
        
        Args:
            project_id: Project ID
            
        Returns:
            Project or None
        """
        return self.db.get_project(project_id)
    
    def list_projects(
        self,
        status: Optional[ProjectStatus] = None,
        limit: int = 100
    ) -> List[Project]:
        """
        List projects with optional filtering
        
        Args:
            status: Filter by status
            limit: Maximum number of projects
            
        Returns:
            List of projects
        """
        return self.db.get_projects(status=status, limit=limit)
    
    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[ProjectStatus] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update project details
        
        Args:
            project_id: Project ID
            name: New name
            description: New description
            status: New status
            config: New configuration
            
        Returns:
            True if updated successfully
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Update fields
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if status is not None:
            project.status = status
        if config is not None:
            project.config.update(config)
        
        return self.db.update_project(project)
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete project and all related data
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted successfully
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        return self.db.delete_project(project_id)
    
    def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """
        Get project statistics
        
        Args:
            project_id: Project ID
            
        Returns:
            Project statistics
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        return self.db.get_project_stats(project_id)
    
    def archive_project(self, project_id: str) -> bool:
        """
        Archive a project
        
        Args:
            project_id: Project ID
            
        Returns:
            True if archived successfully
        """
        return self.update_project(project_id, status=ProjectStatus.ARCHIVED)
    
    def activate_project(self, project_id: str) -> bool:
        """
        Activate an archived project
        
        Args:
            project_id: Project ID
            
        Returns:
            True if activated successfully
        """
        return self.update_project(project_id, status=ProjectStatus.ACTIVE)