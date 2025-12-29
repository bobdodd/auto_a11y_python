"""
Demo site route for Quebec insurance company presentation
Serves the static demo site with intentional accessibility issues
"""

from flask import Blueprint, send_from_directory, current_app
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
demo_bp = Blueprint('demo', __name__)


@demo_bp.route('/')
@demo_bp.route('/<path:filename>')
def serve_demo(filename='index.html'):
    """Serve demo site files"""
    try:
        # Get demo site directory
        demo_dir = Path(__file__).parent.parent.parent.parent / 'demo_site'

        # Handle subdirectories (css, js, images, pdfs)
        file_path = demo_dir / filename

        # If it's a directory or doesn't exist, try appending index.html
        if file_path.is_dir():
            filename = str(Path(filename) / 'index.html')
            file_path = demo_dir / filename

        # Check if file exists
        if not file_path.exists():
            logger.warning(f"Demo file not found: {filename}")
            return f"File not found: {filename}", 404

        # Get the directory and filename
        directory = str(file_path.parent)
        file_name = file_path.name

        return send_from_directory(directory, file_name)

    except Exception as e:
        logger.error(f"Error serving demo file {filename}: {e}", exc_info=True)
        return f"Error: {str(e)}", 500


@demo_bp.route('/info')
def demo_info():
    """Information about the demo site and its intentional issues"""
    return """
    <html>
    <head><title>Demo Site Information</title></head>
    <body style="font-family: sans-serif; max-width: 800px; margin: 50px auto; line-height: 1.6;">
        <h1>Quebec Insurance Company Demo Site</h1>
        <p>This demo site contains <strong>intentional accessibility issues</strong> for presentation purposes.</p>

        <h2>Intentional Issues Included:</h2>
        <ol>
            <li><strong>ErrMissingAccessibleName</strong> - Icon buttons without accessible names (toolbar)</li>
            <li><strong>ErrTimersWithoutControls</strong> - Auto-playing carousel without pause/stop controls</li>
            <li><strong>ErrDocumentLinkWrongLanguage</strong> - English PDF linked from French page without warning</li>
            <li><strong>WarnInfiniteAnimationSpinner</strong> - Loading spinner that doesn't announce to screen readers</li>
            <li><strong>ErrInappropriateMenuRole</strong> - Main navigation using incorrect menu role</li>
            <li><strong>Interactive map with aria-hidden="true"</strong> - Map is hidden but still keyboard focusable</li>
            <li><strong>Language switcher buried in tab order</strong> - tabindex="99" makes it hard to reach</li>
            <li><strong>Fake headings</strong> - Styled divs instead of proper h2, h3 elements (AI detection)</li>
            <li><strong>Mixed language content without lang attributes</strong> - English phrases in French pages (AI detection)</li>
            <li><strong>Color contrast issues</strong> - Desktop sidebar with insufficient contrast (#999 on #ddd)</li>
            <li><strong>Responsive design issues</strong> - Desktop-only content with accessibility problems</li>
        </ol>

        <h2>Access the Demo:</h2>
        <ul>
            <li><a href="/demo/">French version (index.html)</a></li>
            <li><a href="/demo/index-en.html">English version</a></li>
            <li><a href="/demo/services.html">Services page (French)</a></li>
        </ul>

        <h2>For Testing:</h2>
        <p>Add this URL to autoA11y as a website: <code>http://127.0.0.1:5001/demo/</code></p>
        <p>Then scan the pages to detect all intentional accessibility issues.</p>

        <p><a href="/">Back to autoA11y</a></p>
    </body>
    </html>
    """
