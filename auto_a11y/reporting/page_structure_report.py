"""
Site Structure Report Generator
Generates a tree view of website pages based on URL hierarchy
"""

import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, unquote
from datetime import datetime
import json
import csv
from io import StringIO
from collections import defaultdict

from auto_a11y.models import Page, PageStatus

logger = logging.getLogger(__name__)


class PageNode:
    """Represents a node in the page tree structure"""
    
    def __init__(self, name: str, url: str = None, is_directory: bool = False):
        self.name = name
        self.url = url
        self.is_directory = is_directory
        self.children = []
        self.page_data = None
        self.stats = {
            'total_pages': 0,
            'tested_pages': 0,
            'pages_with_issues': 0,
            'total_violations': 0,
            'total_warnings': 0
        }
    
    def add_child(self, child: 'PageNode'):
        """Add a child node"""
        self.children.append(child)
    
    def find_or_create_child(self, name: str, is_directory: bool = False) -> 'PageNode':
        """Find existing child or create new one"""
        for child in self.children:
            if child.name == name and child.is_directory == is_directory:
                return child
        
        new_child = PageNode(name, is_directory=is_directory)
        self.add_child(new_child)
        return new_child
    
    def update_stats(self, page: Page):
        """Update statistics based on page data"""
        self.stats['total_pages'] += 1
        if page.status == PageStatus.TESTED:
            self.stats['tested_pages'] += 1
        if page.has_issues:
            self.stats['pages_with_issues'] += 1
        self.stats['total_violations'] += page.violation_count
        self.stats['total_warnings'] += page.warning_count
    
    def aggregate_stats(self):
        """Aggregate statistics from children"""
        for child in self.children:
            child.aggregate_stats()
            self.stats['total_pages'] += child.stats['total_pages']
            self.stats['tested_pages'] += child.stats['tested_pages']
            self.stats['pages_with_issues'] += child.stats['pages_with_issues']
            self.stats['total_violations'] += child.stats['total_violations']
            self.stats['total_warnings'] += child.stats['total_warnings']
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            'name': self.name,
            'url': self.url,
            'is_directory': self.is_directory,
            'stats': self.stats,
            'children': [child.to_dict() for child in self.children]
        }


