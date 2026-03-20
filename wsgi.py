"""WSGI entry point for production (Gunicorn / Render)."""

from config import config
from auto_a11y.web.app import create_app

app = create_app(config)
