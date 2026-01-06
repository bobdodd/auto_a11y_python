"""
Flask application factory
"""

from flask import Flask, render_template, jsonify, request, session, g, redirect, url_for
from flask_cors import CORS
from flask_babel import Babel
from flask_login import LoginManager, current_user, login_required
import logging

from auto_a11y.core import Database
from auto_a11y.web.routes import (
    projects_bp,
    websites_bp,
    pages_bp,
    testing_bp,
    reports_bp,
    api_bp,
    scripts_bp,
    website_users_bp,
    project_users_bp,
    project_participants_bp,
    recordings_bp,
    drupal_sync_bp,
    discovered_pages_bp,
    automated_tests_bp,
    auth_bp
)
from auto_a11y.web.routes.demo import demo_bp

logger = logging.getLogger(__name__)


def create_app(config):
    """
    Create Flask application
    
    Args:
        config: Application configuration object
        
    Returns:
        Flask app instance
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Apply configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG
    
    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Configure Flask-Babel for internationalization
    import os
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'fr']
    # Use absolute path to translations directory
    translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = translations_dir

    logger.info(f"Translations directory: {translations_dir}")
    logger.info(f"Translations directory exists: {os.path.exists(translations_dir)}")
    if os.path.exists(translations_dir):
        logger.info(f"Contents: {os.listdir(translations_dir)}")

    def get_locale():
        """Determine the best locale to use for the request"""
        # Check if user explicitly set language
        if 'language' in session:
            locale = session['language']
            logger.debug(f"Locale from session: {locale}")
            return locale
        # Otherwise, try to match browser language preferences
        locale = request.accept_languages.best_match(['en', 'fr']) or 'en'
        logger.debug(f"Locale from browser: {locale}")
        return locale

    babel = Babel(app, locale_selector=get_locale)

    # Initialize database connection (needed before Flask-Login)
    app.db = Database(config.MONGODB_URI, config.DATABASE_NAME)

    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return app.db.get_app_user(user_id)

    # Make get_locale, config, and current_user available to all templates
    @app.context_processor
    def inject_globals():
        return dict(
            get_locale=get_locale,
            show_error_codes=config.SHOW_ERROR_CODES,
            current_user=current_user
        )
    
    # Store config for access in routes
    app.app_config = config
    
    # Initialize test configuration with database and debug mode
    from auto_a11y.config import get_test_config
    app.test_config = get_test_config(
        database=app.db,
        debug_mode=config.DEBUG
    )
    
    # Start task runner
    from auto_a11y.core.task_runner import task_runner
    task_runner.start()
    
    # Language switching route
    @app.route('/set-language/<language>')
    def set_language(language):
        """Set the user's preferred language"""
        if language in ['en', 'fr']:
            session['language'] = language
        return jsonify({'status': 'success', 'language': language})

    # Register blueprints
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(websites_bp, url_prefix='/websites')
    app.register_blueprint(pages_bp, url_prefix='/pages')
    app.register_blueprint(testing_bp, url_prefix='/testing')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(scripts_bp, url_prefix='/scripts')
    app.register_blueprint(website_users_bp, url_prefix='/users')
    app.register_blueprint(project_users_bp, url_prefix='')
    app.register_blueprint(project_participants_bp, url_prefix='')
    app.register_blueprint(recordings_bp, url_prefix='/recordings')
    app.register_blueprint(drupal_sync_bp, url_prefix='/drupal')
    app.register_blueprint(discovered_pages_bp, url_prefix='')
    app.register_blueprint(automated_tests_bp, url_prefix='/automated_tests')
    app.register_blueprint(demo_bp, url_prefix='/demo')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Global login requirement - protect all routes except auth, static, demo, and health
    @app.before_request
    def require_login():
        """Require login for all routes except auth, static, demo, and health endpoints"""
        allowed_endpoints = [
            'auth.login', 'auth.register', 'auth.logout',
            'static', 'health', 'set_language'
        ]
        if request.endpoint and request.endpoint in allowed_endpoints:
            return None
        if request.endpoint and request.endpoint.startswith('static'):
            return None
        if request.endpoint and request.endpoint.startswith('demo.'):
            return None
        if request.path.startswith('/demo'):
            return None
        if not current_user.is_authenticated:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login', next=request.url))

    # Custom Jinja filters
    @app.template_filter('error_code_only')
    def error_code_only(violation_id):
        """Extract just the error code from full violation ID (e.g., 'event_handlers_WarnTabindexDefaultFocus' -> 'WarnTabindexDefaultFocus')"""
        if not violation_id or '_' not in violation_id:
            return violation_id

        # Split by underscore and find the part that starts with Err/Warn/Info/Disco/AI
        parts = violation_id.split('_')
        for i, part in enumerate(parts):
            if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                # Join from here to the end
                return '_'.join(parts[i:])

        # If no match, return original
        return violation_id

    @app.template_filter('wcag_understanding_url')
    def wcag_understanding_url(criterion):
        """Generate WCAG 2.2 Understanding URL for a criterion"""
        from auto_a11y.reporting.wcag_mapper import format_wcag_link
        return format_wcag_link(criterion, 'understanding')

    @app.template_filter('wcag_quickref_url')
    def wcag_quickref_url(criterion):
        """Generate WCAG 2.2 Quick Reference URL for a criterion"""
        from auto_a11y.reporting.wcag_mapper import format_wcag_link
        return format_wcag_link(criterion, 'quickref')

    @app.template_filter('wcag_name')
    def wcag_name(criterion):
        """Extract just the name from a WCAG criterion string (e.g., '2.4.8 Location (Level AAA)' -> 'Location')"""
        # Handle both full format "2.4.8 Location (Level AAA)" and short format "2.4.8"
        if not criterion:
            return criterion

        # Split and check if we have a name part
        parts = str(criterion).split()
        if len(parts) >= 2:
            # Extract name (everything after the number, before the level)
            # e.g., "2.4.8 Location (Level AAA)" -> parts[1] = "Location"
            # e.g., "5.2.4 Accessibility Supported" -> parts[1:] = ["Accessibility", "Supported"]
            name_parts = []
            for i, part in enumerate(parts[1:], 1):
                if part.startswith('('):  # Stop at "(Level"
                    break
                name_parts.append(part)
            return ' '.join(name_parts) if name_parts else parts[0]

        return criterion

    # Main routes
    @app.route('/')
    def index():
        """Home page - redirect to dashboard if logged in"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard"""
        # Get only the latest test results for each page
        pages = list(app.db.pages.find({'status': 'tested'}))
        total_violations = 0
        total_warnings = 0
        total_info = 0
        total_discovery = 0
        
        for page in pages:
            # Get the latest test result for this page
            # Note: page_id is stored as string in test_results
            latest_result = app.db.test_results.find_one(
                {'page_id': str(page['_id'])},
                sort=[('created_at', -1)]
            )
            
            if latest_result:
                # For existing data, we need to categorize from violations array
                # New data will have separate arrays
                if 'info' in latest_result and 'discovery' in latest_result:
                    # New format with separate arrays
                    total_violations += len(latest_result.get('violations', []))
                    total_warnings += len(latest_result.get('warnings', []))
                    total_info += len(latest_result.get('info', []))
                    total_discovery += len(latest_result.get('discovery', []))
                else:
                    # Old format - categorize based on ID patterns
                    for item in latest_result.get('violations', []):
                        item_id = item.get('id', '')
                        if '_Err' in item_id:
                            total_violations += 1
                        elif '_Warn' in item_id:
                            total_warnings += 1
                        elif '_Info' in item_id:
                            total_info += 1
                        elif '_Disco' in item_id:
                            total_discovery += 1
                        else:
                            total_violations += 1  # Default to violations
                    
                    # Also count items in warnings array
                    total_warnings += len(latest_result.get('warnings', []))
        
        stats = {
            'projects': len(app.db.get_projects()),
            'total_pages': app.db.pages.count_documents({}),
            'tested_pages': app.db.pages.count_documents({'status': 'tested'}),
            'total_violations': total_violations,
            'total_warnings': total_warnings,
            'total_info': total_info,
            'total_discovery': total_discovery,
            'total_test_results': app.db.test_results.count_documents({})
        }
        return render_template('dashboard.html', stats=stats, config=app.app_config)
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if app.db.client else 'disconnected'
        })
    
    @app.route('/help')
    def help():
        """Help and documentation page"""
        return render_template('help.html')

    @app.route('/screenshots/<path:filename>')
    def serve_screenshot(filename):
        """Serve screenshot files"""
        from flask import send_from_directory
        import os
        screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
        return send_from_directory(screenshots_dir, filename)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """404 error handler"""
        if '/api/' in request.path:
            return jsonify({'error': 'Endpoint not found'}), 404
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 error handler"""
        logger.error(f"Internal error: {error}")
        if '/api/' in request.path:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('500.html'), 500
    
    # Cleanup on shutdown
    @app.teardown_appcontext
    def cleanup(exception=None):
        """Cleanup resources"""
        if exception:
            logger.error(f"Request teardown with exception: {exception}")
    
    logger.info("Flask application created")
    return app