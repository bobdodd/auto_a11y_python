#!/usr/bin/env bash
# Render build script — runs on every deploy
set -o errexit

echo "==> Installing system packages..."
apt-get update -qq
# WeasyPrint dependencies
apt-get install -y -qq --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    libffi-dev libcairo2 libglib2.0-0 shared-mime-info

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Running database setup..."
python -c "
from config import config
from auto_a11y.core.database import Database
db = Database(config.MONGODB_URI, config.DATABASE_NAME)
if db.test_connection():
    db.create_indexes()
    print('Database indexes created.')
else:
    print('WARNING: Could not connect to database during build.')
"

# Install Playwright + Chromium only when BROWSER_MODE is "local"
if [ "${BROWSER_MODE:-local}" = "local" ]; then
    echo "==> Installing Playwright Chromium (BROWSER_MODE=local)..."
    # Playwright's own deps installer handles the remaining OS libraries
    python -m playwright install --with-deps chromium
else
    echo "==> Skipping Playwright install (BROWSER_MODE=${BROWSER_MODE})"
fi

echo "==> Build complete."