class PageStructureReport:
    """Generates site structure tree report"""
    
    def __init__(self, database, website, pages: List[Page], project=None):
        """
        Initialize site structure report
        
        Args:
            database: Database instance
            website: Website object
            pages: List of pages to include in report
            project: Optional Project object
        """
        self.database = database
        self.website = website
        self.pages = pages
        self.project = project
        self.root = None
        self.tree_data = None
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate the page structure report
        
        Returns:
            Report data dictionary
        """
        logger.info(f"Generating site structure report for website {self.website.id}")
        
        # Build the tree structure
        self.root = self._build_tree()
        
        # Aggregate statistics
        self.root.aggregate_stats()
        
        # Generate report data
        self.tree_data = {
            'report_type': 'site_structure',
            'project': {
                'id': self.project.id if self.project else None,
                'name': self.project.name if self.project else 'No Project'
            },
            'website': {
                'id': self.website.id,
                'name': self.website.name,
                'url': self.website.url
            },
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_pages': len(self.pages),
                'tested_pages': sum(1 for p in self.pages if p.status == PageStatus.TESTED),
                'pages_with_issues': sum(1 for p in self.pages if p.has_issues),
                'total_violations': sum(p.violation_count for p in self.pages),
                'total_warnings': sum(p.warning_count for p in self.pages),
                'max_depth': self._calculate_max_depth(self.root, 0)
            },
            'tree': self.root.to_dict()
        }
        
        logger.info(f"Site structure report generated with {len(self.pages)} pages")
        return self.tree_data
    
    def _build_tree(self) -> PageNode:
        """
        Build tree structure from pages
        
        Returns:
            Root node of the tree
        """
        # Parse the website URL to get the base
        base_url = urlparse(self.website.url)
        root_name = base_url.netloc or 'Root'
        root = PageNode(root_name, self.website.url, is_directory=True)
        
        # Process each page
        for page in self.pages:
            self._add_page_to_tree(root, page)
        
        return root
    
    def _add_page_to_tree(self, root: PageNode, page: Page):
        """
        Add a page to the tree structure
        
        Args:
            root: Root node of the tree
            page: Page to add
        """
        parsed_url = urlparse(page.url)
        
        # Get the path components
        path = parsed_url.path
        if not path or path == '/':
            # This is the homepage
            root.url = page.url
            root.page_data = page
            root.update_stats(page)
            return
        
        # Split path into components
        path_parts = [p for p in path.split('/') if p]
        
        # Handle query parameters and fragments
        if parsed_url.query:
            # Add query as a separate component
            query_part = f"?{parsed_url.query}"
            path_parts.append(query_part)
        
        if parsed_url.fragment:
            # Add fragment as a separate component
            fragment_part = f"#{parsed_url.fragment}"
            path_parts.append(fragment_part)
        
        # Navigate/create the tree structure
        current_node = root
        
        for i, part in enumerate(path_parts):
            # Decode URL encoding
            part = unquote(part)
            
            # Check if this is the last part (the actual page)
            is_last = (i == len(path_parts) - 1)
            
            if is_last:
                # This is a page, not a directory
                child = current_node.find_or_create_child(part, is_directory=False)
                child.url = page.url
                child.page_data = page
                child.update_stats(page)
            else:
                # This is a directory
                child = current_node.find_or_create_child(part, is_directory=True)
                if not child.url:
                    # Set URL for directory based on path so far
                    dir_path = '/'.join(path_parts[:i+1])
                    child.url = f"{parsed_url.scheme}://{parsed_url.netloc}/{dir_path}/"
            
            current_node = child
    
    def _calculate_max_depth(self, node: PageNode, current_depth: int) -> int:
        """
        Calculate maximum depth of the tree
        
        Args:
            node: Current node
            current_depth: Current depth level
            
        Returns:
            Maximum depth found
        """
        if not node.children:
            return current_depth
        
        max_depth = current_depth
        for child in node.children:
            child_depth = self._calculate_max_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def to_html(self) -> str:
        """
        Generate HTML report with interactive tree view
        
        Returns:
            HTML string
        """
        if not self.tree_data:
            self.generate()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Site Structure Report - {self.website.name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .tree {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.8;
        }}
        .tree-node {{
            padding: 4px 0;
            margin: 2px 0;
            border-radius: 4px;
            transition: background-color 0.2s;
        }}
        .tree-node:hover {{
            background-color: rgba(0, 123, 255, 0.05);
        }}
        .tree-children {{
            margin-left: 35px;
            padding-left: 10px;
            border-left: 1px solid #e0e0e0;
        }}
        .tree-root > .tree-children {{
            margin-left: 0;
            padding-left: 0;
            border-left: none;
        }}
        .node-toggle {{
            cursor: pointer;
            user-select: none;
            margin-right: 8px;
            display: inline-block;
            width: 20px;
            text-align: center;
            font-family: monospace;
            font-size: 14px;
            color: #666;
            transition: transform 0.2s ease;
            transform-origin: center;
        }}
        .node-toggle.expanded {{
            transform: rotate(90deg);
        }}
        .node-toggle:hover {{
            color: #333;
        }}
        .node-icon {{
            margin-right: 8px;
            font-size: 16px;
        }}
        .node-name {{
            font-weight: 500;
            color: #333;
            word-break: break-word;
            max-width: 600px;
            display: inline-block;
            vertical-align: middle;
        }}
        .node-url {{
            color: #007bff;
            text-decoration: none;
            word-break: break-word;
            max-width: 600px;
            display: inline-block;
            vertical-align: middle;
        }}
        .node-url:hover {{
            text-decoration: underline;
            color: #0056b3;
        }}
        .node-stats {{
            font-size: 0.85em;
            color: #666;
            margin-left: 12px;
            display: inline-block;
        }}
        .stats-badge {{
            font-size: 0.75em;
            margin-left: 6px;
            padding: 2px 6px;
        }}
        .tree-collapsed {{
            display: none !important;
        }}
        .legend {{
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 20px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .legend > div {{
            margin: 5px 0;
        }}
        /* Directory nodes should be bold */
        .tree-node.is-directory > .node-name {{
            font-weight: 600;
        }}
        /* Add some visual hierarchy */
        .tree-children .tree-children {{
            opacity: 0.95;
        }}
        /* Improve button styling */
        .btn-outline-primary, .btn-outline-secondary {{
            margin-right: 5px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <div class="row">
            <div class="col-12">
                <h1>Site Structure Report</h1>
                <p class="text-muted">
                    <strong>Project:</strong> {self.project.name if self.project else 'No Project'}<br>
                    <strong>Website:</strong> {self.website.name} ({self.website.url})<br>
                    <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Summary</h5>
                        <ul class="list-unstyled">
                            <li><strong>Total Pages:</strong> {self.tree_data['summary']['total_pages']}</li>
                            <li><strong>Tested Pages:</strong> {self.tree_data['summary']['tested_pages']}</li>
                            <li><strong>Pages with Issues:</strong> {self.tree_data['summary']['pages_with_issues']}</li>
                            <li><strong>Total Violations:</strong> <span class="text-danger">{self.tree_data['summary']['total_violations']}</span></li>
                            <li><strong>Total Warnings:</strong> <span class="text-warning">{self.tree_data['summary']['total_warnings']}</span></li>
                            <li><strong>Max Depth:</strong> {self.tree_data['summary']['max_depth']} levels</li>
                        </ul>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-body">
                        <h5 class="card-title">Legend</h5>
                        <div class="legend">
                            <div><i class="bi bi-folder text-warning"></i> Directory/Section</div>
                            <div><i class="bi bi-file-earmark text-primary"></i> Page</div>
                            <div><span class="badge bg-success">Tested</span> Page has been tested</div>
                            <div><span class="badge bg-danger">Issues</span> Page has accessibility issues</div>
                            <div><span class="badge bg-secondary">Not tested</span> Page not yet tested</div>
                        </div>
                        <button class="btn btn-sm btn-outline-primary" onclick="expandAll()">
                            <i class="bi bi-arrows-expand"></i> Expand All
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="collapseAll()">
                            <i class="bi bi-arrows-collapse"></i> Collapse All
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Site Structure Tree</h5>
                        <div class="tree tree-root" id="tree-container">
                            {self._generate_tree_html(self.root)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function toggleNode(nodeId) {{
            const node = document.getElementById(nodeId);
            const toggleId = nodeId.replace('-children', '');
            const toggle = document.getElementById('toggle-' + toggleId);
            
            if (node.classList.contains('tree-collapsed')) {{
                // Expanding
                node.classList.remove('tree-collapsed');
                toggle.classList.add('expanded');
            }} else {{
                // Collapsing
                node.classList.add('tree-collapsed');
                toggle.classList.remove('expanded');
            }}
        }}
        
        function expandAll() {{
            document.querySelectorAll('.tree-children').forEach(node => {{
                node.classList.remove('tree-collapsed');
            }});
            document.querySelectorAll('.node-toggle').forEach(toggle => {{
                toggle.classList.add('expanded');
            }});
        }}
        
        function collapseAll() {{
            document.querySelectorAll('.tree-children').forEach(node => {{
                node.classList.add('tree-collapsed');
            }});
            document.querySelectorAll('.node-toggle').forEach(toggle => {{
                toggle.classList.remove('expanded');
            }});
        }}
    </script>
</body>
</html>
"""
        return html
    
    def _generate_tree_html(self, node: PageNode, node_id: str = "root", depth: int = 0) -> str:
        """
        Generate HTML for a tree node
        
        Args:
            node: Node to generate HTML for
            node_id: Unique ID for the node
            depth: Current depth in tree
            
        Returns:
            HTML string
        """
        # Add class for directories
        node_classes = 'tree-node'
        if node.is_directory:
            node_classes += ' is-directory'
            
        html = f'<div class="{node_classes}">'
        
        # Node content
        if node.children:
            # Start expanded for top levels, collapsed for deeper levels
            is_expanded = depth < 2
            toggle_class = 'node-toggle expanded' if is_expanded else 'node-toggle'
            html += f'<span class="{toggle_class}" id="toggle-{node_id}" onclick="toggleNode(\'{node_id}-children\')">▶</span>'
        else:
            html += '<span style="display: inline-block; width: 28px;"></span>'
        
        # Icon
        if node.is_directory:
            html += '<i class="bi bi-folder-fill text-warning node-icon"></i>'
        else:
            html += '<i class="bi bi-file-earmark text-primary node-icon"></i>'
        
        # Name/URL
        if node.url:
            html += f'<a href="{node.url}" target="_blank" class="node-url">{node.name}</a>'
        else:
            html += f'<span class="node-name">{node.name}</span>'
        
        # Stats badges
        if node.stats['total_pages'] > 0:
            html += '<span class="node-stats">'
            
            if node.stats['tested_pages'] == node.stats['total_pages']:
                html += '<span class="badge bg-success stats-badge">Tested</span>'
            elif node.stats['tested_pages'] > 0:
                html += f'<span class="badge bg-warning stats-badge">{node.stats["tested_pages"]}/{node.stats["total_pages"]} tested</span>'
            else:
                html += '<span class="badge bg-secondary stats-badge">Not tested</span>'
            
            if node.stats['pages_with_issues'] > 0:
                html += f'<span class="badge bg-danger stats-badge">{node.stats["pages_with_issues"]} issues</span>'
            
            if node.stats['total_violations'] > 0:
                html += f'<span class="text-danger ms-2">({node.stats["total_violations"]} violations)</span>'
            
            html += '</span>'
        
        html += '</div>'
        
        # Children
        if node.children:
            # Expand top levels by default
            children_class = 'tree-children' if depth < 2 else 'tree-children tree-collapsed'
            html += f'<div class="{children_class}" id="{node_id}-children">'
            for i, child in enumerate(node.children):
                child_id = f"{node_id}-{i}"
                html += self._generate_tree_html(child, child_id, depth + 1)
            html += '</div>'
        
        return html
    
    def to_json(self) -> str:
        """
        Generate JSON report
        
        Returns:
            JSON string
        """
        if not self.tree_data:
            self.generate()
        
        return json.dumps(self.tree_data, indent=2, default=str)
    
    def to_csv(self) -> str:
        """
        Generate CSV report with flattened tree structure
        
        Returns:
            CSV string
        """
        if not self.tree_data:
            self.generate()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Path',
            'URL',
            'Type',
            'Level',
            'Total Pages',
            'Tested Pages',
            'Pages with Issues',
            'Violations',
            'Warnings'
        ])
        
        # Flatten tree and write rows
        self._write_csv_node(writer, self.root, '', 0)
        
        return output.getvalue()
    
    def _write_csv_node(self, writer, node: PageNode, path: str, level: int):
        """
        Write a node and its children to CSV
        
        Args:
            writer: CSV writer
            node: Node to write
            path: Current path
            level: Current depth level
        """
        current_path = f"{path}/{node.name}" if path else node.name
        
        writer.writerow([
            current_path,
            node.url or '',
            'Directory' if node.is_directory else 'Page',
            level,
            node.stats['total_pages'],
            node.stats['tested_pages'],
            node.stats['pages_with_issues'],
            node.stats['total_violations'],
            node.stats['total_warnings']
        ])
        
        # Write children
        for child in node.children:
            self._write_csv_node(writer, child, current_path, level + 1)
    
    def save(self, format: str = 'html') -> str:
        """
        Save report to file
        
        Args:
            format: Output format (html, json, csv, pdf)
            
        Returns:
            Path to saved file
        """
        from pathlib import Path
        import os
        
        # Get reports directory - check multiple possible locations
        # First try to get from app config if available
        reports_dir = None
        
        # Try getting from Flask current_app if available
        try:
            from flask import current_app
            if current_app and hasattr(current_app, 'app_config'):
                reports_dir = Path(current_app.app_config.REPORTS_DIR)
        except:
            pass
        
        # Fall back to environment variable or default
        if not reports_dir:
            reports_dir_str = os.environ.get('REPORTS_DIR', '/Users/bob3/Desktop/auto_a11y_python/reports')
            reports_dir = Path(reports_dir_str)
        
        # Ensure directory exists
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"page_structure_{self.website.id}_{timestamp}.{format}"
        filepath = reports_dir / filename
        
        # Generate content based on format
        if format == 'html':
            content = self.to_html()
        elif format == 'json':
            content = self.to_json()
        elif format == 'csv':
            content = self.to_csv()
        elif format == 'pdf':
            # For PDF, we'll generate HTML and note that PDF conversion would be needed
            content = self.to_html()
            # In production, you would use a library like weasyprint or pdfkit to convert
            logger.warning("PDF generation not fully implemented, saving as HTML instead")
            filename = filename.replace('.pdf', '.html')
            filepath = reports_dir / filename
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Page structure report saved to {filepath}")
        return str(filepath)