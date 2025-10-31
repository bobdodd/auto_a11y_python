"""
Web routes for Auto A11y Python
"""

from .projects import projects_bp
from .websites import websites_bp
from .pages import pages_bp
from .testing import testing_bp
from .reports import reports_bp
from .api import api_bp
from .scripts import scripts_bp
from .website_users import website_users_bp

__all__ = [
    'projects_bp',
    'websites_bp',
    'pages_bp',
    'testing_bp',
    'reports_bp',
    'api_bp',
    'scripts_bp',
    'website_users_bp'
]