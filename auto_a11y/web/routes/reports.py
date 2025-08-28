"""
Report generation routes
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app, url_for, flash, redirect
from auto_a11y.models import PageStatus
from auto_a11y.reporting import ReportGenerator
from datetime import datetime
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)
reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/dashboard')
def reports_dashboard():
    """Reports dashboard"""
    # Get available reports
    reports_dir = current_app.app_config.REPORTS_DIR
    report_files = list(reports_dir.glob('*.xlsx')) + list(reports_dir.glob('*.html'))
    
    reports = []
    for file in sorted(report_files, key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
        reports.append({
            'filename': file.name,
            'size': file.stat().st_size,
            'created': datetime.fromtimestamp(file.stat().st_mtime),
            'type': file.suffix[1:].upper()
        })
    
    return render_template('reports/dashboard.html', reports=reports)


@reports_bp.route('/generate', methods=['POST'])
def generate_report():
    """Generate accessibility report"""
    data = request.get_json()
    
    project_id = data.get('project_id')
    report_type = data.get('format', 'xlsx')
    include_options = data.get('include', {})
    
    if not project_id:
        return jsonify({'error': 'Project ID required'}), 400
    
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Queue report generation
    report_id = f'report_{project_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    return jsonify({
        'success': True,
        'report_id': report_id,
        'message': f'Report generation started',
        'status_url': url_for('reports.report_status', report_id=report_id)
    })


@reports_bp.route('/report/<report_id>/status')
def report_status(report_id):
    """Check report generation status"""
    # In production, check actual job status
    return jsonify({
        'report_id': report_id,
        'status': 'generating',
        'progress': 75,
        'message': 'Generating report...'
    })


@reports_bp.route('/download/<filename>')
def download_report(filename):
    """Download generated report"""
    reports_dir = current_app.app_config.REPORTS_DIR
    file_path = reports_dir / filename
    
    if not file_path.exists():
        return jsonify({'error': 'Report not found'}), 404
    
    # Security check - ensure file is in reports directory
    if not file_path.resolve().parent == reports_dir.resolve():
        return jsonify({'error': 'Invalid file path'}), 403
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )


@reports_bp.route('/project/<project_id>/summary')
def project_summary(project_id):
    """Generate project summary report"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    stats = current_app.db.get_project_stats(project_id)
    websites = current_app.db.get_websites(project_id)
    
    # Get violation breakdown
    violation_summary = {
        'by_category': {},
        'by_severity': {
            'critical': 0,
            'serious': 0,
            'moderate': 0,
            'minor': 0
        },
        'top_issues': []
    }
    
    # Aggregate data from all test results
    for website in websites:
        pages = current_app.db.get_pages(website.id)
        for page in pages:
            if page.status == PageStatus.TESTED:
                result = current_app.db.get_latest_test_result(page.id)
                if result:
                    for violation in result.violations:
                        # Count by category
                        if violation.category not in violation_summary['by_category']:
                            violation_summary['by_category'][violation.category] = 0
                        violation_summary['by_category'][violation.category] += 1
                        
                        # Count by severity
                        violation_summary['by_severity'][violation.impact.value] += 1
    
    return render_template('reports/project_summary.html',
                         project=project,
                         stats=stats,
                         websites=websites,
                         violation_summary=violation_summary)


@reports_bp.route('/export-csv', methods=['POST'])
def export_csv():
    """Export data as CSV"""
    data = request.get_json()
    
    export_type = data.get('type')  # violations, pages, summary
    filters = data.get('filters', {})
    
    # Generate CSV based on type
    # This would be implemented with actual CSV generation
    
    return jsonify({
        'success': True,
        'message': 'CSV export started',
        'download_url': '/reports/download/export.csv'
    })


@reports_bp.route('/generate/page/<page_id>', methods=['POST'])
def generate_page_report(page_id):
    """Generate report for a single page"""
    format = request.form.get('format', 'html')
    include_ai = request.form.get('include_ai', 'true') == 'true'
    
    try:
        # Initialize report generator
        generator = ReportGenerator(current_app.db, current_app.app_config.__dict__)
        
        # Generate report
        report_path = generator.generate_page_report(
            page_id=page_id,
            format=format,
            include_ai=include_ai
        )
        
        # Return file for download
        return send_file(
            report_path,
            as_attachment=True,
            download_name=Path(report_path).name
        )
        
    except Exception as e:
        logger.error(f"Failed to generate page report: {e}")
        flash(f'Failed to generate report: {str(e)}', 'error')
        return redirect(url_for('pages.view_page', page_id=page_id))


@reports_bp.route('/generate/website/<website_id>', methods=['POST'])
def generate_website_report(website_id):
    """Generate report for entire website"""
    format = request.form.get('format', 'html')
    include_ai = request.form.get('include_ai', 'true') == 'true'
    
    try:
        # Initialize report generator
        generator = ReportGenerator(current_app.db, current_app.app_config.__dict__)
        
        # Generate report
        report_path = generator.generate_website_report(
            website_id=website_id,
            format=format,
            include_ai=include_ai
        )
        
        # Return file for download
        return send_file(
            report_path,
            as_attachment=True,
            download_name=Path(report_path).name
        )
        
    except Exception as e:
        logger.error(f"Failed to generate website report: {e}")
        flash(f'Failed to generate report: {str(e)}', 'error')
        return redirect(url_for('websites.view_website', website_id=website_id))


@reports_bp.route('/generate/project/<project_id>', methods=['POST'])
def generate_project_report(project_id):
    """Generate report for entire project"""
    format = request.form.get('format', 'html')
    
    try:
        # Initialize report generator
        generator = ReportGenerator(current_app.db, current_app.app_config.__dict__)
        
        # Generate report
        report_path = generator.generate_project_report(
            project_id=project_id,
            format=format
        )
        
        # Return file for download
        return send_file(
            report_path,
            as_attachment=True,
            download_name=Path(report_path).name
        )
        
    except Exception as e:
        logger.error(f"Failed to generate project report: {e}")
        flash(f'Failed to generate report: {str(e)}', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))