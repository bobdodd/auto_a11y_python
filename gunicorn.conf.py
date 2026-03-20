"""Gunicorn production configuration for Render deployment."""

import os

# Bind to 0.0.0.0 on the PORT that Render injects (default 10000)
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"

# Workers: Render recommends 2-4 for most apps
workers = int(os.getenv("WEB_CONCURRENCY", 2))

# Timeout: generous for long-running accessibility tests
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))

# Access log to stdout so Render captures it
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
