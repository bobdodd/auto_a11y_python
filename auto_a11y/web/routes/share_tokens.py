"""
Share token management routes for the admin app.
Allows auditors/admins to create, list, and revoke public share links.
"""

import hashlib

from flask import Blueprint, request, current_app, jsonify, url_for
from flask_login import current_user
from flask_babel import _
from itsdangerous import URLSafeSerializer

from auto_a11y.models import ShareToken, TokenScope
from auto_a11y.models.app_user import UserRole
from auto_a11y.web.routes.auth import project_role_required, get_effective_role

share_tokens_bp = Blueprint('share_tokens', __name__)

TOKEN_SALT = 'public-share-token'


def _get_serializer():
    """Get the URL-safe serializer using the app's secret key"""
    return URLSafeSerializer(current_app.config['SECRET_KEY'], salt=TOKEN_SALT)


def _make_token_hash(token_string: str) -> str:
    """Create a SHA-256 hash of a token string"""
    return hashlib.sha256(token_string.encode('utf-8')).hexdigest()


@share_tokens_bp.route('/projects/<project_id>/share-tokens', methods=['POST'])
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)
def create_project_token(project_id):
    """Create a share token scoped to a project"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': _('Project not found')}), 404

    return _create_token(TokenScope.PROJECT, project_id)


@share_tokens_bp.route('/websites/<website_id>/share-tokens', methods=['POST'])
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)
def create_website_token(website_id):
    """Create a share token scoped to a website"""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': _('Website not found')}), 404

    return _create_token(TokenScope.WEBSITE, website_id)


def _create_token(scope: TokenScope, scope_id: str):
    """Shared logic for creating a token"""
    from datetime import datetime, timedelta

    label = request.form.get('label', '').strip()
    if not label:
        label = f"Share link ({scope.value})"

    expires_days = request.form.get('expires_days', '')

    expires_at = None
    if expires_days and expires_days != 'never':
        try:
            days = int(expires_days)
            if days > 0:
                expires_at = datetime.now() + timedelta(days=days)
        except ValueError:
            pass

    serializer = _get_serializer()
    token_string = serializer.dumps({'scope': scope.value, 'scope_id': scope_id})
    token_hash = _make_token_hash(token_string)

    token = ShareToken(
        scope=scope,
        scope_id=scope_id,
        created_by=current_user.id,
        label=label,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    current_app.db.create_share_token(token)

    public_url = url_for('public.token_landing', token=token_string, _external=True)

    return jsonify({
        'status': 'success',
        'token_id': token.id,
        'public_url': public_url,
        'label': label,
        'expires_at': expires_at.isoformat() if expires_at else None,
    })


@share_tokens_bp.route('/projects/<project_id>/share-tokens', methods=['GET'])
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)
def list_project_tokens(project_id):
    """List share tokens for a project"""
    tokens = current_app.db.get_share_tokens_for_scope(TokenScope.PROJECT, project_id)
    return jsonify({
        'tokens': [_token_to_json(t) for t in tokens]
    })


@share_tokens_bp.route('/websites/<website_id>/share-tokens', methods=['GET'])
@project_role_required(UserRole.ADMIN, UserRole.AUDITOR)
def list_website_tokens(website_id):
    """List share tokens for a website"""
    tokens = current_app.db.get_share_tokens_for_scope(TokenScope.WEBSITE, website_id)
    return jsonify({
        'tokens': [_token_to_json(t) for t in tokens]
    })


@share_tokens_bp.route('/share-tokens/<token_id>/revoke', methods=['POST'])
def revoke_token(token_id):
    """Revoke a share token"""
    # Look up token to find its scope, then check project membership
    token = current_app.db.get_share_token(token_id)
    if not token:
        return jsonify({'error': _('Token not found')}), 404

    # Resolve scope_id to project
    if token.scope == TokenScope.WEBSITE:
        website = current_app.db.get_website(token.scope_id)
        project_id = website.project_id if website else None
    else:
        project_id = token.scope_id

    if not current_user.is_admin():
        role = get_effective_role(current_user, request, project_id=project_id)
        if role not in (UserRole.ADMIN, UserRole.AUDITOR):
            return jsonify({'error': 'Insufficient permissions'}), 403

    success = current_app.db.revoke_share_token(token_id)
    if success:
        return jsonify({'status': 'success', 'message': _('Token revoked')})
    return jsonify({'error': _('Token not found')}), 404


def _token_to_json(token: ShareToken) -> dict:
    """Convert a token to a JSON-safe dict"""
    return {
        'id': token.id,
        'label': token.label,
        'scope': token.scope.value,
        'scope_id': token.scope_id,
        'created_at': token.created_at.isoformat() if token.created_at else None,
        'expires_at': token.expires_at.isoformat() if token.expires_at else None,
        'revoked': token.revoked,
        'last_used': token.last_used.isoformat() if token.last_used else None,
        'use_count': token.use_count,
        'is_valid': token.is_valid,
    }
